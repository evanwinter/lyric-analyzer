# Lyric Analyzer and Visualizer

Built on Python 3, uses BeautifulSoup, NLTK, and the Genius API.

### Usage

In your Terminal/command line, run the following commands:
`git clone https://github.com/evanwinter/lyric-analyzer`
`cd lyric-analyzer`

Then, create a [Genius API Client](https://genius.com/api-clients/new).

Create a file in the project root called `config.py` and store you new Genius API client's Access Token in it, like so:
```
# config.py
client_access_token = 'xxx'
```

In your Terminal/command line, run the following command:
`python3 main.py`