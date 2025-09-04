# See LICENSE.md file in project root directory

import json
import time
import traceback
from functools import wraps
from base64 import b64decode
from datetime import datetime
from .api import post, init_api
from cloudevents.http import CloudEvent
from functions_framework import cloud_event

def log(*args):
    print("[" + str(datetime.now()) + "]", *args)

'''
@def_automation(aid, key)
def app(...)
    ...
    
Translates to: app = def_automation(aid, key)(app)

This means def_automation(aid, key) must return a function that takes app as an argument and returns a function that takes *args and **kwargs as arguments.
'''

# Define automation wrapper decorator
def def_automation(aid:str, key:str):
    def decorator(app):
        
        # This is where it gets tricky... The app itself should be registered as a cloud function and we need to use the functions_framework.cloud_event decorator to do that.
        @cloud_event
        @wraps(app)
        def wrapper(e: CloudEvent):
            msg = b64decode(e.data["message"]["data"]).decode()
            
            # The message is a JSON string with the following keys:
            #   team - Team ID string
            #   task - Task ID string
            #   project - Project ID string
            #   config - Automation configuration list of dictionaries
            body = json.loads(msg)
            
            t0 = time.time()
            
            # Parse the request body
            team = body.get('team')
            task = body.get('task')
            project = body.get('project')
            config = body.get('config')
            
            init_api(team, aid, key)
            
            # Ensure all required parameters are present (config can be empty, so don't check)
            if not team or not task or not project:
                log("🚨 Missing required parameters!")
                return
            
            # Ensure that the task is still meant to be started (not completed)
            res = post(f"/auto/{task}/_start")
            if res.status_code != 200:
                log("🚨 Task does not exist or is already in progress!")
                return
            
            try:
                log("Started task:", task)
                
                # Call automation/app function - default status should be "Success" if completed successfully. This will trigger the next task in the project
                status, msg = app(team, task, project, config)
                
                dt = (time.time() - t0) * 1000
                
                if not status:
                    status = "Success"
                if not msg:
                    msg = "Task completed successfully"
                
                # Mark the task as complete and start the next one
                res = post(f"/auto/{task}/_end", {
                    "type": status,
                    "message": msg,
                    "execution_time": dt
                })
                if res.status_code != 200:
                    log("🚨 Failed to report successful task completion!")
                    return
                
                log("✅ Complete! Execution time:", dt, "ms")

            except Exception as e:
                log("🚨 Error!")
                trace = traceback.format_exc()
                print(trace)

                # Report error to the Stax.ai API
                res = post(f"/auto/{task}/_end", {
                    "type": "Error",
                    "error": "An error ocurred in the automation",
                    "traceback": str(e),
                    "execution_time": (time.time() - t0) * 1000
                })
                if res.status_code != 200:
                    log("🚨 Failed to report task error!")
                    return

        return wrapper
    return decorator