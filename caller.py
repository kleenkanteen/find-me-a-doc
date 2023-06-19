# sabih's twilio code

# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse, Play

# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = "ACea117aecf23c9f2b46b7b8f49c651e19"
auth_token = "c60276d30d75c8407890e5da9a7b8c7d"
client = Client(account_sid, auth_token)

response = VoiceResponse()
ngrok_url = "https://aa85-34-138-153-128.ngrok-free.app"

# response.say("hello whats up my nigga")

gather = Gather(
                input='speech',
                action=f'{ngrok_url}/detectNavMenu',
                partial_result_callback=f'{ngrok_url}/detectNavMenuRealtimeTranscription',
                timeout=3)
gather.say("give me all of your money")
# gather.append(Play('https://handler.twilio.com/twiml/EHfbb431b89ccc9f7c0bb61cedc51208c8'))
response.append(gather)
# response.record(transcribe=True, 
# transcribe_callback=f'{ngrok_url}/detectNavMenu')

call = client.calls.create(
  to="+12894007562",
  from_="+16474944892",
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