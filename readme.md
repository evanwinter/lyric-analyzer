# Lyric Analyzer and Visualizer

Built on Python 3, uses BeautifulSoup, NLTK, and the Genius API.

### Usage

In your Terminal/command line, run the following commands:

`git clone https://github.com/evanwinter/lyric-analyzer`

`cd lyric-analyzer`

Then, create a new [Genius API Client](https://genius.com/api-clients/new) and find your Access Token.

Create a file in the project root called `config.py` and store your Access Token in it, like so:
```
# config.py
client_access_token = 'xxx'
```

In your Terminal/command line, install any necessary modules using `pip3 install [modulename]`.

To run the program, run the following line in your Terminal/command line:

`python3 main.py`

### Actions

1. Frequency distribution plot of most-used lyrics.

2. Word cloud of most-used lyrics.

3. Quick summary of lyric analysis in terms of lexical diversity, sentiment intensity, and more.