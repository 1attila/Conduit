from typing import Optional
from pathlib import Path
from socketserver import ThreadingMixIn
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading


class ResourcePackHTTPError(Exception):
    pass


class _SafePackHandler(SimpleHTTPRequestHandler):
    """
    HTTP handler that serves files ONLY from a fixed directory.
    No directory listing, no traversal, GET/HEAD only.
    """


    def __init__(self, *args, directory: Path, **kwargs):

        self._root = directory.resolve()
        super().__init__(*args, directory=str(self._root), **kwargs)


    def list_directory(self, path):

        self.send_error(403, "Directory listing not allowed")

        return None


    def do_POST(self):
        self.send_error(405, "Method not allowed")


    def do_PUT(self):
        self.send_error(405, "Method not allowed")


    def do_DELETE(self):
        self.send_error(405, "Method not allowed")


    def log_message(self, format, *args):
        # Silence default noisy logging
        pass


class _ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = False
    allow_reuse_address = True


class ResourcePackHTTPServer:
    """
    Threaded HTTP server for serving Minecraft resource packs.
    """

    def __init__(
        self,
        directory: Path,
        bind_host: str="127.0.0.1",
        public_host: str="127.0.0.1",
        port: int=8000,
    ) -> None:
        
        if not directory.exists():
            raise FileNotFoundError(directory)

        self.directory = directory.resolve()
        self.bind_host = bind_host
        self.public_host = public_host
        self.port = port
        self._server: Optional[_ThreadedHTTPServer] = None
        self._thread: Optional[threading.Thread] = None


    def start(self) -> None:

        if self._server is not None:
            raise ResourcePackHTTPError("Server already running")

        handler = lambda *args, **kwargs: _SafePackHandler(
            *args,
            directory=self.directory,
            **kwargs,
        )

        self._server = _ThreadedHTTPServer(
            (self.bind_host, self.port),
            handler,
        )

        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="ResourcePackHTTPServer"
        )
        self._thread.start()


    def stop(self, timeout: Optional[float]=5) -> None:

        if self._server is None:
            return

        self._server.shutdown()
        self._server.server_close()

        if self._thread is not None:
            self._thread.join(timeout=timeout)
        
        self._server = None
        self._thread = None


    def url_for(self, relative_path: str) -> str:
        """
        Returns the full URL for a given file.
        """

        relative_path = relative_path.lstrip("/")

        return f"http://{self.public_host}:{self.port}/{relative_path}"