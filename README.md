# Google Drive File Renamer

This is a script that will batch rename JPEG files on your Google Drive based
on the date and time in the existing filename. It will rename files with
filenames in the format `YYYYMMDD_HHMMSS.jpg`.

This is a hobby project of mine to learn about APIs and the Git workflow for a
real-world project.

> **Note:** The commands below use `python` as an example. Depending on your
> system, you may have to use `python`, `python3`, or `py` to invoke Python.

## Naming Conventions

The script will rename JPEG files with filenames in the format
`YYYYMMDD_HHMMSS.jpg`.

For a given JPEG file, if there are no other JPEGs with the same date in its
folder, its new filename will be in the format `YY-MM-DD.jpg`.

If there are other JPEGs with the same date as the file in the folder, its new
filename will be in the format `YY-MM-DD[_1|_2|_3|...].jpg`. That is, the
date followed by an `_1`, `_2`, etc. depending on the order in which
the images were taken.

Here are some examples:
| Files in folder | Filenames after renaming |
| --- | --- |
| `20261014_165136.jpg` | `26-10-14.jpg` |
| `20261014_165136.jpg`, `20261014_165210.jpg` | `26-10-14_1.jpg`, `26-10-14_2.jpg` |
| `20261014_165136.jpg`, `20261014_165157.jpg`, `20261014_165210.jpg` | `26-10-14_1.jpg`, `26-10-14_2.jpg`, `26-10-14_3.jpg`|

## Executable File

### Setup

1. Download `file_renamer.exe` (for Windows) from GitHub Releases.

2. [Configure Google Drive API credentials](https://developers.google.com/workspace/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application)
    and place your `credentials.json` file in the same folder as the `.exe` file.

3. On your first run of `file_renamer.exe` (perhaps with `--dry-run` enabled),
you will have to sign into Google and grant the requested permissions.

### Usage

```powershell
.\file_renamer.exe [--dry-run | --verbose | --help]
```

## Python Script

### Setup

1. Clone this repository:

    ```powershell
   git clone https://github.com/Gallboy2020/google-drive-file-renamer.git
   cd google-drive-file-renamer
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   > **Note:** You may have to activate your virtual environment a different
   > way depending on your environment.

3. Install dependencies:

    Try using `requirements.txt`:
    ```powershell
    python -m pip install -r requirements.txt
    ```

    Alternatively, install the required libraries manually:
    ```powershell
    python -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    ```

4. [Configure Google Drive API credentials](https://developers.google.com/workspace/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application)
    and place your `credentials.json` file in the project folder.

### Usage

```powershell
python file_renamer.py [--dry-run | --verbose | --help]
```

## Options

- `--dry-run`: Preview renames without actually renaming the files
- `--verbose`: Rename files as normal but print each operation
- `--help`: Show a help message and exit

> **Note:** Running with no options will rename files without descriptive
> output.

> **Note:** All of these options are mutually exclusive, i.e. the script only
> accepts one of the three.

## Some Notes

- Use the `--dry-run` and `--verbose` modes to make sure you only rename the
    files you want to.
- To see a help message, use the `--help` option.
- Keep your API credentials and authentication tokens private, i.e. never
    commit `credentials.json` or `token.json` to version control.

## Some Links

- [Google Drive API Python Quickstart](https://developers.google.com/workspace/drive/api/quickstart/python)
- [Google Drive API `files.list` Method](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list)
- [Google Drive API `files.update` Method](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update)

## Contributing

Pull requests are welcome.

Please make sure to update tests and documentation as appropriate.

## Licence

See `LICENCE.txt`.