
from twilio.twiml.voice_response import VoiceResponse
import time, threading

response = VoiceResponse()
listening = False
isHuman = True
key = ""
temp_isHuman = isHuman
temp_key = -1
time_elapsed = time.time()
last_call_time = time.time()
text = ""
num_male_docs = 0
num_female_docs = 0
timeout = 10