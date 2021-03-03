#!/usr/bin/python

import mysql.connector
import sys

server_ip = "127.0.0.1"
config = {
	'user': 'Tester',
	'password': "test",
	'host': '127.0.0.1',
	'database': 'test',
	'raise_on_warnings': False,
	#'use_pure': False,
	#'multi': True,
	'buffered': True
}
config_sdr = {
        'user': 'Cthulhu',
        'password': "AA%^IaRf+1g%p2oV%w=ay^w1NIoC%g",
        'host': '10.4.76.14',
        'database': 'testing',
        'raise_on_warnings': False,
        #'use_pure': False,
        #'multi': True,
        'buffered': True
}

#db = mysql.connector.connect(**config)
try:
	db = mysql.connector.connect(**config_sdr)
	cur = db.cursor()
except:
	info = sys.exc_info()
	print("there was an error")
	print("info 0 is " + str(info[0]))
	print("info 1 is " + str(info[1]))
	quit()
#db = db.close()
#warnings.filterwarnings('error', category=MySQLdb.Warning)
def runquery(sql_query, viewres):
	try:
		output = cur.execute(sql_query) #"<SQL QUERIES GO HERE>")
	except:
		info = sys.exc_info()
		print("there was an error")
		print("info 0 is " + str(info[0]))
		print("info 1 is " + str(info[1]))
		if "Broken pipe" in info[1]:
			global db
			db = mysql.connector.connect(**config_sdr)
			global cur
			cur = db.cursor()
			
	if viewres:
		output = cur.fetchall()
		return output

def quick_query(sql_query, viewres):
	output = cur.execute(sql_query) #"<SQL QUERIES GO HERE>")
	if viewres:
		output = cur.fetchall()
		return output

def sproc(procedure,viewres):
	output = cur.callproc(procedure)
	if viewres:
		output = []
		for result in cur.stored_results():
			output.append(result.fetchall())
		return output

def close():
	db.commit()
	db.close()
