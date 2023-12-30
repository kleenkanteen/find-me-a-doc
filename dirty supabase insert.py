import json, os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Open the JSON file in read mode
with open("clinics.json", "r") as json_file:
    # Load the JSON data into a dictionary
    clinics = json.load(json_file)

# write the clinics dict to the json file and supabase
with open("clinics.json", "r") as outfile:
    for key, value in clinics.items():
            try:
                data, count = supabase.table("clinics").insert({"name": key, "location": value["formatted_address"], "phone": value["formatted_phone_number"], "called": False, "rating": float(value["rating"])}).execute()
            except Exception as e:
                print("Failed to insert into supabase", e)