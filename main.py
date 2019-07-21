# dependencies
import textacy # to create docs/doc metadata, and to lemmatize and tokenize unstructured text
import os # to read and write from disk
import sys # to delete and reload python files
import re # to parse html
import json # to read doc metadata
import uuid # to generate unique IDs for topics
from operator import itemgetter # to sort lists of lists

# global variables
absolute_filepath = os.path.dirname(__file__) # filepath of this script
knowledgePriorityLevel = 1 # boolean used at runtime when run as an API

# general utilities
def generateUuid():
	"""Generate a reasonably unique ID string based on date and time.
	----------Dependencies:
	import uuid

	----------Parameters:
	None

	----------Return:
	a string (e.g. '2017-11-26_9-13_85894b2f')
	"""
	from datetime import datetime
	dateAndTime = datetime.now()
	# generate a random id and truncate the 36 digits to 8
	randomId = str(uuid.uuid4())[:8]
	# create a string containing metadata and the random id
	myUuid = "%s-%s-%s_%s-%s_%s" % (
		str(dateAndTime.year),
		str(dateAndTime.month),
		str(dateAndTime.day),
		str(dateAndTime.hour),
		str(dateAndTime.minute),
		randomId
		)
	print("Generated UUID: ",myUuid)
	return myUuid
def updateTopicsKnown():
	"""Update the global variable topicsKnown, from the file topics_known.py.
	----------Dependencies:
	import os, import sys
	topics_known.py (in this script's directory)

	----------Parameters:
	None

	----------Return:
	None (content is pushed straight to the global variable topicsKnown)
	"""
	# execute 'For each line of text, concatenate to string'.
	# then execute 'exection of that string'.
	exec("stringOfTopicsKnown = '' \nwith open('topics_known.py', 'rt', encoding='utf8') as f:\n\tfor line in f:\n\t\tstringOfTopicsKnown+=line\nexec(stringOfTopicsKnown)")
def sortLists(myLists,index,order):
    """Take a list of lists. Return it sorted by a given index.
	----------Dependencies:
	from operator import itemgetter

	----------Parameters:
	myLists (a list of lists. one item in each of the lists should be an int.)
	index (the index to sort by)
	order Smallest-to-largest is Python's default. If that's not what you want, write 'largestToSmallest'

	----------Return:
	the same list that was passed in, but sorted.
	"""
    sortedLists = sorted(myLists, key=itemgetter(index))
    if order == "largestToSmallest":
    	sortedLists = list(reversed(sortedLists))
    return sortedLists

