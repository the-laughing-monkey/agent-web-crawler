import aiofiles
import asyncio
import subprocess
import csv
import os
import re
import json
from settings import DEFAULT_STATE_FILE
import logging

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.lock = asyncio.Lock()  # Ensure the lock is initialized
        self.cached_content_dir = "data/cached_content"
        self.cached_content_index = "data/cached_content_index.csv"
        os.makedirs(self.cached_content_dir, exist_ok=True)
        self.create_index_file_if_not_exists()

# content cachers and content caching code
    def create_index_file_if_not_exists(self):
        if not os.path.exists(self.cached_content_index):
            with open(self.cached_content_index, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "URL", "File Path"])

    def save_cached_content(self, name: str, url: str, main_content: str, pricing_content: str):
        if main_content is None or pricing_content is None:
            logger.warning(f"Attempt to save None content for {url}")
        else:
            logger.debug(f"Saving content for {url}: {main_content[:100]}")  # Log first 100 characters of main content
        
        main_file_name = f"{name}_{url.replace('/', '_')}_main.txt"
        pricing_file_name = f"{name}_{url.replace('/', '_')}_pricing.txt"
        main_file_path = os.path.join(self.cached_content_dir, main_file_name)
        pricing_file_path = os.path.join(self.cached_content_dir, pricing_file_name)

        with open(main_file_path, 'w', encoding='utf-8') as main_file:
            main_file.write(main_content)
        with open(pricing_file_path, 'w', encoding='utf-8') as pricing_file:
            pricing_file.write(pricing_content)

        logger.debug(f"Saving content for {url}: {main_content[:100]}")
        logger.debug(f"Saving content for {url}: {pricing_content[:100]}")

        self.update_index_file(name, url, main_file_path, pricing_file_path)


    def get_cached_content(self, url: str):
        main_file_path, pricing_file_path = self.get_file_paths_from_index(url)
        if not main_file_path or not os.path.exists(main_file_path):
            self.remove_from_index_file(url)
            return None, None
        with open(main_file_path, 'r') as main_file:
            main_content = main_file.read()
        if pricing_file_path and os.path.exists(pricing_file_path):
            with open(pricing_file_path, 'r') as pricing_file:
                pricing_content = pricing_file.read()
        else:
            pricing_content = None
        return main_content, pricing_content

    def is_content_cached(self, url: str):
        return self.get_file_paths_from_index(url) is not None

    def delete_cached_content(self, url: str):
        file_path = self.get_file_paths_from_index(url)
        if file_path:
            os.remove(file_path)
            self.remove_from_index_file(url)

    def update_index_file(self, name: str, url: str, main_file_path: str, pricing_file_path: str):
        with open(self.cached_content_index, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, url, main_file_path, pricing_file_path])

    def get_file_paths_from_index(self, url: str):
        with open(self.cached_content_index, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                if row[1] == url:
                    return row[2], row[3]
        return None, None

    def remove_from_index_file(self, url: str):
        rows = []
        with open(self.cached_content_index, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        with open(self.cached_content_index, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in rows:
                if row[1] != url:
                    writer.writerow(row)

# Write to CSV
    async def write_to_csv(self, file_path: str, data: list):
        async with self.lock, aiofiles.open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            try:
                # Write data to CSV, ensuring proper handling of special characters
                writer.writerow(data)
                logger.info(f"Data written to {file_path}: {data}")
            except Exception as e:
                logger.error(f"Failed to write data to {file_path}: {e}")

# State checking and loading functions
    def load_state(self) -> dict:
        try:
            with open(self.state_file, 'r') as file:
                state = json.load(file)
                logger.info(f"State loaded successfully from {self.state_file}")
                return state
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"State file not found or invalid. Initializing new state: {e}")
            return {'processed_urls': []}

    def save_state(self, state: dict):
        try:
            with open(self.state_file, 'w') as file:
                json.dump(state, file)
                logger.info(f"State saved successfully to {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to save state to {self.state_file}: {e}")

    def get_processed_urls(self, state_file: str = None) -> list:
        try:
            if state_file is None:
                state_file = self.state_file
            state = self.load_state()
            processed_urls = state.get('processed_urls', [])
            logger.info(f"Processed URLs retrieved from {state_file}")
            return processed_urls
        except Exception as e:
            logger.error(f"Failed to get processed URLs from {state_file}: {e}")
            return []

    def update_processed_urls(self, state_file: str, url: str):
        try:
            state = self.load_state()
            processed_urls = state.get('processed_urls', [])
            if url not in processed_urls:
                processed_urls.append(url)
                state['processed_urls'] = processed_urls
                self.save_state(state)
                logger.info(f"URL '{url}' added to processed URLs in {state_file}")
        except Exception as e:
            logging.error(f"Failed to update processed URLs in {state_file} with URL '{url}': {e}")