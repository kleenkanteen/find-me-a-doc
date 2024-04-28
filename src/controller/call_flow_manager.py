from flask import request, Blueprint
from twilio.twiml.voice_response import VoiceResponse, Gather

from util.logger import logger
import services.calls.active_call_methods as call_methods
import config.active_call_values as call_values

import os

call_flow_manager = Blueprint("call_flow_manager", __name__, url_prefix="/call")

public_url = os.environ.get("NGROK_URL")

@call_flow_manager.route("/intro_message/<int:clinic_id>", methods=["GET", "POST"])
def intro_message(clinic_id: int):

  prompt_retry_count = int(request.args.get('prompt_retry_count', 0))
  #For some reason invalid_value_count is 1 behind, so it's set to 1 instead o 0
  invalid_input_count = int(request.args.get('invalid_value_count', 1))
  timeouts_count = int(request.args.get('timeouts_count', 0))

  logger.info(f"prompt retrys count: {prompt_retry_count}")
  logger.info(f"invalid key count: {invalid_input_count}")
  logger.info(f"timeouts count: {timeouts_count}")

  max_count = max(prompt_retry_count, timeouts_count, invalid_input_count)
  if max_count > call_values.ENDPOINT_HIT_LIMIT:
    return call_methods.handle_endpoint_limits(clinic_id)
   
  print("Intro Message")

  action_url = f'{public_url}/call/handle_intro_message_response/{clinic_id}?prompt_retry_count={prompt_retry_count}&timeouts_count={timeouts_count}&invalid_input_count={invalid_input_count}'

  gather = Gather(
                 action=action_url,
                 timeout=call_values.timeout,
                 num_digits=1
                )
  
  response = VoiceResponse()

  if prompt_retry_count >= call_values.ENDPOINT_HIT_LIMIT:
    gather.say("Hello, I am a robocaller created to gather data on family doctor's accepting patients for public use. I only have 2 questions. The first is, are any family doctors accepting patients? Press 1 for yes or 2 for no")

  else:
     gather.say("Hello, I am a robocaller created to gather data on family doctor's accepting patients for public use. I only have 2 questions. The first is, are any family doctors accepting patients? Press 1 for yes, 2 for no, or 3 to repeat this message")
  response.append(gather)

  #Redirect user in a loop if no option is selected
  new_timeouts_count = timeouts_count + 1
  response.redirect(f'{public_url}/call/intro_message/{clinic_id}?prompt_retry_count={prompt_retry_count}&timeouts_count={new_timeouts_count}&invalid_input_count={invalid_input_count}')

  return str(response)

@call_flow_manager.route("/handle_intro_message_response/<int:clinic_id>", methods=['POST', 'GET'])
def handle_intro_message_response(clinic_id: int):

  prompt_retry_count = int(request.args.get('prompt_retry_count', 0))
  invalid_input_count = int(request.args.get('invalid_value_count', 1))
  timeouts_count = int(request.args.get('timeouts_count', 1))

  response = VoiceResponse()

  logger.info(f"timeouts count: {timeouts_count}")
  logger.info(f"invalid key count: {invalid_input_count}")
  logger.info(f"prompt retrys count: {prompt_retry_count}")

  if 'Digits' in request.values:
      choice = request.values['Digits']
      if choice == '1':

        redirect_response = VoiceResponse()
        redirect_response.redirect(f"{public_url}/call/ask_male_doctors_number/{clinic_id}", method="GET")
        return str(redirect_response)

      if choice == '2':
        return call_methods.outro_message()
      
      if choice == '3':
        new_prompt_retry_count = prompt_retry_count + 1
        url = f'{public_url}/call/intro_message/{clinic_id}?prompt_retry_count={new_prompt_retry_count}&timeouts_count={timeouts_count}&invalid_input_count={invalid_input_count}'
        response.redirect(url, method="POST")
        return str(response)
      
      else:
         new_invalid_input_count = invalid_input_count + 1

         if prompt_retry_count >= 3:
          message = "You can only enter 1 for yes, or 2 for no"
         else:
          message = "You can only enter 1 for yes, 2 for no, or 3 to listen to the introduction again"

         return call_methods.handle_unrecognizable_response(f"call/handle_intro_message_response/{clinic_id}?prompt_retry_count={prompt_retry_count}&timeouts_count={timeouts_count}&invalid_input_count={new_invalid_input_count}", message, num_digits=1)
      
