from app import db
from app import app
from app.translations import AudioBook
from multiprocessing import Process
from flask import request

class Purchase(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
	price = db.Column(db.Float(6,2))
	date = db.Column(db.TIMESTAMP)
	completed = db.Column(db.Boolean)

	def complete(self):
		books_purchased = BookPurchase.query.filter_by(purchase_id=self.id).all()
		for purchased in books_purchased:
			book = AudioBook.query.filter_by(id=purchased.book_id).first()
			book.purchased = True
		self.completed = True
		db.session.commit()

	def initiateParsing(self, books_purchased):
		for purchased in books_purchased:
			book = AudioBook.query.filter_by(id=purchased.book_id).first()
			p = Process(target=book.parse,args=(book.parse_type,))
			p.start()
			

class BookPurchase(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), index=True)
	book_id = db.Column(db.Integer, db.ForeignKey('AudioBook.id'), index=True)
	
class Payment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
	unix_time = db.Column(db.Integer())
	payment_date = db.Column(db.TIMESTAMP)
	last_name = db.Column(db.String(30))
	payment_gross = db.Column(db.Float(6,2))
	payment_fee = db.Column(db.Float(6,2))
	payment_net = db.Column(db.Float(6,2))
	payment_status = db.Column(db.String(15))
	txn_id = db.Column(db.String(25))

	def __repr__(self):
		return '<Payment {}>'.format(self.id)

@app.route('/buy_books',methods=['POST'])
def initiatePurchase():
	print('receiving a request to buy books!!!!!!!!!')
	print(request.form)
	values = request.form;
	#print(request.form)
	for key in values.keys():
		print(key + ' ' + values[key])	
	return "Hi from python"

