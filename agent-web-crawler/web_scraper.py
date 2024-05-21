import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import logging
from gpt_summarizer import GPTSummarizer
from file_manager import FileManager
from utils import exponential_backoff
from settings import BROWSER_EXECUTABLE_PATH, BROWSER_ARGS, MAX_INPUT_TOKENS
from content_processor import ContentProcessor

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, gpt_summarizer: GPTSummarizer, file_manager: FileManager, processed_urls: set):
        self.gpt_summarizer = gpt_summarizer
        self.file_manager = file_manager
        self.content_processor = ContentProcessor()
        self.processed_urls = processed_urls

    async def process_url(self, name: str, url: str, output_file: str, state_file: str, refresh: bool = False, max_retries: int = 3):
        # Skip if already processed
        if url in self.processed_urls:
            logger.info(f"Skipping {url}, already processed.")
            result = (name, url, "Already processed", "N/A")
            print(f"Returning: {result}")
            return result
        
        # Check if content is cached and refresh is not requested
        if not refresh and url not in self.processed_urls and self.file_manager.is_content_cached(url):
            logger.info(f"Loading cached content for {url}")
            main_content, pricing_content = self.file_manager.get_cached_content(url)
            
            if main_content and pricing_content:
                logger.debug(f"Using cached content for {url}")
                summary = await self.gpt_summarizer.summarize(main_content, purpose="summary")
                pricing = await self.gpt_summarizer.summarize(pricing_content, purpose="pricing")
                # Combine main content and pricing content for scoring
                combined_content = main_content + " " + pricing_content
                score, fuzzy_score, analysis = await self.gpt_summarizer.summarize(combined_content, purpose="scoring")
                # Update the state file to mark the URL as processed
                self.file_manager.update_processed_urls(state_file, url)
                return (name, url, summary, pricing, analysis, score, fuzzy_score)
            else:
                logger.info(f"Cached content for {url} is empty. Refreshing...")
        
        # If not cached, needs refreshing, or cached content is empty, scrape and summarize
        for attempt in range(1, max_retries + 1):
            result = await self.scrape_and_summarize(name, url)
            if result and result[2] != "Error in processing":
                # Write the result to the CSV file asynchronously
                await self.file_manager.write_to_csv(output_file, result)
                self.file_manager.update_processed_urls(state_file, url)
                return result
            else:
                logger.error(f"Attempt {attempt} failed for {url}. Retrying after delay...")
                await asyncio.sleep(exponential_backoff(attempt))

        logger.error(f"All attempts failed for {url}.")
        return (name, url, "Error in processing", "Error in processing", "Error in processing", None, None)

    async def scrape_and_summarize(self, name: str, url: str):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(executable_path=BROWSER_EXECUTABLE_PATH, args=BROWSER_ARGS)
                page = await browser.new_page()
                await page.goto(url, timeout=60000)

                content = await page.content()
                logger.info(f"Content extracted from {url}.")

                clean_text = self.content_processor.clean_content(content)
                processed_text_chunks = self.content_processor.chunk_text(clean_text, MAX_INPUT_TOKENS)

                summary = await self.gpt_summarizer.summarize(" ".join(processed_text_chunks), purpose="summary")

                pricing_link = await self.find_pricing_link(page, url)
                if pricing_link:
                    await page.goto(pricing_link, timeout=60000)
                    pricing_content = await page.content()
                    clean_pricing_text = self.content_processor.clean_content(pricing_content)
                    processed_pricing_chunks = self.content_processor.chunk_text(clean_pricing_text, MAX_INPUT_TOKENS)
                    pricing = await self.gpt_summarizer.summarize(" ".join(processed_pricing_chunks), purpose="pricing")
                    self.file_manager.save_cached_content(name, url, clean_text, clean_pricing_text)
                    
                    # Combine main content and pricing content for scoring
                    combined_text = " ".join(processed_text_chunks) + " " + clean_pricing_text
                else:
                    pricing = "No pricing information found."
                    self.file_manager.save_cached_content(name, url, clean_text, "")
                    
                    # Use only main content for scoring
                    combined_text = " ".join(processed_text_chunks)

                score, fuzzy_score, analysis = await self.gpt_summarizer.summarize(combined_text, purpose="scoring")

                await browser.close()
                return (name, url, summary, pricing, analysis, score, fuzzy_score)
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            await browser.close()
            return (name, url, "Error in processing", "Error in processing", "Error in processing", None, None)


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