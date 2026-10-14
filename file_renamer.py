import os.path
from re import search

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata"]


def rename_file(service, fileID, new_name):
    body = {'name': new_name}
    service.files().update(fileId = fileID, body=body).execute()
    # return <above>

def main():

    # Get credentials
    creds = None
    # Attempt to get credentials from token.json.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Query for files to be renamed
    service = build("drive", "v3", credentials=creds)
    all_files = []
    folders_to_search = ["1AdNiRtNL8Yxd9uQbZTM54RkoHmc67y94"]

    try:
        # recursive search from given folder above in folders_to_search
        while folders_to_search:
            curr_folder_id = folders_to_search.pop()
            page_token = None

            while True:
                response = (
                    service.files()
                    .list(
                        q=f"'{curr_folder_id}' in parents and trashed = false",
                        fields="nextPageToken, files(id, name, mimeType, parents)",
                        pageSize=1000,
                        pageToken=page_token,
                    )
                    .execute()
                )

                for item in response.get("files", []):
                    if (
                        item.get("mimeType")
                        == "application/vnd.google-apps.folder"
                    ):  # if folder, add to search list
                        folders_to_search.append(item.get("id"))
                    elif (
                        item.get("mimeType")
                        == "image/jpeg"
                    ):  # if jpeg image, record
                        all_files.append(item)

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

        # extract files that need to be renamed
        p = r'^\d{8}_\d{6}\.jpg$'  # e.g. 20261012_202436.jpg
        to_be_renamed = []
        for file in all_files:
            match = search(p, file["name"])
            if match:
                to_be_renamed.append(file)

        if not to_be_renamed:
            print("No files to be renamed.")
            exit(0)

        # group files by folder in dictonary "folders"
        folders = {}
        for file in to_be_renamed:
            folder = file["parents"][0]  # folder ID
            if folder not in folders:
                folders[folder] = [file]
            else:
                folders[folder].append(file)

        # split files to be renamed into groups based on date
        groups = []
        for files in folders.values():
            # sort files in folder by name (corresponds to date and time)
            files.sort(key=lambda d: d["name"])

            # create renaming groups
            if len(files) == 1:  # if only one file in folder to be renamed
                groups.append(files)
            else:  # break up files in folder based on date
                while files:
                    group = [files.pop(0)]
                    for file in files[:]:
                        if file["name"][:8] == group[0]["name"][:8]:
                            group.append(file)
                            files.remove(file)
                    groups.append(group)

        # rename based on groups
        count = 0
        for group in groups:
            if len(group) == 1:
                name = group[0]["name"]
                new_name = f"{name[2:4]}-{name[4:6]}-{name[6:8]}.jpg"
                rename_file(service, group[0]["id"], new_name)
                count += 1
            else:
                name = group[0]["name"]  # all files are from same date
                name_date = f"{name[2:4]}-{name[4:6]}-{name[6:8]}"
                num = 1
                for file in group:
                    new_name = f"{name_date}_{num}.jpg"
                    rename_file(service, file["id"], new_name)
                    num += 1
                    count += 1

        print(f"{count} file(s) in {len(folders)} folder(s) renamed.")


    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
