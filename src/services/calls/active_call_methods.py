import re, os, time
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
from util.logger import logger
from services.db.database_manager import update_db_on_successful_call, update_db_on_failed_call
from config.active_call_values import timeout

import config.active_call_values as call_values

load_dotenv(override=True)

public_url = os.environ.get("NGROK_URL")

def play_intro_message(client_id: int):
  response = VoiceResponse()
  print("Intro Message")
  gather = Gather(
                input='speech',
                # below is transcription after every person stops talking for at least 5 seconds
                action=f'{public_url}/call/handle_intro_response/{client_id}',
                # below is realtime transcription after every word said
                timeout=timeout)
  gather.say("Hello, I am a robocaller created to gather data on family doctor's accepting patients for public use. I only have 2 questions. The first is, are any family doctors accepting patients? Please reply with yes or no.")
  response.append(gather)
  return str(response)

def outro_message():
  response = VoiceResponse()
  response.say(f"Thank you for your time. Feel free to explore our mission at find me a doc dot c a. Goodbye!")
  return str(response)

def handle_unrecognizable_speech_response(destination_path: str, message: str):
  response = VoiceResponse()
  logger.warning("response not understood")

  gather = Gather(
     input='speech',
     action=f'{public_url}/{destination_path}',
     timeout=timeout
  )

  gather.say(message)
  response.append(gather)

  return str(response)

def processResponse():
  if 'press' in call_values.text:
        isHuman = False
        # Perform actions if the word "press" is present in the transcription
        call_values.text.replace('deception', 'reception')
        if call_values.text.find('reception') < 0:
          logger.warning("issue, reception < 0")
        substring = call_values.text[call_values.text.find('reception'):]
        reg = re.search(r"(?:\d|zero)", substring)
        if reg:
          call_values.key = substring[reg.start()]
          print(f"press key: {call_values.key}")
          if key == "z":
            key = "0"
        else:
          print("No digit in that string")
  else:
      print("human")
      #isHuman = True

def check_elapsed_time():
    global last_call_time
    global listening
    global time_elapsed
    while True:
        time_elapsed = time.time() - last_call_time
        if listening and time_elapsed >= 1.0:
          print("break detected in speech, processing")
          processResponse()

def handle_successful_call(clinic_id):
   import src.config.active_call_values as call_values

   available_female_docs = call_values.num_female_docs
   available_male_docs = call_values.num_male_docs

   logger.debug(f"call was a success, male docs: {call_values.num_male_docs}, female docs: {call_values.num_female_docs}")

   response = update_db_on_successful_call(clinic_id, available_male_docs, available_female_docs)

   logger.debug(f"new clinic data in db: {response}")

   return outro_message()

def handle_failed_call(clinic_id: int):

  response = update_db_on_failed_call(clinic_id)

  logger.debug(f"Response: {response}")