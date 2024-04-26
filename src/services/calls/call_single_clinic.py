from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse
import os
from dotenv import load_dotenv;
from util.logger import logger

load_dotenv()
TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
#For TESTING, uncomment line below
  #PERSONAL_NUMBER = os.environ.get("PERSONAL_NUMBER")
ngrok_url = os.environ.get("NGROK_URL")

def make_call(phone_number: str, clinic_id: int):

  logger.debug(f"received phone number: {phone_number} \n received clinic id: {clinic_id}")

  #For TESTING, uncomment next 3 lines belows
    # if(phone_number != PERSONAL_NUMBER):
    #   logger.critical("PERSONAL_NUMBER does not equal given phone_number from args")
    #   raise ValueError("PERSONAL_NUMBER does not equal given phone_number from args")

  client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

  response = VoiceResponse()
  print("NGROK URL: ", ngrok_url)
  gather = Gather(
                  timeout=10
                )
  response.append(gather)
  response.redirect(f"{ngrok_url}/call/detect_nav_menu/{clinic_id}")

  call = client.calls.create(
    #For TESTING, uncomment line below
      # to=f"+1{PERSONAL_NUMBER}",
    #For PRODUCTION, uncomment line below
      # to=f"+1{phone_number}",
    from_=f"+{TWILIO_NUMBER}",
    timeout=30,
    twiml=str(response)
  )

  return call.sid