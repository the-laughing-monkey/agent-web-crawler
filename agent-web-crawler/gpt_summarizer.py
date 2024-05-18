import re
import openai
from openai import AsyncOpenAI
import logging
from settings import OPENAI_API_KEY, MODEL, MAX_OUTPUT_TOKENS

# Setup logging
logger = logging.getLogger(__name__)

class GPTSummarizer:
    def __init__(self):
        # Create an instance of the AsyncOpenAI class
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def summarize(self, content: str, purpose: str = "summary", heuristics=None) -> str:
        if content is None or "Already processed" in content or "Error in processing" in content:
            logger.error(f"Invalid content for summarization with purpose {purpose}")
            return "No content provided"
                
        messages = []
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
        elif purpose == "scoring":
            with open('prompts-and-plans/prompt-scoring.txt', 'r') as file:
                prompt_scoring_file = file.read()

            prompt = f"Please carefully review this scoring system and then output only SCORE: {{X}} and FUZZY SCORE: {{Y}} where X is a score from -12 to 12, based on the criteria in the scoring system, and Y is a string that can be HORRIBLE, PASSABLE, GOOD, VERYGOOD, EXCELLENT, based on the rules in the scoring system. Finally return your analysis of how you came to your conclusion with ANALYSIS: {{analysis}}.\n\n{prompt_scoring_file}\n\n{content}"

            messages = [
                {"role": "system", "content": "You are a helpful assistant who provides scoring based on given criteria."},
                {"role": "user", "content": prompt}
            ]

        try:

            # Print the messages to standard output
            #print(f"Sending messages to GPT API: {messages}")
            print(f"Sending messages to GPT API: {str(messages)[:200]}")

            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=MAX_OUTPUT_TOKENS
            )
            response_message = response.choices[0].message.content.strip()

            if purpose == "scoring":
                score_match = re.search(r'SCORE:\s*(-?\d+)', response_message)

                fuzzy_scores = ["VERYGOOD", "EXCELLENT", "GOOD", "PASSABLE", "HORRIBLE"]
                fuzzy_score = None

                for score in fuzzy_scores:
                    if score in response_message:
                        fuzzy_score = score
                        break

                if fuzzy_score is None:
                    fuzzy_score = "Fuzzy score N/A"
                    
                analysis_match = re.search(r'ANALYSIS:(.*)', response_message, re.DOTALL)

                score = int(score_match.group(1)) if score_match else 0
                analysis = analysis_match.group(1).strip() if analysis_match else "Analysis not available"

                return score, fuzzy_score, analysis
            else:
                return response_message
        except Exception as e:
            logger.error(f"Error during GPT interaction for {purpose}: {str(e)}")
            return f"Error in processing content: {str(e)}"
