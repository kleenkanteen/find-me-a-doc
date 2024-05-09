# Development Guide

## Setting up Twilio account and environment variables

1. Go to [https://www.twilio.com/login](https://www.twilio.com/login) and create a twilio account. Add and verify your phone number. You will get $15 in free credits. Then get a virtual number that is somewhere in Ontario. Then add your number to be a verified number. Your twilio number can only call verified numbers.
2. Copy `.env.example` and rename the new file to `.env`. Notice this is in `.gitignore` so it won't be pushed to github. Fill in the first 4 variable with your twilio account info. You can find your account sid and auth token in the twilio console. You can find your twilio number in the twilio console as well.
3. For the SUPABASE_URL and SUPABASE_KEY .env variables you can use your own during the development stage, however, kleenkanteen (owner) holds the keys for production. He can send them securely over discord.

## Setting up flask server and initiating a call

1. Run `python3 -m venv venv` to create a virtual environment
2. Run `source venv/bin/activate` to activate the virtual environment or if on windows, run `venv\Scripts\activate.bat`
3. Run `pip install -r requirements.txt` to install all dependencies
4. Fill out all the environment variables in the `.env` file
5. Run `python3 src/app.py` to start the Flask server and trigger the calls

## System Design

Both the Frontend and Backend workflows are explained by diagrams (located in the ***Diagrams*** section).

## Diagrams

1. ### [Bot-driven Call Flow](https://app.eraser.io/workspace/1yvzNivbO1RsB2ufyMGl) - Describes the flow of a call, this is the *main data entry point* for the backend.

2. ### [Backend-Database-Frontend Workflows](https://app.eraser.io/workspace/jmjNomYZkKgB5nVZqnK8?origin=share) - Describes the workflows that both the backend and frontend follow.

## Database schemas

****Clinic schema:****
| Value | Type |
|-------|-------|
| id |string  |
| name | string |
| address | string |
| phone_number | string |
| rating | number |
| called | boolean |
| male_docs_number | number |
| female_docs_number| number |

## Logger

Right now our logger works very simply:

- If a log is of level `debug` or above, it will print the file where it's called, line number and function name.

import it into a file like this:

```python
from main.util.logger import logger
```

1. INFORMATIONAL logs: `print()` for informational logs
2. DEBUG logs: `logger.debug("foo")`
3. WARNING logs: `logger.warning("foo")`
4. ERROR logs: `logger.error("foo")`
5. CRITICAL logs: `logger.critical("foo")`

### Ideal logger:

Ideally, after all calls are made this logger should create a document with detailed information about each call such as:

1. Was it a success or a failure?
2. Time duration
3. Chronological responses from the user
4. How many times a a response was unrecognized
5. If failed call, when did it fail? Did the user hang up? Was an error presented?

## Relevant Files

main/services/caller.py - This initiates the call to the clinic using twilio api

main/app.py -The flask server twilio sends it's speech text transcriptions to and the server responds to twilio with what to say next. Refer to resources/dev_guides/system_design.md to learn more.

main/services/get_clinics_in_toronto.py - The script that uses the google maps api to get all clinics in toronto.

## Dev Tips
- Whenever you add a new library, make sure to add it to the requirements.txt file so others can install all required libraries quickly.

# Folder structure

```
.
├── LICENSE
├── clinics.json
├── src
│   ├── __init__.py
│   ├── app.py				//Contains core server logic & initialization
│   ├── app_setup.py	    //Manages server configuration
│   ├── config 			    //Configuration classes and values used during calls
│   ├── controller	        //REST API controllers
│   ├── models				//Entity classes and schemas
│   ├── util				//Utility and helper functions
│   └── services			//Business logic layer & business-related active-call functions
├── readme.md
├── system_design.md    //System design doc for both backend and frontend
├── requirements.txt
└── resources
    ├── custom_audios	//Custom audios
    └── dev_guides		//Resources for developers
```
