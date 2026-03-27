from typing import Optional, Dict, Any
import traceback
import textwrap
import sys

from mconduit import text


def clean(text: str) -> str:
    return textwrap.dedent(text).replace("'", "`").replace('"', "`")


class ConduitError:
    """
    Utility class to group all infos of errors raised by Conduit or its plugins
    """


    __name: str
    __info: Optional[str]
    __docs: Optional[str]
    __traceback: Optional[Dict[str, Any]]


    def __init__(
        self,
        name: str,
        info: Optional[str],
        docs: Optional[str],
        traceback: Optional[Dict[str, Any]]
    ) -> None:
        
        self.__name = name
        self.__info = info
        self.__docs = docs
        self.__traceback = traceback


    def __eq__(self, other: object) -> bool:

        if not isinstance(other, ConduitError):
            return False

        return (
            self.name == other.name and
            (self.info is not None and (self.info == other.info)) and
            (self.docs is not None and (self.docs == other.docs)) and
            (self.traceback is not None and (self.traceback == other.traceback))
        )

    
    @property
    def name(self) -> str:
        """
        Exception name
        """

        return self.__name


    @property
    def info(self) -> Optional[str]:
        """
        Exception arguments
        """

        return self.__info


    @property
    def docs(self) -> Optional[str]:
        """
        Exception documentation
        """

        return self.__docs


    @property
    def traceback(self) -> Optional[Dict[str, Any]]:
        """
        Dict containing:

        - file
        - function
        - line
        - code
        """

        return self.__traceback


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

        disp = f"{clean(self.__name)}"

        if self.info is not None:
            disp += f": {clean(self.info)}"
        
        elif self.docs is not None:
            disp += f" ({clean(self.docs)})"

        t = text.red(disp)

        if self.traceback is not None:

            tb = text.dark_red("File: ").bold()
            tb += text.red(clean(self.traceback["file"])).italic().endl()
            
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

    if exc_value is None:
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
        name=type(exc_type).__name__,
        info=str(exc_value),
        docs=None,
        traceback=frame_infos,
    )