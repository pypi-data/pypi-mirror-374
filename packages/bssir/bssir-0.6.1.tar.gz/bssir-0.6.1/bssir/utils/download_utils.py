from pathlib import Path
import platform
from zipfile import ZipFile

import requests

from ..metadata_reader import defaults


def download(url: str, path: Path) -> None:
    """Downloads a file from a given URL and saves it to a specified local path.

    This function uses the requests library to send a GET request to the provided URL,
    and then writes the response content to a file at the specified path. If the path
    is not provided, the file is saved in a temporary directory. The function also
    provides an option to display a progress bar during the download.

    Parameters
    ----------
    url : str
        The URL of the file to download.
    path : str, Path, optional
        The local path where the downloaded file should be saved. If None, the file
        is saved in a temporary directory. Default is None.
    show_progress_bar : bool, optional
        If True, a progress bar is displayed during the download. Default is False.

    Returns
    -------
    Path
        The local path where the downloaded file was saved.

    Raises
    ------
    FileNotFoundError
        If the file cannot be found at the given URL.
    """
    response = requests.get(url, timeout=1000, stream=True)
    content_iterator = response.iter_content(chunk_size=4096)
    remote_file_size = response.headers.get("content-length")
    if remote_file_size is not None:
        remote_file_size = int(remote_file_size)
    else:
        raise FileNotFoundError("File is not found on the server")
    if path.exists():
        local_file_size = path.stat().st_size
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        local_file_size = 0
    if remote_file_size == local_file_size:
        return
    with open(path, mode="wb") as file:
        while True:
            try:
                chunk = next(content_iterator)
            except StopIteration:
                break
            except requests.Timeout:
                continue
            file.write(chunk)


def download_7zip():
    """
    Download the appropriate version of 7-Zip for the current operating system
    and architecture, and extract it to the root directory.

    """
    print(
        f"Downloading 7-Zip for {platform.system()} with "
        f"{platform.architecture()[0]} architecture"
    )
    file_name = f"{platform.system()}-{platform.architecture()[0]}.zip"
    file_path = defaults.root_dir.joinpath(file_name)

    url = f"{defaults.mirrors[0].bucket_address}/7-Zip/{file_name}"
    download(url, file_path)

    with ZipFile(file_path) as zip_file:
        zip_file.extractall(defaults.root_dir)
    file_path.unlink()

    with open(defaults.root_dir.joinpath("7-Zip/.gitignore"), mode="w") as file:
        file.write("# This file created automatically by BSSIR\n*\n")

    if platform.system() == "Linux":
        defaults.root_dir.joinpath("7-Zip", "7zz").chmod(0o771)


def download_map(
    map_name: str, source: str, *, map_metadata: dict, maps_directory: Path
) -> None:
    url = map_metadata[map_name][f"{source}_link"]
    file_path = maps_directory.joinpath("map.zip")
    download(url, file_path)
    path = maps_directory.joinpath(map_name)
    path.mkdir(exist_ok=True, parents=True)
    with ZipFile(file_path) as zip_file:
        zip_file.extractall(path)
    file_path.unlink()
