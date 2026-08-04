from typing import (
    Callable,
    Optional,
    Union,
    List,
    Literal,
    ParamSpec,
    Concatenate,
    Any,
    overload,
    get_origin,
    get_args,
    TYPE_CHECKING
)
import textwrap
import inspect

from mconduit.plugins.flag import Flag
from mconduit import text

if TYPE_CHECKING:
    from mconduit.context import Context


P = ParamSpec("P")
CommandFunc = Callable[Concatenate["Context", P], Any]


class GroupCommandCalled(Exception):
    ...

class MissingSelfArgument(Exception):
    ...

class MissingContextArgument(Exception):
    ...

class CommandNotFound(Exception):
    ...

class CastError(Exception):
    ...

class TooManyParameters(Exception):
    ...

class InsufficientParameters(Exception):
    ...

class ChecksNotPassing(Exception):
    ...

class InsufficientPermission(Exception):
    ...

class ListItemTypeNotSpecified(Exception):
    ...


class Parameter:
    """Command parameter"""

    name: str
    type: object
    needed: bool
    default_value: Optional[Any]
    has_default_value: bool


    def __init__(self, a: inspect.Parameter) -> None:

        self.name = a.name
        self.type = a.annotation
        self.default_value = a.default
        self.has_default_value = False
        self.needed = True

        if type(self.default_value) != type(inspect.Parameter.empty):
            self.needed = False
            self.has_default_value = True


