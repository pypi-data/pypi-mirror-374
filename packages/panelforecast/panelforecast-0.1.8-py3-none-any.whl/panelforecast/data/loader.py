import pandas as pd
from pathlib import Path
from typing import Union, Dict, Any

class PanelDataLoader:
    """
    Load and validate panel data from various sources (CSV, DataFrame).
    Supports automatic column standardization, datetime parsing, and structural validation.
    """
    
    @staticmethod
    def load_csv(
        source: Union[str, Path, pd.DataFrame],
        entity_col: str = 'Entity',
        time_col: str = 'Date',
        target_col: str = 'Value',
        **kwargs
    ) -> pd.DataFrame:
        """
        Load panel data from a CSV file or pandas DataFrame.
        
        Args:
            source: File path (str/Path) or pandas DataFrame
            entity_col: Name of entity identifier column
            time_col: Name of time column
            target_col: Name of target/value column
            **kwargs: Passed to pd.read_csv() (ignored if source is DataFrame)
        
        Returns:
            Validated and cleaned DataFrame
        """
        # Load data
        if isinstance(source, (str, Path)):
            try:
                df = pd.read_csv(source, **kwargs)
            except Exception as e:
                raise IOError(f"Failed to read CSV: {e}")
        elif isinstance(source, pd.DataFrame):
            df = source.copy()
        else:
            raise TypeError(f"Expected str, Path, or DataFrame, got {type(source)}")

        # Standardize column names if exactly 3 columns and no match
        if len(df.columns) == 3 and not all(col in df.columns for col in [entity_col, time_col, target_col]):
            df.columns = [entity_col, time_col, target_col]

        # Validate required columns
        required_cols = [entity_col, time_col, target_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Convert time column to datetime
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            try:
                df[time_col] = pd.to_datetime(df[time_col])
            except Exception as e:
                raise ValueError(f"Could not parse '{time_col}' as datetime: {e}")

        # Sort by entity and time
        df = df.sort_values([entity_col, time_col]).reset_index(drop=True)

        return df


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