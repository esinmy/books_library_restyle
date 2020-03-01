# Books grabber from [tululu.org](https://tululu.org/)

This app helps you to download science fiction books in bulk from [tululu.org](https://tululu.org/).

### Installation

In order to run it, you need Python 3.x and a few additional libs.  
To install these libs, simply use pip and requirements.txt:
```
pip install -r requirements.txt
```

### Arguments

User can provide category's start and end page using optional arguments `--start_page` and `--end_page` respectively.  
For example, to download all category's books from pages 10 to 20, run:
```
python parse_tululu_category.py --start_page 10 --end_page 20
```
By default, `--start_page` is equal to `1`, `--end-page` is equal to the last page number of the desired category.  

For convenience, shortcuts `-s` instead of `--start_page` and `-e` instead of `--end_page` can be used:
```
python parse_tululu_category.py -s 5 -e 15
```

### Project's goal

The code is written for educational purposes in the online course for web developers [dvmn.org](https://dvmn.org/).