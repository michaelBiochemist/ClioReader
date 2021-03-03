from flask import url_for,redirect,request,flash, send_from_directory
from flask import render_template
from flask_login import current_user, login_user, logout_user
from werkzeug.datastructures import ImmutableMultiDict, ImmutableOrderedMultiDict
from werkzeug import secure_filename
from app import app
from app import db
from app.config import Config
from app.models import User, Email, ShareObject#, TranslationRequest, AudioBook, AudioChapter
from app.purchasing import Payment
from app.forms import LoginForm, SignUpForm, PasswordResetForm, SettingsForm, ShareForm
from app import logging
from app.translations import Translation,AudioBook,AudioChapter
from app.custom_email import send_password_reset_email
from wtforms.validators import ValidationError
import os
from datetime import datetime, timedelta
from multiprocessing import Process
import time
import requests 
#from flask_weasyprint import HTML, render_pdf

paypal_min_fee = 0.25
root_folder = Config.root_dir + 'app'
project_root = Config.root_dir
@app.route('/')
@app.route('/index')
def index():
	#return app.send_static_file('index.html')
	#print(os.listdir())
	if not current_user.is_authenticated:
		form = SignUpForm()
		forml = LoginForm()
		#return render_template('login.html', form=form, form_l=forml)'''
		#return render_template('polly_main.html', form=form, form_l=forml)
		return render_template('login.html', form=form, form_l=forml)
	else:
		return render_template('polly_main.html')

@app.route('/forgot_password',methods=['GET','POST'])
def forgot_password():	
	if request.method == 'POST':
		form = PasswordResetForm()
		#if form.validate_on_submit():
		if True:
			if form.email.data != "":
				user = User.query.filter_by(email=form.email.data).first()
			else:
				return render_template('forgot_password.html',form=form,message="Please enter a valid user name or email address",passed="no")
			if user:
				new_mail = Email(user_id = user.id, recipient = user.email, message_type = 'Password reset', link_followed = 0, created=db.func.now())
				link_hash = new_mail.set_unique_hash()
				#db.session.add(new_mail)
				#db.session.commit()
				send_password_reset_email(user.email,link_hash)
				return render_template('forgot_password.html',form=form,message='We have sent your password reset email, from Clioreader@gmail.com. Please follow it\'s instructions to reset your password.',passed="yes")
			else:
				return render_template('forgot_password.html',form=form,message="We cannot find a user matching either that user name or email address. Please check your spelling and try again.")
		
	if not current_user.is_authenticated:
		form = PasswordResetForm()
		return render_template('forgot_password.html', form=form, message="",passed='no')
	else:
		return redirect('/userdata')

@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated or request.method == 'GET':
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None or not user.check_password(form.password.data):
			print('invalid email address or password')
			flash('Invalid email address or password')
			return "Invalid email address or password"
			#return redirect(url_for('login'))
		#print('form was validated')
		login_user(user, remember=form.remember_me.data)
		return redirect('/index')
	return render_template('login.html', title='Sign In', form=form)

@app.route('/<ttype>_translations')
def show_translations(ttype):
	if not current_user.is_authenticated:
		return redirect('/index')
	elif ttype == 'audio':
		audiobooks = AudioBook.query.filter_by(user_id=current_user.id).all()
		book_check(audiobooks)
		return render_template('audio_translations.html',AudioBooks=audiobooks)
	elif ttype == 'text':
		translations = Translation.query.filter_by(user_id=current_user.id).all()
		return render_template('text_translations.html',textfiles=translations)

@app.route('/audiobook_<bookid>')
def show_downloadable_audiobook(bookid):
	if not current_user.is_authenticated:
		return redirect('/index')
	audiobook = AudioBook.query.filter_by(id=bookid,user_id=current_user.id).first()
	chapters = AudioChapter.query.filter_by(book_id=bookid).order_by(AudioChapter.order_no.asc()).all()
	return render_template('audiobook_project.html',audiobook=audiobook,all_chapters=chapters)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
		
@app.route('/signup', methods=['GET', 'POST'])
def takesignup():
	if current_user.is_authenticated or request.method == 'GET':
		return redirect(url_for('index'))
	form = SignUpForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,created=datetime.now())
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congrats you are now a registered user!')
		login_user(user, remember=form.remember_me.data)
	return redirect('/index')

