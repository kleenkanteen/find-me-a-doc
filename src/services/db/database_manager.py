from supabase import create_client, Client

from dotenv import load_dotenv
from util.date import current_time
from util.logger import logger
import os

load_dotenv(override=True)
supabase_db_url: str = os.environ.get("SUPABASE_URL")
supabase_db_key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(supabase_db_url, supabase_db_key)

def get_clinics_info():

  data, count = supabase.table('clinics').select('id, phone_number, last_call_date, last_call_success').execute()
  return data

#If call fails, only update last_call_date to (current date) and last_call_success to (false)
def update_db_on_failed_call(clinic_id: int, available_male_docs: int = 0, available_female_docs: int = 0):

  update_data = {'last_call_date': current_time(), 'last_call_success': False}

  if available_male_docs > 0:
    male_docs = available_male_docs
    update_data['available_male_docs'] = male_docs
    logger.debug("Only male docs can be updated")
  
  if available_female_docs > 0:
    female_docs = available_female_docs
    update_data['available_female_docs'] = female_docs
    logger.debug("Only female docs can be updated")
  
  data, count = supabase.table('clinics').update(update_data).eq('id', clinic_id).execute()
  return data

def update_db_on_successful_call(clinic_id: int, available_male_docs: int, available_female_docs: int):

  data, count = supabase.table('clinics').update({'available_male_docs': available_male_docs, 'available_female_docs': available_female_docs, 'last_call_success': True, 'last_call_date': current_time()}).eq('id', clinic_id).execute()
  
  return data

def update_call_final_status(clinic_id: int, call_status: str):

  is_call_status_true = (call_status == "completed")

  data, count = supabase.table('clinics').update({'last_call_success': is_call_status_true }).eq("id", clinic_id).execute()

  return data








