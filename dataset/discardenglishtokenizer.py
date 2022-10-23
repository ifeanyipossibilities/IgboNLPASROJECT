#!/usr/bin/env python3
#import locale
import pyuca
import re
import os, fnmatch
from tempfile import NamedTemporaryFile
#import codecs
#locale.setlocale(locale.LC_COLLATE, 'ig_NG.UTF-8')





import PyPDF2
import textract
import sys

from enchant.checker import SpellChecker
import subprocess




#from nltk.corpus import wordnet





#use Portugal or spanish for tesseract or train new character on tesseract
def extract_text_filename(filename,language='en'):
	"""Extract Document text"""
	return(textract.process(filename, method='tesseract', language=language))



def extract_pdf_text(fileName, language='en', encoding="UTF-8"):
	"""Extract PDF Text"""
	numPages = 0
	pageCount = 0
	text = ""

	#Let's try pdftotext utility
	try:
		pdftesseract_tmp_file = NamedTemporaryFile(suffix=".pdf").name
		subprocess.run(["pdftotext", "-enc", encoding, "-layout", fileName, pdftesseract_tmp_file ])
		with open(pdftesseract_tmp_file, 'r') as f:
			text = f.read()
			if re.match(r'^(\u000c)$', text, re.I | re.S | re.M | re.U) == None and  "" !=  text: #when not empty text will be empty if scanned pdf
				return text
	except FileNotFoundError: #"pdftotext not installed no problem"
		pass

	try:
		pdfFileObj = open(fileName,'rb')
		#The pdfReader variable is a readable object that will be parsed
		pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
		#discerning the number of pages will allow us to parse through all #the pages
		numPages = pdfReader.numPages
	except:
		pass

	#The while loop will read each page
	while pageCount < numPages:
		pageObj = pdfReader.getPage(pageCount)
		pageCount +=1
		textdata = pageObj.extractText()
		#This if statement exists to check if the above library returned #words. It's done because PyPDF2 cannot read scanned files tesseract can, extract the pdf page and pass to tesseract.
		if re.match(r'^(\u000c)$', textdata, re.I | re.S | re.M | re.U)  or  "" ==  textdata:
#			extract the scanned empty word page
			pdfWriter = PyPDF2.PdfFileWriter()
			pdfWriter.addPage(pageObj.getObject())
			pdftesseract_tmp_file = NamedTemporaryFile(suffix=".pdf").name
			with open(pdftesseract_tmp_file, 'wb') as pdftesseract_tmp:
				pdfWriter.write(pdftesseract_tmp)
				try:
					filedata_bytes = extract_text_filename(pdftesseract_tmp_file,language)
					text += filedata_bytes.decode()
				except:
					pass
				os.unlink(pdftesseract_tmp_file)


		else:
			text += textdata

	return text


def read_text(fileName):
	"""Read Text"""
	with open(fileName, "r") as f:
		return f.read()


def wordnet_not_english_words(text):
	"""split text and discard english words 70% effective you need more string stripping (.,>) etc """
	Okwuigbo = set()


#	the following collations are not been interpreted correctly
	"""
		ù ̣
		ò ̣
		ū ̣
		ī ̣
		ì ̣
		Ì ̣
		ō ̣

		"""

#	text = text.replace("ù ̣", "ù")
#	text = text.replace("ò ̣", "ò")
#	text = text.replace("ò ̣", "ò")
#	text = text.replace("ō", "ō")
#	text = text.replace("ū ̣", "ū")
#	text = text.replace("ī ̣", "ī")
#	text = text.replace("ì ̣", "ì")
#	text = text.replace("ì ̣", "ì")
#	text = text.replace("Ì", "Ì")
	for sentence_line in text.split("\n"):
		if re.search(r'^[\s]+$', sentence_line, re.I | re.S | re.M):
			continue
		for igboword in sentence_line.split(" "):
			englishword = wordnet.synsets(igboword) #englishword.definition
			if 0 == len(englishword):
				Okwuigbo.add(igboword)
