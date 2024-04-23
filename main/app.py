from main.app_setup import app
from main.call_all_clinics import call_all_clinics
from dotenv import load_dotenv
import os

load_dotenv()
port = os.environ.get("PORT")

if __name__ == "__main__":
  app.run(
    port=port
  )

call_all_clinics()

print("CALLED ALL CLINICS DONE")






  

