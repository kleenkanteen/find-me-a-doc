import os, json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_KEY = os.environ.get("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_KEY)

def detect_pregenerated_transcript(transcript: str):
    print("generating if human or robot just spoke now...")
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a powerful and wise assistant that is able to distinguish between pre generated dialogues and in real time dialogues. Given a transcript, you will determine whether it is pre generated or a natural transcript. Consider a natural transcript to be one where the content seems shorter and there is a text that starts with a form of salutation/greeting like: 'hello...['rest of the greeting']', or 'hey there...['rest of the greeting']', it could also contain a form of introduction like '[clinic name], how can i help you?', consider anything else non natural (pregenerated). You will respond with this JSON format: '{\"pregenerated\": --boolean--}'",
            },
            {
                "role": "user",
                "content": "this is a medical emergency please hang up and dial 911 if you are calling with critical results please call the ordering physician or the critical results doctor directly if you have an upcoming appointment you wish to cancel press six now if you are calling from a hospital or doctor's office and need urgent assistance press 5 now to book an appointment with your family doctor or specialist press one now to book an appointment or get information about our walk-in clinic please press two to book or get information on diagnostic tests off for a ultrasound mammogram echocardiograms press three now  to book an appointment with our physiotherapy department press four to reach lifelabs please hang up and dial 416-462-8700 for general information including our address fax number and hours of  operation",
            },
            {"role": "assistant", "content": '{"pregenerated": true}'},
            {
                "role": "user",
                "content": "for general information including our address fax number and hours of operation. UW  You've reached the walk-in clinic. If you wish to keep your place in queue and use our callback option, please press one now.  Otherwise, please hold and one of our booking agents will be with you shortly",
            },
            {"role": "assistant", "content": '{"pregenerated": true}'},
            {
                "role": "user",
                "content": "hello, thank you for calling urgent care. how may i help you today? ",
            },
            {"role": "assistant", "content": '{"pregenerated": false}'},
            {"role": "user", "content": "hello, how may i help you today?"},
            {"role": "assistant", "content": '{"pregenerated": false}'},
            {
                "role": "user",
                "content": "SH medical, how can I help?  Hello.  Hi. Hello.  Catfish medical, how can I help?  Sorry, I can't hear you.",
            },
            {"role": "assistant", "content": '{"pregenerated": false}'},
            {
                "role": "user",
                "content": "Hello, Asian. Centro, how can I help you?  Hello. Hello. Can you hear me?",
            },
            {"role": "assistant", "content": '{"pregenerated": false}'},
            {
                "role": "user",
                "content": "Hello, Urgent Care center. How can I help you?",
            },
            {"role": "assistant", "content": '{"pregenerated": false}'},
            {
                "role": "user",
                "content": "Your call will be answered by the next available operator.",
            },
            {"role": "assistant", "content": '{"pregenerated": true}'},
            {
                "role": "user",
                "content": "You're estimate time until reaching an operator is of 3 minutes 45 seconds",
            },
            {"role": "assistant", "content": '{"pregenerated": true}'},
            {"role": "user", "content": transcript},
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    response = completion.choices[0].message.content

    json_response = json.loads(response)

    return json_response["pregenerated"]
