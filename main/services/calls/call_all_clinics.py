from main.services.calls.call_single_clinic import make_call
from main.services.db.database_manager import update_call_final_status
from dotenv import load_dotenv
from twilio.rest import Client
from main.util.logger import logger
from simple_term_menu import TerminalMenu
import os, threading, time, queue, sys

load_dotenv(override=True)
NGROK_URL = os.environ.get("NGROK_URL")
TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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

    #FOR REAL LIFE TESTING OR PRODUCTION: uncomment next two lines of code down below
  # data = get_clinics_ids_and_phone_numbers()
  # clinics = data[1]

    #WHILE DEVELOPING:
  # 1. Replace the X's for real ids in your database. 
  #    They MUST belong to the same instance of your phone number
  #    otherwise, the code will not run.

  clinics = [{
      "id": XX,
      "phone_number": "(XXX) XXX-XXXX"
  },
  {
      "id": XX,
      "phone_number": "(XXX) XXX-XXXX"
  },
  {
      "id": XX,
      "phone_number": "(XXX) XXX-XXXX"
  }]

  for clinic in clinics:
      
      clinic_sid = make_call(clinic["phone_number"], clinic["id"])

      logger.debug(f"Call started...sid: {clinic_sid}")

      q = queue.Queue()

      call_status_poller = threading.Thread(
          target=check_call_status, args=(q, clinic_sid)
      )
      call_status_poller.start()
      call_status_poller.join()

      call_status = q.get()

      update_call_final_status( clinic["id"], call_status)

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