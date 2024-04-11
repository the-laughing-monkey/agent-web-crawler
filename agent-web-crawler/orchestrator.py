import asyncio
import argparse
import logging
import pandas as pd
from asyncio import Semaphore
from settings import (
    DEFAULT_STATE_FILE,
    DEFAULT_INPUT_FILE,
    DEFAULT_OUTPUT_FILE,
    LOG_LEVEL,
    MAX_CONCURRENT_BROWSERS,
    DEFAULT_LOG_FILE  # Included DEFAULT_LOG_FILE
)
from utils import setup_logging

# Set up logging at the start of the orchestrator main function
setup_logging(LOG_LEVEL, DEFAULT_LOG_FILE)

# Now import other modules that may use logging
from web_scraper import WebScraper
from gpt_summarizer import GPTSummarizer
from file_manager import FileManager

logger = logging.getLogger(__name__)

async def main(args):
    logger.info("Starting the application...")

    gpt_summarizer = GPTSummarizer()
    file_manager = FileManager(args.state)
    web_scraper = WebScraper(gpt_summarizer, file_manager)

    # Load the input CSV file into a pandas DataFrame
    data = pd.read_csv(args.input)

    # Semaphore to control concurrency
    semaphore = Semaphore(args.max_concurrent_browsers)

    async def process_with_semaphore(name, url, output, state):
        async with semaphore:
            return await web_scraper.process_url(name, url, output, state)

    # Process each URL in the DataFrame
    tasks = []
    for index, row in data.iterrows():
        name, url = row['Name'], row['URL']
        task = asyncio.create_task(process_with_semaphore(name, url, args.output, args.state))
        tasks.append(task)

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)

    # Check results before creating DataFrame
    for result in results:
        if not isinstance(result, tuple) or len(result) != 4:
            logger.error(f"Invalid result format: {result}")
            continue

    # Filter out None results and ensure only valid results are processed
    valid_results = [result for result in results if result is not None and len(result) == 4]

    logger.info("All URLs processed successfully.")

    # Save the results to the output CSV file
    df = pd.DataFrame(valid_results, columns=['Name', 'URL', 'Summary', 'Pricing'])
    df.to_csv(args.output, index=False)

    logger.info(f"Results saved to {args.output}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Web scraper and summarizer")
    parser.add_argument("--state", type=str, default=DEFAULT_STATE_FILE, help="Path to the state file")
    parser.add_argument("--input", type=str, default=DEFAULT_INPUT_FILE, help="Path to the input CSV file")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_FILE, help="Path to the output CSV file")
    parser.add_argument("--max-concurrent-browsers", type=int, default=MAX_CONCURRENT_BROWSERS, help="Maximum number of concurrent browsers")
    parser.add_argument("--logfile", type=str, default=DEFAULT_LOG_FILE, help="Path to the log file where logs will be written.")
    args = parser.parse_args()

    # Call setup_logging with the logfile argument from the command line
    setup_logging(LOG_LEVEL, args.logfile)

    asyncio.run(main(args))