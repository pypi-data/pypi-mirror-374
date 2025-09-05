import os
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Lock

import requests
from bs4 import BeautifulSoup

from niklibrary.helper.Cmd import Cmd
from niklibrary.helper.Statics import Statics


class OemOp:

    @staticmethod
    def write_all_files(dir_path, overwrite=True):
        all_files_path = dir_path + os.path.sep + "all_files.txt"
        if overwrite or not os.path.exists(all_files_path):
            with open(all_files_path, "w") as f:
                directory = str(dir_path)
                # Walk through the directory and list files
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        # Write the relative file path to the file
                        relative_path = os.path.relpath(os.path.join(root, file), directory)
                        f.write(relative_path.replace("\\", "/") + '\n')
        else:
            print("All files already written")

    @staticmethod
    def get_google_oem_dump_dict(repo_dir):
        supported_partitions = ["system_ext", "product"]
        gapps_dict = {}
        cmd = Cmd()
        for partition in supported_partitions:
            supported_types = {"priv-app": "priv-app", "app": "app"}
            for supported_type in supported_types:
                partition_dir = repo_dir + Statics.dir_sep + partition + Statics.dir_sep + \
                                supported_type + Statics.dir_sep
                for path in Path(partition_dir).rglob("*.apk"):
                    if path.is_file():
                        path = str(path)
                        path = path.replace("\\", "/")
                        file_size = os.stat(path).st_size
                        file_path = str(path)
                        file_location = file_path[len(repo_dir) + 1:]
                        file_path = file_path[len(partition_dir):]
                        folder_name = file_path.split("/")[0]
                        isstub = True if folder_name.__contains__("-Stub") else False
                        package_name = cmd.get_package_name(path)
                        package_version = cmd.get_package_version(path)
                        version_code = cmd.get_package_version_code(path)
                        version = ''.join([i for i in package_version if i.isdigit()])
                        gapps_list = gapps_dict[package_name] if package_name in gapps_dict else []
                        g_dict = {"partition": partition, "type": supported_types[supported_type],
                                  "folder": folder_name, "version_code": version_code, "v_code": version,
                                  "file": file_path, "package": package_name, "version": package_version,
                                  "location": file_location, "isstub": isstub, "size": file_size}
                        gapps_list.append(g_dict)
                        if isstub:
                            apk_gz_folder = folder_name.replace("-Stub", "")
                            for apk_gz_path in Path(str(partition_dir) + apk_gz_folder).rglob("*.apk.gz"):
                                if apk_gz_path.is_file():
                                    apk_gz_file_path = str(apk_gz_path).replace("\\", "/")
                                    file_size = os.stat(apk_gz_file_path).st_size
                                    apk_gz_file_path = apk_gz_file_path[len(partition_dir):]
                                    apk_gz_file_location = str(apk_gz_path)[len(repo_dir) + 1:].replace("\\", "/")
                                    gz_dict = {"partition": partition, "type": supported_types[supported_type],
                                               "folder": apk_gz_folder, "version_code": version_code, "v_code": version,
                                               "file": apk_gz_file_path, "package": package_name,
                                               "version": package_version, "location": apk_gz_file_location,
                                               "isstub": isstub, "size": file_size}
                                    gapps_list.append(gz_dict)
                        if package_name not in gapps_dict:
                            gapps_dict[package_name] = gapps_list
        return gapps_dict

    @staticmethod
    def get_latest_ota_url(device_name, android_version=None):
        url = "https://developers.google.com/android/ota"
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        try:
            response = requests.get(url, cookies={"devsite_wall_acks": "nexus-ota-tos"}, headers=header)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to fetch the page. Error: {str(e)}")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')

        device_section = soup.find(id=device_name)
        if not device_section:
            raise Exception(f"Device {device_name} not found on the page.")

        # Find the table next to the device section
        table = device_section.find_next('table')
        if not table:
            raise Exception(f"No table found for device {device_name}.")

        # Initialize a dictionary to categorize URLs
        categorized_urls = defaultdict(list)

        # Find all rows in the table
        rows = table.find_all('tr')[1:]  # Skip the header row

        for row in rows:
            columns = row.find_all('td')
            if len(columns) < 3:
                continue

            version_info = columns[0].get_text(strip=True)
            link = columns[1].find('a', href=True)['href']
            checksum = columns[2].get_text(strip=True)

            # Extract the month and year from the version_info
            match = re.search(r'\((.*?)\)', version_info)
            if match:
                date_info = match.group(1).split(',')[1].strip()
                date = datetime.strptime(date_info, '%b %Y')
                category = "Regular"
                if 'T-Mobile' in version_info:
                    category = 'T-Mobile'
                elif 'Verizon' in version_info:
                    category = 'Verizon'
                elif 'G-store' in version_info:
                    category = 'G-store'
                categorized_urls[date].append({
                    'url': link,
                    'checksum': checksum,
                    'category': category,
                    'version_info': version_info
                })

        # Sort the categorized URLs by date
        sorted_dates = sorted(categorized_urls.keys(), reverse=True)

        # Find the latest regular build
        latest_regular_url = None
        for date in sorted_dates:
            for url_info in categorized_urls[date]:
                if url_info['category'] == 'Regular':
                    if android_version and f"{android_version}.0.0" not in url_info['version_info']:
                        continue
                    latest_regular_url = url_info['url']
                    break
            if latest_regular_url:
                break

        if not latest_regular_url:
            raise Exception(f"No valid regular OTA URLs found for device {device_name}.")

        return latest_regular_url

    @staticmethod
    def get_google_devices():
        url = "https://developers.google.com/android/ota"
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        try:
            response = requests.get(url, cookies={"devsite_wall_acks": "nexus-ota-tos"}, headers=header)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to fetch the page. Error: {str(e)}")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        google_devices = {}
        # Search only inside the article body
        article = soup.find("div", class_="devsite-article-body")
        if not article:
            print("No article body found.")
            return None
        h2elements = article.find_all("h2")
        # Find all h2 elements with data-text containing "for"
        for h2 in h2elements:
            data_text = h2["data-text"]

            if "for" in data_text:
                # Example: '"frankel" for Pixel 10'
                # Split on 'for'
                try:
                    code_name = h2.get("id")
                    device_name = data_text.split("for", 1)[1].strip()
                    if code_name and device_name:
                        google_devices[code_name] = device_name
                except Exception as parse_error:
                    print(f"Skipping malformed h2: {parse_error}")

        return google_devices

    @staticmethod
    def get_google_oem_dump_dict_async(repo_dir):
        supported_partitions = ("system_ext", "product")
        supported_types = ("priv-app", "app")

        repo_dir = Path(repo_dir).resolve()
        print(f"Scanning repository at {repo_dir} ...")

        gapps_dict = defaultdict(list)
        lock = Lock()
        cmd = Cmd()

        work_items = []
        for partition in supported_partitions:
            for apk_type in supported_types:
                partition_dir = (repo_dir / partition / apk_type)
                if not partition_dir.is_dir():
                    continue
                for root, _, files in os.walk(partition_dir):
                    for fname in files:
                        if fname.endswith(".apk"):
                            work_items.append((partition, apk_type, partition_dir, Path(root) / fname))

        def _relpath_safe(path: Path, start: Path) -> str:
            """Return posix relpath even across drives/case issues."""
            try:
                return path.relative_to(start).as_posix()
            except Exception:
                try:
                    return Path(os.path.relpath(path.as_posix(), start.as_posix())).as_posix()
                except Exception:
                    # last resort: keep absolute posix path
                    return path.as_posix()

        def process_apk(item):
            partition, apk_type, partition_dir, apk_path = item
            apk_path_abs = apk_path.resolve()
            partition_dir_abs = partition_dir.resolve()

            apk_posix = apk_path_abs.as_posix()
            print(f"Processing APK: {apk_posix}")

            try:
                file_size = os.stat(apk_path_abs).st_size
            except OSError:
                return None

            file_location = _relpath_safe(apk_path_abs, repo_dir)  # relative to repo root
            print(f"File location: {file_location}")
            file_path_rel = _relpath_safe(apk_path_abs, partition_dir_abs)  # relative to partition/<type>

            # folder name = first segment after partition_dir (priv-app/app child)
            parts = Path(file_path_rel).parts
            folder_name = parts[0] if parts else ""

            is_stub = folder_name.endswith("-Stub")
            base_folder = folder_name[:-5] if is_stub else folder_name

            package_name = cmd.get_package_name(apk_posix)
            package_version = cmd.get_package_version(apk_posix)
            version_code = cmd.get_package_version_code(apk_posix)
            v_code_numeric = "".join(ch for ch in package_version if ch.isdigit())

            base_dict = {
                "partition": partition,
                "type": apk_type,
                "folder": folder_name,
                "version_code": version_code,
                "v_code": v_code_numeric,
                "file": file_path_rel,
                "package": package_name,
                "version": package_version,
                "location": file_location,
                "isstub": is_stub,
                "size": file_size,
            }

            results = [base_dict]

            if is_stub:
                gz_dir = partition_dir_abs / base_folder
                if gz_dir.is_dir():
                    for root, _, files in os.walk(gz_dir):
                        for fn in files:
                            if fn.endswith(".apk.gz"):
                                gz_path = Path(root) / fn
                                try:
                                    gz_size = os.stat(gz_path).st_size
                                except OSError:
                                    continue
                                gz_file_rel = _relpath_safe(gz_path.resolve(), partition_dir_abs)
                                gz_file_location = _relpath_safe(gz_path.resolve(), repo_dir)
                                results.append({
                                    "partition": partition,
                                    "type": apk_type,
                                    "folder": base_folder,
                                    "version_code": version_code,
                                    "v_code": v_code_numeric,
                                    "file": gz_file_rel,
                                    "package": package_name,
                                    "version": package_version,
                                    "location": gz_file_location,
                                    "isstub": True,
                                    "size": gz_size
                                })

            return package_name, results

        max_workers = os.cpu_count() or 4
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(process_apk, item) for item in work_items]
            for fut in as_completed(futures):
                res = fut.result()
                if not res:
                    continue
                package_name, entries = res
                with lock:
                    gapps_dict[package_name].extend(entries)

        return dict(gapps_dict)
