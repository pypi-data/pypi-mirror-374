import pandas as pd
from pathlib import Path
from typing import Union, Dict, Optional

class PanelDataLoader:
    """
    Load and validate panel data from various sources (CSV, DataFrame).
    
    Supports automatic column standardization, datetime parsing, and structural validation.
    """
    
    @staticmethod
    def load_data(self, source: Union[str, pd.DataFrame], **kwargs) -> 'PanelForecaster':
        """
        Load data from file path or pandas DataFrame.
        
        Args:
            source: Path to CSV file OR a pandas DataFrame
            **kwargs: Passed to PanelDataLoader.load_csv (e.g., entity_col, time_col)
            
        Returns:
            Self (for method chaining)
        """
        # Set defaults
        entity_col = kwargs.pop('entity_col', 'Entity')    # ← pop() removes it from kwargs
        time_col = kwargs.pop('time_col', 'Date')
        target_col = kwargs.pop('target_col', 'Value')
        
        # Now safe to pass kwargs (no duplicates)
        self.data = self.loader.load_csv(
            source,
            entity_col=entity_col,
            time_col=time_col,
            target_col=target_col,
            **kwargs  # any other args (e.g., parse_dates, encoding)
        )
        
        # Validate structure
        self.data_info = self.loader.validate_panel_structure(self.data, entity_col, time_col)
        
        print(f"✅ Loaded panel data: {self.data_info['n_entities']} entities, "
            f"{self.data_info['n_time_periods']} time points")
        return self

    @staticmethod
    def validate_panel_structure(df: pd.DataFrame, entity_col: str, time_col: str) -> Dict:
        """
        Validate and describe the structure of panel data.
        
        Args:
            df: Panel data DataFrame
            entity_col: Entity column name
            time_col: Time column name
        
        Returns:
            Dictionary with metadata about the panel structure
        """
        if df.empty:
            raise ValueError("DataFrame is empty")

        if entity_col not in df.columns:
            raise ValueError(f"Entity column '{entity_col}' not found in data")
        if time_col not in df.columns:
            raise ValueError(f"Time column '{time_col}' not found in data")

        info = {
            'n_entities': df[entity_col].nunique(),
            'n_time_periods': df[time_col].nunique(),
            'total_observations': len(df),
            'is_balanced': False,
            'entities': sorted(df[entity_col].unique().tolist()),
            'time_range': (df[time_col].min(), df[time_col].max()),
            'dtype': dict(df.dtypes),
        }

        # Check balance: same number of observations per entity?
        entity_counts = df.groupby(entity_col).size()
        unique_counts = entity_counts.nunique()
        info['is_balanced'] = unique_counts == 1
        info['min_periods_per_entity'] = entity_counts.min()
        info['max_periods_per_entity'] = entity_counts.max()
        info['mean_periods_per_entity'] = entity_counts.mean()
        info['std_periods_per_entity'] = entity_counts.std()

        return info