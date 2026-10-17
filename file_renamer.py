import sys
import os.path
from re import search

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata"]
# Folder IDs that will be searched recursively for jpeg files
FOLDERS_TO_SEARCH = ["1AdNiRtNL8Yxd9uQbZTM54RkoHmc67y94"]  # Year2_Semester1


def get_credentials():
    creds = None

    # Attempt to get credentials from token.json
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in
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

    return creds


def get_all_jpegs(service):
    all_jpegs = []

    # recursive search from given folders
    to_search = FOLDERS_TO_SEARCH[:]
    while to_search:
        
        curr_folder_id = to_search.pop()
        page_token = None
        while True:
            # get file listing from API
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

            for file in response.get("files", []):
                # if folder, add to search list
                if (file["mimeType"] == "application/vnd.google-apps.folder"):
                    to_search.append(file.get("id"))
                # if jpeg image, record
                elif file["mimeType"] == "image/jpeg":
                    all_jpegs.append(file)

            # break when no more pages to read in
            page_token = response.get("nextPageToken")
            if not page_token:
                break

    return all_jpegs


def get_jpegs_to_rename(all_jpegs):
    p = r'^\d{8}_\d{6}\.jpg$'  # e.g. 20261012_202436.jpg
    to_rename = []
    # record all jpegs that match the format
    for file in all_jpegs:
        match = search(p, file["name"])
        if match:
            to_rename.append(file)

    return to_rename


def group_jpegs(jpegs):
    # Group jpegs into lists for renaming together
    # e.g.  [20261014_165136.jpg, 20261014_165157.jpg, 20261014_165210.jpg]
    #       -> 26-10-14_1.jpg, 26-10-14_2.jpg, 26-10-14_3.jpg

    # group files by parent folder into dictonary
    folders = {}
    for file in jpegs:
        parent = file["parents"][0]  # parent folder ID
        if parent not in folders:
            folders[parent] = [file]
        else:
            folders[parent].append(file)

    # group files in each folder by date
    groups = []
    for files in folders.values():
        # sort files in folder by name (corresponds to date and time)
        files.sort(key=lambda file: file["name"])

        # create renaming groups
        if len(files) == 1:  # if only one file in folder to be renamed
            groups.append(files)
        else:  # group files in folder based on date
            while files:
                group = [files.pop(0)]
                for file in files[:]:
                    # if dates match
                    if file["name"][:8] == group[0]["name"][:8]:
                        # group with other files with same date
                        group.append(file)
                        # remove from list so not grouped twice
                        files.remove(file)
                groups.append(group)

    return groups, len(folders)


def rename_file(service, file_id, new_name):
    body = {'name': new_name}
    service.files().update(fileId = file_id, body=body).execute()

def rename_jpeg_groups(service, groups, dry_run, verbose):
    if dry_run:
        print("DRY-RUN MODE - would rename:")
    elif verbose:
        print("VERBOSE MODE - would rename:")

    file_count = 0
    for group in groups:
        # if only one file in group, simply rename it
        if len(group) == 1:
            name = group[0]["name"]
            new_name = f"{name[2:4]}-{name[4:6]}-{name[6:8]}.jpg"
            if dry_run or verbose:
                print(f"{name} -> {new_name}")
            if not dry_run:
                rename_file(service, group[0]["id"], new_name)
            file_count += 1

        # if more than one file, have to use numbering
        else:
            name = group[0]["name"]  # all files are from same date
            name_date = f"{name[2:4]}-{name[4:6]}-{name[6:8]}"
            num = 1
            for file in group:
                new_name = f"{name_date}_{num}.jpg"
                if dry_run or verbose:
                    print(f"{name} -> {new_name}")
                if not dry_run:
                    rename_file(service, file["id"], new_name)
                num += 1
                file_count += 1

    return file_count


def main():
    # read command line arguments for program options
    dry_run = False
    verbose = False
    if len(sys.argv) == 2:
        if sys.argv[1] == "--dry-run":
            dry_run = True
        elif sys.argv[1] == "--verbose":
            verbose = True

    # authenticate with Google and initialise the Drive API service
    service = build("drive", "v3", credentials=get_credentials())

    try:
        jpegs = get_all_jpegs(service)  # get all jpegs from Google Drive

        to_rename = get_jpegs_to_rename(jpegs)  # filter out ones we want
        if not to_rename:
            print("No files to be renamed.")
            return

        groups, folder_count = group_jpegs(to_rename)  # group for renaming

        file_count = rename_jpeg_groups(service, groups, dry_run, verbose)  # rename files

        if dry_run:
            print(
                f"\nWould have renamed {file_count} file(s) "
                f"in {folder_count} folder(s).\n"
            )
        else:
            print(
                f"\nRenamed {file_count} file(s) "
                f"in {folder_count} folder(s).\n"
            )

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
