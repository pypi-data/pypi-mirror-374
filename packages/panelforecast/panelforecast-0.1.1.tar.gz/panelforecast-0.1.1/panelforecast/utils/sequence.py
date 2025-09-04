import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset
from typing import Tuple, List, Optional

class SequenceGenerator:
    """Generate sequences for neural network training"""
    
    @staticmethod
    def create_sequences(data: pd.DataFrame, 
                        entity_col: str, target_col: str,
                        feature_cols: Optional[List[str]] = None,
                        seq_length: int = 10) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create sequences with optional features"""
        
        xs, ys, es = [], [], []
        
        # Determine input columns
        input_cols = [target_col]
        if feature_cols:
            input_cols.extend(feature_cols)
        
        for entity in data[entity_col].unique():
            entity_data = data[data[entity_col] == entity]
            
            if len(entity_data) <= seq_length:
                continue  # Skip entities with insufficient data
            
            for i in range(len(entity_data) - seq_length):
                # Input sequence (features + target history)
                x = entity_data[input_cols].values[i:i+seq_length]
                # Target (next value)
                y = entity_data[target_col].values[i+seq_length]
                # Entity sequence for embeddings
                e = np.full(seq_length, entity)
                
                xs.append(x)
                ys.append(y)
                es.append(e)
        
        return np.array(xs), np.array(ys), np.array(es)
    
    @staticmethod
    def create_data_loaders(X: np.ndarray, y: np.ndarray, e: np.ndarray,
                          batch_size: int = 32, shuffle: bool = True) -> DataLoader:
        """Create PyTorch DataLoader from sequences"""
        
        X_tensor = torch.from_numpy(X).float()
        y_tensor = torch.from_numpy(y).float().unsqueeze(-1)
        e_tensor = torch.from_numpy(e).long()
        
        dataset = TensorDataset(X_tensor, y_tensor, e_tensor)
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)