"""
Blinkit Quick-Commerce Analytics ETL & Feature Engineering Pipeline
Author: Ayush Kumar Dandapat
Description: Automated ingestion, sanitization, temporal parsing, and 
             business KPI engineering across Blinkit transactional datasets.
"""

import os
import logging
from typing import Dict
import pandas as pd
import numpy as np

# Configure structured enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("BlinkitETL")


class BlinkitETLPipeline:
    """Production ETL Pipeline for Quick-Commerce Operational Analytics."""

    FILE_MAPPING: Dict[str, str] = {
        'blinkit_customers.csv': 'Customers.csv',
        'blinkit_customer_feedback.csv': 'Feedback.csv',
        'blinkit_delivery_performance.csv': 'Delivery.csv',
        'blinkit_inventory.csv': 'Inventory.csv',
        'blinkit_marketing_performance.csv': 'Marketing.csv',
        'blinkit_orders.csv': 'Orders.csv',
        'blinkit_order_items.csv': 'OrderItems.csv',
        'blinkit_products.csv': 'Products.csv'
    }

    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir

    def _sanitize_string_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strip invisible formatting, linebreaks, and edge whitespaces."""
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r'[\r\n]+', ' ', regex=True)
                .str.strip()
            )
            df[col] = df[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})
        return df

    def _process_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse timestamps and compute delivery latency & SLA breach metrics."""
        timestamp_cols = ['order_date', 'promised_delivery_time', 'actual_delivery_time']
        for col in timestamp_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        if 'promised_delivery_time' in df.columns and 'actual_delivery_time' in df.columns:
            # Latency variance in minutes
            df['delay_minutes'] = (
                df['actual_delivery_time'] - df['promised_delivery_time']
            ).dt.total_seconds() / 60.0
            
            # Binary SLA breach flag (1 = late delivery, 0 = on-schedule/early)
            df['is_sla_breach'] = (df['delay_minutes'] > 0).astype(int)

        if 'order_date' in df.columns and 'actual_delivery_time' in df.columns:
            # Total turnaround duration in minutes
            df['fulfillment_duration_mins'] = (
                df['actual_delivery_time'] - df['order_date']
            ).dt.total_seconds() / 60.0

        return df

    def _process_delivery(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize incident remarks and standardize delivery logs."""
        if 'reasons_if_delayed' in df.columns:
            df['reasons_if_delayed'] = df['reasons_if_delayed'].fillna('On Time').str.strip().str.title()
        return df

    def _process_inventory(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize date schemas and calculate stock deficit flags."""
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')

        if 'stock_level' in df.columns and 'reorder_point' in df.columns:
            # Identify stock depletion risks
            df['stock_deficit'] = df['reorder_point'] - df['stock_level']
            df['is_stockout_risk'] = (df['stock_deficit'] > 0).astype(int)

        return df

    def _process_generic_dates(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """Robust parser for auxiliary date fields."""
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        return df

    def run(self) -> None:
        """Execute full transformation lifecycle."""
        logger.info("Starting Blinkit Grocery Analytics ETL Pipeline execution...")

        for raw_filename, clean_filename in self.FILE_MAPPING.items():
            raw_path = os.path.join(self.working_dir, raw_filename)
            clean_path = os.path.join(self.working_dir, clean_filename)

            # Support cases where files are already renamed
            target_source = raw_path if os.path.exists(raw_path) else (
                clean_path if os.path.exists(clean_path) else None
            )

            if not target_source:
                logger.warning(f"Source file not detected: {raw_filename} / {clean_filename}. Skipping.")
                continue

            logger.info(f"Transforming dataset: {os.path.basename(target_source)} -> {clean_filename}")
            df = pd.read_csv(target_source)

            # Stage 1: Text sanitization
            df = self._sanitize_string_data(df)

            # Stage 2: Domain-specific KPI engineering
            if clean_filename == 'Orders.csv':
                df = self._process_orders(df)
            elif clean_filename == 'Delivery.csv':
                df = self._process_delivery(df)
            elif clean_filename == 'Inventory.csv':
                df = self._process_inventory(df)
            elif clean_filename == 'Customers.csv':
                df = self._process_generic_dates(df, 'registration_date')
            elif clean_filename == 'Marketing.csv':
                df = self._process_generic_dates(df, 'date')
            elif clean_filename == 'Feedback.csv':
                df = self._process_generic_dates(df, 'feedback_date')

            # Stage 3: Deduplication & export
            initial_count = len(df)
            df = df.drop_duplicates()
            dedup_diff = initial_count - len(df)
            if dedup_diff > 0:
                logger.info(f"Pruned {dedup_diff} duplicate records from {clean_filename}.")

            df.to_csv(clean_path, index=False)
            logger.info(f"Successfully staged {clean_filename} | Dimensions: {df.shape}")

        logger.info("Pipeline executed successfully. All cleaned datasets are ready.")


if __name__ == "__main__":
    pipeline = BlinkitETLPipeline()
    pipeline.run()
