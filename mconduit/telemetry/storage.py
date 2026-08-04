from typing import Optional, Dict, List, Any
from pathlib import Path
import threading
import logging
import json


logger = logging.getLogger(__name__)


class TelemetryStorage:


    def __init__(self) -> None:
        
        self._lock = threading.Lock()
        self._file_path = Path.cwd() / "telemetry" / "telemetry.jsonl"

        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    
    def append_event(self, event: Dict[str, Any]) -> None:
        
        with self._lock:

            try:
                with self._file_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(event) + "\n")
                
            except Exception as e:
                logger.error(f"Failed to write telemetry: {e}")

    
    def empty_cache(self) -> None:
        
        with self._lock:
            self._file_path.write_text("")

    
    def get_all_events(self) -> Optional[List[Dict[str, Any]]]:
        
        with self._lock:

            if not self._file_path.exists():
                return None

            try:
                with self._file_path.open("r", encoding="utf-8") as f:

                    events = [json.loads(line) for line in f if line.strip()]

                    return events
            
            except Exception as e:
                logger.error(f"Failed to read telemetry: {e}")

        return None