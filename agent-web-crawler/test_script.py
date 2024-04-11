import asyncio
import os
import tempfile
import pandas as pd
import json
from web_scraper import WebScraper
from gpt_summarizer import GPTSummarizer
from file_manager import FileManager
from utils import setup_logging
from settings import DEFAULT_STATE_FILE, DEFAULT_INPUT_FILE, DEFAULT_OUTPUT_FILE, LOG_LEVEL
from orchestrator import main as orchestrator_main
from utils import exponential_backoff


async def test_web_scraper():
    print("Testing WebScraper...")
    # Mocks would be set up here, but for now, let's focus on the tuple unpacking
    gpt_summarizer = GPTSummarizer()
    file_manager = FileManager()
    web_scraper = WebScraper(gpt_summarizer, file_manager)
    url = "https://rask.ai"
    name = "Test Name"
    output_file = "test_output.csv"
    state_file = "test_state.json"
    try:
        # Correctly unpack the tuple returned by process_url
        result = await web_scraper.process_url(name, url, output_file, state_file)
        if result is not None:
            name, url, summary, pricing = result
            if summary and pricing:
                print("WebScraper test: SUCCESS")
            else:
                print("WebScraper test: FAILED - Summary or pricing missing")
        else:
            print("WebScraper test: FAILED - No result returned")
    except Exception as e:
        print(f"WebScraper test: FAILED - {str(e)}")

async def test_gpt_summarizer():
    print("Testing GPTSummarizer...")
    gpt_summarizer = GPTSummarizer()
    content = "This is a sample content to test the GPTSummarizer."
    try:
        summary = await gpt_summarizer.summarize(content)
        print("GPTSummarizer test: SUCCESS")
    except Exception as e:
        print(f"GPTSummarizer test: FAILED - {str(e)}")

async def test_file_manager_load_save_state():
    print("Testing FileManager load_state and save_state...")
    file_manager = FileManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_state_file = os.path.join(temp_dir, "test_state.json")
        initial_state = {'processed_urls': ['https://rask.ai']}

        try:
            # Save the initial state to the file
            file_manager.save_state(test_state_file, initial_state)
            print("State saved successfully.")

            # Load the state from the file
            loaded_state = file_manager.load_state(test_state_file)
            assert loaded_state == initial_state, "Loaded state does not match saved state"
            print("FileManager load_state and save_state test: SUCCESS")

        except Exception as e:
            print(f"FileManager load_state and save_state test: FAILED - {str(e)}")

import asyncio
from utils import exponential_backoff

async def test_exponential_backoff():
    print("Testing exponential_backoff...")
    base_delay = 1.0  # seconds
    max_delay = 32.0  # seconds
    try:
        delays = [exponential_backoff(attempt, base_delay, max_delay) for attempt in range(1, 7)]
        expected_delays = [1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
        for actual, expected in zip(delays, expected_delays):
            assert actual == expected, f"Delay for attempt {delays.index(actual)+1} was {actual}, expected {expected}"
        print("exponential_backoff test: SUCCESS")
    except AssertionError as e:
        print(f"exponential_backoff test: FAILED - {str(e)}")
    except Exception as e:
        print(f"exponential_backoff test: FAILED - Unexpected error: {str(e)}")

# Since the function is now async, we need to run it with an event loop
asyncio.run(test_exponential_backoff())

async def test_orchestrator():
    print("Testing Orchestrator...")
    args = {
        "state": DEFAULT_STATE_FILE,
        "input": DEFAULT_INPUT_FILE,
        "output": DEFAULT_OUTPUT_FILE
    }
    try:
        # Backup existing state file if it exists
        if os.path.exists(args["state"]):
            os.rename(args["state"], args["state"] + ".bak")

        # Run the orchestrator
        await orchestrator_main(args)

        # Check if the output file was created and has the expected content
        assert os.path.exists(args["output"]), f"Output file {args['output']} was not created"
        output_data = pd.read_csv(args["output"])
        assert not output_data.empty, f"Output file {args['output']} is empty"
        # Add more assertions here to validate the content of the output file

        # Check if the state file was updated correctly
        assert os.path.exists(args["state"]), f"State file {args['state']} was not updated"
        with open(args["state"], 'r') as f:
            state_data = json.load(f)
        assert 'processed_urls' in state_data, "State file does not contain 'processed_urls'"
        # Add more assertions here to validate the content of the state file

        print("Orchestrator test: SUCCESS")

    except AssertionError as e:
        print(f"Orchestrator test: FAILED - {str(e)}")
    except Exception as e:
        print(f"Orchestrator test: FAILED - {str(e)}")
    finally:
        # Clean up: Remove test output and state files, restore backup if it exists
        if os.path.exists(args["output"]):
            os.remove(args["output"])
        if os.path.exists(args["state"]):
            os.remove(args["state"])
        if os.path.exists(args["state"] + ".bak"):
            os.rename(args["state"] + ".bak", args["state"])