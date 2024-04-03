#---------------------------------------------------------------------------------------------------
# COIN GURU
# Virtual Assistant based on Lola Platform
#---------------------------------------------------------------------------------------------------
# This is a simple example of how to use 
# Lola SDK to build an AI Virtual Assistant that can answer questions related 
# to the cryptocurrency market.
# Features:
# - Get the price of a cryptocurrency in a specific currency
# - Restrict the assests to the "BTC", "ETH", "ADA", "DOT", "XRP", "LTC", checkout prompt.state.json
# - Implement limits on the number of requests per user based on credits (tokens are used as credits)
#---------------------------------------------------------------------------------------------------

import sys
import os

# Get the parent directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python module search path
sys.path.append(parent_dir)
sys.path.append(parent_dir + '/lolapy')

import os
from time import sleep
from auth_middleware import AuthMiddleware
from lolapy import LolaSDK
from lolapy import LolaContext
from lolapy import ResponseText, ResponseImage
import requests
import json
from dotenv import dotenv_values


config = {
    **dotenv_values("example/.env"),    # load development variables
    **os.environ,               # override loaded values with environment variables
}

# Create a new instance of Lola SDK
# Lola SDK will listen for events and commands from the selected Assistant
lola = LolaSDK(
    lola_token=config['ASSISTANT_TOKEN'],
    prompter_url=config['PROMPTER_URL'],
    # Set to HOST env var to 0.0.0.0 on Railways or Heroku or any other cloud provider
    host=config['HOST'],  
    port=int(config['PORT']),
    # this must be a public url, you can use ngrok to expose your localhost, check README.md
    webhook_url=config['WEBHOOK_URL'],
    # Optional for Session Store into Redis instead of local memory
    # redis_url=config['REDIS_URL']
)

# Register middlewares
# --------------------------------------------------------
auth_middleware = AuthMiddleware()
lola.register_middleware(auth_middleware)




# Hook on every new conversation started by a new user
@lola.on_event('onNewConversation')
def handle_new_conversation(session, ctx: LolaContext, msg):
    print(f'Got new conversation message: {msg["text"]}')
    img_url = "https://firebasestorage.googleapis.com/v0/b/numichat.appspot.com/o/bitcoin-btc-banner-bitcoin-cryptocurrency-concept-banner-background-vector.jpeg?alt=media&token=d9a4e055-e61c-40ac-9584-51d7a3709901"


    # This line will send a message to the user without passing trough the AI
    # but the AI is going to response to the user after this message    
    #------------------------------------------------------------------------
    # return ResponseImage(img_url, "Welcome to CoinGuru!").Send()

    # If you want to response to the user and then disable the AI response
    # only for this message, you can use the following line
    # note the DisableAI() method, this will disable the AI response
    #------------------------------------------------------------------------
    return ResponseImage(img_url, "Welcome to the game!").DisableAI().Send()


# Hook on every message received by Lola from the user
@lola.on_event('onTextMessage')
def handle_text_message(session, ctx: LolaContext, msg, req):
    print(f'Got text message: {msg["text"]}')


@lola.on_client_command('/ping')
def handle_client_command(session, ctx: LolaContext, cmd):
    print(f'Got client command: {cmd}')
    ctx.messanger.send_text_message('pong', blend=False, appendToHistory=False)


# Hook on every image received by Lola from the user
@lola.on_event('onImage')
def handle_text_message(session, ctx: LolaContext, msg):
    attach = msg['attachments'][0]
    print(f'Got image message: {attach["url"]}')
    return ResponseText('You\'ve sent me an image? you made it? Awesome painting').DisableAI().Blend().Send()


@lola.on_command('get_cryptocurrency_price')
def handle_get_cryptocurrency_price(session, ctx: LolaContext, cmd):

    print(f'Got command!')
    cryptocurrency = cmd['data']['args']['cryptocurrency']
    currency = cmd['data']['args']['currency']
    print(f'User wants to know the price of {cryptocurrency} in {currency}')
    
    ctx.messanger.send_text_message(
        f'Did you know that you can get a discount at CoinGuru if you use the code 1234?', 
        blend=True
    )
    ctx.messanger.send_typing_action()    

    # Request to coinbase API to get the price of the cryptocurrency
    #------------------------------------------------------------------------
    url = f"https://api.coinbase.com/v2/prices/{cryptocurrency}-{currency}/spot"
    response = requests.get(url)
    data = json.loads(response.text)

    # When you want to response to a command:
    # you can take the json and build a natural lang response or 
    # you can send the json as a response to the command
    #------------------------------------------------------------------------
    return ResponseText(json.dumps(data)).Send()



# Hook on every timeout triggered
@lola.on_timeout()
def handle_timeout(session, ctx: LolaContext, label):
    print(f'Timeout reached for label: {label}')






# -----------------------------------------------------
# -----------------------------------------------------
# -----------------------------------------------------
# Start Lola SDK
lola.listen(debug=False, disableWebServer=True)

# Setup FastAPI Server
# -----------------------------------------------------
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Repsonse from FastAPI"}

@app.post("/event")
def handle_event_from_lola(req: dict):
    result = lola.process_event(req)
    # Return response 200 to Lola
    return result

print('Lola is listening...')

# Start FastAPI Server
# -----------------------------------------------------
import uvicorn
uvicorn.run(app, host=config['HOST'], port=int(config['PORT']))