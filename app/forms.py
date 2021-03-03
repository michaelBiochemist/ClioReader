from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
	email = StringField('email', validators=[DataRequired()],render_kw={"placeholder":"Email Address"})
	password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder":"Password"})
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class PasswordResetForm(FlaskForm):
	email = StringField('Email')#, render_kw={"placeholder":"Enter Email Address"})
	#submit = SubmitField('Reset Password')

class SignUpForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder":"Enter Password"})
	password_confirm = PasswordField('Confirm Password', validators=[DataRequired()],render_kw={"placeholder":"Confirm Password"})
	firstname = StringField('First Name', validators=[DataRequired()],render_kw={"placeholder":"Enter First Name"})
	email = StringField('Email', validators=[DataRequired()],render_kw={"placeholder":"Enter Email Address"})
	email_confirm = StringField('Confirm Email', validators=[DataRequired()],render_kw={"placeholder":"Confirm Email Address"})
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Get Started')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if self.email.data != self.email_confirm.data:
			print('Your email address and confirmation are not the same.')
			raise ValidationError('Your email address and confirmation are not the same.')
		elif user is not None:
			raise ValidationError('That email is currently in use. Perhaps you would like to try the \'forgot password\' link?')

	def validate_password(self,password):
		#print('self.password is: ' + self.password.data + ". And the password is: " + password.data + " and the confirmation is: " + self.password_confirm.data)
		if self.password.data != self.password_confirm.data:
			print('Your password and confirmation are not the same.')
			raise ValidationError('Your password and confirmation are not the same.')
		else:
			return True
		
class SettingsForm(FlaskForm):
	password = PasswordField('Enter Current Password', validators=[DataRequired()],render_kw={"placeholder":"Old password"})
	new_password = PasswordField('Enter New Password', validators=[DataRequired()],render_kw={"placeholder":"New password"})
	password_confirm = PasswordField('Confirm New Password', validators=[DataRequired()],render_kw={"placeholder":"Confirm new password"})
	submit = SubmitField('Get Started')

	def validate_password(self,active_user):
		#print('self.password is: ' + self.password.data + ". And the password is: " + password.data + " and the confirmation is: " + self.password_confirm.data)
		if self.new_password.data != self.password_confirm.data:
			print('Your password and confirmation are not the same.')
			print(self.new_password.data)
			print(self.password_confirm.data)
			raise ValidationError('Your password and confirmation are not the same.')
		elif active_user is not None:
			if active_user.check_password(self.password.data):
				return True
			else:
				raise ValidationError('Your old password does not match the one we have on file.')
		else:
			raise ValidationError('There is no registered user, how is one changing user settings?')

class ShareForm(FlaskForm):
	title = StringField('Title of the file you want to share', validators=[DataRequired(), Length(max=255)])
	description = TextAreaField('Please tell us about this file and why we sould read/listen to it.')
	reader = StringField('Who read this?', validators=[Length(max=45)])
	speed = StringField('Speed: ', validators=[Length(max=5)])
	shareItem = FileField('Item to Upload',validators=[DataRequired()])
	submit = SubmitField('Share file')
