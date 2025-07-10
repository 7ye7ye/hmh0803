from abc import ABC, abstractmethod
import numpy as np
from typing import List, Dict, Any

class BaseModel(ABC):
    """Abstract base class for all AI models"""
    
    def __init__(self):
        self.is_initialized = False
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the model (load weights, etc.)"""
        pass
        
    @abstractmethod
    async def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess input frame before inference"""
        pass
        
    @abstractmethod
    async def inference(self, input_data: np.ndarray) -> Any:
        """Run model inference"""
        pass
        
    @abstractmethod
    async def postprocess(self, inference_output: Any) -> List[Dict[str, Any]]:
        """Postprocess inference output to standard format"""
        pass
        
    async def __call__(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Process a single frame through the full pipeline"""
        if not self.is_initialized:
            await self.initialize()
            self.is_initialized = True
            
        preprocessed = await self.preprocess(frame)
        inference_output = await self.inference(preprocessed)
        results = await self.postprocess(inference_output)
        return results 