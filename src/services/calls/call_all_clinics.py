from services.calls.call_single_clinic import make_call
from services.db.database_manager import update_call_final_status, get_clinics_info
from dotenv import load_dotenv
from twilio.rest import Client
from util.logger import logger
from util.date import has_passed_30_days_since
from simple_term_menu import TerminalMenu
import os, threading, time, queue, sys

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

        call = client.calls(call_sid).fetch()
        # Possible values: queued, ringing, in-progress, busy, completed, failed, no-answer, canceled
        if call.status in ["completed", "failed", "no-answer", "canceled", "busy"]:
            queue.put(call.status)
            logger.debug(f"final call status is: '{call.status}'")
            break
        time.sleep(5)


def call_all_clinics():

    # for PRODUCTION: uncomment next two lines of code down below
    #   data = get_clinics_info()
    #   raw_clinics = data[1]
    #   due_clinics = filter(is_due_for_call, raw_clinics)

    # for TESTING:
    # 1. Uncomment clinics array of dicts down below
    # 2. Replace the Xs for real ids and phone number in your database.
    #    Ids MUST belong to the same instance of your phone number in the db
    #    otherwise, the code will not run.

    #   due_clinics = [{
    #       "id": "XX",
    #       "phone_number": "(XXX) XXX-XXXX"
    #   },
    #   {
    #       "id": "XX",
    #       "phone_number": "(XXX) XXX-XXXX"
    #   },
    #   {
    #       "id": "XX",
    #       "phone_number": "(XXX) XXX-XXXX"
    #   }

    for clinic in due_clinics:

        clinic_sid = make_call(clinic["phone_number"], clinic["id"])

        logger.debug(f"Call started...sid: {clinic_sid}")

        q = queue.Queue()

        call_status_poller = threading.Thread(
            target=check_call_status, args=(q, clinic_sid)
        )
        call_status_poller.start()
        call_status_poller.join()

        call_status = q.get()

        update_call_final_status(clinic["id"], call_status)

        if clinic["id"] == clinics[-1]["id"]:
            logger.debug("Round of calls done")
            exit()

        options = ["call next clinic", "stop for now"]

        terminal_menu = TerminalMenu(
            options,
            title="Next step",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("underline", "fg_green"),
        )
        menu_terminal_index = terminal_menu.show()

        menu_terminal_choice = options[menu_terminal_index]

        if menu_terminal_choice == options[1]:
            logger.debug(f"You chose to stop the program. Exiting program now.")
            sys.exit()
