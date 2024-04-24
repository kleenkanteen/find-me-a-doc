from flask import request, Blueprint
from twilio.twiml.voice_response import VoiceResponse, Gather, Parameter
import time, os
from dotenv import load_dotenv
from main.util.logger import logger
import main.services.calls.active_call_methods as call_methods
import main.config.active_call_values as call_values

call_flow_manager = Blueprint("call_flow_manager", __name__, url_prefix="/call")

public_url = os.environ.get("NGROK_URL")

@call_flow_manager.route("/detect_nav_menu/<int:clinic_id>", methods=['GET', 'POST'])
def handleRecordingOriginal(clinic_id: int):
    
    call_values.listening = False
    print("detectNavMenu")
    full_response = request.form.get('SpeechResult', '').lower()
    print(f"isHuman? {call_values.isHuman}")
    if call_values.isHuman:
      #Human Detected
      print("human detected")
      return call_methods.play_intro_message(clinic_id)
    else:
      # Robot Detected
      print("robot detected")
      return handle_robot()

@call_flow_manager.route("/handle_intro_response/<int:clinic_id>", methods=['GET', 'POST'])
def handle_intro_response(clinic_id: int):

  full_response = request.form.get('SpeechResult', '').lower()
  logger.debug(f"intro response: {full_response}")
  if 'no' in full_response:
    return call_methods.outro_message()
  elif 'yes' in full_response:
    response = VoiceResponse()
    gather = Gather(
                input='speech',
                action=f'{public_url}/call/handle_number_male_doctors_response/{clinic_id}',
                partial_result_callback=f'{public_url}/call/detect_nav_menu_realtime_transcription/{clinic_id}',
                timeout=call_values.timeout)
    gather.say(f"I see. How many of the available doctors are male? Please reply with just a number")
    response.append(gather)
    return str(response)
  else:
     message = "I'm sorry, I didn't get that. Could you please reply yes or no?"
     logger.warning("Unrecognizable speech at intro response")
     return call_methods.handle_unrecognizable_speech_response(f"/call/handle_intro_response/{clinic_id}", message)

@call_flow_manager.route("/handle_number_male_doctors_response/<int:clinic_id>", methods=['GET', 'POST'])
def handle_number_male_doctors_response(clinic_id: int):

  gather = Gather(
     input="speech",
     partial_result_callback=f'{public_url}/call/detect_nav_menu_realtime_transcription/{clinic_id}',
     action=f'{public_url}/call/handle_number_female_doctors_response/{clinic_id}',
     timeout=call_values.timeout
  )
  response = VoiceResponse()

  speech_result = request.form.get('SpeechResult', '').lower()

  try:
      num_male_docs = int(speech_result)
      logger.debug(f"male doctors: {num_male_docs}")

      call_values.num_male_docs = num_male_docs
         
  except ValueError:
      try:
         number_dict = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten":10}
         call_values.num_male_docs = number_dict[speech_result]
      except KeyError:
        logger.warning("Unrecognizable speech at male response")
        message = "I'm sorry, I didn't get that. Could you say that again?"
        return call_methods.handle_unrecognizable_speech_response(f"/call/handle_number_male_doctors_response/{clinic_id}", message)
  
  gather.say(f"And how many are female? Please answer with just a number")
  response.append(gather)
  return str(response)

@call_flow_manager.route("/handle_number_female_doctors_response/<int:clinic_id>", methods=['GET', 'POST'])
def handle_number_female_doctors_response(clinic_id: int):

  speech_result = request.form.get('SpeechResult', '').lower()

  try:

    num_female_docs = int(speech_result)
    logger.debug(f"female doctors: {num_female_docs}")

    call_values.num_female_docs = num_female_docs
      
  except ValueError:
      try:
         number_dict = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten":10}
         call_values.num_female_docs = number_dict[speech_result]

      except KeyError:
          logger.warning("Unrecognizable speech at female response")
          message = "I'm sorry, I didn't get that. Could you say that again?"
          return call_methods.handle_unrecognizable_speech_response(f"/call/handle_number_female_doctors_response/{clinic_id}", message)

  return call_methods.handle_successful_call(clinic_id)
  
@call_flow_manager.route("/handle_robot/<int:clinic_id>", methods=['GET', 'POST'])
def handle_robot(clinic_id: int):

  response = VoiceResponse()

  print("handle robot")
  print(f"You are a robot and you said to press {call_values.key}")

  response.say(f"You are a robot and you said to press {call_values.key}")
  return str(response)


@call_flow_manager.route("/detect_nav_menu_realtime_transcription/<int:clinic_id>", methods=['GET', 'POST'])
def handleRecording(clinic_id: int):
    
    call_values.last_call_time = time.time()
    call_values.listening = True

    text = request.form.get('UnstableSpeechResult', '').lower()
    logger.debug(f"Unstable speech result: {text}")

    call_methods.processResponse()
    print(f"isHuman?: {call_values.isHuman}")
    return "", 200