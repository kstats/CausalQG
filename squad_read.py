import json
import parser
import re
import nltk

def load():
	filepath = '/Users/tonytu/desktop/dev-v2.0.json'
	with open(filepath) as file:
		data = json.load(file)
	#print data by paragraphs
	print('succesfully loaded {} articles from squad dataset'.format(len(data['data'])))
	return data['data']

def parse(data):
	#extract all paragraphs from json 
	titles = []
	paragraphs = []
	for i in range(len(data)):
		title = data[i]['title']
		titles.append(title)
		for j in range(len(data[i]['paragraphs'])):
			paragraphs.append(data[i]['paragraphs'][j]['context'])
	return titles, paragraphs

def split(paragraphs):
	#return all the three sentence windows for all paragraphs in nested lists
	#the three sentences are contained in a list in the form of string. 
	three_sentence_window = []
	sentences = []
	for paragraph in paragraphs:
		splitted = re.split(r' *[\.\?!][\'"\)\]]* *', paragraph)[:-1]
		sentences.append(splitted)
		three_sentence_window.append([splitted[i:i+3] for i in range(0, len(splitted), 3)])
	return three_sentence_window
		
if __name__ == '__main__':
	paragraphs = load()
	# parse(paragraphs)
	# print(paragraphs[0]['paragraphs'][0]['context'])
	titles, paragraphs = parse(paragraphs)
	split(paragraphs)