###########################################################################
@app.route('/hackathons/<project>')
def grab_hackathon(project):
	return render_template('/hackathons/' + project)
###########################################################################


@app.route('/<path:path>')
def get_static(path):
	return app.send_static_file(path)

@app.route('/contactform', methods=['POST'])
def submit_contact():
	contactspecs = request.form	
	usetime = datetime.now().isoformat()
	contact_history = open('./data/contact_history','a')
	contact_history.write(usetime + ' -- ' + unicode(contactspecs))
	contact_history.close()
	return render_template('/auto/thankyoupage.html')

#This section of routes deals with purchasing the app on paypal
@app.route('/purchase/')
def purchase():
	print(current_user)
	try:
		return render_template("subscribe.html")
	except e:
		return(str(e))

@app.route('/success/')
def success():
	try:
		print(request.form)
		print(request.cookies)
		return render_template("success.html")
	except e:
		return(str(e))

@app.route('/ipn/',methods=['POST'])
def ipn():
	global root_folder
	global project_root
	global paypal_min_fee
	print("Posted to ipn")
	try:
		arg = ''
		request.parameter_storage_class = ImmutableOrderedMultiDict
		values = request.form
		for x, y in values.items():
			print(x + '|||' + y)
			if x == 'custom':
				y_parse=y.split('|')
				uid=y_parse[0]
				books = y_parse[1].split('row')[1:]
				book_sum = paypal_min_fee
				print(book_sum)
				audiobooks = AudioBook.query.filter_by(user_id=uid).all()
				print(books)
				for book in audiobooks:
				#books.reverse()
				#for bookId in books:
					print('getting next book')
					#book = AudioBook.query.get(bookId)
					print(str(type(book.id)))
					print(book.id)
					if str(book.id) in books:
						use_price = book.price
						print(book.name + ' ' + str(use_price))
						print('checking if after or next')
						print(str(type(use_price)) + ' ' + str(type(book_sum)))
						book_sum+=float(book.price)
						book.purchased = True
				print(book_sum)
			arg += "&{x}={y}".format(x=x,y=y)
		print('arg is:')
		print(arg)
		validate_url = 'https://www.paypal.com' \
					   '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
					   .format(arg=arg)
		print('validating url ' + validate_url)
		r = requests.get(validate_url)
		print("got validated url")
		verified = r.text
		print(verified)
		if verified == 'VERIFIED':
			try:
				payer_email =  request.form.get('payer_email')
				unix = int(time.time())
				payment_date = request.form.get('payment_date')
				delta = timedelta(hours=3)
				payment_date = datetime.strptime(payment_date[:-4],'%H:%M:%S %b %d, %Y')
				payment_date += delta
				print('payment date is ' + str(payment_date.isoformat()))
				print('user id is' + str(uid))
				last_name = request.form.get('last_name')
				payment_gross = float(request.form.get('payment_gross'))
				print('payment gross is ' + str(payment_gross))
				print('payment by books is ' + str(book_sum))
				if not (float(payment_gross) > float(book_sum)-0.02 and float(payment_gross) < float(book_sum)+0.02):
					return 'There was a pricing error. The paypal payment was ' + str(payment_gross) + ' whereas the price on our records was ' + str(book_sum)
				payment_fee = float(request.form.get('payment_fee'))
				payment_net = float(payment_gross) - float(payment_fee)
				payment_status = request.form.get('payment_status')
				txn_id = request.form.get('txn_id')
				print('got other info')

				with open(project_root + 'logs/ipnout.txt','a') as f:
					data = 'SUCCESS\n'+str(values)+'\n'
					f.write(data)
			except Exception as e:
				with open(root_folder+'logs/ipnout.txt','a') as f:
					data = 'ERROR WITH IPN DATA\n'+str(values)+'\n'
					f.write(str(e))
					f.write(data)

			print('posting info to sql db')
			try:
				payment = Payment(user_id=uid,unix_time=unix, payment_date=payment_date, last_name=last_name, payment_gross=payment_gross, payment_fee=payment_fee, payment_net=payment_net, payment_status=payment_status, txn_id=txn_id)
				print(str(payment))
				db.session.add(payment)
				db.session.commit()
				print('payment id is ' + str(payment.id))
				for book in audiobooks:
					if book.id in books:
						book.purchased = True
						book.payment = payment.id
						db.session.commit()
						p = Process(target=book.parse,args=(book.parse_type,))
						p.start()
				#user = User.query.filter_by(id=uid).first()
				#purchase = Purchase.query.filter_by(user_id=uid,completed=False,price=payment_gross)
				#purchase.complete();
			except Exception as e:
				print(str(e))
		else:
			with open(project_root + 'logs/ipnout.txt','a') as f:
				data = 'FAILURE\n'+str(values)+'\n'
				f.write(data)

		return r.text
	except Exception as e:
		return str(e)

