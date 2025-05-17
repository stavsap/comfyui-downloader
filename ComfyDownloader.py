import os
import random
import requests
from tqdm import tqdm

TOKEN_SOURCE_TYPE_PLAIN = "plain"
TOKEN_SOURCE_TYPE_ENV_VAR = "environment variable"
TOKEN_SOURCE_TYPE_PATH = "path to file"

def delete(file_name, path):
    os.remove(os.path.join(path, file_name))

def is_exist(file_name, path):
    """
    Check if a file exists at the specified path.

    Args:
        file_name (str): The name of the file to check.
        path (str): The directory path to check in.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    # Join the path and file name to create the full file path
    full_path = os.path.join(path, file_name)

    # Check if the file exists
    return os.path.isfile(full_path)

def download_file(url, file_name, path, token=None):
    if not os.path.exists(path):
        os.makedirs(path)
    headers = {}
    if token is not None:
        if url.startswith("https://huggingface.co"):
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"Token given but domain not supported! [{url}]")
    with requests.get(url, stream=True, allow_redirects=True, headers = headers) as response:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 4096  # 4KB blocks
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=file_name)
        with open(os.path.join(path, file_name), 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder: '{folder_path}', created.")

class Downloader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "url": ("STRING", {
                    "multiline": False,
                }),
                "path": ("STRING", {
                    "multiline": False,
                }),
                "file_name": ("STRING", {
                    "multiline": False,
                }),
                "force": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "summary": ("DOWNLOAD_SUMMARY", {"forceInput": False},),
                "token": ("STRING", {"forceInput": False},),
            }
        }

    RETURN_TYPES = ("DOWNLOAD_SUMMARY",)
    RETURN_NAMES = ("summary",)
    FUNCTION = "downloader"
    CATEGORY = "Downloader"

    def downloader(self, url, path, file_name, force, token=None, summary=None):
        # TODO handle token if needed.
        if force:
            delete(file_name, path)

        if summary is None:
            summary = []
        if not is_exist(file_name, path):
            create_folder_if_not_exists(path)
            download_file(url, file_name, path, token=token)
            result = f"downloaded {url} to {os.path.join(path, file_name)}"
        else:
            result = f"{os.path.join(path, file_name)} present"
        summary.append(result)
        return (summary, )

    @classmethod
    def IS_CHANGED(s, url, path, file_name, token, summary=None):
        return random.uniform(0, 100000)

class DownloadSummaryParser:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "summary": ("DOWNLOAD_SUMMARY",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "parse"
    CATEGORY = "Downloader"

    def parse(self, summary):
        text = "\n"

        for e in summary:
            text += f"- {e}\n"

        return (text, )

class DownloadTokenLoader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("STRING",{
                    "multiline": False,
                }),
                "type": ([TOKEN_SOURCE_TYPE_PLAIN,TOKEN_SOURCE_TYPE_ENV_VAR,TOKEN_SOURCE_TYPE_PATH], {})
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("token",)
    FUNCTION = "load"
    CATEGORY = "Downloader"

    def load(self, value, type):
        if type == TOKEN_SOURCE_TYPE_ENV_VAR:
            value = os.environ.get(value)
        if type == TOKEN_SOURCE_TYPE_PLAIN:
            with open(value, 'r', encoding='utf-8') as file:
                value = file.read()
        print(value)
        return (value, )


NODE_CLASS_MAPPINGS = {
    "Downloader": Downloader,
    "DownloadSummaryParser": DownloadSummaryParser,
    "DownloadTokenLoader": DownloadTokenLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Downloader": "Downloader",
    "DownloadSummaryParser": "Download Summary Parser",
    "DownloadTokenLoader": "Download Token Loader",
}
