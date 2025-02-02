#!/usr/bin/env python3
import os
import subprocess
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import getpass

# Load environment variables from .env file
load_dotenv()

# Configure logging to see info/debug messages on the console
logging.basicConfig(level=logging.INFO)

# Get the Slack Bot token and target channel ID from environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
TARGET_CHANNEL_ID = os.environ.get("TARGET_CHANNEL_ID")

if not all([SLACK_BOT_TOKEN, SLACK_APP_TOKEN, TARGET_CHANNEL_ID]):
    logging.error("SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and TARGET_CHANNEL_ID must be set in the environment.")
    exit(1)

# Initialize the Slack Bolt App
app = App(token=SLACK_BOT_TOKEN)

@app.message("")
def handle_message(message, say, client):
    """
    This function is called on every incoming message event.
    It checks that the message is from the target channel and not sent by a bot,
    then executes the message text as a shell command.
    """
    channel = message.get("channel")
    text = message.get("text", "")
    user_id = message.get("user")
    
    # Process only messages in our target channel
    if channel != TARGET_CHANNEL_ID:
        return

    # Get user info
    try:
        user_info = client.users_info(user=user_id)
        username = user_info["user"]["name"]
    except Exception as e:
        username = "unknown_user"
        logging.error(f"Failed to get user info: {e}")

    logging.info(f"Received command from {username}: {text}")

    # Get current working directory and username
    current_path = os.getcwd()
    system_user = getpass.getuser()
    # Get the shortened path (similar to bash prompt)
    home = os.path.expanduser("~")
    if current_path.startswith(home):
        current_path = "~" + current_path[len(home):]

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

    # Format the response like a terminal prompt
    prompt = f"{system_user}@{os.uname().nodename}:{current_path}$ {text}"
    response_message = f"```{prompt}\n{output}```"

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
