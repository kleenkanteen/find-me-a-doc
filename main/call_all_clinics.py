from main.services.calls.caller import make_call
from main.services.db.database_manager import get_clinics_ids_and_phone_numbers
from main.config import active_call_values as call_values

def call_all_clinics():

  data = get_clinics_ids_and_phone_numbers()  

  clinics = data[1]

  for clinic in clinics:
    if(clinic['id'] == 54):
      print("\nCLINIC DATA: ", clinic)
      call_values.current_clinic_id = clinic['id']
      make_call(clinic['phone_number'], clinic['id'])
