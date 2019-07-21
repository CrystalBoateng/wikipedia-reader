# dependencies
from operator import itemgetter # to sort lists of lists.
import json # to read doc metadata.
import os # to read and write from disk.
import re # to parse html.
import sys # to delete and reload python files.
import uuid # to generate unique IDs for topics.
import textacy # to create docs/metadata; to lemmatize and tokenize text.

# global variables
absolute_filepath = os.path.dirname(__file__) # filepath of this script
knowledge_priority_level = 1 # boolean used at runtime when run as an API

# general utilities
def generate_uuid():
    """Generate a reasonably unique ID string based on date and time.
    ----------Dependencies:
    import uuid

    ----------Parameters:
    None

    ----------Return:
    a string (e.g. '2017-11-26_9-13_85894b2f')
    """
    from datetime import datetime
    date_and_time = datetime.now()
    # generate a random id and truncate the 36 digits to 8
    random_id = str(uuid.uuid4())[:8]
    # create a string containing metadata and the random id
    myUuid = "%s-%s-%s_%s-%s_%s" % (
        str(date_and_time.year),
        str(date_and_time.month),
        str(date_and_time.day),
        str(date_and_time.hour),
        str(date_and_time.minute),
        random_id
        )
    print("Generated UUID: ",myUuid)
    return myUuid
def update_topics_known():
    """Update the global variable topics_known, from the file topics_known.py.
    ----------Dependencies:
    import os, import sys
    topics_known.py (in this script's directory)

    ----------Parameters:
    None

    ----------Return:
    None (content is pushed straight to the global variable topics_known)
    """
    # execute 'for each line of text, concatenate to string'.
    # then execute 'the exection of that string'.
    exec("string_of_topics_known = '' \nwith open('topics_known.py', 'rt', encoding='utf8') as f:\n\tfor line in f:\n\t\tstring_of_topics_known+=line\nexec(string_of_topics_known)")
def sort_lists(my_lists,index,order):
    """Take a list of lists. Return it sorted by a given index.
    ----------Dependencies:
    from operator import itemgetter

    ----------Parameters:
    my_lists (a list of lists. one item in each list should be an integer.)
    index (the index to sort by)
    order Smallest-to-largest is Python's default. If that's not what you want, write 'largest_to_smallest'.

    ----------Return:
    the same list that was passed in, but sorted.
    """
    sortedLists = sorted(my_lists, key=itemgetter(index))
    if order == "largest_to_smallest":
        sortedLists = list(reversed(sortedLists))
    return sortedLists

