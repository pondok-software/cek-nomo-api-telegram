from flask import Flask, json, Response
from flask_restful import reqparse, abort, Api, Resource, request

from telethon import TelegramClient, errors, events, sync
from telethon.tl.types import InputPhoneContact
from telethon import functions, types
from dotenv import load_dotenv
import argparse
import os
from getpass import getpass
import asyncio

load_dotenv()

result = {}

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('task')

def get_names(phone_number):
    try:
        print('radad')
        client = TelegramClient(PHONE_NUMBER, API_ID, API_HASH)
        client.connect()
        contact = InputPhoneContact(client_id = 0, phone = phone_number, first_name="", last_name="")
        contacts = client(functions.contacts.ImportContactsRequest([contact]))
        username = contacts.to_dict()['users'][0]['username']
        if not username:
            print("*"*5 + f' Response detected, but no user name returned by the API for the number: {phone_number} ' + "*"*5)
            del_usr = client(functions.contacts.DeleteContactsRequest(id=[username]))
            return "error"
        else:
            del_usr = client(functions.contacts.DeleteContactsRequest(id=[username]))
            return username
    except Exception as e:
        print(e)
        return "error"


class CheckPhoneNumber(Resource):
    def get(self):
        try:
            input_phones = request.args['phonenumber']
            if not input_phones or input_phones == '':
                return Response(
                    response=json.dumps({
                        "mesage": "Phone Number is required",
                        "code": 400
                    }),
                    status=400,
                    mimetype="application/json")        
            else:
                api_res = get_names(input_phones)
                result['userId'] = api_res
                if (result['userId'] and result['userId'] != 'error'):
                    return Response(
                        response=json.dumps({
                            "mesage": "Phone number is registered on telegram",
                            "code": 200
                        }),
                        status=200,
                        mimetype="application/json")
                else:
                    return Response(
                        response=json.dumps({
                            "mesage": "Checking error or Phone number is not registered on telegram",
                            "code": 404
                        }),
                        status=404,
                        mimetype="application/json")        
        except Exception as er:
            return Response(
                response=json.dumps({
                    "mesage": "Internal server error",
                    "code": 500
                }),
                status=500,
                mimetype="application/json")
        

##
## Actually setup the Api resource routing here
##
api.add_resource(CheckPhoneNumber, '/check')


if __name__ == '__main__':    
    parser = argparse.ArgumentParser(description='Check to see if a phone number is a valid Telegram account')

    args = parser.parse_args()

    client = TelegramClient(PHONE_NUMBER, API_ID, API_HASH)
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(PHONE_NUMBER)
        try:
            client.sign_in(PHONE_NUMBER, input('Enter the code (sent on telegram): '))
        except errors.SessionPasswordNeededError:
            pw = getpass('Two-Step Verification enabled. Please enter your account password: ')
            client.sign_in(password=pw)
    app.run(debug=True)
