#!/usr/bin/env python3
"""
Auto-fix data quality issues
Self-healing script that detects and fixes common data problems
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAutoFix:
    """Automatically detect and fix data quality issues"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.fixes_applied = []
        
    def load_data(self) -> pd.DataFrame:
        """Load data with error handling"""
        try:
            return pd.read_csv(self.data_path)
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def fix_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix missing values with intelligent imputation"""
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            logger.info(f"Found {missing_count} missing values - applying fixes...")
            
            # Numeric columns: fill with median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isnull().any():
                    median_val = df[col].median()
                    df[col].fillna(median_val, inplace=True)
                    self.fixes_applied.append(f"Filled {col} missing values with median: {median_val:.2f}")
            
            # Categorical columns: fill with mode
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if df[col].isnull().any():
                    mode_val = df[col].mode()[0] if not df[col].mode().empty else 'UNKNOWN'
                    df[col].fillna(mode_val, inplace=True)
                    self.fixes_applied.append(f"Filled {col} missing values with mode: {mode_val}")
        
        return df
    
    def fix_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cap extreme outliers using IQR method"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if outliers > 0:
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                self.fixes_applied.append(f"Capped {outliers} outliers in {col}")
        
        return df
    
    def fix_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            df = df.drop_duplicates()
            self.fixes_applied.append(f"Removed {duplicates} duplicate rows")
        
        return df
    
    def fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix incorrect data types"""
        for col in df.columns:
            # Try to convert object columns to numeric if possible
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                    self.fixes_applied.append(f"Converted {col} to numeric type")
                except (ValueError, TypeError):
                    pass  # Keep as object
        
        return df
    
    def validate_and_fix(self) -> bool:
        """Run all validation and fixes"""
        try:
            logger.info(f"Loading data from {self.data_path}...")
            df = self.load_data()
            
            original_shape = df.shape
            logger.info(f"Original data shape: {original_shape}")
            
            # Apply all fixes
            df = self.fix_missing_values(df)
            df = self.fix_duplicates(df)
            df = self.fix_outliers(df)
            df = self.fix_data_types(df)
            
            # Save fixed data
            df.to_csv(self.data_path, index=False)
            
            logger.info(f"✅ Data fixes completed. Final shape: {df.shape}")
            if self.fixes_applied:
                logger.info("Fixes applied:")
                for fix in self.fixes_applied:
                    logger.info(f"  - {fix}")
            else:
                logger.info("No fixes needed - data quality is good!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Auto-fix failed: {e}")
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-fix data quality issues')
    parser.add_argument('--data-path', default='data/raw/housing.csv',
                       help='Path to data file')
    args = parser.parse_args()
    
    fixer = DataAutoFix(args.data_path)
    success = fixer.validate_and_fix()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
