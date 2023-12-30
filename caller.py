# start call
# sabih's twilio code, this initiates the call. This has to be copied on a local ide then ran, because while the flask server above is running, no other code block can run on google collab.

# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse, Play
import requests

# Set environment variables for your credentials
# Read more at http://twil.io/secure

# for sabihs twilio account, can only call his number
#account_sid = "ACea117aecf23c9f2b46b7b8f49c651e19"
#auth_token = "c60276d30d75c8407890e5da9a7b8c7d"

# for raghavs twilio account, can only call his number
account_sid = "ACea117aecf23c9f2b46b7b8f49c651e19"
auth_token = "c60276d30d75c8407890e5da9a7b8c7d"
client = Client(account_sid, auth_token)

response = VoiceResponse()
ngrok_url = "https://069c-72-141-93-40.ngrok-free.app/"

gather = Gather(
                input='speech',
                # below is transcription after every person stops talking for at least 5 seconds
                action=f'{ngrok_url}detect_nav_menu',
                # below is realtime transcription after every word said
                partial_result_callback=f'{ngrok_url}detect_nav_menu_realtime_transcription',
                timeout=3)
gather.say("Hello my dear")
# gather.append(Play('https://handler.twilio.com/twiml/EHfbb431b89ccc9f7c0bb61cedc51208c8'))
response.append(gather)

# response = requests.get(f'{ngrok_url}/nav_menu_result')
# data = response.json()

# print(data['is_human'], data['press_key'])

# response.record(transcribe=True,
# transcribe_callback=f'{ngrok_url}/detectNavMenu')

call = client.calls.create(
  # sabihs number, change to raghavs number if using raghavs twilio account
  to="+12894007562",
  from_="+16137045634",
  timeout=30,
  twiml=str(response)
)

call_sid = call.sid

# pass onto flask endpoint for asking introduction question

# pass onto flask endpoint for asking gender question

print(call.sid)

# call using twilio
# if there is a navigation menu, get to reception
# say initial voice prompt, add press 4 to repeat
# ask if any female doctor,