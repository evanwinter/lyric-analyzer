#!/usr/bin/env python
from os import path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests
import sys
import json
import string
import config
from collections import Counter
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import RegexpTokenizer

CLIENT_ACCESS_TOKEN = config.client_access_token
headers = {'Authorization': 'Bearer ' + CLIENT_ACCESS_TOKEN}

def get_artist_from_name(name):

	raw_artist_name = name

	proceed = 'n'
	while proceed == 'n':

		url = 'https://api.genius.com/search'
		data = {'q': raw_artist_name}
		response = requests.get(url, data=data, headers=headers)
		data = response.json()
		hits = data['response']['hits']
		artist_ids = {}
		possible_artists = []

		if len(hits) > 0:
			for hit in hits:
				this_id = hit['result']['primary_artist']['id']
				this_name = hit['result']['primary_artist']['name']
				artist_ids[this_name] = this_id
				possible_artists.append(this_name)

			most_likely_artist = Counter(possible_artists).most_common()[0][0]

			# Check that it's the right artist.
			proceed = input('Did you mean ' + most_likely_artist + '? (y/n) ')
			if proceed == 'n':
				raw_artist_name = input('Enter an artist or band name here: ')
		else:
			print('No artists found. Please try again.')
			raw_artist_name = input('Enter an artist or band name here: ')

	return artist_ids[most_likely_artist]

def get_songs_for_artist(artist_id):

	curr_page = 1
	next_page = True
	all_songs = []

	while next_page:

		url = 'https://api.genius.com/artists/' + str(artist_id) + '/songs'
		params = {
			'page': curr_page,
			'sort': 'popularity',
			'per_page': 50
		}
		response = requests.get(url, headers=headers, params=params)
		data = response.json()
		songs = data['response']['songs']

		for song in songs:
			# Only use songs on which this artist is the primary artist
			if song['primary_artist']['id'] == artist_id:
				all_songs.append(song['path'])

		next_page = data['response']['next_page']
		curr_page += 1

		print('Found ' + str(len(all_songs)) + ' songs...')

	return all_songs

def get_lyrics_for_songs(song_paths):

	all_lyrics = ''
	count = 1
	
	for path in song_paths:

		print('Getting lyrics to song ' + str(count) + '/' + str(len(song_paths)))

		url = 'https://genius.com' + path
		response = requests.get(url)
		html = BeautifulSoup(response.text, "html.parser")

		song_lyrics = html.find('div', class_='lyrics').get_text()
		all_lyrics += song_lyrics

		count += 1

	return all_lyrics

def filter_lyrics(all_lyrics):
	filter_words = [ "the", "nt", "m", "s", "ai", "re", "ll", "verse", "intro", "chorus", "i", "you", "and", "me", "a", "it", "im", "my", "to", "on", "in", "that", "wan", "na", "is", "your", "so", "of", "its", "for", "at", "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "cant", "will", "just", "don", "should", "now", "aint", "arent", "couldnt", "didnt", "doesnt", "hadnt", "hasnt", "havent", "isnt", "mightn", "shouldnt", "wasnt", "werent", "wont", "wouldnt", "like" ]
	# digit_words = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
	# song_structure_words = [ "[intro", "[verse", "[chorus", "[hook", "[prechorus", "[bridge", "intro", "verse", "chorus", "hook", "prechorus" ]



	lyrics = nltk.word_tokenize(all_lyrics)

	# Strip punctuation
	lyrics = ["".join(c for c in s if c not in string.punctuation) for s in lyrics]

	# Filter out boring words
	lyrics = [x for x in lyrics if ((x.lower() not in filter_words))]

	# Remove empty tokens
	lyrics = [s.lower() for s in lyrics if s]

	return lyrics

def analyze_lyrics(lyrics):

	most_common_words = Counter(lyrics).most_common()
	# print(most_common_words)

	return most_common_words


def main():
	
	# Get the name of the artist from the user.
	raw_artist_name = input('Enter an artist or band name here: ')

	# Find the actual artist in the Genius data.
	artist = get_artist_from_name(raw_artist_name)


	# Get a list of all songs by this artist.
	print('Getting songs...')
	songs = get_songs_for_artist(artist)
	
	# Get lyrics to each song by this artist.
	print('Getting lyrics...')
	lyrics = get_lyrics_for_songs(songs)

	print('Preparing lyrics for analysis...')
	clean_lyrics = filter_lyrics(lyrics)

	print('Analyzing lyrics...')
	most_freq = analyze_lyrics(clean_lyrics)

	print('1 = Frequency distribution plot of most used lyrics')
	print('2 = Word cloud of most used lyrics')
	print('3 = Print all lyrics')

	action = input('What would you like to do next? (1-3) ')

	# Plot frequency distribution
	if action == '1':
		fdist = nltk.FreqDist(clean_lyrics)
		fdist.plot(20)
	# Display word cloud
	elif action == '2':
		d = {}
		for lyric in most_freq:
			d[lyric[0]] = lyric[1]	
		wordcloud = WordCloud().generate_from_frequencies(d)
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis("off")
		plt.show()

	# Print out all lyrics
	elif action == '3':
		print(lyrics)

	print("Done!")


if __name__ == "__main__":
	main()