# reading
def parseHtml(input_array, source):
	"""Parse a list of HTML strings and return the list with less markup.
	This function is called only by loadHtml(). It should not be called directly.
	----------Dependencies:
	none

	----------Parameters:
	input_array (a list of strings. each string contains HTML.)

	----------Return:
	a list of strings containing few or no html tags
	"""
	output_array = []
	for i in range(len(input_array)):
		line = input_array[i]
		# remove leading indentations.
		line = re.sub("\t", "", str(line))
		line = re.sub("  ", "", str(line))
		# retain only content in titles, headers, and paragraph tags.
		substringToKeep = None
		if (line.startswith('<title>') or
			line.startswith('<h1') or 
			line.startswith( '</figure><h1') or 
			line.startswith('<h2') or 
			line.startswith( '</figure><h2') or 
			line.startswith('<h3') or 
			line.startswith('<h4') or 
			line.startswith('<h5') or 
			line.startswith('<h6') or 
			line.startswith('<h7') or
			line.startswith('<p>') or 
			line.startswith('<p ') or 
			line.startswith('</figure><p ')
			):
			substringToKeep = line
		# if there's anything in substringToKeep, clean it up and append it.
		if substringToKeep:
			# remove attributes.
			substringToKeep = re.sub(' action="[^\"]*"', "", substringToKeep) # remove action attributes
			substringToKeep = re.sub(' action=\'[^\"]*\'', "", substringToKeep) # same, but with single-quotes
			substringToKeep = re.sub(' alt="[^\"]*"', "", substringToKeep) # remove alt attributes
			substringToKeep = re.sub(' alt=\'[^\"]*\'', "", substringToKeep) # same, but with single-quotes
			substringToKeep = re.sub(' class="[^\"]*"', "", substringToKeep) # remove class attributes
			substringToKeep = re.sub(' class=\'[^\"]*\'', "", substringToKeep) # same, but with single-quotes
			substringToKeep = re.sub(' href="[^\"]*"', "", substringToKeep) # remove href attributes
			substringToKeep = re.sub(' href=\'[^\"]*\'', "", substringToKeep) # same, but with single-quotes
			substringToKeep = re.sub(' id="[^\"]*"', "", substringToKeep) # remove id attributes
			substringToKeep = re.sub(' id=\'[^\"]*\'', "", substringToKeep) # same, but with single-quotes
			substringToKeep = re.sub(' lang="[^\"]*"', "", substringToKeep) # remove lang attributes
			substringToKeep = re.sub(' lang=\'[^\"]*\'', "", substringToKeep) # same, but with single-quotes
			substringToKeep = re.sub(' title="[^\"]*"', "", substringToKeep) # remove title attributes
			substringToKeep = re.sub(' title=\'[^\"]*\'', "", substringToKeep) # same, but with single-quotes
			substringToKeep = re.sub(' style="[^\"]*"', "", substringToKeep) # remove style attributes
			substringToKeep = re.sub(' style=\'[^\"]*\'', "", substringToKeep) # same, but with single-quotes
			# remove certain opening tags.
			substringToKeep = re.sub('\<.\>', "", substringToKeep) # all 1-character tags, incl. <p>
			substringToKeep = re.sub('\<..\>', "", substringToKeep) # all 2-character tags, incl. <p>
			substringToKeep = re.sub('\<...\>', "", substringToKeep) # all 3-character tags, incl. <p>
			substringToKeep = re.sub('<span>', "", substringToKeep)
			substringToKeep = re.sub('<strong>', "", substringToKeep)
			# remove all closing tags.
			substringToKeep = re.sub("<\/[^>]*>", "", substringToKeep) 
			# clean up wikipedia pages in a specific way.
			if source == "wikipedia":
				substringToKeep = re.sub('\[.\]', "", substringToKeep) # delete 1-digit footnotes
				substringToKeep = re.sub('\[..\]', "", substringToKeep) # delete 2-digit footnotes
				substringToKeep = re.sub('\[...\]', "", substringToKeep) # delete 3-digit footnotes
				substringToKeep = re.sub('\[....\]', "", substringToKeep) # delete 3-digit tags
				substringToKeep = re.sub('\[citation', "", substringToKeep) # delete '[citation needed]'
				substringToKeep = re.sub('\[citation need', "", substringToKeep) # delete '[citation needed]'
				substringToKeep = re.sub('\[citation needed\]', "", substringToKeep) # delete '[citation needed]'
				substringToKeep = re.sub('needed\]', "", substringToKeep) # delete '[citation needed]'
				# delete useless headings.
				if substringToKeep == (
					"Contents\n" or 
					"External links\n" or 
					"Further reading\n" or 
					"Navigation menu\n" or 
					"References\n" or 
					"See also\n" or 
					"In other projects\n" or 
					"Interaction\n" or
					"Languages\n" or 
					"More\n" or 
					"Namespaces\n" or 
					"Navigation\n" or 
					"Notes\n" or 
					"Personal tools\n" or 
					"Print/export\n" or 
					"Tools\n" or 
					"Views\n" or 
					"Works cited\n"
				):
					substringToKeep = ""
			output_array.append(substringToKeep)
	if output_array:
		return output_array
	else:
		return ("BAD REQUEST\t\tNo content matched the criteria to push to temp_processing_text.txt.")
