from flask import Flask
from pyngrok import ngrok
import os
from dotenv import load_dotenv

load_dotenv(override=True)
port = os.environ.get("PORT")
ngrok_auth_token: str = os.environ.get("NGROK_AUTH_TOKEN")

print(f"PORT: {port}")

app = Flask(__name__)

ngrok.set_auth_token(ngrok_auth_token)
public_url = ngrok.connect(port).public_url
os.environ["NGROK_URL"] = public_url
print(f"ngrok link: {public_url}")

from main.controller.api import api
app.register_blueprint(api)


