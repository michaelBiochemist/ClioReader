"""Getting Started Example for Python 2.7+/3.3+"""
import logging
import boto3 #for bucket stuff
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir

logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
#session = Session(profile_name="adminuser")
session = Session(profile_name="default")
polly = session.client("polly")
s3 = boto3.resource('s3')
bucket = s3.Bucket('lovecraftian1337speechsynthesispwnagebucket')
def speak(use_text):
	try:
		# Request speech synthesis
		response = polly.synthesize_speech(Text=use_text, OutputFormat="mp3", VoiceId="Joanna")
	except (BotoCoreError, ClientError) as error:
		# The service returned an error, exit gracefully
		print(error)
		sys.exit(-1)
	
	# Access the audio stream from the response
	if "AudioStream" in response:
		# Note: Closing the stream is important as the service throttles on the
		# number of parallel connections. Here we are using contextlib.closing to
		# ensure the close method of the stream object will be called automatically
		# at the end of the with statement's scope.
		with closing(response["AudioStream"]) as stream:
			output = os.path.join(gettempdir(), "speech.mp3")
			output = "speech.mp3"
	
			try:
				# Open a file for writing the output as a binary stream
				with open(output, "wb") as file:
					file.write(stream.read())
			except IOError as error:
				# Could not write to file, exit gracefully
				print(error)
				sys.exit(-1)
	
	else:
		# The response didn't contain audio data, exit gracefully
		print("Could not stream audio")
		sys.exit(-1)
	
	# Play the audio using the platform's default player
	"""
	if sys.platform == "win32":
		os.startfile(output)
	else:
		# the following works on Mac and Linux. (Darwin = mac, xdg-open = linux).
		opener = "open" if sys.platform == "darwin" else "xdg-open"
		subprocess.call([opener, output])
	"""
def large_speech(use_text):
	response = polly.start_speech_synthesis_task(VoiceId='Joanna',
		OutputS3BucketName='lovecraftian1337speechsynthesispwnagebucket',
		OutputS3KeyPrefix='key',
		OutputFormat='mp3', 
		Text = use_text)
	response2 = polly.get_speech_synthesis_task(TaskId = response['SynthesisTask']['TaskId'])
	return {'task_id':response['SynthesisTask']['TaskId'],'status':response2['SynthesisTask']['TaskStatus']}

def get_task_status(task_id):
	response = polly.get_speech_synthesis_task(TaskId=task_id)
	if response['SynthesisTask'].get('OutputUri') != None:
		return [response['SynthesisTask']['TaskStatus'],response['SynthesisTask']['OutputUri']]
	else:	
		return [response['SynthesisTask']['TaskStatus'],-1]

def download(aws_file_key,file_save_path):
	global bucket
	bucket.load()
	bucket.download_file(aws_file_key,file_save_path)
	

def bucket_stuff():
	global bucket
	bucket.load()
	item_list = list(bucket.objects.all())
	for j in item_list:
		print(j.key)

def empty_bucket():
	s3 = boto3.resource('s3')
	bucket = s3.Bucket('lovecraftian1337speechsynthesispwnagebucket')
	bucket.load()
	item_list = list(bucket.objects.all())
	to_delete = []
	for j in item_list:
		to_delete.append({'Key':j.key})
	bucket.delete_objects(Delete={'Objects': to_delete})
		

if __name__ == "__main__":
	use_file = open(sys.argv[1])
	use_text = use_file.read()
	use_file.close()
	speak(use_text)
