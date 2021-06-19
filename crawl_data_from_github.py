import argparse
import base64
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
import os
import random
import requests
import time
from tqdm import tqdm


OAUTH_TOKEN = "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"
USERNAME = "arti32lehtonen"
MAX_THREADS = 5

QUERY_TIME = time.time()
DELAY_BETWEEN_QUERIES = 0.5


def pretty_time(seconds):
    if seconds > 3600:
        return f"{seconds // 3600} hours {seconds % 3600 // 60} minutes {seconds % 60} seconds"
    elif seconds > 60:
        return f"{seconds // 60} minutes {seconds % 60} seconds"
    return f"{seconds} seconds"


def get_response(url):
    global QUERY_TIME
    auth = (USERNAME, OAUTH_TOKEN)
    p_marker = url.rfind("?")
    params = {
        'ref': url[p_marker + 5:]
    }
    url = url[:p_marker]

    current_time = time.time()
    if current_time < QUERY_TIME:
        sleep_time = QUERY_TIME - current_time
        print(f"Request limit reached. Sleeping for {pretty_time(sleep_time)}")
        time.sleep(sleep_time + DELAY_BETWEEN_QUERIES)
    return requests.get(url, auth=auth, params=params)


def get_json_by_url(url):
    global QUERY_TIME
    response = get_response(url)
    while response.status_code != requests.codes.ok:
        print(url)
        print(f"Response code: {response.status_code} Message: {response.json()['message']}")
        print(f"Headers: {response.headers}")
        if response.status_code == requests.codes.NOT_FOUND:
            return {'type': 'error'}
        elif response.status_code == requests.codes.FORBIDDEN:
            headers = response.headers
            if headers['X-RateLimit-Remaining'] == '0':
                current_time = time.time()
                end_time = int(headers['X-RateLimit-Reset'])
                wait_time = end_time - current_time
                print(f"No more requests waiting for {pretty_time(wait_time)}")
                time.sleep(wait_time)
            elif response.json()['message'].contains('The requested blob is too large'):
                return {'type': 'error'}
        response = get_response(url)
        if response.headers['X-RateLimit-Remaining'] == '0':
            QUERY_TIME = int(response.headers['X-RateLimit-Reset'])

    if response.headers['X-RateLimit-Remaining'] == '0':
        QUERY_TIME = int(response.headers['X-RateLimit-Reset'])

    rem_time = int(response.headers['X-RateLimit-Reset']) - time.time()
    rem_req = int(response.headers['X-RateLimit-Remaining'])
    if rem_req > 0:
        print(f"Remaining requests: {rem_req} Time: {rem_time} Time/request: {rem_time / rem_req}")
    return response.json()


def get_github_file_by_url(url):
    response = get_json_by_url(url)
    if not isinstance(response, dict):
        return b''
    if response['type'] != 'file':
        return b''
    return base64.b64decode(response['content'])


def download_file(url, file_destination):
    if os.path.isfile(file_destination):
        return
    file_content = get_github_file_by_url(url)
    with open(file_destination, 'wb') as f:
        f.write(str.encode(url + '\n'))
        f.write(file_content)


def delete_wrong_urls(urls):
    new_urls = []
    for url in urls:
        q_mark = url.rfind('?')
        url_no_param = url[:q_mark].lower()
        if url_no_param.endswith('.R') or url_no_param.endswith('.r'):
            new_urls.append(url)
    return new_urls


def download_all_files(filename, folder):
    with open(filename) as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]
    urls = delete_wrong_urls(urls)

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        threads = []

        num_urls = list(enumerate(urls))
        random.shuffle(num_urls)

        for i, url in tqdm(num_urls):
            file = f"{i}.R"
            file = os.path.join(folder, file)
            while len(threads) >= 2 * MAX_THREADS:
                for future in as_completed(threads):
                    break
                threads.remove(future)
            threads.append(executor.submit(download_file, url, file))

        for future in as_completed(threads):
            pass


def main(filename, folder):
    os.makedirs(folder, exist_ok=True)
    download_all_files(filename, folder)


if __name__ == "__main__":
    description = (
        "Crawl files from GitHub. "
        "Don't forget to set OAUTH_TOKEN and TOKEN_USERNAME!"
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-u', '--urls', metavar='<file name>', type=str,
                        help='Name of the file with the urls which data will be crawled.')
    parser.add_argument('-f', '--folder', metavar='<folder name>', type=str,
                        default='data/raw_files',
                        help='Name of the folder in which downloaded files will be stored.')
    arguments = parser.parse_args()
    main(arguments.urls, arguments.folder)
    print("Done!")
