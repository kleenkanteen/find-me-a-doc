from flask import Flask
from pyngrok import ngrok
from flask import request
from twilio.twiml.voice_response import VoiceResponse, Gather
import time, re, os
import threading
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

port_no = 5000
app = Flask(__name__)
ngrok.set_auth_token("2QNcZlJxo2W7BBC0lOxTONHpPy5_7eZrvDxtjyt6RMUJztGw7")
public_url =  ngrok.connect(port_no).public_url
os.environ["NGROK_URL"] = public_url
print(f"ngrok link: {public_url}")
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

def play_intro_message():
  response = VoiceResponse()
  print("Intro Message")
  gather = Gather(
                input='speech',
                # below is transcription after every person stops talking for at least 5 seconds
                action=f'{public_url}/handle_intro_response',
                # below is realtime transcription after every word said
                timeout=3)
  gather.say("Hello, I am a robocaller created to gather data on family doctor's accepting patients for public use. I only have 2 questions. The first is, are any family doctors accepting patients? Please reply with yes or no.")
  response.append(gather)
  return str(response)

@app.route("/handle_intro_response", methods=['GET', 'POST'])
def handle_intro_response():
  full_response = request.form.get('SpeechResult', '').lower()
  if full_response == "no":
    return outro_message()
  elif full_response == "yes":
    response = VoiceResponse()
    gather = Gather(
                input='speech',
                # below is transcription after every person stops talking for at least 5 seconds
                action=f'{public_url}/handle_intro_response',
                # below is realtime transcription after every word said
                partial_result_callback=f'{public_url}detect_nav_menu_realtime_transcription',
                timeout=3)
    gather.say(f"I see. How many of these available doctors are male? Please answer with just a number.")
    response.append(gather)
    return str(response)

@app.route("/handle_number_male_doctors_response", methods=['GET', 'POST'])
def handle_number_male_doctors_response():
  full_response = request.form.get('SpeechResult', '').lower()
  global num_male_docs
  try:
      num_male_docs = int(full_response)
  except ValueError:
      number_dict = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
      num_male_docs = number_dict[full_response]
  return outro_message()
  
@app.route("/handle_robot", methods=['GET', 'POST'])
def handle_robot():
  response = VoiceResponse()
  global key
  print("handle robot")
  print(f"You are a robot and you said to press {key}")
  response.say(f"You are a robot and you said to press {key}")
  return str(response)

@app.route("/detect_nav_menu", methods=['GET', 'POST'])
def handleRecordingOriginal():
    global response
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
      return play_intro_message()
    else:
      # Robot Detected
      print("robot detected")
      return handle_robot()
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

def outro_message():
  response = VoiceResponse()
  response.say(f"I see, thank you for your time, goodbye.")
  return str(response)

app.run(port=port_no)