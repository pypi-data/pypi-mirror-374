# import modules
import os
import requests
from bs4 import BeautifulSoup
import zipfile

# define download function
def download_databases(url = "https://nces.ed.gov/ipeds/use-the-data/download-access-database", download_directory="ipeds_databases"):
    """
    Download IPEDS data from NCES.
    """
    # identify .zip files
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    zip_url_list = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.zip'):
            # make full URL if link is relative
            if not href.startswith(('http://', 'https://')):
                full_zip_url = requests.compat.urljoin(url, href)
            else:
                full_zip_url = href
            zip_url_list.append(full_zip_url)
    
    # download .zip files
    print(f"Downloading IPEDS databases...")

    # create download_directory
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
   
    for zip_url in zip_url_list:
        try:
            # define filepath for each .zip file
            zip_filename = os.path.basename(zip_url)
            filepath = os.path.join(download_directory, zip_filename)

            # skip downloading existing .zip files
            if os.path.exists(filepath):
                print(f"{filepath} already exists. Skipping download.")
            else:
                zip_response = requests.get(zip_url, stream=True)
                zip_response.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in zip_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Successfully downloaded {zip_url}")

        # display any errors
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {zip_url}: {e}")
        except Exception as e:
            print(f"Error downloading {zip_url}: {e}")

    # extract .accdb files
    print(f"Extracting IPEDS databases...")

    for filename in os.listdir(download_directory):
        if filename.endswith(".zip"):
            zip_filepath = os.path.join(download_directory, filename)
            try:
                with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                    for member in zip_ref.namelist():
                        # ignoring directories, extract only .accdb files
                        if not member.endswith('/') and member.endswith('.accdb'):
                            # do not create subdirectories
                            base_filename = os.path.basename(member)
                            # handle potential root directories (empty string)
                            if base_filename:
                                source = zip_ref.open(member)
                                target_path = os.path.join(download_directory, base_filename)
                                
                                with open(target_path, "wb") as target:
                                    target.write(source.read())
                                print(f"Successfully extracted '{member}'")

            # display any errors
            except zipfile.BadZipFile:
                print(f"Error extracting {filename}: Not a valid .zip file.")
            except Exception as e:
                print(f"Error extracting {filename}: {e}")

# call function
# download_databases()