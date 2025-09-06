import os
import urllib.request
import zipfile


def download_flowmaps(output_folder: str):
    filename = 'flowmaps.zip'

    # TODO: give ability to select different versions
    url = f"https://hestia.earth/flowmaps/{filename}"

    os.makedirs(output_folder, exist_ok=True)

    zip_file_path = os.path.join(output_folder, filename)

    # Download the zip file
    print(f"Downloading from {url}...")
    urllib.request.urlretrieve(url, zip_file_path)
    print("Download complete.")

    # Unzip the file
    print("Unzipping file...")
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)
    print("Unzipping complete.")

    # Clean up by removing the downloaded zip file
    os.remove(zip_file_path)
    print("Original zip file removed.")
