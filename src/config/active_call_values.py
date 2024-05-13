from twilio.twiml.voice_response import VoiceResponse
import time

response = VoiceResponse()
key = ""
temp_key = -1
time_elapsed = time.time()
last_call_time = time.time()
text = ""
male_docs_number = None
female_docs_number = None
<<<<<<< HEAD
timeout = 3
=======
timeout = 4
>>>>>>> master
ENDPOINT_HIT_LIMIT = 3


def reset_call_values():
    global key, temp_key, time_elapsed, last_call_time, text, female_docs_number, male_docs_number
    key = ""
    temp_key = -1
    # idk what this 2 do, but still
    time_elapsed = time.time()
    last_call_time = time.time()
    text = ""
    male_docs_number = None
    female_docs_number = None