@app.route("/settings")
def getUserSettings():
	if not current_user.is_authenticated:
		return redirect(url_for('index'))
	form = SettingsForm()
	return render_template("change_password.html", user=current_user, form=form)

@app.route('/about')
def showAbout():
	if not current_user.is_authenticated:
		return redirect(url_for('index'))
	return render_template("about.html")

@app.route("/update_password", methods=["POST"])
def updateSetting():
	form = SettingsForm()
	if not current_user.is_authenticated:
		return redirect(url_for('index'))
		
	try:
		if current_user.forgot_password:
			current_user.set_password(form.new_password.data)
			current_user.forgot_password = False
			db.session.commit()
			return "Your password was successfully changed!"

		validation = form.validate_password(current_user)
		print('validated password')
		if validation:
			print(form.new_password.data)
			current_user.set_password(form.new_password.data)
			db.session.commit()
			return "Your password was successfully changed!"
		else:
			print(validation)
		
	except ValidationError as e:
		print("Error is: " + str(e))
		return(str(e))

@app.route("/loginFromEmail_<email_hash>")
def login_from_email(email_hash):
	email = Email.query.filter_by(unique_hash=email_hash).first()
	if email.validate():
		user = User.query.filter_by(id=email.user_id).first()
		user.forgot_password = True
		db.session.commit()
		login_user(user, remember=False)
		flash('Please reset your password. Feel free to igore the "Current Password" box and only input the new passwords.')
		return redirect('/settings')
	errormsg = 'This email link is either older than 24 hours or is not the one most recently sent. Please use the most recent password reset email or create a new request.'
	form = PasswordResetForm()
	return render_template('forgot_password.html',form=form,message=errormsg)
	
	#user = User.query.filter_by(email=form.email.data).first()
	#login_user(user, remember=False)


def book_check(audiobooks):
	for book in audiobooks:
		if book.status == 'Not Started' and book.purchased == 1:
			p = Process(target=book.parse,args=(book.parse_type,))
			p.start()
		book.check_status()

@app.route("/shareItem", methods=["GET","POST"])
def share_item():
	form = ShareForm()
	print(request.method)
	if request.method == "POST":
		if form.validate_on_submit():
			shareObject = ShareObject(title=form.title.data, description=form.description.data, user_id=current_user.id, reader=form.reader.data, speed=form.speed.data) 
			filename = secure_filename(form.shareItem.data.filename)
			db.session.add(shareObject)
			db.session.commit()
			share_dir = Config.insider_share_dir + str(shareObject.id)
			os.mkdir(share_dir)
			form.shareItem.data.save(share_dir + '/' +  filename)
			shareObject.link = share_dir + '/' + filename
			db.session.commit()
			flash("Thank you for adding to the collection. Shall you add another?")
			#return render_template("shareItem.html",form=form)
		else:
			print('Validation failed')
			flash("There was a validation error")
		
	#else:
	return render_template("shareItem.html",form=form)

@app.route("/insider")
def view_insider():
	if current_user.is_authenticated:
		if current_user.insider == True:
			shareObjects = ShareObject.query.all()
			return render_template('/insider.html',allShares=shareObjects)
	return redirect(url_for('index'))

@app.route("/data/shared/<sid>/<fname>")
def serve_shared_file(sid, fname):
	return send_from_directory('../data/shared/'+ str(sid), fname, as_attachment=True)	
