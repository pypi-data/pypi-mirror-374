import os
import sys
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv


def upload_to_slack(file_path: str, channel_id: Optional[str] = None, initial_comment: Optional[str] = None) -> bool:
    """
    Upload a file to Slack channel.
    
    Args:
        file_path: Path to the file to upload
        channel_id: Slack channel ID (optional, uses env var if not provided)
        initial_comment: Optional comment to post with the file
        
    Returns:
        bool: True if upload successful, False otherwise
    """
    # Load environment variables
    load_dotenv()
    
    # Get Slack credentials from environment
    slack_token = os.environ.get('PROJECT_SLACK_BOT_TOKEN')
    print(f"SLACK_BOT_TOKEN: {slack_token}")
    if not slack_token:
        print("Error: SLACK_BOT_TOKEN not found in environment variables")
        return 
    
    # Use provided channel_id or get from environment
    channel = channel_id or os.environ.get('PROJECT_SLACK_CHANNEL_ID')
    if not channel:
        print("Error: No channel ID provided and SLACK_CHANNEL_ID not found in environment")
        return False
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    # Get file size in MB
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"Uploading file: {os.path.basename(file_path)} ({file_size_mb:.2f} MB)")
    
    # Initialize Slack client
    client = WebClient(token=slack_token)
    
    try:
        # Upload file
        print(f"Uploading to Slack channel: {channel}")
        response = client.files_upload_v2(
            channel=channel,
            file=file_path,
            title=os.path.basename(file_path),
            initial_comment=initial_comment or f"Firmware build completed: {os.path.basename(file_path)}"
        )
        
        # Get file info from response
        file_info = response.get("file", {})
        file_url = file_info.get("permalink")
        
        print(f"[SUCCESS] File uploaded successfully!")
        print(f"   File ID: {file_info.get('id')}")
        print(f"   File URL: {file_url}")
        
        return True
        
    except SlackApiError as e:
        error_msg = e.response.get('error', 'Unknown error')
        print(f"[ERROR] Slack API Error: {error_msg}")
        
        # Print full error details for debugging
        print(f"   Full error response: {e.response}")
        
        # Provide helpful error messages
        if error_msg == 'invalid_auth':
            print("   Check that your SLACK_BOT_TOKEN is correct")
            print("   Token should start with 'xoxb-'")
        elif error_msg == 'channel_not_found':
            print("   Check that the channel ID is correct and the bot is added to the channel")
            print("   Channel ID should look like: C1234567890")
        elif error_msg == 'not_in_channel':
            print("   The bot needs to be invited to the channel. Use: /invite @your-bot-name")
        elif error_msg == 'file_too_large':
            print(f"   File size ({file_size_mb:.2f} MB) exceeds Slack limit")
        elif error_msg == 'missing_scope':
            print("   The bot needs 'files:write' permission")
            print("   Go to https://api.slack.com/apps and add the scope")
        elif error_msg == 'no_permission':
            print("   The bot doesn't have permission to upload to this channel")
        elif error_msg == 'not_authed':
            print("   No authentication token provided or token is invalid")
            
        return False
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return False


def validate_slack_config() -> bool:
    """
    Validate that Slack configuration is properly set up.
    
    Returns:
        bool: True if configuration is valid
    """
    load_dotenv()
    
    token = os.environ.get('PROJECT_SLACK_BOT_TOKEN')
    channel = os.environ.get('PROJECT_SLACK_CHANNEL_ID')
    
    if not token:
        print("Warning: PROJECT_SLACK_BOT_TOKEN not configured")
        return False
        
    if not channel:
        print("Warning: PROJECT_SLACK_CHANNEL_ID not configured")
        return False
        
    # Basic token format validation
    if not token.startswith('xoxb-'):
        print("Warning: PROJECT_SLACK_BOT_TOKEN should start with 'xoxb-'")
        return False
        
    return True


if __name__ == "__main__":
    # Test the configuration
    if validate_slack_config():
        print("Slack configuration is valid")
    else:
        print("Slack configuration needs to be set up")