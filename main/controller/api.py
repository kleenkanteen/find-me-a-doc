from flask import Flask, jsonify, request, Blueprint
from pyngrok import ngrok
from twilio.twiml.voice_response import VoiceResponse, Gather
import time, re, os
from dotenv import load_dotenv

import main.services.active_call_methods as call
import main.config.active_call_values as call_values

load_dotenv()
public_url = os.environ.get("NGROK_URL")

api = Blueprint("api", __name__, url_prefix="/")

# @api.get("/test")
# def test():
#    return os.environ.get("NGROK_URL")

@api.route("/detect_nav_menu", methods=['GET', 'POST'])
def handleRecordingOriginal():
    call_values.listening = False
    print("detectNavMenu")
    full_response = request.form.get('SpeechResult', '').lower()
    print("isHuman", call_values.isHuman)
    if call_values.isHuman:
      #Human Detected
      print("human detected")
      return call.play_intro_message()
    else:
      # Robot Detected
      print("robot detected")
      return handle_robot()

@api.route("/handle_intro_response", methods=['GET', 'POST'])
def handle_intro_response():
  print("HANDLE INTRO RESPONSE FORM: ", request.form);
  full_response = request.form.get('SpeechResult', '').lower()
  if 'no' in full_response:
    return call.outro_message()
  elif 'yes' in full_response:
    response = VoiceResponse()
    gather = Gather(
                input='speech',
                # below is transcription after every person stops talking for at least 5 seconds
                action=f'{public_url}/handle_number_male_doctors_response',
                # below is realtime transcription after every word said
                partial_result_callback=f'{public_url}/detect_nav_menu_realtime_transcription',
                timeout=call_values.timeout)
    gather.say(f"I see. How many of these available doctors are male? Please answer with just a number")
    response.append(gather)
    return str(response)
  else:
     message = "I'm sorry, I didn't get that. Could you say that again? Please reply with a yes or no"
     return call.handle_unrecognizable_speech_response("/handle_intro_response", message)


@api.route("/handle_number_male_doctors_response", methods=['GET', 'POST'])
def handle_number_male_doctors_response():

  gather = Gather(
     input="speech",
     action=f'{public_url}/handle_number_female_doctors_response',
     timeout=call_values.timeout
  )

  full_response = request.form.get('SpeechResult', '').lower()

  
  response = VoiceResponse()

  if 'many' in full_response:
    call_values.num_male_docs = 999

  try:
      num_male_docs = int(full_response)

      if (type(num_male_docs) == int) and num_male_docs > 10:
         call_values.num_male_docs = 999
      else: 
        call_values.num_male_docs = num_male_docs
         
  except ValueError:
      try:
         number_dict = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten":10}
         call_values.num_male_docs = number_dict[full_response]
      except KeyError:
        message = "I'm sorry, I didn't get that. Could you say that again? If there are more than 10 available male doctors say many"
        return call.handle_unrecognizable_speech_response("/handle_number_male_doctors_response", message)
  
  gather.say(f"I see. And how many are female? Please answer with just a number")
  response.append(gather)
  return str(response)
  

@api.route("/handle_number_female_doctors_response", methods=['GET', 'POST'])
def handle_number_female_doctors_response():
  full_response = request.form.get('SpeechResult', '').lower()
  print("HANDLE NUMBER OF FEMALE DOCTORS RESPONSE, form: ", request.form) 
  try:

    num_female_docs = int(full_response)

    if (type(num_female_docs) == int) and num_female_docs > 10:
      call_values.num_female_docs = 999
    else: 
      call_values.num_female_docs = num_female_docs
      
  except ValueError:
      try:
         number_dict = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten":10}
         call_values.num_female_docs = number_dict[full_response]

      except KeyError:
          message = "I'm sorry, I didn't get that. Could you say that again? If there are more than 10 available female doctors say many"
          return call.handle_unrecognizable_speech_response("/handle_number_female_doctors_response", message)

  return call.on_call_success()
  
@api.route("/handle_robot", methods=['GET', 'POST'])
def handle_robot():
  response = VoiceResponse()
  print("handle robot")
  print(f"You are a robot and you said to press {call_values.key}")
  response.say(f"You are a robot and you said to press {call_values.key}")
  return str(response)

@api.route("/detect_nav_menu_realtime_transcription", methods=['GET', 'POST'])
def handleRecording():
    print(f"\npost form data = {request.form}")
       
    call_values.last_call_time = time.time()
    call_values.listening = True

    text = request.form.get('UnstableSpeechResult', '').lower()
    print(text)
    call.processResponse()
    print("isHuman", call_values.isHuman)
    return "", 200

   