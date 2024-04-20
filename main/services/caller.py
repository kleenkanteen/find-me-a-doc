from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse
import os, json
from dotenv import load_dotenv;

load_dotenv(override=True)
TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
PERSONAL_NUMBER = os.environ.get("PERSONAL_NUMBER")
ngrok_url = os.environ.get("NGROK_URL")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

response = VoiceResponse()
print("NGROK URL: ", ngrok_url)
gather = Gather(
                # below is transcription after every person stops talking for at least 5 seconds
                # action=f'{ngrok_url}/test',
                # below is realtime transcription after every word said
                partial_result_callback=f'{ngrok_url}/call/detect_nav_menu_realtime_transcription',
                timeout=10
              )
# we can play audio files if we upload them to the twilio console and pass the url of the file
# gather.append(Play('https://handler.twilio.com/twiml/EHfbb431b89ccc9f7c0bb61cedc51208c8'))
response.append(gather)
response.redirect(f"{ngrok_url}/call/detect_nav_menu")
# response = requests.get(f'{ngrok_url}/nav_menu_result')
# data = response.json()

# print(data['is_human'], data['press_key'])

# response.record(transcribe=True,
# transcribe_callback=f'{ngrok_url}/detectNavMenu')

call = client.calls.create(
  # sabihs number, change to raghavs number if using raghavs twilio account
  to=f"+1{PERSONAL_NUMBER}",
  from_=f"+{TWILIO_NUMBER}",
  timeout=30,
  twiml=str(response)
)

call_sid = call.sid
print(call.sid)