def loadHtml(myURL,sourceToLoad="Unknown"):
	"""Download and parse HTML from a webpage. Push to temp_processing_text.txt.
	This function is only called by read(). It should not be called directly.
	----------Dependencies:
	import os, import sys, import re, absolute_filepath

	----------Parameters:
	myURL (a string. must begin with http:// or https://)
	sourceToLoad (optional string)

	----------Return:
	None (data is pushed directly to temp_processing_text.txt and 
	temp_preprocessing_text.txt)
	"""
	# download webpage content and push to temp_preprocessing_text.txt.
	import urllib.request
	with urllib.request.urlopen(myURL) as response:
		urlContent = response.read()
		# write content to disk so that it can be converted to a real string.
		with open(absolute_filepath+'/temp_preprocessing_text.txt', 'wb') as f:
		    f.write(urlContent)
	# pull the content from temp_preprocessing_text.txt
	urlContent_raw = []
	with open('temp_preprocessing_text.txt', 'rt', encoding="utf8") as f:
	    for line in f:
	    	urlContent_raw.append(line)
	if not urlContent_raw:
		print("Warning: no content downloaded to temp_preprocessing_text.txt.")
	urlContent_ready = parseHtml(urlContent_raw, sourceToLoad)
	# push content to temp_processing_text.txt
	with open(absolute_filepath+'/temp_processing_text.txt', 'w', encoding='utf-8') as f:
	    for i in range(len(urlContent_ready)):
		    f.write(urlContent_ready[i])
def loadText(textToLoad): 
	"""Push a string to temp_processing_text.txt.
	This function is called by read(). It should not be called directly.
	----------Dependencies:
	import os, absolute_filepath

	----------Parameters:
	textToLoad (a string)

	----------Return:
	None (data is pushed directly to temp_processing_text.txt)
	"""
	textToLoad = str(textToLoad)
	# add at least one line, to ensure that the doc can be saved
	textToLoad += "\n011001010110111001100100"
	# empty temp_preprocessing_text.txt (because loadHtml does too).
	with open(absolute_filepath+'/temp_preprocessing_text.txt', 'w', encoding='utf-8') as f:
	    f.write("")
	# write textToLoad to temp_processing_text.txt
	with open(absolute_filepath+'/temp_processing_text.txt', 'w', encoding='utf-8') as f:
	    f.write(textToLoad)
def tokenize(source,title):
	"""Pull text from temp_processing_text.txt and save its bag of terms to the list urlContent_raw.
	----------Dependencies:
	temp_processing_text.txt (in this script's directory). This is the 
		text that gets tokenized.
	my_corpus (folder in this script's directory)
	import os, absolute_filepath (global variable)
	generateUuid()
		import uuid

	----------Parameters:
	source (a string)
	title (a string)

	----------Return:
	None
	"""
	# pull text from temp_processing_text.txt
	textToTokenize = ""
	with open('temp_processing_text.txt', 'r', encoding="utf8") as f:
	    for line in f:
	    	textToTokenize += line+"\n"
	# generate a unique key for this reading
	docName = generateUuid()
	# create a doc and metadata so that tokenization can occur.
	metadata = {
	     'title': title,
	     'source': source,
	     'myKey' : docName}
	doc = textacy.Doc(textToTokenize, metadata=metadata, lang="en") 
	#create a json bag of terms. convert it to a python list.
	docTermsJson = doc.to_bag_of_terms(
		ngrams=2, 
		named_entities=True, 
		normalize='lemma', 
		as_strings=True
		)
	docTerms = []
	for key, value in docTermsJson.items():
		docTerms.append([key,value])
	# sort the list
	docTerms = sortLists(docTerms,1,'largestToSmallest')
	# place all terms into secondaryTerms.
	# place terms with above-average frequency (>1 mentions) into primaryTerms.
	primaryTerms = []
	secondaryTerms = []
	for i in range(len(docTerms)):
		if docTerms[i][1] > 1:
			primaryTerms.append(docTerms[i][0])
		secondaryTerms.append(docTerms[i][0])
	# set title to the most common term (if any terms exist)
	title = docTerms[0][0] if docTerms else 'Untitled'
	# overwrite the previous metadata now that a better title exists
	metadata = {
	     'title': title,
	     'source': source,
	     'myKey' : docName} 
	doc = textacy.Doc(textToTokenize, metadata=metadata, lang="en") 
	# save the doc
	doc.save(absolute_filepath+'/my_corpus', name=docName)
	# generate final list of all data/vectors
	newTopic = [
		docName,
		knowledgePriorityLevel,
		title,
		[source],
		primaryTerms,
		secondaryTerms,
		False
	]
	# update topics_known.py with latest topic read
	newTopic = str(newTopic)+","+"\n]"
	lines = open(absolute_filepath+'/topics_known.py', encoding="utf8").readlines()
	open(absolute_filepath+'/topics_known.py', encoding="utf8").close()
	w = open(absolute_filepath+'/topics_known.py','w', encoding="utf8")
	# delete the last line of the file
	w.writelines([item for item in lines[:-1]])
	w.close()
	# add newTopic as the last 2 lines of the file
	with open(absolute_filepath+'/topics_known.py', 'a', encoding="utf8") as f:
	    f.write(newTopic)
	# update the global variable 'topicsKnown'
	updateTopicsKnown()
	print("Finished reading about %s." % title)
