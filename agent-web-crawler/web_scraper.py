import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import logging
from gpt_summarizer import GPTSummarizer
from file_manager import FileManager
from utils import exponential_backoff
from settings import BROWSER_EXECUTABLE_PATH, BROWSER_ARGS
from content_processor import ContentProcessor

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, gpt_summarizer: GPTSummarizer, file_manager: FileManager):
        self.gpt_summarizer = gpt_summarizer
        self.file_manager = file_manager
        self.content_processor = ContentProcessor()

    async def process_url(self, name: str, url: str, output_file: str, state_file: str, max_retries: int = 3):
        if url in self.file_manager.get_processed_urls(state_file):
            logger.info(f"Skipping {url}, already processed.")
            return (name, url, "Already processed", "N/A")

        async def scrape_and_summarize():
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(executable_path=BROWSER_EXECUTABLE_PATH, args=BROWSER_ARGS)
                    page = await browser.new_page()
                    await page.goto(url, timeout=60000)

                    content = await page.content()
                    logger.info(f"Content extracted from {url}.")

                    clean_text = self.content_processor.clean_content(content)
                    safe_chunk_size = 119000  # Adjust this value based on your specific prompt size and needs
                    processed_text_chunks = self.content_processor.chunk_text(clean_text, safe_chunk_size)

                    results = []
                    for chunk in processed_text_chunks:
                        summary = await self.gpt_summarizer.summarize(chunk, purpose="summary")
                        results.append(summary)
                    combined_summary = " ".join(results)

                    pricing_link = await self.find_pricing_link(page, url)
                    if pricing_link:
                        logger.info(f"Navigating to pricing page: {pricing_link}")
                        await page.goto(pricing_link, timeout=60000)
                        pricing_content = await page.content()
                        clean_pricing_text = self.content_processor.clean_content(pricing_content)
                        processed_pricing_chunks = self.content_processor.chunk_text(clean_pricing_text, safe_chunk_size)
                        
                        pricing_results = []
                        for chunk in processed_pricing_chunks:
                            pricing = await self.gpt_summarizer.summarize(chunk, purpose="pricing")
                            pricing_results.append(pricing)
                        combined_pricing = " ".join(pricing_results)
                    else:
                        combined_pricing = "No pricing information found."

                    await browser.close()
                    return (name, url, combined_summary, combined_pricing)
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                await browser.close()
                return (name, url, "Error in processing", "Error in processing")

        for attempt in range(1, max_retries + 1):
            result = await scrape_and_summarize()
            if result and result[2] != "Error in processing":
                # Write the result to the CSV file asynchronously
                await self.file_manager.write_to_csv(output_file, result)
                self.file_manager.update_processed_urls(state_file, url)
                return result
            else:
                logger.error(f"Attempt {attempt} failed for {url}. Retrying after delay...")
                await asyncio.sleep(exponential_backoff(attempt))

        logger.error(f"All attempts failed for {url}.")
        return (name, url, "Error in processing", "Error in processing")

    async def find_pricing_link(self, page, base_url):
        pricing_keywords = ["pricing", "plans", "cost", "price", "buy", "subscribe"]
        
        for keyword in pricing_keywords:
            try:
                pricing_link = await page.query_selector(f"a:text-matches('{keyword}', 'i')")
                if pricing_link:
                    href = await pricing_link.get_attribute("href")
                    if href.startswith("http"):
                        return href
                    else:
                        return urljoin(base_url, href)
            except Exception as e:
                logger.warning(f"Error finding pricing link with keyword '{keyword}': {str(e)}")
        
        logger.info("No pricing link found.")
        return None