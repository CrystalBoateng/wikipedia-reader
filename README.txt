wikipedia-reader    version 1.0    12/05/2017


SUMMARY
--------------------
wikipedia-reader is a program written in Python, to quickly tokenize wikipedia articles (and other unstructured text in English), and then pull the tokens into the current runtime. This will be part of a larger project on cognitive modelling, and therefore will NOT be updated as an independent project.

Tokenization and lemmatization are performed by Textacy, which is built on the spaCy Python library. For more information on these, see https://textacy.readthedocs.io/en/stable/index.html or https://spacy.io/

A working internet connection is required for this program to access wikipedia articles. Using an online proxy server or running this program in a cloud computing environment may cause complications or prevent the article's content from downloading.


DEPENDENCIES/SYSTEM REQUIREMENTS
--------------------
Python (https://www.python.org/downloads/)
NumPy+mkl (https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
scikit-learn (http://scikit-learn.org/stable/)
spaCy 2.0.2 (https://spacy.io/usage/)
textacy (https://textacy.readthedocs.io/en/latest/index.html)


GENERAL USAGE NOTES
--------------------
I'm using WinPython 3.5.4Qt5 IDLEX on Windows, but other IDEs and Operating Systems should work just fine. 
At runtime, the following commands are available: 
	'read' (e.g. read https://en.wikipedia.org/wiki/Carpinus_betulus)

	'read this from mySource: myParagraph' (e.g. read this from wikipedia: A folksinger or folk singer is a person who sings folk music.)

	'exit'


CHANGE LOG
--------------------
None


LICENSING
--------------------
This code is provided under a GNU General Public License (GPLv3) license, and is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Additionally, each of the dependencies listed above, has its own licensing agreement; none of those dependencies come packaged with this code.
See the GNU General Public License for more details.