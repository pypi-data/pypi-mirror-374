import os
import serial
import sys
import subprocess
import glob
import time
import re
import json

# Function to run a command and check for errors
def run_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        sys.exit(e.returncode)

def parse_commit_message():
    """Parse CI_COMMIT_MESSAGE to extract required information."""
    commit_message = os.getenv("CI_COMMIT_MESSAGE", "")
    if not commit_message:
        print("CI_COMMIT_MESSAGE environment variable is not set.")
        return None, None
    
    # Split message by spaces
    parts = commit_message.split()
    
    if len(parts) < 1:
        print(f"Invalid CI_COMMIT_MESSAGE format: {commit_message}")
        print("At least 1 piece of information is required.")
        return None, None
    
    # First information is filename (existing logic)
    filename = parts[0].split("[")[0] if "[" in parts[0] else parts[0]
    
    # Extract Google Drive file ID from bracket content
    if "[" in parts[0]:
        try:
            bracket_content = parts[0].split("[")[1].split("]")[0]
            pipe_parts = bracket_content.split("|")
            if len(pipe_parts) >= 4:
                google_drive_file_id = pipe_parts[3]
            else:
                print(f"Invalid bracket format in CI_COMMIT_MESSAGE: {parts[0]}")
                print("Expected format: filename[info1|info2|info3|file_id]")
                return None, None
        except Exception as e:
            print(f"Error parsing bracket content: {e}")
            return None, None
    else:
        # If no bracket, assume the whole first part is the file ID
        google_drive_file_id = parts[0]
    
    print(f"Parsed info - Filename: {filename}, Google Drive ID: {google_drive_file_id}")
    return filename, google_drive_file_id

# Use regular expression to find the pattern
def get_sha(file):
    matched = re.search(r'_([a-f0-9]{8})[_\.]', file)
    if matched:
        sha = matched.group(1)
    else:
        sha = ""
    return sha

def cleanup_downloaded_files(file_path):
    """Clean up downloaded temporary files."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Temporary file deleted: {file_path}")
        else:
            print(f"File to delete does not exist: {file_path}")
    except Exception as e:
        print(f"Error occurred while deleting file: {e}")

def create_temp_directory(base_dir="temp_downloads"):
    """Create temporary download directory."""
    try:
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    except Exception as e:
        print(f"Error occurred while creating temporary directory: {e}")
        return None

def read_serial(ser,sha=""):
        print("----- Reading from the serial port -----")
        sha_check = False
        start_time = time.time()
        try:
            while time.time() - start_time < 6:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        if sha and sha in line:
                            sha_check = True
                        print(line)
                except serial.SerialTimeoutException:
                    pass
        except Exception as e:
            print(f"An error occurred: {e}")

        if sha:
            if sha_check:
                print(f'*** {sha} programming success.')
            else:
                print(f'*** {sha} programmed fail !!!!')

def check_stlink(sn):
    run_command(['STM32_Programmer_CLI.exe', '-l', 'stlink']);

def open_stlink():
    runner_name = os.getenv("RUNNER_NAME")
    stlink_name = os.getenv("STLINK_NAME")
    # Load the stlink_list.json file
    with open('stlink_list.json', 'r') as f:
        stlink_list = json.load(f)

    # Get the stlink details using the stlink_name key from the stlink_list
    if f'{runner_name}-{stlink_name}' in stlink_list:
        stlink_details = stlink_list[f'{runner_name}-{stlink_name}']
        print(f"STLink details for {stlink_name}: {stlink_details}")
        stlink_port = stlink_details.get('port')
        stlink_sn = stlink_details.get('sn')
    else:
        print(f"No details found for the key '{stlink_name}'. Exiting with status 1.")
        sys.exit(1)

    check_stlink(stlink_sn)

    try:
        ser = serial.Serial(stlink_port, 115200, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port")
        ser = None
        pass

    return ser,stlink_sn
