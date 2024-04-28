
from twilio.twiml.voice_response import VoiceResponse
import time

response = VoiceResponse()
key = ""
temp_key = -1
time_elapsed = time.time()
last_call_time = time.time()
text = ""
num_male_docs = 0
num_female_docs = 0
timeout = 4
ENDPOINT_HIT_LIMIT = 3

def reset_call_values():
  global key, temp_key, time_elapsed, last_call_time, text, num_female_docs, num_male_docs
  key = ""
  temp_key = -1
  #idk what this 2 do, but still
  time_elapsed = time.time()
  last_call_time = time.time()
  text = ""
  num_female_docs = 0
  num_male_docs = 0
