from main.services.calls.call_single_clinic import make_call
from main.services.db.database_manager import get_clinics_ids_and_phone_numbers
from dotenv import load_dotenv
from main.util.logger import logger
import os

# This portion has been adapted for development purposes only
# Enter your mock clinic id in your .env file

load_dotenv(override=True)
MOCK_CLINIC_ID: int = int(os.environ.get("MOCK_CLINIC_ID"))

def call_all_clinics():

  data = get_clinics_ids_and_phone_numbers()  

  clinics = data[1]

  for clinic in clinics:
    if(clinic['id'] == MOCK_CLINIC_ID):
      make_call(clinic['phone_number'], clinic['id'])
    elif(clinic['id'] == clinics[-1]['id']):
      logger.critical(f"Your MOCK CLINIC ID is not valid. current clinic Id: {clinic['id']}. Yours: {MOCK_CLINIC_ID}")