@call_flow_manager.get("/ask_male_doctors_number/<int:clinic_id>")
def ask_male_doctors_number(clinic_id: int):

  timeouts_count = int(request.args.get('timeouts_count', 0))

  logger.info(f'timeouts_count when asking male doctors number: {timeouts_count}')

  if timeouts_count > call_values.ENDPOINT_HIT_LIMIT:
    return call_methods.handle_endpoint_limits(clinic_id)

  gather = Gather(
          action=f'{public_url}/call/handle_number_male_doctors_response/{clinic_id}',
          timeout=call_values.timeout,
          num_digits=2,
          )
  if timeouts_count == 0:
    gather.say(f"I see. How many of the available doctors are male? Please type the number on your keypad.")
  else:
    gather.say(f"How many of the available doctors are male? Please type the number on your keypad.")

  response = VoiceResponse()
  response.append(gather)

  new_timeouts_count = timeouts_count + 1
  response.redirect(f'{public_url}/call/ask_male_doctors_number/{clinic_id}?timeouts_count={new_timeouts_count}', method="GET")
  return str(response)

     
@call_flow_manager.route("/handle_number_male_doctors_response/<int:clinic_id>", methods=['POST', 'GET'])
def handle_number_male_doctors_response(clinic_id: int):

  invalid_input_count = int(request.args.get('invalid_input_count', 1))

  logger.info(f'invalid_input_count when asking male doctors number: {invalid_input_count}')

  if invalid_input_count > call_values.ENDPOINT_HIT_LIMIT:
    return call_methods.handle_endpoint_limits(clinic_id)

  if 'Digits' in request.values:
    
    response = VoiceResponse()

    try:
      call_values.num_male_docs = int(request.values['Digits'])
      logger.info(f"male doctors: {call_values.num_male_docs}")

      response.redirect(f'{public_url}/call/ask_female_doctors_number/{clinic_id}', method='GET')
      return str(response)
    
    except (ValueError, TypeError) as e:
       new_invalid_input_count = invalid_input_count + 1
       logger.error(f"type error exception thrown. error message: {e}")
       message="Please try again, enter numeric values only"
       return call_methods.handle_unrecognizable_response(f'/call/handle_number_male_doctors_response/{clinic_id}?invalid_input_count={new_invalid_input_count}', message, num_digits=2)

  else:
    message = "I'm sorry, I didn't get that. Could you type the number on your keypad?"
    logger.critical("Attribute 'Digits' doesn't exist in request values")

    new_invalid_input_count = invalid_input_count + 1
    return call_methods.handle_unrecognizable_response(f"/call/handle_intro_response/{clinic_id}?invalid_input_count={new_invalid_input_count}", message, num_digits=2)

@call_flow_manager.get("ask_female_doctors_number/<int:clinic_id>")
def ask_female_doctors_number(clinic_id: int):


  timeouts_count = int(request.args.get('timeouts_count', 0))

  logger.info(f'timeouts_count when asking female doctors number: {timeouts_count}')

  if timeouts_count > call_values.ENDPOINT_HIT_LIMIT:
    return call_methods.handle_endpoint_limits(clinic_id)

  gather = Gather(
          action=f'{public_url}/call/handle_female_doctors_number/{clinic_id}',
          timeout=call_values.timeout,
          num_digits=2,
          )
  
  if timeouts_count == 0:
    gather.say(f"I see. How many of the available doctors are female? Please type the number on your keypad.")
  else:
    gather.say(f"How many of the available doctors are female? Please type the number on your keypad.")

  response = VoiceResponse()
  response.append(gather)

  new_timeouts_count = timeouts_count + 1
  response.redirect(f'{public_url}/call/ask_female_doctors_number/{clinic_id}?timeouts_count={new_timeouts_count}', method='GET')
  return str(response)


@call_flow_manager.route("/handle_female_doctors_number/<int:clinic_id>", methods=['GET', 'POST'])
def handle_number_female_doctors_response(clinic_id: int):

  invalid_input_count = int(request.args.get('invalid_input_count', 1))

  logger.info(f'invalid_input_count when asking female doctors number: {invalid_input_count}')

  if invalid_input_count > call_values.ENDPOINT_HIT_LIMIT:
    return call_methods.handle_endpoint_limits(clinic_id)
   
  if 'Digits' in request.values:
     
     try:
      call_values.num_female_docs = int(request.values['Digits'])
      logger.info(f"female doctors: {call_values.num_female_docs}")

     except (ValueError, TypeError) as e:
      new_invalid_input_count = invalid_input_count + 1
      logger.error(f"type error exception thrown. error message: {e}")
      message="Please try again, enter numeric values only"
      return call_methods.handle_unrecognizable_response(f'/call/handle_female_doctors_number/{clinic_id}?invalid_input_count={new_invalid_input_count}', message, num_digits=2)

  else:
     message = "I'm sorry, I didn't get that. Could you type the number on your keypad?"
     logger.critical("Attribute 'Digits' doesn't exist in request.values")
     return call_methods.handle_unrecognizable_response(f"/call/ask_female_doctors_number/{clinic_id}?invalid_input_count={invalid_input_count}", message, num_digits=2)
  
  return call_methods.handle_successful_call(clinic_id)