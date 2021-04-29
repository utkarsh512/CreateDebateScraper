# CreateDebate Scrapper API
[CreateDebate](https://www.createdebate.com/) is an online forum that allows students and experts alike to debate a variety of topics and practice persuasive writing. It has a large corpus of data related to a vast number of topics. This API allows to scrape all the debates related to a particular topic.
## Tutorial
The URL structure of CreateDebate is pretty simple to decode. Consider the following URL
```
https://www.createdebate.com/browse/debates/all/mostheated/alltypes/alltime/Politics/0/24/open
```
![](CreateDebate.JPG)
Let's split the URL into floowing components:
* __Base URL__: `https://www.createdebate.com/browse/debates/all/`
* __Sort By__: `mostheated` (available options are `mostheated`, `mostrecent`, `mostarguments`, `mostvotes`, `newactivity` and `randomly`)
* __Type of Debate__: `alltypes` (other available options can be checked from the `Type` dropdown of the webpage)
* __Time of Debate__: `alltime` (other available options can be checked from the `Period` dropdown of the webpage)
* __Topic__: `Politics` (other available options can be checked from the webpage)
* __Offset__: Starting index of the post array (see Notes section for more detail)
* __PerPage__: Number of posts displayed on a single page (available options are 12, 24, 48 and 96; see Notes section for more detail)
* __State of Post__: `open` (other options are `closed` and `both`)

### Notes
CreateDebate displays subaaray of the main post array using `[offset : offset + perpage]`. This API uses <kbd>PerPage</kbd> of 96, and <kbd>Offset</kbd> is increased in steps of 96 to scrape entire data set with given constraints.

## Requirements
* BeautifulSoup (bs4)

## Start scrapping
To scrape all the debates under default constraints for <kbd>Topic: Politics</kbd>, run this command in the terminal
```bash
$ python scrape.py --data_dir dataset --tag Politics --page_count 104
```
Here, 104 is the total number of pages showed on the webpage when <kbd>PerPage</kbd> is set to 96. The parameters can be changed as per one's need.
