import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder, StandardScaler
from typing import Tuple,  Optional, List

class PanelPreprocessor:
    """Advanced preprocessing for panel data"""
    
    def __init__(self):
        self.entity_encoder = None
        self.scalers = {}
        self.feature_scalers = {}
        self.is_fitted = False
    
    def fit_transform(self, data: pd.DataFrame, 
                     entity_col: str, time_col: str, target_col: str,
                     feature_cols: Optional[List[str]] = None,
                     scaler_type: str = 'minmax') -> pd.DataFrame:
        """Fit preprocessor and transform data"""
        
        # Encode entities
        self.entity_encoder = LabelEncoder()
        data[entity_col] = self.entity_encoder.fit_transform(data[entity_col])
        
        # Scale target variable by entity
        entities = data[entity_col].unique()
        for entity in entities:
            entity_mask = data[entity_col] == entity
            entity_data = data[entity_mask]
            
            # Fit scaler on target
            if scaler_type == 'minmax':
                scaler = MinMaxScaler()
            elif scaler_type == 'standard':
                scaler = StandardScaler()
            else:
                raise ValueError("scaler_type must be 'minmax' or 'standard'")
                
            data.loc[entity_mask, target_col] = scaler.fit_transform(
                entity_data[[target_col]]
            ).flatten()
            self.scalers[entity] = scaler
            
            # Scale feature columns if provided
            if feature_cols:
                feature_scaler = MinMaxScaler()
                data.loc[entity_mask, feature_cols] = feature_scaler.fit_transform(
                    entity_data[feature_cols]
                )
                self.feature_scalers[entity] = feature_scaler
        
        self.is_fitted = True
        return data
    
    def transform(self, data: pd.DataFrame, 
                  entity_col: str, target_col: str,
                  feature_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """Transform new data using fitted preprocessor"""
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        data = data.copy()
        
        # Transform entities
        data[entity_col] = self.entity_encoder.transform(data[entity_col])
        
        # Transform target and features
        for entity in data[entity_col].unique():
            if entity in self.scalers:
                entity_mask = data[entity_col] == entity
                data.loc[entity_mask, target_col] = self.scalers[entity].transform(
                    data[entity_mask][[target_col]]
                ).flatten()
                
                if feature_cols and entity in self.feature_scalers:
                    data.loc[entity_mask, feature_cols] = self.feature_scalers[entity].transform(
                        data[entity_mask][feature_cols]
                    )
        
        return data
    
    def split_panel_data(self, data: pd.DataFrame, entity_col: str,
                        train_ratio: float = 0.7, val_ratio: float = 0.15,
                        time_col: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split panel data maintaining temporal order within entities"""
        
        train_data, val_data, test_data = [], [], []
        
        for entity in data[entity_col].unique():
            entity_data = data[data[entity_col] == entity].copy()
            
            # Sort by time if time column provided
            if time_col:
                entity_data = entity_data.sort_values(time_col)
            
            n = len(entity_data)
            train_size = int(n * train_ratio)
            val_size = int(n * val_ratio)
            
            train_data.append(entity_data.iloc[:train_size])
            val_data.append(entity_data.iloc[train_size:train_size + val_size])
            test_data.append(entity_data.iloc[train_size + val_size:])
        
        return (pd.concat(train_data), pd.concat(val_data), pd.concat(test_data))
    
    def inverse_transform_target(self, predictions: np.ndarray, 
                               entity_ids: np.ndarray) -> np.ndarray:
        """Inverse transform predictions back to original scale"""
        result = np.zeros_like(predictions)
        
        for i, (pred, entity_id) in enumerate(zip(predictions, entity_ids)):
            if entity_id in self.scalers:
                result[i] = self.scalers[entity_id].inverse_transform([[pred]])[0, 0]
            else:
                result[i] = pred  # If no scaler, return as is
                
        return result