#!/usr/bin/env python
import config
from os import path
import requests
import sys
import json
import string
from time import sleep
from bs4 import BeautifulSoup
from collections import Counter
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Get access token for Genius API from 'config.py' file and add to request headers.
CLIENT_ACCESS_TOKEN = config.client_access_token
headers = {'Authorization': 'Bearer ' + CLIENT_ACCESS_TOKEN}

def get_artist_from_query(query):
	"""
	Returns the id of the artist chosen by the user. 
	"""
	raw_artist_name = query
	proceed = 'n'
	while proceed == 'n':
		
		artist_dict = {} # dictionary for names and ids of possible target artists
		possible_artists = [] # list for names of possible artists

		url = 'https://api.genius.com/search'
		data = {'q': raw_artist_name}
		response = requests.get(url, data=data, headers=headers)
		data = response.json()
		hits = data['response']['hits']

		# For every search result, add that artist's name and id to dictionary
		if len(hits) > 0:
			for hit in hits:
				this_id = hit['result']['primary_artist']['id']
				this_name = hit['result']['primary_artist']['name']
				artist_dict[this_name] = this_id
				possible_artists.append(this_name)

			most_likely_artist = Counter(possible_artists).most_common()[0][0]

			# Verify with the user that we've got the correct artist
			proceed = input('Did you mean ' + most_likely_artist + '? (y/n)\n> ')
			if proceed == 'n':
				# If not, prompt for another try.
				print('Try tweaking your spelling or adding a song title by this artist to your query.')
				raw_artist_name = input('> ')
		else:
			# If this query yields no results, prompt for another try.
			print('No artists found. You can try adding a song title by this artist to your query to get more specific results.')
			raw_artist_name = input('> ')

	# Return the id associated with the name of the most likely artist.
	return artist_dict[most_likely_artist]

def get_songs_for_artist(artist_id):
	"""
	Return a list of url paths to every song for which the target artist is listed as the primary artist 
	(i.e. not a producer, writer, etc)
	"""
	curr_page = 1
	next_page = True # will be set to false when the current page of results is the last one
	all_songs = [] # list of all desired song url paths

	while next_page:

		# Request the next 50 most popular songs by this artist
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
			if song['primary_artist']['id'] == artist_id:
				# only append to list if target artist is the primary artist
				all_songs.append(song['path'])

		next_page = data['response']['next_page']
		curr_page += 1

		print('Found ' + str(len(all_songs)) + ' songs')

	return all_songs

def get_lyrics_for_songs(song_paths):
	"""
	Return a string containing the lyrics to each song in the list of song url paths.
	"""
	all_lyrics = ''
	count = 1
	
	for path in song_paths:

		print('Getting lyrics to songs (' + str(count) + '/' + str(len(song_paths)) + ')')

		url = 'https://genius.com' + path
		response = requests.get(url)
		html = BeautifulSoup(response.text, "html.parser")

		song_lyrics = html.find('div', class_='lyrics').get_text()
		all_lyrics += song_lyrics

		count += 1

	return all_lyrics

