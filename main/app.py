from main.app_setup import app
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
  app.run()

print("port ran")
  

