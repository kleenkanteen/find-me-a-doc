import os, json
from ..util import remove_dots_and_commas
from ..logger import logger
from .util import prompt

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_KEY = os.environ.get("OPENAI_KEY")


def clean_transcript(transcript):

    transcript = remove_dots_and_commas(transcript)

    client = OpenAI(api_key=OPENAI_KEY)

    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": "You will be given a transcript. Your mission is to grab the options that you are given and list them in order, beware that there wont be punctuation signs, joining the option to the key must be done meticulously.",
            },
            {
                "role": "user",
                "content": "this is a medical emergency please hang up and dial 911 if you are calling with critical results please call the ordering physician or the critical results doctor directly if you have an upcoming appointment you wish to cancel press six now if you are calling from a hospital or doctor's office and need urgent assistance press 5 now to book an appointment with your family doctor or specialist press one now to book an appointment or get information about our walk-in clinic please press two to book or get information on diagnostic tests off for a ultrasound mammogram echocardiograms press three now  to book an appointment with our physiotherapy department press four to reach lifelabs please hang up and dial 416-462-8700 for general information including our address fax number and hours of  operation",
            },
            {
                "role": "assistant",
                "content": "If you are calling with critical results: Call the ordering physician.\nIf you have an upcoming appointment you wish to cancel: Press 6\nIf you are calling from a hospital or doctors office and need urgent assistance: Press 5 now\nTo book an appointment with your family doctor or specialist: Press 1\nTo book an appointment or get information about our walk-in clinic: Press 2\nTo book or get information on diagnostic tests off for a ultrasound mammogram echocardiograms: Press 3\nTo book an appointment with our physiotherapy department: Press 4\nTo reach LifeLabs: Please hang up\nDial 416 462 8700 for general information including our address, fax number and hours of operation.",
            },
            {
                "role": "user",
                "content": "for general information including our address fax number and hours of operation. UW  You've reached the walk-in clinic. If you wish to keep your place in queue and use our callback option, please press one now.  Otherwise, please hold and one of our booking agents will be with you shortly",
            },
            {
                "role": "assistant",
                "content": "For general information including our address fax number and hours of operation: No answer provided\nIf you wish to keep your place in queue and use our callback option: Press 1 now\nPlease hold and one of our booking agents will be with you shortly",
            },
            {"role": "user", "content": transcript},
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    response = completion.choices[0].message.content

    print(f"\ntranscript to be evaluated: {response}\n")

    return response


def find_next_nav_menu_key(transcript: str):

    transcript = clean_transcript(transcript)

    client = OpenAI(api_key=OPENAI_KEY)

    completion_messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": "For walk-in clinic: Press one, For family medicine: Press two, For sports medicine: Press three, For pain clinic: Press four",
        },
        {"role": "assistant", "content": '{"digit": 1, "human_reached": false}'},
        {
            "role": "user",
            "content": "If this is an emergency: Hang up and call 911. Bring your physical health card to each visit. Clinic will close once patient capacity is reached. Rude or aggressive behavior can lead to dismissal. Please hold for attendant",
        },
        {"role": "assistant", "content": '{"digit": null, "human_reached": true}'},
        {
            "role": "user",
            "content": "To visit our website: No answer provided. To book an appointment for a covetous office: No answer provided. To register to speak to a physician: No answer provided. To speak to a USB physician: Press 1. To book a covet screening test: Press 2. For health records insurance and lawyers request: Press 3. To speak to the front desk: Press 4",
        },
        {"role": "assistant", "content": '{"digit": 4, "human_reached": true}'},
        {
            "role": "user",
            "content": "For general information including our address, fax number, and hours of operation: No answer provided. If you wish to keep your place in queue and use our callback option: Press one now. Please hold and one of our booking agents will be with you shortly",
        },
        {"role": "assistant", "content": '{"digit": null, "human_reached": true}'},
        {
            "role": "user",
            "content": "To have an agent call you back to the phone number one 587-324-2269: Press 1. To check a different callback number: Press 2. To listen again: Press 3. To return to the queue on hold: Press 0",
        },
        {"role": "assistant", "content": '{"digit": 0, "human_reached": true}'},
        {"role": "user", "content": "To speak to a representative, please press 3"},
        {"role": "assistant", "content": '{"digit": 3, "human_reached": true}'},
        {"role": "user", "content": transcript},
    ]

    completion = client.chat.completions.create(
        model="gpt-4-turbo", messages=completion_messages
    )

    response = completion.choices[0].message.content

    json_response = json.loads(response)

    if not is_valid_response(json_response):
        logger.debug(
            f"error: chatgpt returned an invalid response. gpt response: {json_response}"
        )
        return

    logger.info(f"\nGPT response: {json_response}\n")
    return json_response


def is_valid_response(obj):
    if not isinstance(obj, dict):
        return False

    if "digit" not in obj or "human_reached" not in obj:
        return False

    if obj["digit"] is None and obj["human_reached"] is False:
        logger.error("GPT could not find a reasonable answer.")
        return False

    if not isinstance(obj["human_reached"], bool):
        return False

    if obj["human_reached"] == False:
        return isinstance(obj["digit"], int)

    return True
