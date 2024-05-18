# Agent Web Crawler Setup Guide

The web crawler script will crawl the web from a series of input URLs in a csv file and it will read the websites, summarize them and dig up pricing information.

It's useful for researching competitors and partners.

It uses a combination of [GPT-4](https://platform.openai.com/docs/api-reference/chat/create), [Langchain](https://python.langchain.com/docs/get_started/introduction/), BeautifulSoup, and it has built in protections like exponentation back off to deal with OpenAI rate limits, state saving, and async spin up of headless Chrome browsers with [Playwright](https://playwright.dev/) to make the script go much faster.

### Required

Python 3.10 and Docker Desktop knowledge


Let's Get Started Now

## CRITICAL NOTE ##
If you want to use GPT to score a product/company, you will need to modify the prompts-and-plans/prompt-scoring.txt file with your own questions and then set the purpose to scoring in the gpt_summarizer.py file.

Then RENAME prompt-scorting.txt.EXAMPLE to prompt-scoring.txt.

The prompt in gpt_summarizer.py is set to:          

   ```
   elif purpose == "scoring":
         with open('prompts-and-plans/prompt-scoring.txt', 'r') as file:
            prompt_scoring_file = file.read()

         prompt = f"Please carefully review this scoring system and then output only SCORE: {{X}} and FUZZY SCORE: {{Y}} where X is a score from -12 to 12, based on the criteria in the scoring system, and Y is a string that can be HORRIBLE, PASSABLE, GOOD, VERYGOOD, EXCELLENT, based on the rules in the scoring system. Finally return your analysis of how you came to your conclusion with ANALYSIS: {{analysis}}.\n\n{prompt_scoring_file}\n\n{content}"
   ```

Adjust YOUR scoring based on the questions you add to the prompt-scoring.txt file.  Currently scoring goes from -12 to 12 because my set of proprietary questions is 12 questions long.  If you want to change that you will need to adjust the scoring.py file as well.

## Creating a Persistent Docker Volume

1. Open Docker Desktop.
2. Navigate to "Volumes".
3. Click "Create".
4. Name the volume `container-storage`. Note that storage size is dynamic and need not be specified.

## Configuring Docker Environment on MacOS

1. Open Terminal.
2. Add Docker to your PATH:
   ```
   export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin/"
   ```

## Running the Docker Container

1. For Apple Arm Silicon, launch an x64 instance of Ubuntu:
   ```
   docker run -it --platform linux/amd64 --shm-size=2gb --name my-ubuntu -v container-storage:/data ubuntu /bin/bash -c "tail -f /dev/null"
   ```
   Alternatively, use a pre-built image if available:
   ```
   docker run -it --platform linux/amd64 --shm-size=2gb --name my-ubuntu -v container-storage:/data my-agent-web-crawler:v2 /bin/bash -c "tail -f /dev/null"
   ```
   The running image will be referred to as `my-ubuntu`.

## Accessing the Container

1. Open a new Terminal tab and connect to the container:
   ```
   docker exec -it my-ubuntu /bin/bash
   ```
2. Inside the container, create a directory in `/data`:
   ```
   mkdir /data
   ```

## Transferring Files to the Container from your desktop

1. Copy necessary files from your local machine to the container:
   ```
   docker cp /local/path/to/my/files/agent-web-crawler my-ubuntu:/data/
   ```

## Setting Environment Variables Inside the Container

1. Set your OpenAI API key:
   ```
   export OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

## Installing Dependencies Inside the Container

1. Update package lists and install essential tools:
   ```
   apt-get update && apt-get install -y sudo pip software-properties-common vim wget
   ```
2. Install Google Chrome:
   ```
   apt-get update && apt-get install gnupg wget -y && \
   wget --quiet --output-document=- https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/google-archive.gpg && \
   sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && \
   apt-get update && \
   apt-get install google-chrome-stable -y --no-install-recommends && \
   rm -rf /var/lib/apt/lists/*
   ```

## Verifying Python Installation and Dependencies

1. Check the installed Python version:
   ```
   python3 --version
   ```
2. Install Python dependencies:
   ```
   cd /data/agent-web-crawler
   pip install -r requirements.txt
   ```

## Testing Browser Launch

1. Manually launch Google Chrome to verify installation:
   ```
   /usr/bin/google-chrome-stable --headless --no-sandbox --disable-gpu --no-zygote --dump-dom https://www.google.com/
   ```
2. Alternatively, run the provided test script:
   ```
   python3 ./test_browser_launch.py
   ```

## Creating your own container

1. You can use the docker commit to write a fully baked container once you have it up and running:

   ```
   docker commit <container-id> <image-name>:<tag> Replace <container-id> with the ID of your container. Specify the desired name and optionally a tag for the new image. For example: 
   ```

2. To find the ID number of your container you can use: 

   ```
   docker ps -a
   ```

3. Then to commit a file, with the example ID of 9eab03b20c79 you could do the following:

   ```
   docker commit 9eab03b20c79 my-agent-web-crawler:v1 
   ```

4. To update it, simply get the new version number with ps -a and then update the version number:

   ```
   docker commit 7xa60b22a092 my-agent-web-crawler:v1 
   ```


## Running the Web Crawler Script

1. Execute the web crawler script with the following command to log to stdout and stderr and to a log file (which happens automatically now):
   ```
   python3.10 websucker.py --start --input ./data/input_file.csv --output ./data/output_file.csv --max-concurrent-browsers 5

   ```

## Additional Script Management Commands and Examples

To start the main script with default settings:
  
  ```
  python websucker.py --start
  ```

To start the main script and force it to download content again instead of using cached local content use the --refresh switch.
  
  ```
  python websucker.py --start --input your_input_file.csv --output your_output_file.csv --max-concurrent-browsers 5 --refresh
  ```


To start the main script with all your own settings and to log to a file instead of the screen do the following:
  
  ```
  python websucker.py --start --input your_input_file.csv --output your_output_file.csv --max-concurrent-browsers 5 --logfile your_log_file.log
  ```

To set the max concurrent browsers:

  ```
   python websucker.py --max-concurrent-browsers 5
  ```

To stop the main script:

  ```
  python websucker.py --stop
  ```

To pause the main script:

  ```
  python websucker.py --pause
  ```

To resume a paused script:

  ```
  python websucker.py --resume
  ```

To view help:

  ```
  python websucker.py --help
  ```
