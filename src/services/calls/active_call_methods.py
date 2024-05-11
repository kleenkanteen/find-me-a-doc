import re, os, time
from dotenv import load_dotenv
from util.logger import logger

from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from services.db.database_manager import (
    update_db_on_successful_call,
    update_db_on_failed_call,
)

from config.active_call_values import timeout
import config.active_call_values as call_values
import services.calls.active_call_methods as call_methods

load_dotenv(override=True)

public_url = os.environ.get("NGROK_URL")
TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def outro_message():
    response = VoiceResponse()
    response.play("https://findadoc-7179.twil.io/outro_message.mp3")
    return str(response)


def handle_unrecognizable_response(path: str, message_url: str, num_digits: int):
    response = VoiceResponse()

    logger.warning(f"\nresponse not understood on path: {path}\n")

    gather = Gather(
        action=f"{public_url}/{path}", timeout=timeout, num_digits=num_digits
    )

    response.play(message_url)
    response.append(gather)

    return str(response)


def processResponse():
    if "press" in call_values.text:
        isHuman = False
        # Perform actions if the word "press" is present in the transcription
        call_values.text.replace("deception", "reception")
        if call_values.text.find("reception") < 0:
            logger.warning("issue, reception < 0")
        substring = call_values.text[call_values.text.find("reception") :]
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
        # isHuman = True


def check_elapsed_time():
    global last_call_time
    global listening
    global time_elapsed
    while True:
        time_elapsed = time.time() - last_call_time
        if listening and time_elapsed >= 1.0:
            print("break detected in speech, processing")
            processResponse()


def handle_endpoint_limits(clinic_id: int):
    response = VoiceResponse()
    response.play("https://findadoc-7179.twil.io/maximum_retries_reached.mp3")
    response.hangup()

    handle_failed_call(clinic_id)

    return str(response)


def handle_successful_call(clinic_id):

    logger.debug(
        f"call was a success, male docs: {call_values.male_docs_number} | female docs: {call_values.female_docs_number}"
    )

    # If by any chance either value is not selected, fire failed call handler
    if call_values.male_docs_number is None or call_values.female_docs_number is None:
        return handle_failed_call(clinic_id)

    call_values.intro_message_iterations = 0

    updated_clinic_data = update_db_on_successful_call(
        clinic_id, call_values.male_docs_number, call_values.female_docs_number
    )

    call_data = get_latest_call_data()

    logger.end_of_call_info(
        call_data,
        clinic_name=updated_clinic_data["name"],
        clinic_id=clinic_id,
        male_docs_number=call_values.male_docs_number,
        female_docs_number=call_values.female_docs_number,
        success="true",
    )

    logger.debug(f"successful call, updated full db data: {updated_clinic_data}")

    return outro_message()


def handle_failed_call(clinic_id: int):

    logger.debug(
        f"failed call values: male: {call_values.male_docs_number} | female: {call_values.female_docs_number}"
    )

    updated_clinic_data = update_db_on_failed_call(
        clinic_id, call_values.male_docs_number, call_values.female_docs_number
    )

    call_data = get_latest_call_data()

    logger.end_of_call_info(
        call_data,
        clinic_name=updated_clinic_data["name"],
        clinic_id=clinic_id,
        male_docs_number=call_values.male_docs_number,
        female_docs_number=call_values.female_docs_number,
        success="false",
    )

    logger.debug(f"failed call, db update of doc nums with whatever was gathered: {updated_clinic_data}")


def get_call_data(call_sid):

    # This Twilio client method retrieves call data by SID
    # https://www.twilio.com/docs/voice/tutorials/how-to-retrieve-call-logs/python#retrieve-call-by-id-example
    client_data = client.calls(call_sid).fetch()

    return client_data.__dict__


def get_latest_call_data():

    client_data = client.calls.list(limit=1)[0]

    return client_data.__dict__
