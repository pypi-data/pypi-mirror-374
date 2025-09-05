import os
import time
import requests
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
import numpy as np

from pathlib import Path
from datetime import datetime, timedelta

from rtedata.tools import Logger
from rtedata.catalog import Catalog

class Retriever:
    def __init__(self, token: str, logger: Logger, catalog: Catalog):
        self.token = token
        self.logger = logger
        self.catalog = catalog

        self.headers = {
            "User-Agent": "rtedata python package (contact: henriupton99@gmail.com)",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _get_request_content_from_key(self, key: str) -> str:
        if key not in self.catalog.keys:
            raise KeyError(f"Invalid input 'data_type' keyword: '{key}'. Must be one of {self.catalog.keys}")
        request_url, catalog_url, docs_url, category, schema = self.catalog.get_key_content(key)
        return request_url, catalog_url, docs_url, category, schema
    
    @staticmethod
    def _convert_date_to_iso8601(date: datetime) -> datetime:
        return date.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _convert_date_to_datetime(date_str: str) -> datetime:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return date
        except ValueError:
            raise ValueError("Invalid date format. Expected 'YYYY-MM-DD HH:MM:SS'")
    
    def _generate_tasks(self, start_date: str, end_date: str, base_url: str) -> list[str]:
        task_start_date = start_date
        tasks = []
        while task_start_date < end_date:
            task_end_date = min(task_start_date + timedelta(days=4), end_date)
            start = self._convert_date_to_iso8601(task_start_date - timedelta(days=1))
            end = self._convert_date_to_iso8601(task_end_date + timedelta(days=1))
            tasks.append(f"{base_url}?start_date={start}&end_date={end}")
            task_start_date = task_end_date
        return tasks

    def retrieve(self, start_date: str, end_date: str, data_type: list[str] | str, output_dir: str | None = None) -> dict:
        
        if output_dir is not None:
          output_dir = Path(output_dir)
          if not output_dir.exists():
              os.makedirs(output_dir, exist_ok=True)

        if isinstance(data_type, str):
            data_type = data_type.split(",")

        start_date = self._convert_date_to_datetime(start_date)
        end_date = self._convert_date_to_datetime(end_date)

        if (end_date - start_date).days < 1:
            raise ValueError("Retrieval error : Time difference between input end_date and start_date must be greather than 1 day")
        
        dfs = {}

        for dtype in data_type:
            start_time = time.time()
            request_url, catalog_url, docs_url, category, schema = self._get_request_content_from_key(dtype)
            tasks = self._generate_tasks(start_date, end_date, request_url)
            dfs_tasks = []

            for url in tasks:
                self.logger.info(f"Requesting '{dtype}' from URL: {url}")
                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    data = next(iter(data.values()))
                    df = pd.json_normalize(data, sep="_", errors="ignore", **schema)
                    df = df.replace({None: np.nan})
                    if not df.empty:
                        dfs_tasks.append(df)
                else:
                    self.logger.error(f"Failed to retrieve '{dtype}': {response.status_code} - {response.text}")
                    if docs_url is not None:
                        self.logger.info(f"You can check the related docs at : {docs_url}")
              
            if len(dfs_tasks) == 0:
                self.logger.warning(f"No available data found for data_type={dtype} between given dates. It will then not appear in the resulting dict of datasets")
                if docs_url is not None:
                    self.logger.info(f"You can check the related docs at : {docs_url}")
                continue
            
            for colname in dfs_tasks[0].columns:
                if any(df[colname].isna().all() for df in dfs_tasks):
                    self.logger.warning(f"Detected column '{colname}' with all NA values. It will be removed from resulting dataframe as it is not a consistent column")
                    dfs_tasks = [df.drop([colname], axis=1) for df in dfs_tasks]
            
            df_final = pd.concat(dfs_tasks)
            df_final.drop_duplicates(inplace=True)
                
            if output_dir is not None:
                start = start_date.strftime("%Y%m%d")
                end = end_date.strftime("%Y%m%d")
                filepath = os.path.join(output_dir, f"{dtype}_{start}-{end}.csv")
                df_final.to_csv(filepath, sep=",", index=False)
                self.logger.info(f"Data saved at path : {filepath}")
            
                time.sleep(2)
            
            else:
                elapsed = round(time.time() - start_time, 4)
                self.logger.info(f"Success: '{dtype}' retrieved in {elapsed} seconds")
                dfs[dtype] = df_final

        return dfs