def filter_lyrics(all_lyrics):
	"""
	Return a collection of words after filtering out insignificant/irrelevant words and stripping punctuation.
	"""
	lyrics = nltk.word_tokenize(all_lyrics)
	
	# Strip punctuation
	lyrics = ["".join(c for c in s if c not in string.punctuation) for s in lyrics]
	
	# Filter out anything to be ignored in data visualizations
	filter_words = [ "d", "ca", "t", "’", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "the", "nt", "m", "s", "ve", "gon", "ai", "re", "ll", "verse", "intro", "chorus", "i", "you", "and", "me", "a", "it", "im", "my", "to", "on", "in", "that", "wan", "na", "is", "your", "so", "of", "its", "for", "at", "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "cant", "will", "just", "don", "should", "now", "aint", "arent", "couldnt", "didnt", "doesnt", "hadnt", "hasnt", "havent", "isnt", "mightn", "shouldnt", "wasnt", "werent", "wont", "wouldnt", "like" ]
	lyrics = [x for x in lyrics if ((x.lower() not in filter_words))]
	
	# Remove empty tokens
	lyrics = [s.lower() for s in lyrics if s]

	# Return 'clean' lyrics
	return lyrics

def calculate_most_freq(lyrics):
	"""
	Return a collection of tuples each consisting of a word and how many times that
	word appears in this artist's lyrics.
	"""
	most_common_words = Counter(lyrics).most_common()
	return most_common_words

def display_freq_dist_plot(lyrics):
	"""
	Displays a frequency distribution plot for this artist's lyrics (after filtering out insignificant words).
	"""
	clean_lyrics = lyrics
	fdist = nltk.FreqDist(clean_lyrics)
	fdist.plot(30)

def display_word_cloud(lyrics):
	"""
	Displays a word cloud for this artist's lyrics (after filtering out insignificant words).
	Words are sized according to their relative frequency.
	"""
	most_freq_lyrics = lyrics
	
	# Create dictionary in which words are keys and their frequency are values.
	d = {}
	for lyric in most_freq_lyrics:
		d[lyric[0]] = lyric[1]

	# From that dictionary of frequencies, generate and display word cloud.
	wordcloud = WordCloud().generate_from_frequencies(d)
	plt.imshow(wordcloud, interpolation='bilinear')
	plt.axis("off")
	plt.show()

def calculate_lexical_diversity(all_tokens, unique_tokens):
	"""
	Calculates lexical diversity for a body of lyrics.	
	Lexical diversity = (# of unique tokens) / (total # of tokens)
	"""
	num_words = len(all_tokens.split())
	num_unique_words = len(unique_tokens)
	lexical_diversity = (float(num_unique_words) / num_words) * 100
	
	return lexical_diversity

def calculate_sentiment_intensity(lyrics):
	"""
	Calculates the compound sentiment intensity (how positive or negative) of a body of lyrics.
	Scale of -1.0 (negative sentiment) to +1.0 (positive sentinent).
	"""
	all_lyrics = lyrics
	sia = SIA()
	res = sia.polarity_scores(all_lyrics)
	return res['compound']

def main():
	"""
	Main function that calls other methods.
	"""

	# Get name of target artist from user
	raw_query = input("\nEnter an artist or band name here (or 'quit' to exit the program)\n> ")

	if raw_query == 'quit':
		print('Goodbye!')
		sys.exit(-1)

	# Find artist in Genius's data
	target_artist = get_artist_from_query(raw_query)

	# Get all songs by artist
	print('\nGetting songs... (this may take several minutes)')
	songs = get_songs_for_artist(target_artist)
	
	# Get lyrics to each song.
	print('\nGetting lyrics...')
	all_lyrics = get_lyrics_for_songs(songs)

	# Filter out insignificant lyrics and strip punctuation
	print('\nPreparing lyrics for analysis...')
	clean_lyrics = filter_lyrics(all_lyrics)

	# Count frequency of each word in filtered/cleaned lyrics
	print('Analyzing lyrics... (this too may take a few minutes)')
	most_freq_lyrics = calculate_most_freq(clean_lyrics)
	lexical_diversity = calculate_lexical_diversity(all_lyrics, most_freq_lyrics)
	# sentiment_intensity = calculate_sentiment_intensity(all_lyrics)
	print('Analysis completed!')

	# Loop until user chooses to exit the program
	done = ''
	while done != 'exit':

		# Get desired action from user.
		print('\n1 = Frequency distribution plot of most used words')
		print('2 = Word cloud of most used words')
		print('3 = Print analysis summary')
		print('4 = Choose a new artist\n')
		action = input("What would you like to do next? (1-4) or 'quit'\n> ")

		if action == '1':
			# Plot frequency distribution
			display_freq_dist_plot(clean_lyrics)

		elif action == '2':
			# Display word cloud
			display_word_cloud(most_freq_lyrics)

		elif action == '3':
			# Display analysis summary
			print('\nLexical diversity: ' + str(lexical_diversity) + ' percent')
			print('Number of songs: ' + str(len(songs)))
			# print('Sentiment intensity: ' + str(sentiment_intensity))

		elif action == '4':
			# Start the main function over with a new artist.
			main()

		# Exit gracefully.
		elif action == 'quit':
			print('Goodbye!')
			sys.exit(-1)

		else:
			print("\nPlease enter a number between 1 and 4 or 'quit'!\n")

		sleep(2)

if __name__ == "__main__":
	main()