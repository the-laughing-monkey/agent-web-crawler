import asyncio
import sys
import argparse
import logging
import pandas as pd
import csv
from asyncio import Semaphore
from web_scraper import WebScraper
from settings import (
    DEFAULT_STATE_FILE,
    DEFAULT_INPUT_FILE,
    DEFAULT_OUTPUT_FILE,
    LOG_LEVEL,
    MAX_CONCURRENT_BROWSERS,
    DEFAULT_LOG_FILE
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

    # Retrieve processed URLs before creating the WebScraper instance
    processed_urls = file_manager.get_processed_urls(args.state)
    web_scraper = WebScraper(gpt_summarizer, file_manager, processed_urls)

    # Load the input CSV file into a pandas DataFrame
    data = pd.read_csv(args.input)

    # Semaphore to control concurrency
    semaphore = Semaphore(args.max_concurrent_browsers)


    # Open the output CSV file in append mode
    with open(args.output, 'a', newline='') as csvfile:
        fieldnames = ['Name', 'URL', 'Summary', 'Pricing', 'Analysis', 'Score', 'FuzzyScore']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file is empty
        if csvfile.tell() == 0:
            writer.writeheader()

        # Process each URL in the DataFrame
        tasks = []
        for index, row in data.iterrows():
            name, url = row['Name'], row['URL']
            
            # Check if the URL has already been processed
            if url in file_manager.get_processed_urls(args.state):
                logger.info(f"Skipping {url}, already processed.")
                continue
            
            task = asyncio.create_task(process_with_semaphore(name, url, args.output, args.state, writer, semaphore, web_scraper, csvfile, args.refresh))
            tasks.append(task)

        try:
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
        finally:
            # Close the CSV file and exit the event loop
            csvfile.close()

    logger.info(f"Results saved and cleaned in {args.output}")

async def process_with_semaphore(name, url, output, state, writer, semaphore, web_scraper, csvfile, refresh):
    async with semaphore:
        result = await web_scraper.process_url(name, url, output, state, refresh)

        if result[2] == "Already processed":
            logger.info(f"Skipping writing {url} to CSV, already processed.")
            return  # Ensure no further processing or GPT requests are made for this URL

        if not isinstance(result, tuple) or len(result) not in (4, 7):
            logger.error(f"Invalid result format: {result}")
            return

        elif len(result) == 7:
            name, url, summary, pricing, analysis, score, fuzzy_score = result
            # Process each field if necessary (e.g., stripping extra characters, handling newlines)
            name = name.strip()
            url = url.strip()
            summary = summary.replace('\n', ' ').strip()
            pricing = pricing.replace('\n', ' ').strip()
            analysis_text = analysis.replace('\n', ' ').strip() if analysis else "Analysis not available"
        else:
            name, url, summary, pricing = result
            analysis_text, score, fuzzy_score = "Analysis not available", None, None
        
        try:
            # Write the result to the CSV file immediately
            writer.writerow({
                'Name': name,
                'URL': url,
                'Summary': summary,
                'Pricing': pricing,
                'Analysis': analysis_text,
                'Score': score,
                'FuzzyScore': fuzzy_score
            })
            
            # Ensure the data is flushed to the file  
            csvfile.flush()
        except Exception as e:
            logger.error(f"Error writing result to CSV: {str(e)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Web scraper and summarizer")
    parser.add_argument("--state", type=str, default=DEFAULT_STATE_FILE, help="Path to the state file")
    parser.add_argument("--input", type=str, default=DEFAULT_INPUT_FILE, help="Path to the input CSV file")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_FILE, help="Path to the output CSV file")
    parser.add_argument("--max-concurrent-browsers", type=int, default=MAX_CONCURRENT_BROWSERS, help="Maximum number of concurrent browser instances")
    parser.add_argument("--refresh", action="store_true", help="Force refresh of cached content")
    args = parser.parse_args()

    # Set the event loop policy to WindowsSelectorEventLoopPolicy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main(args))