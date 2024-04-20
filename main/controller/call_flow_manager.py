from flask import request, Blueprint
from twilio.twiml.voice_response import VoiceResponse, Gather
import time, os
from dotenv import load_dotenv
from main.util.logger import logger

import main.services.active_call_methods as call_methods
import main.config.active_call_values as call_values

load_dotenv()
public_url = os.environ.get("NGROK_URL")

call_flow_manager = Blueprint("call_flow_manager", __name__, url_prefix="/call")

@call_flow_manager.route("/detect_nav_menu", methods=['GET', 'POST'])
def handleRecordingOriginal():
    call_values.listening = False
    print("detectNavMenu")
    full_response = request.form.get('SpeechResult', '').lower()
    print(f"isHuman? {call_values.isHuman}")
    if call_values.isHuman:
      #Human Detected
      print("human detected")
      return call_methods.play_intro_message()
    else:
      # Robot Detected
      print("robot detected")
      return handle_robot()

@call_flow_manager.route("/handle_intro_response", methods=['GET', 'POST'])
def handle_intro_response():
  full_response = request.form.get('SpeechResult', '').lower()
  logger.debug(f"intro response: {full_response}")
  if 'no' in full_response:
    return call_methods.outro_message()
  elif 'yes' in full_response:
    response = VoiceResponse()
    gather = Gather(
                input='speech',
                # below is transcription after every person stops talking for at least 5 seconds
                action=f'{public_url}/call/handle_number_male_doctors_response',
                # below is realtime transcription after every word said
                partial_result_callback=f'{public_url}/call/detect_nav_menu_realtime_transcription',
                timeout=call_values.timeout)
    gather.say(f"I see. How many of the available doctors are male? Please reply with just a number")
    response.append(gather)
    return str(response)
  else:
     message = "I'm sorry, I didn't get that. Could you please reply yes or no?"
     logger.warning("Unrecognizable speech at intro response")
     return call_methods.handle_unrecognizable_speech_response("/call/handle_intro_response", message)

@call_flow_manager.route("/handle_number_male_doctors_response", methods=['GET', 'POST'])
def handle_number_male_doctors_response():

  gather = Gather(
     input="speech",
     action=f'{public_url}/call/handle_number_female_doctors_response',
     timeout=call_values.timeout
  )
  response = VoiceResponse()

  full_response = request.form.get('SpeechResult', '').lower()

  if 'many' in full_response:
    call_values.num_male_docs = 999

  try:
      num_male_docs = int(full_response)
      logger.debug(f"male doctors: {num_male_docs}")

      call_values.num_male_docs = num_male_docs
         
  except ValueError:
      try:
         number_dict = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten":10}
         call_values.num_male_docs = number_dict[full_response]
      except KeyError:
        logger.warning("Unrecognizable speech at male response")
        message = "I'm sorry, I didn't get that. Could you say that again? If there are more than 10 available male doctors say many"
        return call_methods.handle_unrecognizable_speech_response("/call/handle_number_male_doctors_response", message)
  
  gather.say(f"And how many are female? Please answer with just a number")
  response.append(gather)
  return str(response)

@call_flow_manager.route("/handle_number_female_doctors_response", methods=['GET', 'POST'])
def handle_number_female_doctors_response():

  full_response = request.form.get('SpeechResult', '').lower()

  if 'many' in full_response:
    call_values.num_male_docs = 999

  try:

    num_female_docs = int(full_response)
    logger.debug(f"female doctors: {num_female_docs}")

    call_values.num_female_docs = num_female_docs
      
  except ValueError:
      try:
         number_dict = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten":10}
         call_values.num_female_docs = number_dict[full_response]

      except KeyError:
          logger.warning("Unrecognizable speech at female response")
          message = "I'm sorry, I didn't get that. Could you say that again? If there are more than 10 available female doctors say many"
          return call_methods.handle_unrecognizable_speech_response("/call/handle_number_female_doctors_response", message)

  return call_methods.on_call_success()
  
@call_flow_manager.route("/handle_robot", methods=['GET', 'POST'])
def handle_robot():
  response = VoiceResponse()

  print("handle robot")
  print(f"You are a robot and you said to press {call_values.key}")

  response.say(f"You are a robot and you said to press {call_values.key}")
  return str(response)

@call_flow_manager.route("/call/detect_nav_menu_realtime_transcription", methods=['GET', 'POST'])
def handleRecording():
       
    call_values.last_call_time = time.time()
    call_values.listening = True

    text = request.form.get('UnstableSpeechResult', '').lower()
    print(f"Unstable speech result: {text}")

    call_methods.processResponse()
    print(f"isHuman?: {call_values.isHuman}")
    return "", 200

   