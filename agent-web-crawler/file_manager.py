import aiofiles
import csv
import json
from settings import DEFAULT_STATE_FILE
import logging

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self, state_file: str = DEFAULT_STATE_FILE):
        self.state_file = state_file
        logger.info(f"FileManager initialized with state file: {self.state_file}")

    async def write_to_csv(self, file_path: str, data: tuple):
        try:
            # Use 'a' mode for appending to the CSV file
            async with aiofiles.open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                await writer.writerow(data)  # Write the data tuple asynchronously
                logger.info(f"Data successfully written to {file_path}: {data}")
        except Exception as e:
            logger.error(f"Failed to write data to {file_path}: {e}")

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