from flask_mail import Message
from app import mail
from app import db
from datetime import datetime

#print('root url is ' + app.root_url)
def send_email(subject, sender, recipient, text_body, html_body):
	msg = Message(subject, sender=sender, recipients=[recipient])
	msg.body = text_body
	msg.html = html_body
	mail.send(msg)

def send_password_reset_email(recipient, use_hash):
	#global app.root_url
	subject = 'Password reset request'
	localhost = 'www.clioreader.com/'
	full_link = localhost + 'loginFromEmail_' + use_hash
	text_body = 'Hello, \nThere has been an attempt here at medhub for a user to reset your password. If it was you, please click this link: ' + full_link + ' and do so. This link will be good for 24 hours. Thanks,\rMichael van Dyk (creator of ClioReader)'
	#text_body = 'Gimme dat password!'
	html_body = 'Greetings<br>It appears that someone (hopefully you) attempted to log in and clicked the "forgot password" link. If you need to reset your password please click the link here: <a href="' + full_link + '">' + full_link + '</a>.<br>I hope you have a wonderful rest of your day. <br>Sincerely,<br>Michael van Dyk, creator of ClioReader.com'
	sender = 'ClioReader@gmail.com'
	send_email(subject, sender, recipient, text_body, html_body)
