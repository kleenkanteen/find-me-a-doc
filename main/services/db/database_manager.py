from dotenv import load_dotenv
from supabase import create_client, Client
from main.util.date import current_time
import os

load_dotenv()
supabase_db_url: str = os.environ.get("SUPABASE_URL")
supabase_db_key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(supabase_db_url, supabase_db_key)

def get_clinics_ids_and_phone_numbers():

  data, count = supabase.table('clinics').select('id, phone_number').execute()
  return data

#If call fails, update last_call_date to (current date) and last_call_success to (false)
def update_db_on_failed_call(clinic_id: int):
  
  data, count = supabase.table('clinics').update({'last_call_date': current_time(), 'last_call_success': False}).eq('id', clinic_id).execute()
  print(f"DATA: {data}")
  print(f"COUNT: {count}")
  return data

def update_db_on_successful_call(clinic_id: int, available_male_docs: int, available_female_docs: int):

  data, count = supabase.table('clinics').update({'available_male_docs': available_male_docs, 'available_female_docs': available_female_docs, 'last_call_success': True, 'last_call_date': current_time()}).eq('id', clinic_id).execute()

  print(f"DATA: {data}")
  
  return data







