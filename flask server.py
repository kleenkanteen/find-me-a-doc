# Flask server code to receive twilio post requests that contain the transcripted user speech when they respond. Twilio sends us the speech to text transcriptions.

from flask import Flask
from pyngrok import ngrok
from flask import request
from twilio.twiml.voice_response import VoiceResponse
import time, re
import threading

port_no = 5000
app = Flask(__name__)
ngrok.set_auth_token("2QNcZlJxo2W7BBC0lOxTONHpPy5_7eZrvDxtjyt6RMUJztGw7")
public_url =  ngrok.connect(port_no).public_url
response = VoiceResponse()
listening = False
isHuman = True
key = ""
temp_isHuman = isHuman
temp_key = -1
time_elapsed = time.time()
last_call_time = time.time()
text = ""

# when gather ends then check isHuman variable
# either press tocorresponding button or give the response to the human

def processResponse():
  global text
  global isHuman
  global key
  if 'press' in text:
        isHuman = False
        # Perform actions if the word "press" is present in the transcription
        text.replace('deception', 'reception')
        if text.find('reception') < 0:
          print("issue")
        substring = text[text.find('reception'):]
        reg = re.search(r"(?:\d|zero)", substring)
        if reg:
          key = substring[reg.start()]
          print(f"press key: {key}")
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

def nav_menu_press_button():
  print("hello")

def play_intro_message(response):
  print("Intro Message")
  response.say("Intro Message")
  gather = Gather(
                input='speech',
                # below is transcription after every person stops talking for at least 5 seconds
                action=f'{public_url}/handle_intro_response',
                # below is realtime transcription after every word said
                partial_result_callback=f'{ngrok_url}detect_nav_menu_realtime_transcription',
                timeout=5)
  gather.say("give me all of your money")
  response.append(gather)
  return

@app.route("/handle_intro_response", methods=['GET', 'POST'])
def handleRecordingOriginal():

def handle_robot(response, key):
  print("handle robot")
  print(f"You are a robot and you said to press {key}")
  response.say(f"You are a robot and you said to press {key}")
  return

@app.route("/detect_nav_menu", methods=['GET', 'POST'])
def handleRecordingOriginal():
    global response
    response = VoiceResponse()
    global listening
    global isHuman
    global key
    global text
    listening = False
    print("detectNavMenu")
    full_response = request.form.get('SpeechResult', '').lower()
    print("isHuman", isHuman)
    if isHuman:
      #Human Detected
      print("human detected")
      play_intro_message(response)
    else:
      # Robot Detected
      print("robot detected")
      handle_robot(response, key)
    temp_isHuman = isHuman
    temp_key = -1
    if key != "":
      temp_key = int(key)
    key = ""
    text = ""
    isHuman = True
    listening = False
    print(full_response)
    return str(response)

@app.route("/detect_nav_menu_realtime_transcription", methods=['GET', 'POST'])
def handleRecording():
    global last_call_time
    global listening
    global text
    last_call_time = time.time()
    listening = True

    text = request.form.get('UnstableSpeechResult', '').lower()
    print(text)
    processResponse()
    print("isHuman", isHuman)
    return "", 200

print(f"ngrok link: {public_url}")

app.run(port=port_no)