from main.app_setup import app
from dotenv import load_dotenv
import os

load_dotenv()
port = os.environ.get("PORT")

if __name__ == "__main__":
  app.run(
    port=port
  )
  

