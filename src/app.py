import os, threading, sys
from util.logger import logger
from dotenv import load_dotenv

from app_setup import app
from services.calls.call_all_clinics import call_all_clinics

load_dotenv(override=True)
port = os.environ.get("PORT")


def start_server():
    logger.info("Starting flask server...")
    app.run(port=port)


if __name__ == "__main__":

    try:

        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        logger.loud(f'url: {os.environ.get("NGROK_URL")}')

        call_all_clinics()

        server_thread.join()

    except KeyboardInterrupt:
        logger.warning("Forced shutdown requested. Exiting the program now...")
        sys.exit(0)