class Command:
    """
    Plugin command
    """

    _name: str
    _aliases: List[str]
    _flags: List[str]
    _docs: str
    _fallback: Callable
    _parameters: List[Parameter]
    _subcommands: List["Command"]
    _list_offset: Optional[int]
    _list_type: Optional[object]
    _checks: List[Callable]
    

    def __init__(
        self,
        fallback: Callable,
        **kwargs
    ) -> None:
        
        self._fallback = fallback # Bind happens in Plugin._recursive_command_bind()
        self._name = kwargs.pop("name", fallback.__name__)
        self._aliases = kwargs.pop("aliases", [])
        self._docs = kwargs.pop("docs", fallback.__doc__)

        kwargs_checks = kwargs.pop("checks", [])
        
        if not isinstance(kwargs_checks, list): # So that users can do checks=check1 instead of checks=[check1]
            kwargs_checks = [kwargs_checks]
        
        self._checks = list(kwargs_checks)

        func_checks = getattr(self._fallback, "_checks", [])
        self._checks.extend(func_checks)
        
        if not isinstance(self._aliases, list):
            self._aliases = [self._aliases]

        parameters = inspect.Signature.from_callable(fallback).parameters
        self._parameters = [Parameter(arg) for arg in parameters.values()]
        self._parameters.pop(0) # 'self' param (bind in Plugin._recursive_command_bind())
        self._subcommands = []
        self._flags = []
        
        if len(self._parameters) == 0:
            raise MissingContextArgument()
        
        if not str(self._parameters[0].type) in ["<class 'mconduit.context.Context'>", "Context"]:
            raise MissingContextArgument(
                f"Found {self._parameters[0].name} of type {self._parameters[0].type} in {self._name}"
            )
            
        self._parameters.pop(0) # 'Context' param
        self._split_flags()
        self._list_type = None
        self._list_offset = self._get_list_offset()

        if self.docs is not None:
            self._docs = textwrap.dedent(self.docs)

    
    def _get_list_offset(self) -> Optional[int]:
        """
        Returns the index where the parameter of type list is, if any

        This automatically sets _list_type aswell
        """

        for i, param in enumerate(self._parameters):
            
            if (
                get_origin(param.type) is list or
                get_origin(param.type) is List
            ):

                list_type = get_args(param.type)

                if len(list_type) == 0:
                    raise ListItemTypeNotSpecified()

                self._list_type = list_type[0]
                return i

        return None
            

    def _split_flags(self) -> None:
        """
        Separates normal parameters from flags
        """

        temp_flags: List[Parameter] = []
        
        for parameter in self._parameters:
            
            if parameter.type is Flag:
                temp_flags.append(parameter)

        for flag in temp_flags:
            
            self._parameters.remove(flag)
            self._flags.append(flag.name)
        
        return None


    def _run_checks(self, ctx: "Context") -> bool:
        """
        Runs all the command checks with the given Context 
        """

        for check in self._checks:
            
            if not check(ctx):
                return False
        
        return True

    
    def _get_command_completions(
        self,
        cmd: List[str],
        ctx: "Context"
    ) -> List[str]:
        """
        Returns all the command and subcommand completions that passes passes the checks
        """

        if not self._run_checks(ctx):
            return []

        command_completions = []
        is_command = cmd[0] in self.names

        if not is_command:
            
            for cname in self.names:
                if cname.startswith(cmd[0]):
                    return [cname]

            return []
        
        if len(cmd) > 1:

            for subcommand in self._subcommands:

                for completion in subcommand._get_command_completions(cmd[1:], ctx):
                    command_completions.append(cmd[0] + completion)

            return command_completions

        for subcommand in self._subcommands:
            command_completions.append(cmd[0] + subcommand.names[0])
            
        command_completions.append(cmd[0] + " ".join(f"<{param.name}>" for param in self._parameters))
        
        return command_completions


    @property
    def names(self) -> List[str]:
        """
        Command name and aliases
        """
        
        return [self._name] + self._aliases
    

    @property
    def subcommands(self) -> List["Command"]:
        """
        Command's subcommands
        """

        return self._subcommands

    
    @property
    def docs(self) -> str:
        """
        Command short doc
        """
        
        return self._docs


    @property
    def fallback(self) -> Callable:
        """
        Function that is associated with this command
        """

        return self._fallback
    
    
    def _execute(
        self,
        ctx: "Context",
        args: List[str],
        flags: List[str]
    ) -> bool:
        """
        Tries to execute the command or it's sub-commands.

        Can raise errors
        """
        
        if not self._run_checks(ctx):
            raise ChecksNotPassing()
        
        if len(args) > 0:
            
            for subcommand in self._subcommands:

                if args[0] in subcommand.names:
                    try:
                        command_args = args[1:] if len(args) > 1 else []

                        if subcommand._execute(ctx, command_args, flags):
                            return True
                    except Exception as e:
                        raise e
        try:
            fn_input = self._prepare_args(ctx, args, flags)
            self._fallback(*fn_input)

            ctx.server.handler.telemetry.command_invoked(
                ctx.server,
                getattr(self._fallback, "__self__"),
                self._name
            )
            return True
        
        except Exception as e:
            raise e


    def _cast(
        self,
        value: str,
        _type: Any
    ) -> object:
        """
        Tries to cast a specific value to it's type

        If type it's Union, tries to cast all it's values until it finds one that works
        """

        if get_origin(_type) is Optional:

            for t in get_args(_type):
                try:
                    return self._cast(value, t)
                except:
                    return None
                
        elif get_origin(_type) is Union:

            for t in get_args(_type):
                try:
                    return self._cast(value, t)
                except:
                    pass
            raise CastError(f"Cannot convert `{value}` into `{_type}`")

        elif get_origin(_type) is Literal:
            return value
        
        elif _type is bool:

            lowered = value.lower()

            if lowered in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
                return True
            elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
                return False
            else:
                raise CastError(f"Cannot convert `{value}` into `bool`")

        try:
            return _type(value)
        except:
            raise CastError(f"Cannot convert `{value}` into `{_type}`")
                

    def _match_args(
        self,
        ctx: "Context",
        args: List[str]
    ) -> List[Any]:
        """
        Match the passed args to the function parameters and  casts them.

        Can handle Lists and default values
        """
        
        if len(self._parameters) == 0:
            if len(args) > 0:
                raise TooManyParameters()
            
            return [ctx]
        
        fn_input: List[Any] = [ctx]
        n_input = len(args)

        if self._list_offset is not None:
            
            args_after_list = len(self._parameters) - self._list_offset - 1
            n_list = max(n_input - args_after_list - self._list_offset, 1)

            try:
                for i in range(self._list_offset):
                    
                    param = self._parameters[i]

                    if i < len(args):
                        item = self._cast(args[i], param.type)
                    elif param.has_default_value:
                        item = param.default_value
                    else:
                        raise InsufficientParameters()
                    
                    fn_input.append(item)

            except Exception as e:
                raise e
            
            if n_input - 1 < self._list_offset:

                if self._list_offset + 1 != len(self._parameters):
                    
                    param = self._parameters[self._list_offset]

                    if param.has_default_value:
                        fn_input.append(param.default_value)
                    else:
                        raise InsufficientParameters()
            
            else:
                param_list = list()

                try:
                    for i in range(self._list_offset, self._list_offset + n_list):
                    
                        param_list.append(
                            self._cast(args[i], self._list_type)
                        )
                except Exception as e:
                    raise e
            
                fn_input.append(param_list)
            
            try:
                for i in range(self._list_offset + 1, len(self._parameters)):
                    
                    param = self._parameters[i]
                    offset = i + n_list - 1

                    if offset < n_input:
                        item = self._cast(args[offset], param.type)
                    elif param.has_default_value:
                        item = param.default_value
                    else:
                        raise InsufficientParameters()

                    fn_input.append(item)
                
            except Exception as e:
                raise e
        else:

            if n_input > len(self._parameters):
                raise TooManyParameters()
            
            try:
                for i, param in enumerate(self._parameters):
                    
                    if i < len(args):
                        item = self._cast(args[i], param.type)
                    elif param.needed:
                        raise InsufficientParameters()
                    else:
                        item = param.default_value
                    
                    fn_input.append(item)

            except Exception as e:
                raise e

        return fn_input
    

    def _prepare_flags(
        self,
        fn_input: List[Any],
        flags: List[str]
    ) -> List[Any]:
        """
        Appends all the flags
        """
        
        for flag in self._flags:
            fn_input.append(f"--{flag}" in flags)

        return fn_input
    

    def _prepare_args(
        self,
        ctx: "Context",
        args: List[str],
        flags: List[str]
    ) -> List[str]:
        """
        Convert and matches all the arguments to pass to the function
        """
        
        fn_input = self._match_args(ctx, args)
        fn_input = self._prepare_flags(fn_input, flags)
        
        return fn_input
    

    def _get_docstring(self, prefix: str="!!") -> text.Text:
        """
        Return command documentation with parameter annotation
        """
        
        t = prefix + str(self._name) + " "
        t += " ".join([f"<{param.name}>" for param in self._parameters])

        if len(self._parameters) > 0:
            t += " "
        
        t += " ".join([f"--{flag}" for flag in self._flags])

        doc = text.bold(t)

        if len(self._aliases) > 0:
            doc += text.gold("\nAliases:")

            for alias in self._aliases:

                al = text.gray(f"{prefix}{alias}").underlined()
                al.hover(show_text="Click to paste in chat!")
                al.click(suggest_command=f"{prefix}{alias}")

                doc += " "
                doc += al

        if self._docs is not None:
            doc += text.italic(f"\n{self._docs.strip()}")

        doc += "\n"

        if len(self._subcommands) > 0:

            doc += text.gold("Subcommands:")

            for subcommand in self._subcommands:

                sb = text.gray(f"{subcommand.names[0]}").underlined()
                sb.hover(show_text="Click to paste in chat!")
                sb.click(suggest_command=f"{prefix} {self._name} {subcommand.names[0]}")
            
                doc += " "
                doc += sb

            doc += "\n\n"

        if len(self._parameters) > 0:
            doc += text.gold("Parameters: \n")

        for param in self._parameters: # This might be replaced by a table

            doc += text.white(f"  • {param.name}: ")
            doc += text.gray(param.type) # type: ignore
            
            if not param.needed:
                doc += text.white(f"={param.default_value}")

            doc += "\n"

        """
        if len(self._flags) > 0:
            doc += "Flags: \n"

        for flag in self._flags:

            doc += f"--{flag}\n" """
        
        return doc
        

    def add_check(self, fn: Callable[["Context"], bool]) -> "Command":
        """
        Adds a check to this command
        """

        self._checks.append(fn)
        return self


    @classmethod
    def group(cls, name: str, **kwargs) -> "Command":
        """
        This function creates commands that can't be invoked alone but it's subcommans can

        e.g:
        ```
        my_base_group = Command.grop("test")

        @my_base_group.command
        def my_command(self, ctx: Context):
            ...
        ```

        > `!! test` will raise `GroupCommandCalled`

        > `!! test my_command` will call `my_command`
        """

        def fallback(self, ctx: "Context"):
            raise GroupCommandCalled()

        return cls(name=name, fallback=fallback, **kwargs)


    @overload
    def command(self, fn: CommandFunc) -> "Command":
        ...


    @overload
    def command(self, fn: None = None, **attrs) -> Callable:
        ...


    def command(
        self,
        fn: Optional[CommandFunc] = None,
        **attrs
    ) -> Union["Command", Callable]:
        """
        A decorator that transforms the function into a Plugin Command
        """

        def decorator(fn: Callable) -> None:
            self._subcommands.append(Command(fn, **attrs))
    
        if fn is not None:
            self._subcommands.append(Command(fn, **attrs))
            return self
        else:
            return decorator


@overload
def command(fn: CommandFunc) -> "Command":
    ...


@overload
def command(fn: None = None, **attrs) -> Callable[[CommandFunc], "Command"]:
    ...


def command(
    fn: Optional[CommandFunc] = None,
    **attrs
) -> Union["Command", Callable[[CommandFunc], "Command"]]:
    """
    A decorator that transforms the function into a Plugin Command
    """

    def decorator(fn: Callable):
        return Command(fn, **attrs)
    
    if fn is not None:
        return Command(fn, **attrs)
    else:
        return decorator