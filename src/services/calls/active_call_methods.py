import re, os, time
from dotenv import load_dotenv
from urllib.parse import urlparse, urlencode, parse_qs
from util.logger import logger

from twilio.twiml.voice_response import VoiceResponse, Gather
from services.db.database_manager import update_db_on_successful_call, update_db_on_failed_call

from config.active_call_values import timeout
import config.active_call_values as call_values
import services.calls.active_call_methods as call_methods

load_dotenv(override=True)

public_url = os.environ.get("NGROK_URL")

def outro_message():
  response = VoiceResponse()
  response.say(f"Thank you for your time. Feel free to explore our mission at find me a doc dot c a. Goodbye!")
  return str(response)

def handle_unrecognizable_response(path: str, message: str, num_digits: int):
  response = VoiceResponse()

  logger.warning(f"\nresponse not understood on path: {path}\n")

  gather = Gather(    
     action=f"{public_url}/{path}",
     timeout=timeout,
     num_digits=num_digits
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

def handle_endpoint_limits(clinic_id: int):
   response = VoiceResponse()
   response.say("The maximum amount of retries has been reached. Feel free to explore our mission at find me a doc dot c a. Goodbye!")
   response.hangup()

   handle_failed_call(clinic_id)

   return str(response)

def handle_successful_call(clinic_id):
   import config.active_call_values as call_values

   call_values.intro_message_iterations = 0

   available_female_docs = call_values.num_female_docs
   available_male_docs = call_values.num_male_docs

   logger.debug(f"call was a success, male docs: {call_values.num_male_docs}, female docs: {call_values.num_female_docs}")

   response = update_db_on_successful_call(clinic_id, available_male_docs, available_female_docs)

   logger.debug(f"clinic id: {clinic_id}. new clinic data in db: {response}")

   call_values.reset_call_values()

   return outro_message()

def handle_failed_call(clinic_id: int):

  male_doctors_available = call_values.num_male_docs
  female_doctors_available = call_values.num_female_docs

  response = update_db_on_failed_call(clinic_id, male_doctors_available, female_doctors_available)

  call_values.reset_call_values()

  logger.debug(f"partial db update: {response}")   