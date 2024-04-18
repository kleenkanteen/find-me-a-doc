import re, os, time
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

import main.config.active_call_values as call_values

load_dotenv()

public_url = os.environ.get("NGROK_URL")

def test():
   return {
      "success": "success2"
   }

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
  print("GATHER INFO: ", gather)
  return str(response)

def outro_message():
  response = VoiceResponse()
  response.say(f"I see, thank you for your time. Goodbye.")
  return str(response)

def handle_unrecognizable_speech_response(destination_path: str, message: str):
  response = VoiceResponse()
  print("RESPONSE NOT UNDERSTOOD")

  gather = Gather(
     input='speech',
     action=f'{public_url}/{destination_path}',
     timeout=5
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
          print("issue")
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


def on_call_success():
   import main.config.active_call_values as call_values
   print(f"CALL WAS A SUCCESS, male docs: {call_values.num_male_docs}, female docs: {call_values.num_female_docs}")
   return outro_message()