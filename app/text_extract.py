#!/usr/bin/python3
"""
This is for reading PDF files and eventually other file types as well and for converting them into text. 
Borrowed from the Rizwan Qaiser's blog on 05/11/17
Written by Michael van Dyk starting 11/13/18
"""

import PyPDF2
import textract
from datetime import datetime
#from app.translations import Translation
from app import db
#from nltk.tokenize import word_tokenize -- not looking to tokenize the words right now
#from nltk.corpus import stopwords

import sys

filename = sys.argv[1]

def pdf(filename):
	pdfFileObj = open(filename,'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	
	num_pages = pdfReader.numPages
	print('total pages: ' + str(num_pages))
	current_page = 0 
	text = ""
	try:
		text = textract.process(filename, method='tesseract',language='eng')
		return {'num_pages':num_pages, 'text': text}
	except:
		print('There was an error attempting to process your file')
		print(sys.exc_info())
		exit()
def extract(translation_request, filename):
	translation_request.set_status('Starting')
	translation_request.name_pdf = filename
	
def pdf_experimental(filename):
	pdfFileObj = open(filename,'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	
	num_pages = pdfReader.numPages
	print('total pages: ' + str(num_pages))
	current_page = 0 
	text = ""
	try:
		while current_page < num_pages:
			pageObj = pdfReader.getPage(current_page)
			current_page+=1
			text += pageObj.extractText()
			if current_page > 10 and text == "":
				break
		print('exceeded while loop: ' + str(datetime.now().isoformat()))
		if text == "":
			print('The standard text processing method yielded nothing. Switching to tesseract.')
			text = textract.process(filename, method='tesseract',language='eng')
	except:
		print('Error using the standard text processing method. Switching to tesseract. ' + str(datetime.now().isoformat()))
		print(sys.exc_info()[0])
		text = textract.process(filename, method='tesseract',language='eng')
	return text
		

if __name__ == '__main__':
	print('Starting conversion ' + str(datetime.now().isoformat()))
	outfile = open(sys.argv[2],'wb')
	outfile.write(pdf(sys.argv[1])['text'])
	outfile.close()
	print('Finished conversion ' + str(datetime.now().isoformat()))
