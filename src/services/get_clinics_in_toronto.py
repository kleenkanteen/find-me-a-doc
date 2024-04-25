import requests, json, os
from supabase import create_client, Client
from dotenv import load_dotenv

# This script gets the details of all the medical clinics in Toronto using Google Maps API and stores it in supabase.

load_dotenv(override=True)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# https://developers.google.com/maps/documentation/places/web-service/search-text
API_KEY = os.environ.get("MAPS_KEY")
fields = "name,types,formatted_phone_number"
url = f"https://-/json?query=medical%20clinics%20in%20Toronto&key={API_KEY}"
payload={}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)
response = response.json()

clinics = {}

while True:
    for place in response["results"]:
        place_id = place["place_id"]
        place_details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name%2Crating%2Cformatted_phone_number&key={API_KEY}"
        place_details_response = requests.request("GET", place_details_url, headers=headers, data=payload)
        place_details_response = place_details_response.json()
        details = place_details_response["result"]
        # check if every clinic has a phone number and if so, add to clinics dict
        if "formatted_phone_number" in details:
            details['formatted_address'] = place['formatted_address']
            clinics[details["name"]] = details
            print("ADDED", details["name"])
    if "next_page_token" not in response or response["next_page_token"] == "":
        break
    # add next page token to url and redo request
    # using https://developers.google.com/maps/documentation/places/web-service/details to get the phone number, for some reason not in the textsearch result
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=medical%20clinics%20in%20Toronto&key={API_KEY}&pagetoken={response['next_page_token']}"
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()

# write the clinics dict to the json file and supabase
with open("clinics.json", "w") as outfile:
    for key, value in clinics.items():
            try:
                data, count = supabase.table("clinics").insert({
                                                                "name": key,
                                                                "location": value["formatted_address"],
                                                                "phone": value["formatted_phone_number"],
                                                                "called": False,
                                                                "rating": float(value["rating"])
                }).execute()
                
            except Exception as e:
                print("Failed to insert into supabase", e)
    # Write the contents of the dictionary as a JSON string to the file
    json.dump(clinics, outfile)

# Open the JSON file in read mode
with open("clinics.json", "r") as json_file:
    # Load the JSON data into a dictionary
    clinics = json.load(json_file)


# Iterate over the clinics and add a new "called" field to each one
for clinic in clinics:
    clinics[clinic]["called"] = False

# Open the JSON file in write mode
with open("ClinicsCalledData.json", "w") as json_file:
    # Write the updated clinics data back to the file
    json.dump(clinics, json_file)
