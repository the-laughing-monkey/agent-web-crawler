import asyncio
import openai
from openai import AsyncOpenAI
from settings import OPENAI_API_KEY

class GPTSummarizer:
    def __init__(self):
        # Create an instance of the AsyncOpenAI class
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def summarize(self, content: str, purpose: str = "summary") -> str:
        if purpose == "summary":
            messages = [
                {"role": "system", "content": "You are a helpful assistant who provides summaries."},
                {"role": "user", "content": f"Summarize this content into 3 to 5 bullet points:\n{content}"}
            ]
        elif purpose == "pricing":
            messages = [
                {"role": "system", "content": "You are a helpful assistant who extracts pricing information."},
                {"role": "user", "content": f"Extract pricing information from this content:\n{content}"}
            ]
        else:
            raise ValueError("Unsupported purpose specified.")

        try:
            # Use the client instance to create the chat completion asynchronously
            response = await self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages
            )
            # Extract and return the text from the response
            response_message = response.choices[0].message.content.strip()
            return response_message
        except Exception as e:
            print(f"Error during GPT interaction for {purpose}: {str(e)}")
            return "Error in processing content"