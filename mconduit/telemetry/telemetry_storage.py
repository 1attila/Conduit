from typing import Dict, Any
from pathlib import Path
import threading
import json


class TelemetryStorage:

    def __init__(self) -> None:
        
        self.__lock = threading.Lock()
        self.__path = Path.cwd() / "telemetry"

        if not self.__path.exists():
            self.__path.mkdir(parents=True, exist_ok=True)

    
    def store(self, event: Dict[str, Any]) -> None:
        
        file = self.__path / "telemetry.json"

        with self.__lock:
            if file.exists():

                with file.open() as f:
                    try:
                        content = json.load(f)
                    except:
                        content = []
            else:
                content = []

            content.append(event)
            try:
                data = json.dumps(content, indent=4)
                file.write_text(data)
            except:
                pass