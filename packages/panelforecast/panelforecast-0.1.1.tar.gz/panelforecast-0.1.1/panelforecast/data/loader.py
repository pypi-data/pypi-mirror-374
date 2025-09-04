import pandas as pd
from pathlib import Path
from typing import Union, Dict

class PanelDataLoader:
    """Load and validate panel data from various sources"""
    
    @staticmethod
    def load_csv(file_path: Union[str, Path], 
                 entity_col: str = 'Entity',
                 time_col: str = 'Date', 
                 target_col: str = 'Value',
                 **kwargs) -> pd.DataFrame:
        """Load panel data from CSV file"""
        df = pd.read_csv(file_path, **kwargs)
        
        # Standardize column names
        if len(df.columns) == 3 and not all(col in df.columns for col in [entity_col, time_col, target_col]):
            df.columns = [entity_col, time_col, target_col]
        
        # Validate required columns
        required_cols = [entity_col, time_col, target_col]
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")
        
        # Convert time column to datetime
        df[time_col] = pd.to_datetime(df[time_col])
        
        return df
    
    @staticmethod
    def validate_panel_structure(df: pd.DataFrame, entity_col: str, time_col: str) -> Dict:
        """Validate and describe panel data structure"""
        info = {
            'n_entities': df[entity_col].nunique(),
            'n_time_periods': df[time_col].nunique(),
            'total_observations': len(df),
            'is_balanced': False,
            'entities': df[entity_col].unique().tolist(),
            'time_range': (df[time_col].min(), df[time_col].max())
        }
        
        # Check if balanced panel
        entity_counts = df.groupby(entity_col).size()
        info['is_balanced'] = len(entity_counts.unique()) == 1
        info['min_periods_per_entity'] = entity_counts.min()
        info['max_periods_per_entity'] = entity_counts.max()
        
        return info
