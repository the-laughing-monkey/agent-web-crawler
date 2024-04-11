import logging
import os

# OpenAI API settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GPT_ENGINE = "gpt-4-turbo"
GPT_MAX_TOKENS = 120000

# Playwright browser settings
BROWSER_EXECUTABLE_PATH = "/usr/bin/google-chrome-stable"
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-sync",
    "--disable-translate",
    "--mute-audio",
    "--safebrowsing-disable-auto-update",
    "--ignore-certificate-errors",
    "--ignore-ssl-errors",
    "--ignore-certificate-errors-spki-list",
    "--no-zygote",
    "--disable-gpu",
]

# Maximum number of concurrent browsers
MAX_CONCURRENT_BROWSERS = 5

# File paths
DEFAULT_STATE_FILE = "script_state.json"
DEFAULT_INPUT_FILE = "input_file.csv"
DEFAULT_OUTPUT_FILE = "output_with_summaries_and_pricing.csv"
DEFAULT_LOG_FILE = "web-crawler-agent.log" 

# Logging settings
LOG_LEVEL = logging.INFO