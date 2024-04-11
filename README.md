# Agent Web Crawler Setup Guide

The web crawler script will crawl the web from a series of input URLs in a csv file and it will read the websites, summarize them and dig up pricing information.

It's useful for researching competitors and partners.

It uses a combination of [GPT-4](https://platform.openai.com/docs/api-reference/chat/create), [Langchain](https://python.langchain.com/docs/get_started/introduction/), BeautifulSoup, and it has built in protections like exponentation back off to deal with OpenAI rate limits, state saving, and async spin up of headless Chrome browsers with [Playwright](https://playwright.dev/) to make the script go much faster.

### Required

Python 3.10 and Docker Desktop knowledge


### Let's Get Started Now

## Creating a Persistent Docker Volume

1. Open Docker Desktop.
2. Navigate to "Volumes".
3. Click "Create".
4. Name the volume `container-storage`. Note that storage size is dynamic and need not be specified.

## Configuring Docker Environment on MacOS

1. Open Terminal.
2. Add Docker to your PATH if you are using a Mac or Linux:
   ```
   export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin/"
   ```

## Running the Docker Container

1. For Apple Arm Silicon, launch an x64 instance of Ubuntu:
   ```
   docker run -it --platform linux/amd64 --shm-size=2gb --name my-web-crawler -v container-storage:/data ubuntu /bin/bash -c "tail -f /dev/null"
   ```
   Alternatively, use a pre-built image if available (Currently the below image is NOT publically avaiable so make your own from the default Ubuntu image by following the instructions here in this readme and then do a "docker commit"):
   ```
   docker run -it --platform linux/amd64 --shm-size=2gb --name my-web-crawler -v container-storage:/data my-agent-web-crawler:v2 /bin/bash -c "tail -f /dev/null"
   ```
   The running image will be referred to as `my-web-crawler`.

## Accessing the Container

1. Open a new Terminal tab and connect to the container:
   ```
   docker exec -it my-web-crawler /bin/bash
   ```
2. Inside the container, create a directory in `/data`:
   ```
   mkdir /data
   ```

## Transferring Files to the Container from your desktop

1. Copy necessary files from your local machine to the container:
   ```
   docker cp /local/path/to/my/files/agent-web-crawler my-web-crawler:/data/
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

1. Manually launch Google Chrome to verify installation.  This will make a little PNG in the current directoy, a screenshot of the Google webpage.  That will let you know it's working:
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
   docker commit 7xa60b22a092 my-agent-web-crawler:v2 
   ```


## Running the Web Crawler Script

1. Execute the web crawler script with the following command to log to stdout and stderr:
   ```
   python3.10 websucker.py --start --state ./data/state.txt --input ./data/input_file.csv --output ./data/output_file.csv --max-concurrent-browsers 5

   ```

2. Also, please NOTE if you want to log to a file instead, logging via the --logfile switch is broken (to be fixed in a later iteration) so just use &> at the end of the script to log to a file until it is fixed in later updates.

To start the main script with your own settings:

   ```
   python3.10 websucker.py --start ./data/state.txt --input ./data/input_file.csv --output ./data/output_file.csv --max-concurrent-browsers 5
   ```

## Additional Script Management Commands and Examples

To start the main script with default settings:
  
  ```
  python websucker.py --start
  ```

To start the main script with all your own settings and log to a file instead of the screen, do the following:
  
  ```
  python websucker.py --start --input your_input_file.csv --output your_output_file.csv --max-concurrent-browsers 5 &> ./data/agent-crawler.log
  ```

To set the max concurrent browsers:

  ```
   python websucker.py --max-concurrent-browsers 5
  ```

To log to a file:

  ```
   python websucker.py --start &> ./data/agent-crawler.log
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
