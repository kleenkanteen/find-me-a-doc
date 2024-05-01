from dotenv import load_dotenv
import os, threading, time, queue, sys

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from services.calls.call_single_clinic import make_call
from services.db.database_manager import update_call_final_status, get_clinics_info
from .active_call_methods import get_call_data

from util.logger import logger
from util.date import has_passed_30_days_since
import config.active_call_values as call_values
from .active_call_methods import handle_failed_call

import inquirer
from inquirer.themes import GreenPassion

load_dotenv(override=True)
NGROK_URL = os.environ.get("NGROK_URL")
TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def is_due_for_call(clinic):
    # Checks if a clinic is due for a call based on last call success or elapsed days.
    last_call_success = clinic["last_call_success"]
    last_call_date = clinic["last_call_date"]
    last_call_was_a_month_ago = has_passed_30_days_since(last_call_date)

    return not last_call_success or last_call_was_a_month_ago


def check_call_status(queue, call_sid):

    while True:

        time.sleep(5)

        call_data = get_call_data(call_sid)
        call_status = call_data["status"]

        # Possible values: queued, ringing, in-progress, busy, completed, failed, no-answer, canceled
        if call_status in ["completed", "failed", "no-answer", "canceled", "busy"]:
            queue.put({"call_status": call_status, "call_data": call_data})
            logger.info(f"final call status is: '{call_status}'")
            break


def call_all_clinics():

    mode: str = os.environ.get("MODE")
    PERSONAL_NUMBER = os.environ.get("PERSONAL_NUMBER")
    MOCK_CLINIC_ID = os.environ.get("MOCK_CLINIC_ID")

    if mode == "PROD":
        data = get_clinics_info()
        raw_clinics = data[1]
        due_clinics = filter(is_due_for_call, raw_clinics)

    # mock list of clinics you can call for testing, i.e. yourself
    if mode == "DEV":
        due_clinics = [{"id": MOCK_CLINIC_ID, "phone_number": PERSONAL_NUMBER}]

    for clinic in due_clinics:

        clinic_id = clinic["id"]

        try:
            clinic_sid = make_call(clinic["phone_number"], clinic_id)
        except TwilioRestException as e:
            logger.error(f"Twilio error, message: {e}")

        logger.debug(f"Call started...sid: {clinic_sid}")

        q = queue.Queue()

        call_status_poller = threading.Thread(
            target=check_call_status, args=(q, clinic_sid)
        )
        call_status_poller.start()
        call_status_poller.join()

        result = q.get()

        call_status = result["call_status"]

        update_call_final_status(clinic["id"], call_status)

        # If user hangs up, call status is marked as completed without any http response.
        # Hence the check for None in either value
        if call_status == "completed" and (
            call_values.male_docs_number is None
            or call_values.female_docs_number is None
        ):
            handle_failed_call(clinic_id)

        # Reset all call values after each call
        call_values.reset_call_values()

        if clinic["id"] == due_clinics[-1]["id"]:
            logger.debug("Round of calls done")
            exit()

        questions = [
            inquirer.List(
                "next_clinic",
                message="Call next clinic?",
                choices=["Yes", "No"],
            ),
        ]

        answer = inquirer.prompt(questions, theme=GreenPassion())

        if answer["next_clinic"] == "No":
            logger.debug(f"You chose to stop the program. Exiting program now.")
            sys.exit()
