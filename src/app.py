from app_setup import app
from services.calls.call_all_clinics import call_all_clinics
from dotenv import load_dotenv
from util.logger import logger
import os, threading, sys, traceback, signal, time, multiprocessing
from flask import request

load_dotenv(override=True)
port = os.environ.get("PORT")

def start_server():
  logger.debug("Starting flask server...")
  app.run(
    port=port
  )

if __name__ == '__main__':
    
    try:

        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        call_all_clinics()

        server_thread.join()


    except KeyboardInterrupt:
      logger.warning("Forced shutdown requested. Exiting the program now...")
      sys.exit(0)