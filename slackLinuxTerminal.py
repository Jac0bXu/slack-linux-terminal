#!/usr/bin/env python3
import os
import subprocess
import logging
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.rtm_v2 import RTMClient

# Load environment variables from .env file
load_dotenv()

# Configure logging to see info/debug messages on the console
logging.basicConfig(level=logging.INFO)

# Get the Slack Bot token and target channel ID from environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
TARGET_CHANNEL_ID = os.environ.get("TARGET_CHANNEL_ID")

if not SLACK_BOT_TOKEN or not TARGET_CHANNEL_ID:
    logging.error("Both SLACK_BOT_TOKEN and TARGET_CHANNEL_ID must be set in the environment.")
    exit(1)

# Initialize the Slack WebClient
web_client = WebClient(token=SLACK_BOT_TOKEN)

@RTMClient.run_on(event="message")
def handle_message(**payload):
    """
    This function is called on every incoming message event.
    It checks that the message is from the target channel and not sent by a bot,
    then executes the message text as a shell command.
    """
    data = payload.get("data", {})
    channel = data.get("channel")
    text = data.get("text", "")
    subtype = data.get("subtype", None)  # e.g., 'bot_message' for bot messages

    # Process only messages in our target channel and skip bot messages
    if channel != TARGET_CHANNEL_ID or (subtype is not None and subtype == "bot_message"):
        return

    logging.info(f"Received command: {text}")

    # Execute the shell command
    try:
        # The command is executed with a timeout for safety (adjust timeout as needed)
        result = subprocess.run(text, shell=True, capture_output=True, text=True, timeout=15)
        # Use stdout if available; otherwise, use stderr
        output = result.stdout if result.stdout else result.stderr
        if not output.strip():
            output = "[No output]"
    except Exception as e:
        output = f"Error executing command: {e}"

    # Format the output inside a code block for readability in Slack
    response_message = f"```\n{output}\n```"

    # Send the response back to the same channel
    try:
        web_client.chat_postMessage(channel=channel, text=response_message)
        logging.info("Command output sent to Slack.")
    except Exception as e:
        logging.error(f"Failed to post message to Slack: {e}")

def main():
    # Initialize and start the RTM (Real Time Messaging) client
    rtm_client = RTMClient(token=SLACK_BOT_TOKEN)
    logging.info("Starting Slack RTM client...")
    rtm_client.start()

if __name__ == "__main__":
    main()
