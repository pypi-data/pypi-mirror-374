from abc import ABC, abstractmethod
import torch
import torch.nn as nn
from typing import Dict, Any, Tuple, Optional

class BasePanelModel(nn.Module, ABC):
    """Base class for all panel forecasting models"""
    
    def __init__(self):
        super().__init__()
        self.is_fitted = False
        self.model_info = {}
    
    @abstractmethod
    def forward(self, input_seq: torch.Tensor, entity_seq: torch.Tensor) -> torch.Tensor:
        """Forward pass of the model"""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return model information"""
        return self.model_info
    
    def count_parameters(self) -> int:
        """Count trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)