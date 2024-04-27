import os
from dotenv import load_dotenv

from flask import Flask, request
from pyngrok import ngrok

load_dotenv(override=True)

port = os.environ.get("PORT")
ngrok_auth_token: str = os.environ.get("NGROK_AUTH_TOKEN")

print(f"PORT: {port}")

app = Flask(__name__)

ngrok.set_auth_token(ngrok_auth_token)
public_url = ngrok.connect(port).public_url
os.environ["NGROK_URL"] = public_url

from controller.call_flow_manager import call_flow_manager

app.register_blueprint(call_flow_manager)



