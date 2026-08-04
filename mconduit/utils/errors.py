from typing import Optional, Dict, Any
from pathlib import Path
import traceback
import textwrap
import sys

from mconduit import text, constants


def clean(text: str) -> str:
    return textwrap.dedent(text.strip("\n")).replace("'", "`").replace('"', "`").strip("\n")


class ConduitError:
    """
    Utility class to group all infos of errors raised by Conduit or its plugins
    """


    _name: str
    _info: Optional[str]
    _docs: Optional[str]
    _traceback: Optional[Dict[str, Any]]


    def __init__(
        self,
        name: str,
        info: Optional[str],
        docs: Optional[str],
        traceback: Optional[Dict[str, Any]]
    ) -> None:
        
        self._name = name
        self._info = info
        self._docs = docs
        self._traceback = traceback


    def __eq__(self, other: object) -> bool:

        if not isinstance(other, ConduitError):
            return False

        if self.name != other.name:
            return False

        try:
            if self.info != other.info:
                return False
        
            if self.docs != other.docs:
                return False

            if self.traceback != other.traceback:
                return False

        except ValueError:
            return False
        
        return True

    
    @property
    def name(self) -> str:
        """
        Exception name
        """

        return self._name


    @property
    def info(self) -> Optional[str]:
        """
        Exception arguments
        """

        return self._info


    @property
    def docs(self) -> Optional[str]:
        """
        Exception documentation
        """

        return self._docs


    @property
    def traceback(self) -> Optional[Dict[str, Any]]:
        """
        Dict containing:

        - file
        - function
        - line
        - code
        """

        return self._traceback


    @staticmethod
    def from_exception(exception: Exception) -> "ConduitError":
        """
        Creates a ConduitError from a raised Exception
        """

        tb = exception.__traceback__
        frames = traceback.extract_tb(tb)
        last_frame = frames[-1] if frames else None

        frame_infos = {
            "file": last_frame.filename,
            "function": last_frame.name,
            "line": last_frame.lineno,
            "code": last_frame.line
        } if last_frame else None

        args = getattr(exception, "args", ())
        info = str(args[0]) if args else None

        return ConduitError(
            name=type(exception).__name__,
            info=info,
            docs=type(exception).__doc__,
            traceback=frame_infos
        )
    

    def to_text(self) -> text.Text:
        """
        Builds a Json Text that can be used in Minecraft
        """

        disp = f"{clean(self.name)}"

        if self.info is not None:
            disp += f": {clean(self.info)}"
        
        elif self.docs is not None:
            disp += f" ({clean(self.docs)})"

        t = text.red(disp)

        if self.traceback is not None:

            tb = text.dark_red("File: ").bold()

            cleaned_path = Path(clean(self.traceback["file"]))

            if constants.PLUGINS_DIR in cleaned_path.parts and "mconduit" not in cleaned_path.parts:

                plugins_dir = Path(constants.PLUGINS_DIR).resolve()
                cleaned_path = cleaned_path.relative_to(plugins_dir)

            elif "mconduit" in cleaned_path.parts:

                conduit_path = constants.CONDUIT_PATH.parent.resolve()
                cleaned_path = cleaned_path.relative_to(conduit_path)
            
            tb += text.red(str(cleaned_path)).italic().endl()
            
            if self.traceback["function"] != "<module>":

                tb += text.dark_red("Function: ").bold()
                tb += text.red(clean(self.traceback["function"])).italic().endl()

            tb += text.dark_red("Line: ").bold()
            tb += text.red(clean(str(self.traceback["line"]))).italic().endl()

            tb += text.dark_red("Code: ").bold()
            tb += text.red(clean(self.traceback["code"])).italic()
            
            t.hover(show_text=tb)

        return t


def get_last_error() -> Optional[ConduitError]:
    """
    Returns the last raised error
    """

    exc_type, exc_value, exc_traceback = sys.exc_info()

    if exc_type is None or exc_value is None:
        return None

    frames = traceback.extract_tb(exc_traceback)
    last_frame = frames[-1] if frames else None

    frame_infos = {
        "file": last_frame.filename,
        "function": last_frame.name,
        "line": last_frame.lineno,
        "code": last_frame.line
    } if last_frame else None

    return ConduitError(
        name=exc_type.__name__,
        info=str(exc_value),
        docs=None,
        traceback=frame_infos,
    )