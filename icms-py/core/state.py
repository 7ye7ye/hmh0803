import numpy as np
import asyncio
import time
from typing import Dict, Any

class AppState:
    def __init__(self):
        self.latest_frame: np.ndarray | None = None
        self.processed_frame: np.ndarray | None = None
        self.latest_vector: str | None = None
        self.last_face_location: Dict | None = None
        self.is_ai_processing: bool = False
        self.lock = asyncio.Lock()
        self.stats: Dict[str, Any] = {
            "total_frames_streamed": 0,
            "ai_tasks_triggered": 0,
            "faces_detected": 0,
            "last_detection_time": None,
            "error_count": 0,
            "fps_report": {
                "start_time": time.time(),
                "frame_count": 0,
                "fps": 0.0
            }
        }

app_state = AppState()