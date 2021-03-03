from app import db
from flask import request,url_for,redirect,flash,send_from_directory
from flask_login import current_user#, UserMixin
from app import app
from multiprocessing import Process
from app import polly_interface as polly
from werkzeug.utils import secure_filename
#from app import text_extract
import os
import sys
import PyPDF2
from datetime import datetime
#from app.purchasing import Payment #Purchase
import textract

books_folder = 'data/audiobooks/'
translations_folder = 'data/translations/'
uploads_folder = 'data/uploads/'
max_chapter_length = 80000
polly_price = 4 / 1000000 #Four dollars per 1 million characters
markup = 2.0
min_paypal_percentage = 0.029
max_paypal_percentage = 0.044

class Translation(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
	name_pdf = db.Column(db.String(255))
	name_text = db.Column(db.String(255))
	num_pages = db.Column(db.Integer)
	status = db.Column(db.String(25))
	date_started = db.Column(db.TIMESTAMP)
	date_completed = db.Column(db.TIMESTAMP)
	downloaded = db.Column(db.Boolean)
	book_id = db.Column(db.Integer,db.ForeignKey('AudioBook.id'),index=True)

	def __init__(self, uid, name_pdf,date_started,):
		self.name_pdf = name_pdf
		self.user_id = uid
		print('Initializing sql entry ' + self.name_pdf)
		self.status = 'Not Started'
		self.date_started = date_started
		db.session.add(self)
		db.session.commit()

	def setup_dirs(self):
		global translations_folder
		global uploads_folder
		print(self.name_pdf)
		use_dir = translations_folder + str(self.user_id) + '/'
		try:
			os.makedirs(use_dir)
		except:
			pass
		os.rename(uploads_folder + self.name_pdf,use_dir + self.name_pdf)
	
	def set_status(self, new_status):
		self.status = new_status
		db.session.commit()

	def fromPDF(self):
		global translations_folder
		use_dir = translations_folder + str(self.user_id) + '/'
		filename = self.name_pdf
		self.name_text = filename[:-3] + 'txt'
		self.set_status('Started')

		pdfFileObj = open(use_dir + filename,'rb')
		pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	
		self.num_pages = pdfReader.numPages
		print('total pages: ' + str(self.num_pages))
		db.session.commit()
		current_page = 0
		text = ""
		try:
			text = textract.process(use_dir + filename, method='tesseract',language='eng')
			outfile = open(use_dir + self.name_text,'wb')
			outfile.write(text)
			outfile.close()
			self.date_completed = datetime.now()
			self.set_status('Ready for Download')
		except:
			print('There was an error processing your file')
			print(sys.exc_info())
			self.set_status = 'Failed'
		db.session.commit()
		#return self.status

class AudioBook(db.Model):
	global books_folder
	global markup
	__tablename__ = 'AudioBook'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
	name = db.Column(db.String(255))
	parse_type = db.Column(db.String(45))
	status = db.Column(db.String(45))
	purchased = db.Column(db.Boolean)
	payment = db.Column(db.Integer, db.ForeignKey('payment.id'), index=True)

	cost_amazon = db.Column(db.Numeric(10,4))
	cost_total = db.Column(db.Numeric(10,4))
	price = db.Column(db.Numeric(10,4))

	date_started = db.Column(db.TIMESTAMP)
	date_completed = db.Column(db.TIMESTAMP)
	downloaded = db.Column(db.Boolean)
	source_file = ''
	source_text = ''

	def __init__(self, user_id, name, source_dir, parse_type):
		self.name = name
		self.user_id = user_id
		db.session.add(self)
		db.session.commit()
		use_dir = self.get_directory()
		os.makedirs(use_dir)
		self.source_file = self.name + '.txt'
		self.parse_type = parse_type

		read_text = open(source_dir + self.source_file, 'r')
		source_text = read_text.read()
		read_text.close()

		write_text = open(use_dir + '/' + self.source_file, 'w')
		write_text.write(source_text)
		write_text.close()
		self.source_text = source_text
		self.estimate_cost()
		self.status = 'Not Started'
		db.session.commit()

	def get_directory(self):
		return books_folder + str(self.user_id) + '/' + str(self.id)

	def get_source_text(self):
		use_dir = self.get_directory() + '/'
		infile = open(use_dir + self.name + '.txt')
		source_text = infile.read()
		infile.close()
		return source_text

	def estimate_cost(self):
		global polly_price
		global markup
		global max_paypal_percentage

		if self.source_text == '':
			self.source_text = self.get_source_text()
		num_characters = len(self.source_text)
		self.cost_amazon = num_characters * polly_price
		self.price = markup * self.cost_amazon
		self.price = round((0.004 + self.price),2) # round price
		self.cost_total = self.cost_amazon + self.price * max_paypal_percentage

	def check_status(self):
		if self.status not in ('Not Started','Parsing','Ready for Download'):
			chapters = AudioChapter.query.filter_by(book_id=self.id).all()
			chapters_complete = 0
			for chapter in chapters:
				p = Process(target=chapter.check_status)
				p.start()
				if chapter.status == 'failed':
					self.status = chapter.status
					db.session.commit()
					return self.status
			for chapter in chapters:
				if chapter.status in ('inProgress','complete','scheduled','completed'):
					self.status = 'in progress'
					break
				elif chapter.status == 'Ready for Download':
					chapters_complete+=1
				else:
					print('Checking status for audiobook: "' + self.name + '" got an unfamiliar status for chapter: "' + chapter.name + '" status: "' + chapter.status + '"')
			if chapters_complete == len(chapters):
				self.status = 'Ready for Download'
			db.session.commit()
		return self.status
		
	def parse(self, parse_type):
		global max_chapter_length
		if self.source_text != '':
			source_text = self.source_text
		else:
			source_text = self.get_source_text()
		order_no = 0
		self.status = 'Parsing'
		db.session.commit()
		if parse_type == 'syntax':
			if source_text.find('<title>') != -1:
				title_start = source_text.find('<title>') + 7 
				title_end = source_text.find('</title>') 
			if title_start != 6 and title_end != -1 and title_end - title_start < 255:
				self.name = source_text[title_start:title_end]
				source_text = source_text.replace('<title>','',1)
				source_text = source_text.replace('</title>','',1)
				
			next_chapter = source_text.find('<chapter>')
			ch_name = source_text[next_chapter:].find('\n')
			while next_chapter != -1:
				ch_end_line = source_text[next_chapter:].find('\n')
				ch_title = source_text[next_chapter + len('<chapter>'): ch_end_line]
				ch_title = ch_title[:255]
				source_text = source_text[next_chapter + len('<chapter>'):]
				next_chapter = source_text.find('<chapter>')
				if next_chapter != -1:
					ch_text = source_text[:next_chapter]
				else:
					ch_text = source_text

				while len(ch_text) > max_chapter_length:
					last_line = get_last_line(ch_text[:max_chapter_length])
					audio_chapter = AudioChapter(ch_title,ch_text[:last_line],order_no,self.id)
					ch_text = ch_text[last_line:]
					order_no+=1

				audo_chapter = AudioChapter(ch_title,ch_text,order_no,self.id)
				order_no+=1
		else:	
			while len(source_text) > max_chapter_length:
				last_line = get_last_line(source_text[:max_chapter_length])
				print('last line is ' + str(last_line))
				audio_chapter = AudioChapter('Part ' + str(order_no+1),source_text[:last_line],order_no,self.id)
				source_text = source_text[last_line:]
				order_no+=1
			audio_chapter = AudioChapter('Part ' + str(order_no+1),source_text,order_no, self.id)
		self.status = 'Parsed'
		db.session.commit()

class AudioChapter(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	book_id = db.Column(db.Integer,db.ForeignKey('AudioBook.id'),index=True)
	order_no = db.Column(db.Integer)
	name = db.Column(db.String(300))
	aws_file_key = db.Column(db.String(255))
	aws_path = db.Column(db.String(255))
	aws_task_id = db.Column(db.String(255))
	status = db.Column(db.String(45))

	def __init__(self,name,text,order_no,book_id):
		self.name = name
		self.book_id=book_id
		self.order_no = order_no
		task = polly.large_speech(text)
		self.aws_task_id = task['task_id']
		print(task.keys())
		try:
			self.status = task['TaskStatus']
		except:
			self.status = task['status']

		db.session.add(self)
		db.session.commit()

	def check_status(self):
		downloadable = False
		download_now = False
		status = polly.get_task_status(self.aws_task_id)
		print(self.status.lower())
		print(status[0])
		if self.status.lower() == 'completed' or str(status[0]) == 'completed':
			print('download now set to true')
			download_now = True	
		self.status = status[0]
		if status[1] != -1:
			parse_path = status[1]
			keyloc = parse_path.find('key')
			self.aws_path = parse_path[:keyloc]
			self.aws_file_key = parse_path[keyloc:]
			print('downloadable set to true by current aws call')
			downloadable = True
		elif self.aws_file_key != None:
			print('downloadable set to true by stored data')
			downloadable = True
		db.session.commit()
		if downloadable and download_now:
			print('calling self.download')
			self.download()

	def download(self):
		print('Downloading chapter ' + self.name)
		book = AudioBook.query.filter_by(id=self.book_id).first()
		polly.download(self.aws_file_key,book.get_directory() + '/' + str(self.order_no) + ' - ' + self.name + '.mp3')
		self.status = 'Ready for Download'
		db.session.commit()
		#return self.status()
				
def get_last_line(text):
	last_line = text[:max_chapter_length].rfind('\n\n')
	if last_line == -1:
		last_line = text[:max_chapter_length].rfind('\n')
	if last_line == -1:
		last_line = text[:max_chapter_length].rfind(' ')
	if last_line == -1:
		return max_chapter_length
	return last_line
		

@app.route('/pdftotxt',methods=["POST"])
def translate_from_pdf():
	form = request.form.to_dict()
	#find code to get attachments here
	attachments = request.files.to_dict()
	for attachment in attachments:
		attachments[attachment].save()
		translation = Translation(user_id=current_user,name_pdf=attachments[attachment].filename,date_started=datetime.now())
		p = Process(target=translation.fromPDF,args=attachment)
		p.start()
	return "Hi"

@app.route('/MakeTranslation',methods=["GET","POST"])
def create_audio_book():
	if not current_user.is_authenticated:
		return MakeTranslation_Error('Please log in or register to use this function.')
	if request.method == "POST":
		form = request.form.to_dict()
		attachments = request.files.to_dict()
		if attachments == {}:
			return MakeTranslation_Error('Please attach a file that you want to convert.')	
		
		attachment = request.files['toConvert']
		filename = secure_filename(attachment.filename)
		attachment.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

		if form['convType'] == "audiobook":
		# Check that file uploaded is indeed a text file.
		# 
			#audiobook = AudioBook(user_id=current_user,name=form.name.data,status="Not Started",parse_type="manual")
			if filename[-4:].lower() != '.txt':
				return MakeTranslation_Error('To make an audiobook, please attach a text file, one that ends with \'.txt\'.')	
			print(app.config['UPLOAD_FOLDER']) # delete later
			audiobook = AudioBook(current_user.id,filename[:-4],app.config['UPLOAD_FOLDER'],parse_type="manual")
		else:
			if filename[-4:].lower() != '.pdf':
				return MakeTranslation_Error('To convert PDF to text, please attach a PDF file, one that ends with \'.pdf\'.')	
			translation = Translation(current_user.id,name_pdf=filename,date_started=datetime.now())
			translation.setup_dirs()
			p = Process(target=translation.fromPDF)
			p.start()
			db.session.commit()
			
	else:
		print("Request method is GET")
	return(redirect(url_for('index')))

def MakeTranslation_Error(error_message):
	flash(error_message)
	return(redirect(url_for('index')))

@app.route('/download_text_<text_id>')
def serve_translation(text_id):
	print('this function was called')
	global translations_folder
	if not current_user.is_authenticated:
		return redirect(url_for('index'))
	translation = Translation.query.filter_by(id=text_id,user_id=current_user.id).first()
	return send_from_directory( '../' + translations_folder + str(translation.user_id) + '/' , translation.name_text, as_attachment=True, mimetype='text/plain')


@app.route('/download_audio_chapter_<chapter_id>')
def serve_audio_chapter(chapter_id):
	print('this function was called')
	global books_folder
	if not current_user.is_authenticated:
		return redirect(url_for('index'))
	audio_chapter = AudioChapter.query.filter_by(id=chapter_id).first()
	audio_book = AudioBook.query.filter_by(id=audio_chapter.book_id,user_id=current_user.id).first()
	if audio_book is None:
		return "Error: This user does not have access to this audiobook"
	return send_from_directory('../' + audio_book.get_directory() + '/',  str(audio_chapter.order_no) + ' - ' + audio_chapter.name + '.mp3', as_attachment=True, mimetype='audio/mpeg3')

@app.route('/create_audiobooks', methods=['POST'])
def create_audio_book_from_translation():
	global translations_folder
	values = request.form
	for x, y in values.items():
		print(x + '\t' + y)	
		if y == 'on':
			txt = Translation.query.filter_by(id=x,user_id=current_user.id).first()
			audiobook = AudioBook(current_user.id,txt.name_text[:-4],translations_folder + str(current_user.id) + '/',parse_type="manual")
			print('audiobook id is ' + str(audiobook.id))
			txt.book_id=audiobook.id
			db.session.commit()
			
	return redirect('/text_translations')