# reading
def parse_html(input_array, source):
    """Parse a list of HTML strings and return the list with less markup.
    This function is called only by load_html(). It should not be called directly.
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
        substring_to_keep = None
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
            substring_to_keep = line
        # if there's anything in substring_to_keep, clean it up and append it.
        if substring_to_keep:
            # remove attributes.
            substring_to_keep = re.sub(' action="[^\"]*"', "", substring_to_keep) # remove action attributes
            substring_to_keep = re.sub(' action=\'[^\"]*\'', "", substring_to_keep) # same, but with single-quotes
            substring_to_keep = re.sub(' alt="[^\"]*"', "", substring_to_keep) # remove alt attributes
            substring_to_keep = re.sub(' alt=\'[^\"]*\'', "", substring_to_keep) # same, but with single-quotes
            substring_to_keep = re.sub(' class="[^\"]*"', "", substring_to_keep) # remove class attributes
            substring_to_keep = re.sub(' class=\'[^\"]*\'', "", substring_to_keep) # same, but with single-quotes
            substring_to_keep = re.sub(' href="[^\"]*"', "", substring_to_keep) # remove href attributes
            substring_to_keep = re.sub(' href=\'[^\"]*\'', "", substring_to_keep) # same, but with single-quotes
            substring_to_keep = re.sub(' id="[^\"]*"', "", substring_to_keep) # remove id attributes
            substring_to_keep = re.sub(' id=\'[^\"]*\'', "", substring_to_keep) # same, but with single-quotes
            substring_to_keep = re.sub(' lang="[^\"]*"', "", substring_to_keep) # remove lang attributes
            substring_to_keep = re.sub(' lang=\'[^\"]*\'', "", substring_to_keep) # same, but with single-quotes
            substring_to_keep = re.sub(' title="[^\"]*"', "", substring_to_keep) # remove title attributes
            substring_to_keep = re.sub(' title=\'[^\"]*\'', "", substring_to_keep) # same, but with single-quotes
            substring_to_keep = re.sub(' style="[^\"]*"', "", substring_to_keep) # remove style attributes
            substring_to_keep = re.sub(' style=\'[^\"]*\'', "", substring_to_keep) # same, but with single-quotes
            # remove certain opening tags.
            substring_to_keep = re.sub('\<.\>', "", substring_to_keep) # all 1-character tags, incl. <p>
            substring_to_keep = re.sub('\<..\>', "", substring_to_keep) # all 2-character tags, incl. <p>
            substring_to_keep = re.sub('\<...\>', "", substring_to_keep) # all 3-character tags, incl. <p>
            substring_to_keep = re.sub('<span>', "", substring_to_keep)
            substring_to_keep = re.sub('<strong>', "", substring_to_keep)
            # remove all closing tags.
            substring_to_keep = re.sub("<\/[^>]*>", "", substring_to_keep) 
            # clean up wikipedia pages in a specific way.
            if source == "wikipedia":
                substring_to_keep = re.sub('\[.\]', "", substring_to_keep) # delete 1-digit footnotes
                substring_to_keep = re.sub('\[..\]', "", substring_to_keep) # delete 2-digit footnotes
                substring_to_keep = re.sub('\[...\]', "", substring_to_keep) # delete 3-digit footnotes
                substring_to_keep = re.sub('\[....\]', "", substring_to_keep) # delete 3-digit tags
                substring_to_keep = re.sub('\[citation', "", substring_to_keep) # delete '[citation needed]'
                substring_to_keep = re.sub('\[citation need', "", substring_to_keep) # delete '[citation needed]'
                substring_to_keep = re.sub('\[citation needed\]', "", substring_to_keep) # delete '[citation needed]'
                substring_to_keep = re.sub('needed\]', "", substring_to_keep) # delete '[citation needed]'
                # delete useless headings.
                if substring_to_keep == (
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
                    substring_to_keep = ""
            output_array.append(substring_to_keep)
    if output_array:
        return output_array
    else:
        return ("BAD REQUEST\t\tNo content matched the criteria to push to \
         temp_processing_text.txt.")
def load_html(my_url,source_to_load="Unknown"):
    """Download and parse HTML from a webpage. Push to temp_processing_text.txt.
    This function is only called by read(). It should not be called directly.
    ----------Dependencies:
    import os, import sys, import re, absolute_filepath

    ----------Parameters:
    my_url (a string. must begin with http:// or https://)
    source_to_load (optional string)

    ----------Return:
    None (data is pushed directly to temp_processing_text.txt and 
    temp_preprocessing_text.txt)
    """
    # download webpage content and push to temp_preprocessing_text.txt.
    import urllib.request
    with urllib.request.urlopen(my_url) as response:
        urlContent = response.read()
        # write content to disk so that it can be converted to a real string.
        with open(absolute_filepath+'/temp_preprocessing_text.txt', \
            'wb') as f:
            f.write(urlContent)
    # pull the content from temp_preprocessing_text.txt
    urlContent_raw = []
    with open('temp_preprocessing_text.txt', 'rt', encoding="utf8") as f:
        for line in f:
            urlContent_raw.append(line)
    if not urlContent_raw:
        print("Warning: no content downloaded to temp_preprocessing_text.txt.")
    urlContent_ready = parse_html(urlContent_raw, source_to_load)
    # push content to temp_processing_text.txt
    with open(absolute_filepath+'/temp_processing_text.txt', \
        'w', encoding='utf-8') as f:
        for i in range(len(urlContent_ready)):
            f.write(urlContent_ready[i])
def load_text(text_to_load): 
    """Push a string to temp_processing_text.txt.
    This function is called only by read(). It should not be called directly.
    ----------Dependencies:
    import os, absolute_filepath

    ----------Parameters:
    text_to_load (a string)

    ----------Return:
    None (data is pushed directly to temp_processing_text.txt)
    """
    text_to_load = str(text_to_load)
    # add at least one line, to ensure that the doc can be saved
    text_to_load += "\n011001010110111001100100"
    # empty temp_preprocessing_text.txt (because load_html does too).
    with open(absolute_filepath+'/temp_preprocessing_text.txt', 'w', encoding='utf-8') as f:
        f.write("")
    # write text_to_load to temp_processing_text.txt
    with open(absolute_filepath+'/temp_processing_text.txt', 'w', encoding='utf-8') as f:
        f.write(text_to_load)
def tokenize(source,title):
    """Pull text from temp_processing_text.txt and save its bag of terms to
        the list urlContent_raw.
    ----------Dependencies:
    temp_processing_text.txt (in this script's directory). This is the 
        text that gets tokenized.
    my_corpus (folder in this script's directory)
    import os, absolute_filepath (global variable)
    generate_uuid()
        import uuid

    ----------Parameters:
    source (a string)
    title (a string)

    ----------Return:
    None
    """
    # pull text from temp_processing_text.txt
    text_to_tokenize = ""
    with open('temp_processing_text.txt', 'r', encoding="utf8") as f:
        for line in f:
            text_to_tokenize += line+"\n"
    # generate a unique key for this reading
    doc_name = generate_uuid()
    # create a doc and metadata so that tokenization can occur.
    metadata = {
         'title': title,
         'source': source,
         'myKey' : doc_name}
    doc = textacy.Doc(text_to_tokenize, metadata=metadata, lang="en") 
    #create a json bag of terms. convert it to a python list.
    doc_terms_json = doc.to_bag_of_terms(
        ngrams=2, 
        named_entities=True, 
        normalize='lemma', 
        as_strings=True
        )
    doc_terms = []
    for key, value in doc_terms_json.items():
        doc_terms.append([key,value])
    # sort the list
    doc_terms = sort_lists(doc_terms,1,'largest_to_smallest')
    # place terms with above-average frequency (>1 mentions) into... 
    # ...primary_terms. place all terms into secondary_terms.
    primary_terms = []
    secondary_terms = []
    for i in range(len(doc_terms)):
        if doc_terms[i][1] > 1:
            primary_terms.append(doc_terms[i][0])
        secondary_terms.append(doc_terms[i][0])
    # set title to the most common term (if any terms exist)
    title = doc_terms[0][0] if doc_terms else 'Untitled'
    # overwrite the previous metadata now that a better title exists
    metadata = {
         'title': title,
         'source': source,
         'myKey' : doc_name} 
    doc = textacy.Doc(text_to_tokenize, metadata=metadata, lang="en") 
    # save the doc
    doc.save(absolute_filepath+'/my_corpus', name=doc_name)
    # generate final list of all data/vectors
    new_topic = [
        doc_name,
        knowledge_priority_level,
        title,
        [source],
        primary_terms,
        secondary_terms,
        False
    ]
    # update topics_known.py with latest topic read
    new_topic = str(new_topic)+","+"\n]"
    lines = open(absolute_filepath+'/topics_known.py', \
        encoding="utf8").readlines()
    open(absolute_filepath+'/topics_known.py', encoding="utf8").close()
    w = open(absolute_filepath+'/topics_known.py','w', encoding="utf8")
    # delete the last line of the file
    w.writelines([item for item in lines[:-1]])
    w.close()
    # add new_topic as the last 2 lines of the file
    with open(absolute_filepath+'/topics_known.py', \
        'a', encoding="utf8") as f:
        f.write(new_topic)
    # update the global variable 'topics_known'
    update_topics_known()
    print("Finished reading about %s." % title)
def read(read_request):
    """Determine a reading's content and metadata. Call a function to read it.
    ----------Dependencies:
    tokenize()
        generate_uuid ()

    ----------Parameters:
    read_request

    ----------Return:
    True.
    The learned data is saved directly to topics_known.txt and to /my_corpus.
    """
    source_to_read = None
    text_to_read = None
    title_to_read = None
    url_to_read = None
    requires_html_parse = None
    if read_request.startswith('read http'):
        # determine the source of a reading
        if read_request.find("wikipedia."):
            source_to_read = "wikipedia"
        else: 
            # set the domain name as the source
            source_to_read = read_request[5:] # remove the word 'read '
            if source_to_read.startswith("http"):
                startPos = 3 + re.search("://", source_to_read).start()
            else:
                startPos = 0
            source_to_read = source_to_read[startPos:]
            periodPos = re.search("\.", source_to_read).start()
            source_to_read = source_to_read[:periodPos]
        # set temporary doc metadata values since tokenization hasn't 
        # yet occured.
        text_to_read = None
        title_to_read = "Unknown"
        requires_html_parse = True
        # keep everything after 'read '
        url_to_read = read_request[5:] 
        print("I will try to read the following:")

    elif read_request.startswith('read this from '):
        source_to_read = read_request[15:]
        colonPos = re.search(":", source_to_read).start()
        source_to_read = source_to_read[:10]
        text_to_read = re.split("read this from .*:", read_request)[1]
        title_to_read = 'Unknown'
        requires_html_parse = False
        print("Trying to read the following:")

    else:
        source_to_read = 'Unknown'
        text_to_read = read_request[5:]
        title_to_read = 'Unknown'
        requires_html_parse = False
        print("Trying to read the following:")

    print("\tsource_to_read:",source_to_read)
    print("\ttext_to_read:",text_to_read)
    print("\ttitle_to_read:",title_to_read)
    print("\turl_to_read:",url_to_read)
    print("\trequires_html_parse:",requires_html_parse)

    # load content into temp_processing_text.txt and 
    # save doc/metadata to my_corpus
    if requires_html_parse:
        load_html(url_to_read,source_to_read) 
    else:
        load_text(text_to_read) 
    tokenize(source_to_read,title_to_read)
    return True

# main loop
update_topics_known()
reading_loop = True
while reading_loop:
    input_parsed = False
    print("\n\nAVAILABLE COMMANDS: \n\t'read' (e.g. read https://en.wikipedia.org/wiki/Carpinus_betulus)\n\t'read this from source: paragraph' (e.g. read this from wikipedia: A folksinger or folk singer is a person who sings folk music.)\n\t'exit'")
    reading_loop_input = input('--> ')
    # if reading_loop_input starts with read
    if reading_loop_input.startswith('read '):
        input_parsed = True
        read(reading_loop_input)
    # exit the main loop
    if reading_loop_input == 'exit' or reading_loop_input == 'abort':
        input_parsed = True
        # clear the contents of the two temporary .txt files
        with open(absolute_filepath + \
            '/temp_preprocessing_text.txt', 'w', encoding='utf-8') as f:
            f.write("")
        with open(absolute_filepath + \
            '/temp_processing_text.txt', 'w', encoding='utf-8') as f:
            f.write("")
        reading_loop = False
    # report syntax errors
    if input_parsed == False:
        print("I don't understand '%s'." % reading_loop_input)
print("===== Exiting Script =====")
