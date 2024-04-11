import argparse
import subprocess
import signal
import sys
import os
import logging
from settings import (
    DEFAULT_STATE_FILE,
    DEFAULT_INPUT_FILE,
    DEFAULT_OUTPUT_FILE,
    LOG_LEVEL,
    MAX_CONCURRENT_BROWSERS,
    DEFAULT_LOG_FILE
)
# Logging to logfile is still broken but it can be called via &> at the end of a script so all good
from utils import setup_logging

# Update the command to run the main script using the orchestrator module
MAIN_SCRIPT_CMD = ["python3", "orchestrator.py"]

# PID file for tracking the main script's process
PID_FILE = "main.pid"

def start_process(args, max_concurrent_browsers):
    max_concurrent_browsers_arg = ["--max-concurrent-browsers", str(max_concurrent_browsers)]
    with open(PID_FILE, 'w') as pid_file:
        process = subprocess.Popen(MAIN_SCRIPT_CMD + max_concurrent_browsers_arg + args)
        pid_file.write(str(process.pid))
    logging.info("Process started with PID: %s", process.pid)

def stop_process():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as pid_file:
            pid = int(pid_file.read())
        os.kill(pid, signal.SIGTERM)
        os.remove(PID_FILE)
        logger.info("Process stopped.")
    else:
        logger.info("No running process found.")

def pause_process():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as pid_file:
            pid = int(pid_file.read())
        os.kill(pid, signal.SIGSTOP)
        logger.info("Process paused.")
    else:
        logger.info("No running process to pause.")

def resume_process():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as pid_file:
            pid = int(pid_file.read())
        os.kill(pid, signal.SIGCONT)
        logger.info("Process resumed.")
    else:
        logger.info("No paused process to resume.")

def main():
    parser = argparse.ArgumentParser(description="Wrapper script to control the execution of the main script.")
    parser.add_argument("--start", action="store_true", help="Start the main script.")
    parser.add_argument("--stop", action="store_true", help="Stop the main script.")
    parser.add_argument("--pause", action="store_true", help="Pause the main script.")
    parser.add_argument("--resume", action="store_true", help="Resume the main script.")
    parser.add_argument("--state", type=str, default=DEFAULT_STATE_FILE, help="Path to the state file.")
    parser.add_argument("--input", type=str, default=DEFAULT_INPUT_FILE, help="Path to the input file.")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_FILE, help="Path to the output file.")
    parser.add_argument("--logfile", type=str, default=DEFAULT_LOG_FILE, help="Path to the log file where logs will be written.")
    parser.add_argument("--max-concurrent-browsers", type=int, default=MAX_CONCURRENT_BROWSERS, help="Maximum number of concurrent browsers.")
    
    args = parser.parse_args()
    
    # Set up logging with the default log file if --logfile is not specified
    setup_logging(LOG_LEVEL, args.logfile if args.logfile else None)

    # Now that logging is setup, call orchestrator main
    from orchestrator import main as orchestrator_main

    main_script_args = []
    if args.state:
        main_script_args += ["--state", args.state]
    if args.input:
        main_script_args += ["--input", args.input]
    if args.output:
        main_script_args += ["--output", args.output]

    if args.start:
        start_process(main_script_args, args.max_concurrent_browsers)
    elif args.stop:
        stop_process()
    elif args.pause:
        pause_process()
    elif args.resume:
        resume_process()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()