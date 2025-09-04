# Stax.ai CX Automation SDK

This project is created and maintained by [Stax.ai, Inc.](https://stax.ai). This is proprietary to Stax.ai, Inc. Unauthorized use, copy, license, or modification of this project and all associated source code is strictly prohibited.

## About

...coming soon...

## Installation

```sh
pip install stax_cx_automation_sdk
```

## Usage

### Create a Stax.ai automation

Do this by creating a database entry manually that matches the schema for `Automation`.

### Write your automation app

```py
import os
from stax_cx_automation_sdk import def_automation

# This is the `_id` of the automation from the DB and the token user for cross-internal system communication
@def_automation(os.getenv('AUTOMATION_ID'), os.getenv('INTERNAL_KEY'))
def app(team:str, task:str, project:str, config:list[dict]):
    '''
    Your custom automation app. Is provided the following arguments:
    - team [str]: Team ID string
    - task [str]: Task ID string
    - project [str]: Project ID string
    - config [list[dict]]: Pipeline configuration for automation

    Return the following arguments:
    - status [str]: One of Success, Error, Active
    - message [str]: Human-readable message to go with the status
    If there is an error, raise an exception with a nice human-readable error message to show up on the log.
    '''

    # Put your automation functionality here
    # ...

    # Raise an exception to stop the pipeline and flag the task
    raise Exception("Oops, something went wrong!")

    # The return 
    return "Success", "The required action has been completed" # Replace this with something more relevant, for example: 'Email sent to: naru@stax.ai'
```

### Using the Stax.ai API

A pre-authenticated instance of the Stax.ai API is available to be used. See example below:

```py
from stax_cx_automation_sdk import api

res = api.get("/todo/project/66906152e0f1a56abd992a60")

res = api.post("/todo/project/_list", {
    "search": "foo"
})

res = api.patch("/todo/project/66906152e0f1a56abd992a60", {
    "tags": [ "Test" ]
})

res = api.delete("/todo/project/66906152e0f1a56abd992a60")
```

These calls are made with the team ID, automation header and key for authorization.

### Testing your automation

To test your automation, simply comment out the `@def_automation` line and call the `app` function with the appropriate input arguments.

### Deploy your automation

1. Navigate to the `Project CX` Google Cloud topic.
2. Create a Pub/Sub topic with the name: `auto-{NAME}`, for example `auto-send-email`.
3. Create a Cloud Function with the same name as the Pub/Sub topic.
4. Set the trigger type to `Cloud Pub/Sub`.
5. Pick the previously created Pub/Sub topic.
6. Select the appropriate memory, CPU, timeout, and concurrency settings.
7. Select the `App Engine default service account`.
8. Add the runtime environment variable: `AUTOMATION_ID` and `INTERNAL_KEY`.
9. Ensure your entry file is called `main.py` and that you have a `requirements.txt` file with your dependencies.
10. Load your source code as a ZIP and configure the function appropriately (make sure the entry-point is set.)
11. Test your function, and deploy it!
12. Set the `url` property in the automation to your Pub/Sub topic name.

## Developers

### Building this SDK

[For Stax.ai, Inc. developers only]

1. Increment the minor/major version in `setup.py`.
2. `python3 -m pip install --upgrade build`
3. `python3 -m build`
4. `python3 -m pip install --upgrade twine`
5. `python3 -m twine upload dist/*`
6. Request the PyPi API token from Naru if you don't have it.