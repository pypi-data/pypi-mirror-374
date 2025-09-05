import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import json

def get_google_drive_service():
    """Create Google Drive API service object."""
    try:
        # service account key file path
        SERVICE_ACCOUNT_FILE = 'service-account-key.json'
        
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"Service account key file not found: {SERVICE_ACCOUNT_FILE}")
            return None
        
        # Set permission scope - 읽기 전용에서 전체 권한으로 변경
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # Service account authentication
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # Build Drive API service
        service = build('drive', 'v3', credentials=credentials)
        print("Google Drive API service created successfully")
        print(f"Service account email: {credentials.service_account_email}")
        return service
    except Exception as e:
        print(f"Error occurred while creating Google Drive service: {e}")
        return None

def download_file_from_google_drive(file_id, destination_path):
    """Download file from Google Drive."""
    try:
        service = get_google_drive_service()
        if not service:
            print("Failed to initialize Google Drive service.")
            return False
        
        # Get file metadata - supportsAllDrives=True 추가
        try:
            file_metadata = service.files().get(
                fileId=file_id,
                fields='id, name, size',
                supportsAllDrives=True
            ).execute()
            file_name = file_metadata.get('name')
            file_size = file_metadata.get('size', 'Unknown')
            print(f"Downloading file from Google Drive: {file_name} (size: {file_size} bytes)")
        except HttpError as e:
            if e.resp.status == 404:
                print(f"File not found on Google Drive. File ID: {file_id}")
                print("Possible causes:")
                print("1. File ID is incorrect")
                print("2. Service account doesn't have access to the file")
                print("3. File has been deleted or moved")
                print(f"Please share the file with service account: ci-tools-drive-folder-access@jltech-smartfactory.iam.gserviceaccount.com")
            elif e.resp.status == 403:
                print(f"Access denied to file. File ID: {file_id}")
                print(f"Please share the file with service account: ci-tools-drive-folder-access@jltech-smartfactory.iam.gserviceaccount.com")
            else:
                print(f"Error occurred while getting file metadata: {e}")
            return False
        
        # Download file - supportsAllDrives=True는 get_media에는 적용되지 않음
        request = service.files().get_media(fileId=file_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%")
        
        # Save file
        destination_dir = os.path.dirname(destination_path)
        if destination_dir:  # 디렉토리가 있는 경우에만 생성
            os.makedirs(destination_dir, exist_ok=True)
        
        with open(destination_path, 'wb') as f:
            f.write(file_io.getvalue())
        
        print(f"File download completed: {destination_path}")
        return True
        
    except HttpError as e:
        print(f"Google Drive API error occurred: {e}")
        if e.resp.status == 404:
            print(f"File not found. Please check if the file ID is correct: {file_id}")
            print(f"Or share the file with service account: ci-tools-drive-folder-access@jltech-smartfactory.iam.gserviceaccount.com")
        elif e.resp.status == 403:
            print(f"Access denied. Please share the file with service account: ci-tools-drive-folder-access@jltech-smartfactory.iam.gserviceaccount.com")
        return False
    except Exception as e:
        print(f"Unexpected error occurred during Google Drive file download: {e}")
        return False

def get_file_info_from_google_drive(file_id):
    """Get file information from Google Drive."""
    try:
        service = get_google_drive_service()
        if not service:
            print("Failed to initialize Google Drive service.")
            return None
        
        # Get file metadata - supportsAllDrives=True 추가
        try:
            file_metadata = service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, createdTime, modifiedTime, owners, parents, shared, trashed',
                supportsAllDrives=True
            ).execute()
            print(f"File info retrieved successfully: {file_metadata.get('name')}")
            return file_metadata
        except HttpError as e:
            if e.resp.status == 404:
                print(f"File not found on Google Drive. File ID: {file_id}")
                print("Possible causes:")
                print("1. File ID is incorrect")
                print("2. Service account doesn't have access to the file")
                print("3. File has been deleted or moved")
                print(f"Please share the file with service account: ci-tools-drive-folder-access@jltech-smartfactory.iam.gserviceaccount.com")
            elif e.resp.status == 403:
                print(f"Access denied to file. File ID: {file_id}")
                print(f"Please share the file with service account: ci-tools-drive-folder-access@jltech-smartfactory.iam.gserviceaccount.com")
            else:
                print(f"Error occurred while getting file info: {e}")
            return None
        
    except Exception as e:
        print(f"Unexpected error occurred while getting Google Drive file info: {e}")
        return None 