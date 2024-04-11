from bs4 import BeautifulSoup
from langchain_openai import OpenAI
import os

class ContentProcessor:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise EnvironmentError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        self.llm = OpenAI(api_key=self.openai_api_key)

    def clean_content(self, html_content):
        """Clean and extract text from HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()  # Remove these two elements and their contents
        text = soup.get_text(separator=' ', strip=True)
        return text

    def chunk_text(self, text, max_length):
        """Chunk text into parts with a maximum length."""
        chunks = []
        while text:
            if len(text) > max_length:
                space_index = text.rfind(' ', 0, max_length)
                if space_index == -1:
                    space_index = max_length
                chunks.append(text[:space_index])
                text = text[space_index:].lstrip()
            else:
                chunks.append(text)
                break
        return chunks