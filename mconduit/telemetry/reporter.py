from typing import Dict, Any
import urllib.request
import threading
import logging
import random
import json
import time

from .storage import TelemetryStorage


logger = logging.getLogger(__name__)


class TelemetryReporter(threading.Thread):


    def __init__(self, endpoint: str) -> None:

        super().__init__(name="TelemetryReporter")

        self.endpoint = endpoint
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._storage = TelemetryStorage()

        self._interval = 60 * 5 # 5 minutes
        self._initial_delay = random.uniform(10.0, 60.0)


    
    def stop(self):
        
        self._stop_event.set()
        self._report()

    
    def append_event(self, event: Dict[str, Any]) -> None:
        self._storage.append_event(event)


    def _report(self) -> None:

        events = self._storage.get_all_events()

        if events is None:
            return

        payload = json.dumps({"events": events}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        
        req = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers=headers,
            method="POST"
        )

        for attempt in range(3):

            try:
                with urllib.request.urlopen(req, timeout=10.0) as response:

                    if response.satus in [200, 201]:

                        self._storage.empty_cache()
                        return

            except Exception as e:
                time.sleep(1)


    def run(self):

        self._stop_event.wait(self._initial_delay)

        while not self._stop_event.is_set():
            
            self._report()
            self._stop_event.wait(self._interval)