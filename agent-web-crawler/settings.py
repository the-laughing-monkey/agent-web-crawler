import logging
import os

# OpenAI API settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-4o"
MAX_INPUT_TOKENS = 119000
MAX_OUTPUT_TOKENS = 4096

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
DEFAULT_STATE_FILE = "data/script_state.json"
DEFAULT_INPUT_FILE = "data/input_file.csv"
DEFAULT_OUTPUT_FILE = "data/output_with_analysis.csv"
DEFAULT_LOG_FILE = "data/web-crawler-agent.log" 

# Logging settings
LOG_LEVEL = logging.INFO