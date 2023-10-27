import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload



def authenticate_gdrive():
    # Path to the token file
    token_file = 'token.json'

    # Define the scopes needed for Google Drive API
    scopes = ['https://www.googleapis.com/auth/drive.file']

    # Check if token file exists
    if not os.path.exists(token_file):
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', scopes)
        credentials = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(credentials.to_json())

    # Load the credentials from the saved token file
    credentials = Credentials.from_authorized_user_file(token_file, scopes)

    return credentials



def upload_file_to_folder(service, file_path, folder_id):
    # Define file metadata
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id],
        'appProperties': {'CreationTime': str(datetime.datetime.now())}
    }

    # Upload the file
    media = MediaFileUpload(file_path, resumable=True)
    request = service.files().create(body=file_metadata, media_body=media)

    response = None
    try:
        response = request.execute()
        print('File uploaded successfully!')
        print(f'File ID: {response["id"]}')
    except Exception as e:
        print(f'Error uploading file: {e}')

    return response



def get_files_in_folder(service, folder_id):
    files = None
    try:
        results = service.files().list(q=f"'{folder_id}' in parents", orderBy='createdTime').execute()
        files = results.get('files', [])
        print('Files listed successfully')
    except Exception as e:
        print(f'Error listing files: {e}')
    return files




def delete_file_by_id(service, file_id):
    try:
        # Delete the file by ID
        service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
        print(f'File with ID {file_id} deleted successfully.')
    except Exception as e:
        print(f'Error deleting file: {e}')
