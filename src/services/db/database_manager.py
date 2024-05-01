from supabase import create_client, Client

from dotenv import load_dotenv
import os

from util.date import current_time
from util.logger import logger

load_dotenv(override=True)
supabase_db_url: str = os.environ.get("SUPABASE_URL")
supabase_db_key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(supabase_db_url, supabase_db_key)

def get_clinics_info():

    data, count = (
        supabase.table("clinics")
        .select("id, phone_number, last_call_date, last_call_success")
        .execute()
    )
    return data[1][0]


# If call fails, update last_call_date to (current date), last_call_success to (false), and corresponding docs values to NULL
def update_db_on_failed_call(
    clinic_id: int, 
    available_male_docs=None, 
    available_female_docs=None
):

    update_data = {
        "last_call_date": current_time(),
        "last_call_success": False,
        "available_female_docs": available_female_docs,
        "available_male_docs": available_male_docs,
    }

    data, count = (
        supabase.table("clinics").update(update_data).eq("id", clinic_id).execute()
    )


def update_db_on_successful_call(
    clinic_id: int, 
    available_male_docs: int, 
    available_female_docs: int
):

    data, count = (
        supabase.table("clinics")
        .update(
            {
                "available_male_docs": available_male_docs,
                "available_female_docs": available_female_docs,
                "last_call_success": True,
                "last_call_date": current_time(),
            }
        )
        .eq("id", clinic_id)
        .execute()
    )


def update_call_final_status(clinic_id: int, call_status: str):

    is_call_status_true = call_status == "completed"

    data, count = (
        supabase.table("clinics")
        .update({"last_call_success": is_call_status_true})
        .eq("id", clinic_id)
        .execute()
    )