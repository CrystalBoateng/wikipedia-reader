#{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}
#{}
#{}	@@		Load dependencies and global variables
#{}
#{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}

#load NLP dependencies
import textacy #to create docs/doc metadata, and to lemmatize and tokenize unstructured text
import os #to read and write from disk
import sys #to delete and reload python files
import re #to parse html
import json #to read doc metadata
import uuid #to generate unique IDs for topics
from operator import itemgetter #to sort lists of lists

#declare global variables
absolute_filepath = os.path.dirname(__file__) #the filepath of this script.
knowledgePriorityLevel = 1




#{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}
#{}
#{}	@@		Functions
#{}
#{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}

#General utilities
def generateUuid():
	"""Generate a reasonably unique ID string based on date and time.
	----------Dependencies:
	import uuid

	----------Parameters:
	None

	----------Returns:
	a string (e.g. '2017-11-26_9-13_85894b2f')
	"""
	from datetime import datetime
	dateAndTime = datetime.now()
	randomId = str(uuid.uuid4()) #generate a UUID
	randomId = randomId[:8] #truncate it because 36 digits is too long
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

	----------Returns:
	None (content is pushed straight to the global variable topicsKnown)
	"""
	#exec 'For each line of text, concat to string.' then exec 'exec of that string'.
	exec("stringOfTopicsKnown = '' \nwith open ('topics_known.py', 'rt', encoding='utf8') as f:\n\tfor line in f:\n\t\tstringOfTopicsKnown+=line\nexec(stringOfTopicsKnown)")
def sortLists(myLists,index,order):
    """Takes a list of lists. Returns it sorted by a given index.
	----------Dependencies:
	from operator import itemgetter

	----------Parameters:
	myLists (a list of lists. one item in each of the lists should be an int.)
	index (the index to sort by)
	order Smallest-to-largest is Python's default. If that's not what you want, write 'largestToSmallest'

	----------Returns:
	the same list you passed in, but sorted.
	"""

    sortedLists = sorted(myLists, key=itemgetter(index))
    if order == "largestToSmallest":
    	sortedLists = list(reversed(sortedLists))
    return sortedLists

#Reading
def loadHtml(myURL,sourceToLoad="Unknown"):
	"""Download HTML from a webpage and push the useful parts of the text to temp_processing_text.txt.
	This function is called by read(). It should not be called directly.
	----------Dependencies:
	import os, import sys, import re, absolute_filepath

	----------Parameters:
	myURL (a string. must begin with http:// or https://)
	sourceToLoad (optional string)

	----------Returns:
	None (data is pushed directly to temp_processing_text.txt and temp_preprocessing_text.txt)
	"""
	#download webpage content and push to temp_preprocessing_text.txt
	import urllib.request
	with urllib.request.urlopen(myURL) as response:
		urlContent = response.read()
		# this can't be converted to a real string, until it's written to disk.
		with open(absolute_filepath+'/temp_preprocessing_text.txt', 'wb') as f: #wb stands for write as 'bytes'
		    f.write(urlContent)
	del urlContent #save some memory

	#Pull from temp_preprocessing_text.txt
	urlContent_raw = []
	with open ('temp_preprocessing_text.txt', 'rt', encoding="utf8") as f:
	    for line in f: #For each line of text, store in a string variable in the list urlContent_raw.
	    	urlContent_raw.append(line)
	assert len(urlContent_raw) > 0, "Hey, there is no content to pull from temp_preprocessing_text.txt"

	#Parse the HTML 
	urlContent_ready = []
	for i in range (0,len(urlContent_raw)):
		line = urlContent_raw[i]
		#remove leading indentations
		line = re.sub("\t", "", str(line))
		line = re.sub("  ", "", str(line))

		# Sort out what to keep.
		substringToKeep = None
			#keep titles
		if line[:5] == '<title>': #maybe try line.find instead, for reuters
			substringToKeep = line
			#keep headers
		elif line[:3] == '<h1' or line[:12] == '</figure><h1' or line[:3] == '<h2' or line[:12] == '</figure><h2' or line[:3] == '<h3' or line[:3] == '<h4' or line[:3] == '<h5' or line[:3] == '<h6' or line[:3] == '<h7':
			substringToKeep = line
			#keep paragraphs
		# print(line.find('<p '),line.find('<p>')) # for debugging reuters articles
		elif line[:3] == '<p>' or line[:3] == '<p ' or line[:12] == '</figure><p ': #for wikipedia articles
		# if line.find('<p ')>0 or line.find('<p>')>0: #for reuters articles
			substringToKeep = line
			# print(line)
		# #keep ul, ol, and li
		# elif line[:4] == '<ul>' or line[:4] == '<ul ' or line[:4] == '<ol>' or line[:4] == '<ol ' or line[:4] == '<li>' or line[:4] == '<li ':
		# 	substringToKeep = line
		# #keep tables, tr, td
		# elif line[:4] == '<table>' or line[:4] == '<table ' or line[:4] == '<tr>' or line[:4] == '<tr ' or line[:4] == '<td>' or line[:4] == '<td ':
		# 	substringToKeep = line
		else:
			pass #don't keep anything else.
		
		# If there's anything in substringToKeep, clean it up and append it.
		if substringToKeep != None:
			# print("I identified a line to keep.")

			#remove attributes
			substringToKeep = re.sub(' action="[^\"]*"', "", substringToKeep) #remove action attributes
			substringToKeep = re.sub(' action=\'[^\"]*\'', "", substringToKeep) #same, but with single-quotes
			substringToKeep = re.sub(' alt="[^\"]*"', "", substringToKeep) #remove alt attributes
			substringToKeep = re.sub(' alt=\'[^\"]*\'', "", substringToKeep) #same, but with single-quotes
			substringToKeep = re.sub(' class="[^\"]*"', "", substringToKeep) #remove class attributes
			substringToKeep = re.sub(' class=\'[^\"]*\'', "", substringToKeep) #same, but with single-quotes
			substringToKeep = re.sub(' href="[^\"]*"', "", substringToKeep) #remove href attributes
			substringToKeep = re.sub(' href=\'[^\"]*\'', "", substringToKeep) #same, but with single-quotes
			substringToKeep = re.sub(' id="[^\"]*"', "", substringToKeep) #remove id attributes
			substringToKeep = re.sub(' id=\'[^\"]*\'', "", substringToKeep) #same, but with single-quotes
			substringToKeep = re.sub(' lang="[^\"]*"', "", substringToKeep) #remove lang attributes
			substringToKeep = re.sub(' lang=\'[^\"]*\'', "", substringToKeep) #same, but with single-quotes
			substringToKeep = re.sub(' title="[^\"]*"', "", substringToKeep) #remove title attributes
			substringToKeep = re.sub(' title=\'[^\"]*\'', "", substringToKeep) #same, but with single-quotes
			substringToKeep = re.sub(' style="[^\"]*"', "", substringToKeep) #remove style attributes
			substringToKeep = re.sub(' style=\'[^\"]*\'', "", substringToKeep) #same, but with single-quotes
			#remove certain opening tags
			substringToKeep = re.sub('\<.\>', "", substringToKeep) #all 1-character tags, incl. <p>
			substringToKeep = re.sub('\<..\>', "", substringToKeep) #all 2-character tags, incl. <p>
			substringToKeep = re.sub('\<...\>', "", substringToKeep) #all 3-character tags, incl. <p>
			substringToKeep = re.sub('<span>', "", substringToKeep)
			substringToKeep = re.sub('<strong>', "", substringToKeep)
			#remove ALL closing tags
			substringToKeep = re.sub("<\/[^>]*>", "", substringToKeep) 

			#clean up specific websites in a specific way
			if sourceToLoad == "wikipedia": #If it's wikipedia...
				substringToKeep = re.sub('\[.\]', "", substringToKeep) #delete 1-digit footnotes
				substringToKeep = re.sub('\[..\]', "", substringToKeep) #delete 2-digit footnotes
				substringToKeep = re.sub('\[...\]', "", substringToKeep) #delete 3-digit footnotes
				substringToKeep = re.sub('\[....\]', "", substringToKeep) #delete 3-digit tags
				substringToKeep = re.sub('\[citation', "", substringToKeep) #delete [citation needed] Note: this is not currently working - try printing the line here, to fix.
				substringToKeep = re.sub('\[citation need', "", substringToKeep) #same
				substringToKeep = re.sub('\[citation needed\]', "", substringToKeep) #same
				substringToKeep = re.sub('needed\]', "", substringToKeep) #same
				#delete these suseless headings:
				if substringToKeep == "Contents\n" or substringToKeep == "External links\n" or substringToKeep == "Further reading\n" or substringToKeep == "Navigation menu\n" or substringToKeep == "References\n" or substringToKeep == "See also\n" or substringToKeep == "In other projects\n" or substringToKeep == "Interaction\n":
					substringToKeep = ""
				elif substringToKeep == "Languages\n" or substringToKeep == "More\n" or substringToKeep == "Namespaces\n" or substringToKeep == "Navigation\n" or substringToKeep == "Notes\n" or substringToKeep == "Personal tools\n" or substringToKeep == "Print/export\n" or substringToKeep == "Tools\n" or substringToKeep == "Views\n" or substringToKeep == "Works cited\n":
					substringToKeep = ""
				else:
					pass
			if sourceToLoad == "bbc" and i == 0: #If it's bbc...
				substringToKeep = "" #delete the first index bc its just a bunch of javascript

			urlContent_ready.append(substringToKeep)
	del urlContent_raw #save some memory
	# print (urlContent_ready)
	if len(urlContent_ready) == 0:
		return ("BAD REQUEST\t\tNo content matched the criteria to push to temp_processing_text.txt.")

	#Push to temp_processing_text.txt
	with open(absolute_filepath+'/temp_processing_text.txt', 'w', encoding='utf-8') as f:
	    for i in range (0,len(urlContent_ready)):
		    f.write(urlContent_ready[i])
	del urlContent_ready #save some memory
def loadText(textToLoad):
	"""Push a string to temp_processing_text.txt.
	This function is called by read(). It should not be called directly.
	----------Dependencies:
	import os, absolute_filepath

	----------Parameters:
	textToLoad

	----------Returns:
	None (data is pushed directly to temp_processing_text.txt)
	"""
	textToLoad = str(textToLoad)
	textToLoad += "\n011001010110111001100100" #to make sure there is always at least one line in the txt file, so that doc can be saved.

	#Empty temp_preprocessing_text.txt (because loadHtml does too).
	with open(absolute_filepath+'/temp_preprocessing_text.txt', 'w', encoding='utf-8') as f:
	    f.write("")

	#Push textToLoad to temp_processing_text.txt
	with open(absolute_filepath+'/temp_processing_text.txt', 'w', encoding='utf-8') as f:
	    f.write(textToLoad)
def tokenize(source,title):
	"""Pull text from temp_processing_text.txt, save its bag of terms and log having read it.
	----------Dependencies:
	temp_processing_text.txt (in this script's directory). This is the text that gets tokenized.
	my_corpus (folder in this script's directory)
	import os, absolute_filepath (global variable)
	generateUuid()
		import uuid

	----------Parameters:
	source (a string)
	title (a string)

	----------Returns:
	None
	"""
	#Pull text from temp_processing_text.txt
	textToTokenize = ""
	with open ('temp_processing_text.txt', 'r', encoding="utf8") as f:
	    for line in f: #For each line of text, store in a string variable in the list urlContent_raw.
	    	textToTokenize += line+"\n"

	#generate a unique key for this reading
	docName = generateUuid()
	#create the doc and metadata (because tokenization can't happen until the doc is created)
	metadata = {
	     'title': title,
	     'source': source,
	     'myKey' : docName} 
	doc = textacy.Doc(textToTokenize, metadata=metadata, lang="en") 

	#create a json bag of terms. convert it to a python list.
	docTermsJson = doc.to_bag_of_terms(ngrams=2, named_entities=True, normalize='lemma', as_strings=True)
	docTerms = []
	for key, value in docTermsJson.items():
		docTerms.append([key,value])
	del docTermsJson

	#sort the list
	docTerms = sortLists(docTerms,1,'largestToSmallest')

	#Place terms with above-average frequency (>1 mentions) into primaryTerms. Place all terms into secondaryTerms.
	primaryTerms = []
	secondaryTerms = []
	for i in range (0,len(docTerms)):
		if docTerms[i][1] > 1:
			primaryTerms.append(docTerms[i][0])
		secondaryTerms.append(docTerms[i][0])
	# set title = the most common term (if any terms exist)
	if len(docTerms) > 0:
		title = docTerms[0][0] 
	else:
		title = 'Untitled'
	#This is better than <h1> bc it is tokenized in the same way that the terms in other network nodes, are tokenized. But another option is to search through primaryTerms and find the first (or longest) one that matches the first line of temp_processing_text.txt, and use that term instead.
	
	#overwrite previous metadata now that there's a real title
	metadata = {
	     'title': title,
	     'source': source,
	     'myKey' : docName} 
	doc = textacy.Doc(textToTokenize, metadata=metadata, lang="en") 
	
	#save the doc
	doc.save(absolute_filepath+'/my_corpus', name=docName)

	#generate final list of all data/vectors
	newTopic = [docName,knowledgePriorityLevel,title,[source],primaryTerms,secondaryTerms,False]

	# update topics_known.py
	newTopic = str(newTopic)+","+"\n] # the last line in the file must be a ]." # add ] to newTopic
	lines = open(absolute_filepath+'/topics_known.py', encoding="utf8").readlines()
	open(absolute_filepath+'/topics_known.py', encoding="utf8").close()
	w = open(absolute_filepath+'/topics_known.py','w', encoding="utf8")
	w.writelines([item for item in lines[:-1]]) #delete the last line of the file
	w.close()
	#add newTopic as the last 2 lines of the file
	with open(absolute_filepath+'/topics_known.py', 'a', encoding="utf8") as f: #a means append
	    f.write(newTopic)
	#update the global variable 'topicsKnown'
	updateTopicsKnown()

	# #save the name of this reading (docName) in the file table_of_contents.txt
	# with open(absolute_filepath+'/my_corpus/table_of_contents.txt', 'a') as f: #a means append
	#     f.write('\n'+docName)
	print ("I've finished reading about %s." % title)
def read(readRequest):
	"""Use the format of a read request, to detrmine the reading's content and metadata. Then call a function to read it.
	----------Dependencies:
	tokenize()
		generateUuid ()

	----------Parameters:
	readRequest

	----------Returns:
	True: if it executes the whole function successfully.
	The learned data is saved directly to topics_known.txt and to /my_corpus
	"""
	sourceToRead = None
	textToRead = None
	titleToRead = None
	urlToRead = None
	requiresHtmlParse = None

	if readRequest[:9] == 'read http':
		#determine source
		wiki = None #if it's wikipedia, then it's wikipedia
		if readRequest.find("wikipedia.") > 0:
			sourceToRead = "wikipedia"
		else: #if it's not wikipedia, then the source is the domain name
			sourceToRead = readRequest[5:] #remove the word 'read '
			if sourceToRead[:4] == "http":
				startPos = 3 + re.search("://", sourceToRead).start()
			else:
				startPos = 0
			sourceToRead = sourceToRead[startPos:]
			periodPos = re.search("\.", sourceToRead).start()
			sourceToRead = sourceToRead[:periodPos]
		#determine text (the content)
		textToRead = None
		#title wont be determined until text is tokenized
		titleToRead = "Unknown"
		requiresHtmlParse = True
		#determine urlToRead
		urlToRead = readRequest[5:] #everything after 'read '
		print ("I will try to read the following:")

	elif readRequest[:15] == 'read this from ':
		#determine source
		sourceToRead = readRequest[15:]
		colonPos = re.search(":", sourceToRead).start()
		sourceToRead = sourceToRead[:10]
		#determine text (the content)
		textToRead = re.split("read this from .*:", readRequest)
		textToRead = textToRead[1]
		titleToRead = 'Unknown' #final title wont be determined until text is tokenized
		requiresHtmlParse = False
		print ("I will try to read the following:")

	else:
		sourceToRead = 'Unknown'
		#determine text (the content)
		textToRead = readRequest[5:]
		titleToRead = 'Unknown' #final title wont be determined until text is tokenized
		requiresHtmlParse = False
		print ("I will try to read the following:")



	print ("\tsourceToRead:",sourceToRead)
	print ("\ttextToRead:",textToRead)
	print ("\ttitleToRead:",titleToRead)
	print ("\turlToRead:",urlToRead)
	print ("\trequiresHtmlParse:",requiresHtmlParse)

	if requiresHtmlParse == True:
		loadHtml(urlToRead,sourceToRead) #load content into temp_processing_text.txt and save doc/metadata to my_corpus
		tokenize(sourceToRead,titleToRead) #tokenize temp_processing_text.txt
		return True
	else:
		loadText(textToRead) #load content into temp_processing_text.txt and save doc/metadata to my_corpus
		tokenize(sourceToRead,titleToRead) #tokenize temp_processing_text.txt
		return True




#{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}
#{}
#{}	@@		Main Loop
#{}
#{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}
updateTopicsKnown()

readingLoop = True
while readingLoop == True:
	inputParsed = False
	print("\n\nAVAILABLE COMMANDS: \n\t'read' (e.g. read https://en.wikipedia.org/wiki/Carpinus_betulus)\n\t'read this from source: paragraph' (e.g. read this from wikipedia: A folksinger or folk singer is a person who sings folk music.)\n\t'exit'")
	readingLoop_input = input('--> ')

	#if readingLoop_input starts with read
	if readingLoop_input[:5] == 'read ':
		readingSuccess = False
		inputParsed = True
		read(readingLoop_input)

	#exit the main loop
	if readingLoop_input == 'exit' or readingLoop_input == 'abort':
		inputParsed = True
		readingLoop = False
	
	#handle syntax errors
	if inputParsed == False:
		print ("I don't understand '%s'." % readingLoop_input)
print("===== Exiting Script =====")