# RCompletion Evaluation Dataset (RCED)

Evaluation dataset for the R programming language completion task from the
*Time-Efficient Code Completion Model for the R Programming Language* paper.

Dataset was collected from the GitHub open-source projects.
You can use the link (link here) to download it or collect it manually using the GitHub API. 

# Dataset structure
Dataset consists of the synthetic completion events for the R programming language.

All events are divided into following groups:
* 6 dataset groups correspond to the completion events following the operators
$, %>%, ->, :: <-, = 
* 4 dataset groups cover autocompletion events during the positional or keyword
arguments completion in vectors or functions
* 1 group contains packages import usage contexts
* 2 groups correspond to the completion of a variable or a function name at the start of a
new line

Also, we divide the dataset into prefix and non-prefix (`full`) groups.
The last program token is always incomplete in the prefix group.

Each group volume is reported in the following table.

|                       | with prefix | w/o prefix | total |
|-----------------------|:-----------:|:----------:|-------|
| after operator $      | 964         | 1194       | 2158  |
| after operator %>%    | 667         | 826        | 1493  |
| after operator ->     | 19          | 24         | 43    |
| after operator ::     | 457         | 567        | 1024  |
| after operator <-     | 1675        | 2073       | 3748  |
| after operator =      | 2005        | 2483       | 4488  |
| c key argument        | 267         | 331        | 598   |
| c positional argument | 793         | 983        | 1776  |
| f key argument        | 3986        | 4934       | 8920  |
| f positional argument | 3007        | 3723       | 6730  |
| library               | 341         | 407        | 748   |
| new line variable     | 792         | 982        | 1774  |
| new line function     | 497         | 616        | 1113  |


# How to use the dataset?

You can load the dataset as lists of dicts using the following code:
```python
import json
evaluation_data = []
with open('<PATH_TO_EVENTS_FILE>', 'r', encoding='utf8') as f:
    for line in f:
        evaluation_data.append(json.loads(line))
```

Each element of the `evaluation_data` is a `dict` with the following fields:
* `url` - link from which the file was downloaded.
* `before_cursor` - context of the completion event.
* `after_cursor` - answer for the completion event.
* `after_cursor_token` - full-answer for the completion event. If `prefix` == `'full'` then
  it is equal to the `after_cursor`. If `prefix` == `'prefix'` then it is equal to the desired 
  programming token.
* `group` - group of the completion event.
* `prefix` - If `prefix` == `'prefix'` then the last programming token of the context is unfinished 
  and should be continued. If `prefix` == `'prefix'` then answer corresponds to the new unseen token.


# How to collect the dataset from the GitHub?

1. Get Personal access token on https://github.com/settings/tokens.
   
2. Change OAUTH_TOKEN variable to your token and
   USERNAME variable to your GitHub login
   in the `crawl_data_from_github.py` script.
   
3. Run `crawl_data_from_github.py`. It is important to note that github has rate limit of 5,000 requests per hour.
You can wait for an hour or run download script again after an hour after your limit is expired:
   ```
   python crawl_data_from_github.py --urls=data/urls_to_download.txt --folder=<FOLDER_WITH_RAW_FILES>
   ```

4. Run `get_events_from_data.py`:
   ```
   python get_events_from_data.py --indexes=data/indexes_to_extract.json --folder=<FOLDER_WITH_RAW_FILES> --events=data/extracted_events.json
   ```
