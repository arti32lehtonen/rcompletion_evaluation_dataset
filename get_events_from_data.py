import argparse
import json
import os
import re


def extract_info_and_save(all_event_info, folder_with_raw_files, file_with_final_events):
    available_files = set(os.listdir(folder_with_raw_files))
    n_missed_events = 0

    url_to_local_filename = dict()
    for local_file_name in available_files:
        global_file_name = f'{folder_with_raw_files}/{local_file_name}'
        with open(global_file_name, 'r') as f_in:
            url = f_in.readline().strip()
            url_to_local_filename[url] = local_file_name

    with open(file_with_final_events, 'w') as f_out:
        for i, event in enumerate(all_event_info):
            if event['url'] not in url_to_local_filename:
                n_missed_events += 1
                continue

            local_file_name = url_to_local_filename[event['url']]
            with open(f"{folder_with_raw_files}/{local_file_name}") as f_in:
                content = f_in.read()

            url, _, code = content.partition('\n')
            code = re.sub('^[\n\ufeff]+', '', code)

            event_info = json.dumps({
                'url': url,
                'before_cursor': code[:event["position"]],
                'after_cursor': event['answer_end'],
                'after_cursor_token': event['answer_full'],
                'group': event['group'],
                'prefix': event['prefix']
            })
            f_out.write(event_info + '\n')

    total_extracted_events = len(all_event_info) - n_missed_events
    print(f'Total extracted events: {total_extracted_events}, {n_missed_events} is missed')


def main(indexes_filename, folder_with_raw_files, file_with_final_events):
    all_event_info = []
    with open(indexes_filename, 'r') as f:
        for line in f:
            event_info = json.loads(line)
            all_event_info.append(event_info)

    extract_info_and_save(all_event_info, folder_with_raw_files, file_with_final_events)


if __name__ == "__main__":
    description = "Extract evaluation completion events from the downloaded files."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--indexes', metavar='<file name>', type=str,
                        default='data/indexes_to_extract.json',
                        help='Name of the file with the index structure.')
    parser.add_argument('-f', '--folder', metavar='<folder name>', type=str,
                        default='data/raw_files',
                        help='Name of the folder in which downloaded files will be stored.')
    parser.add_argument('-e', '--events', metavar='<file name>', type=str,
                        default='data/extracted_events.json',
                        help='Name of the file with the final evaluation examples.')
    arguments = parser.parse_args()
    main(arguments.indexes, arguments.folder, arguments.events)
    print("Done!")
