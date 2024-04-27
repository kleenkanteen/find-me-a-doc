import os
from util.logger import logger
from dotenv import load_dotenv

from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse

load_dotenv(override=True)
TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
MODE = os.environ.get("MODE")
PERSONAL_NUMBER = os.environ.get("PERSONAL_NUMBER")
ngrok_url = os.environ.get("NGROK_URL")

def make_call(phone_number: str, clinic_id: int):

  logger.debug(f"received phone number: {phone_number} \n received clinic id: {clinic_id}")

  if MODE == "DEV": 
    if(phone_number != PERSONAL_NUMBER):
      logger.critical("PERSONAL_NUMBER does not equal given phone_number from args")
      raise ValueError("PERSONAL_NUMBER does not equal given phone_number from args")

  client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

  response = VoiceResponse()
  print("NGROK URL: ", ngrok_url)
  gather = Gather(
                  timeout=10
                )
  response.append(gather)
  response.redirect(f"{ngrok_url}/call/detect_nav_menu/{clinic_id}")

  if MODE == "DEV": 
    number_called = PERSONAL_NUMBER
  else: 
    number_called = phone_number

  call = client.calls.create(
    to=f"+1{number_called}",
    from_=f"+1{TWILIO_NUMBER}",
    timeout=30,
    twiml=str(response)
  )

  return call.sid