from cgi import test
from flask import Flask
from flask_restful import Api, Resource
import requests
import time
import oauth2 as oauth2
from pprint import pprint
import json
from flask_cors import CORS
import pyaudio
import websockets
import asyncio
import base64

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

# starts recording
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)

# the AssemblyAI endpoint we're going to hit
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

#Please enter AssemblyAI Auth key
auth_key = "AssemblyAI_key"

go = True
wrkmet = 0
result = ''

#Please enter User Access Token and User ID
access_token = 'ACCESS_TOKEN'
user_id = 'USER_ID'

async def send_receive():
   async with websockets.connect(
       URL,
       extra_headers=(("Authorization", auth_key),),
       ping_interval=5,
       ping_timeout=20
   ) as _ws:
       await asyncio.sleep(0.1)
       session_begins = await _ws.recv()

       async def send():
           while go:
               try:
                   data = stream.read(FRAMES_PER_BUFFER)
                   data = base64.b64encode(data).decode("utf-8")
                   json_data = json.dumps({"audio_data": str(data)})
                   await _ws.send(json_data)

               except websockets.exceptions.ConnectionClosedError as e:
                   assert e.code == 4008
                   break
               except Exception as e:
                   assert False, "Not a websocket 4008 error"
               await asyncio.sleep(0.01)

           return True

       async def receive():
           while True:
               try:
                   result_str = await _ws.recv()

                   if ("good" in json.loads(result_str)['text']):
                       global result
                       result = "Thats great!"
                       global go 
                       go = False
                       global wrkmet
                       wrkmet = 4
                       return

                   elif ("bad" in json.loads(result_str)['text']):
                       result = "Oh no! That's ok you got this!"
                       go = False
                       wrkmet = -4
                       return

                   elif ("ok" in json.loads(result_str)['text']):
                       result = "It's alright to have an ok day!"
                       go = False
                       wrkmet = 0
                       return

               except websockets.exceptions.ConnectionClosedError as e:
                #    print(e)
                   assert e.code == 4008
                   break
               except Exception as e:
                   assert False, "Not a websocket 4008 error"

       send_result, receive_result = await asyncio.gather(send(), receive())
       return wrkmet

def fitBitData():
    workoutmeter = 0
    #Please enter your own user access token and user ID
    global access_token
    global user_id
    activity_request = requests.get('https://api.fitbit.com/1/user/'+user_id+'/activities/steps/date/today/today.json',
                                    headers = {'Authorization': 'Bearer ' + access_token})

    sleep_request = requests.get('https://api.fitbit.com/1/user/'+user_id+'/sleep/date/today.json',
                                    headers = {'Authorization': 'Bearer ' + access_token})

    
    #STEPS
    stepsdata = (activity_request.json()['activities-steps'])
    for line in stepsdata:
        steps = int(line['value'])

    timeresult = time.localtime()

    if timeresult.tm_hour == 0:
        stepshr = steps
    else:
        stepshr = steps / timeresult.tm_hour

    if (stepshr < 150):
        workoutmeter += 2

    elif (150 < stepshr < 420):
        workoutmeter += 0

    elif (stepshr > 420):
        workoutmeter -= 2


    #SLEEP
    sleepdata = (sleep_request.json()['sleep'])
    for line in sleepdata:
        sleep = int(line['value'])

    if (sleep > 8):
        workoutmeter += 2

    elif (4 < sleep < 8):
        workoutmeter += 0

    elif (sleep < 4):
        workoutmeter -= 2


    #Body Goals Information
    bodygoals_request = requests.get('https://api.fitbit.com/1/user/'+user_id+'/body/log/weight/goal.json',
                                    headers = {'Authorization': 'Bearer ' + access_token})
    
    profile_request = requests.get('https://api.fitbit.com/1/user/'+user_id+'/profile.json',
                                    headers = {'Authorization': 'Bearer ' + access_token})

    user_height = int(profile_request.json()['user']['height'])
    bodygoals_type = (bodygoals_request.json()['goal']['goalType'])
    bodygoals_date = (bodygoals_request.json()['goal']['startDate'])
    bodygoals_starting_weight = int(bodygoals_request.json()['goal']['startWeight'])
    bodygoals_goal_weight = int(bodygoals_request.json()['goal']['weight'])

    goal_weight_difference = (bodygoals_starting_weight) - (bodygoals_goal_weight)
    bmi_calculation = (bodygoals_starting_weight) / ((user_height/100)**2)
    

    if (bodygoals_type == "LOSE"):
        if (bmi_calculation >= 25.0):
            workoutmeter += 1
        else:
            workoutmeter += 0

    return workoutmeter
        

def workoutDecide(workout_meter):
    global result
    if(-3 <= workout_meter <= 3):
        result += " You can work out if you'd like!"
    elif(4 <= workout_meter <= 7):
        result += " We encourage you to workout"
    elif(8 <= workout_meter <= 10):
        result += " We strongly encourage you to workout!"
    elif(-7 <= workout_meter <= -4):
        result += " We encourage you to take a rest day"
    elif(-10 <= workout_meter <= -8):
        result += " We strongly encourage you to take a rest day!"
    else:
        result += " Error"
    return result


def main():
    wrkmeter = 0
    wrkmeter = asyncio.run(send_receive())
    wrkmeter += fitBitData()
    return workoutDecide(wrkmeter)

class FitBit(Resource):
    def get(self):
        activity_request = requests.get('https://api.fitbit.com/1/user/'+user_id+'/activities/steps/date/today/today.json',
        headers = {'Authorization': 'Bearer ' + access_token})

        sleep_request = requests.get('https://api.fitbit.com/1/user/'+user_id+'/sleep/date/today.json',
        headers = {'Authorization': 'Bearer ' + access_token})
        
        return {
                "steps": activity_request.json()['activities-steps'][0]['value'],
                "sleep": sleep_request.json()['summary']['totalTimeInBed']
               }

        
    def post(self):
        return {"result": main()}

api.add_resource(FitBit, "/FitBit")

if __name__ == "__main__":
    app.run(debug=True)