#			else:
#				print(f"{igboword}")

	return  "\n".join(sorted(Okwuigbo, key=pyuca.Collator().sort_key))






def enchant_not_english_words(text):
	"""split text and discard english words 95% effective"""
	Okwuigbo = set()
	for sentence_line in text.split("\n"):
		if re.search(r'^[\s]+$', sentence_line, re.I | re.S | re.M):
			continue
		for igboword in sentence_line.split(" "):
			chkr = SpellChecker('en_US')
			chkr.set_text(igboword)
			for eng_err in chkr:
				suggest = eng_err.suggest()
				if suggest:
					Okwuigbo.add(eng_err.word)
				else:
					Okwuigbo.add(eng_err.word)

	return "\n".join(sorted(Okwuigbo, key=pyuca.Collator().sort_key))




def sort_collation(text):
	"""Sort Collation"""
	return "\n".join(sorted(set(text.split("\n")), key=pyuca.Collator().sort_key))



def read_folder_text_token(folder,pattern=None):
	"""Read folder text and tokenize none english"""
	text = ""
	for root, dirs, files in os.walk(folder):
		for name in files:
			if pattern and fnmatch.fnmatch(name, pattern):
				filename = os.path.join(root, name)
			else:
				filename = os.path.join(root, name)
			try:
				text += read_text(filename)
			except UnicodeDecodeError:
				text +=""

	return enchant_not_english_words(text)



def combine_folder_text(folder,pattern=None):
	"""combine folder text"""

	combinedfileName = os.path.join(folder, "..{0}..{0}combine-{1}dir.txt".format(os.sep,os.path.basename(os.path.dirname(folder))))

	if os.path.exists(combinedfileName):
		os.unlink(combinedfileName)

	text = ""
	for root, dirs, files in os.walk(folder):
		for name in files:

			if pattern and fnmatch.fnmatch(name, pattern):
				filename = os.path.join(root, name)
			else:
				filename = os.path.join(root, name)
			try:

				text += read_text(filename)
				text += f"\n\n\n\n\n\n\n\n\n----{filename}-----\n\n\n\n\n\n\n\n\n"
			except UnicodeDecodeError:
				text +=""
	save_text_to_file(text=text, fileName=combinedfileName)




def save_text_to_file(text, fileName, scope='w'):
	"""Save text file"""
	with open(fileName, scope) as o:
		o.write(text)


def tokenize_dir_text(folder, outputFilename=None):
	text = read_folder_text_token(folder)
	tokenfileName = os.path.join(folder, "..{0}..{0}token-{1}dir.txt".format(os.sep,os.path.basename(os.path.dirname(folder))))
	if outputFilename:
		tokenfileName = outputFilename
	save_text_to_file(text=text, fileName=tokenfileName)

if __name__ == "__main__":
	folder = "/Users/ifeanyi/currentporoject/IgboLanguageProject/IGBONLPMINE/textdata/"
	tokenfile = "/Users/ifeanyi/currentporoject/IgboLanguageProject/token-textdata.txt"
	tokenfileoutput = "/Users/ifeanyi/currentporoject/IgboLanguageProject/token-dir-textdata.txt"
#	/Users/ifeanyi/currentporoject/IgboLanguageProject/IGBONLP/ig_monoling/text
#	/Users/ifeanyi/currentporoject/IgboLanguageProject/python/Okwuigbo-Igbowords.txt
#	/Users/ifeanyi/currentporoject/IgboLanguageProject/Igbodicrefined.txt
#	text = extract_pdf_text(sys.argv[1])
#	text = extract_text_filename(sys.argv[1])



#	combine_folder_text("/Users/ifeanyi/currentporoject/IgboLanguageProject/IGBONLPMINE/textdata/")
	text = read_text(tokenfile)


	with open(tokenfileoutput, 'w') as o:
		text = sort_collation(text)
		o.write(text)