def read(readRequest):
	"""Determine a reading's content and metadata. Call a function to read it.
	----------Dependencies:
	tokenize()
		generateUuid ()

	----------Parameters:
	readRequest

	----------Return:
	True.
	The learned data is saved directly to topics_known.txt and to /my_corpus
	"""
	sourceToRead = None
	textToRead = None
	titleToRead = None
	urlToRead = None
	requiresHtmlParse = None
	if readRequest[:9] == 'read http':
		# determine the source of a reading
		if readRequest.find("wikipedia.") > 0:
			sourceToRead = "wikipedia"
		else: 
			# set the domain name as the source
			sourceToRead = readRequest[5:] # remove the word 'read '
			if sourceToRead[:4] == "http":
				startPos = 3 + re.search("://", sourceToRead).start()
			else:
				startPos = 0
			sourceToRead = sourceToRead[startPos:]
			periodPos = re.search("\.", sourceToRead).start()
			sourceToRead = sourceToRead[:periodPos]
		# set temporary doc metadata values since tokenization hasn't yet occured.
		textToRead = None
		titleToRead = "Unknown"
		requiresHtmlParse = True
		# keep everything after 'read '
		urlToRead = readRequest[5:] 
		print("I will try to read the following:")

	elif readRequest[:15] == 'read this from ':
		sourceToRead = readRequest[15:]
		colonPos = re.search(":", sourceToRead).start()
		sourceToRead = sourceToRead[:10]
		textToRead = re.split("read this from .*:", readRequest)[1]
		titleToRead = 'Unknown'
		requiresHtmlParse = False
		print("Trying to read the following:")

	else:
		sourceToRead = 'Unknown'
		textToRead = readRequest[5:]
		titleToRead = 'Unknown'
		requiresHtmlParse = False
		print("Trying to read the following:")

	print("\tsourceToRead:",sourceToRead)
	print("\ttextToRead:",textToRead)
	print("\ttitleToRead:",titleToRead)
	print("\turlToRead:",urlToRead)
	print("\trequiresHtmlParse:",requiresHtmlParse)

	# load content into temp_processing_text.txt and 
	# save doc/metadata to my_corpus
	if requiresHtmlParse:
		loadHtml(urlToRead,sourceToRead) 
	else:
		loadText(textToRead) 
	tokenize(sourceToRead,titleToRead)
	return True

# main loop
updateTopicsKnown()
readingLoop = True
while readingLoop == True:
	inputParsed = False
	print("\n\nAVAILABLE COMMANDS: \n\t'read' (e.g. read https://en.wikipedia.org/wiki/Carpinus_betulus)\n\t'read this from source: paragraph' (e.g. read this from wikipedia: A folksinger or folk singer is a person who sings folk music.)\n\t'exit'")
	readingLoop_input = input('--> ')
	# if readingLoop_input starts with read
	if readingLoop_input[:5] == 'read ':
		readingSuccess = False
		inputParsed = True
		read(readingLoop_input)
	# exit the main loop
	if readingLoop_input == 'exit' or readingLoop_input == 'abort':
		inputParsed = True
		# clear the contents of the two temporary .txt files
		with open(absolute_filepath + \
			'/temp_preprocessing_text.txt', 'w', encoding='utf-8') as f:
		    f.write("")
		with open(absolute_filepath + \
			'/temp_processing_text.txt', 'w', encoding='utf-8') as f:
			f.write("")
		readingLoop = False
	# handle syntax errors
	if inputParsed == False:
		print("I don't understand '%s'." % readingLoop_input)
print("===== Exiting Script =====")
