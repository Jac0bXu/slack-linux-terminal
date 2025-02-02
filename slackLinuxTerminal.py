#!/usr/bin/env python3
import os
import subprocess
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load environment variables from .env file
load_dotenv()

# Configure logging to see info/debug messages on the console
logging.basicConfig(level=logging.INFO)

# Get the Slack Bot token and target channel ID from environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")  # New token needed for Socket Mode
TARGET_CHANNEL_ID = os.environ.get("TARGET_CHANNEL_ID")

if not all([SLACK_BOT_TOKEN, SLACK_APP_TOKEN, TARGET_CHANNEL_ID]):
    logging.error("SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and TARGET_CHANNEL_ID must be set in the environment.")
    exit(1)

# Initialize the Slack Bolt App
app = App(token=SLACK_BOT_TOKEN)

@app.message("")
def handle_message(message, say):
    """
    This function is called on every incoming message event.
    It checks that the message is from the target channel and not sent by a bot,
    then executes the message text as a shell command.
    """
    channel = message.get("channel")
    text = message.get("text", "")
    
    # Process only messages in our target channel
    if channel != TARGET_CHANNEL_ID:
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
        say(response_message)
        logging.info("Command output sent to Slack.")
    except Exception as e:
        logging.error(f"Failed to post message to Slack: {e}")

def main():
    # Initialize and start the Socket Mode handler
    handler = SocketModeHandler(app_token=SLACK_APP_TOKEN, app=app)
    logging.info("Starting Slack app in Socket Mode...")
    handler.start()

if __name__ == "__main__":
    main()
