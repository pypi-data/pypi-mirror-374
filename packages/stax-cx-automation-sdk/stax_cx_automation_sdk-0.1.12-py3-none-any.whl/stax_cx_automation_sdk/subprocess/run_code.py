import os
import pickle
import shutil
import sys
import subprocess
from bson import ObjectId
from ..db import db


def run_code(team: str, automation_id: str, context: dict, requirements: str, code: str, function_params: dict={}):
    '''
    Run the provided code in a subprocess with the given context
    Requires a team API key to be available for the team
    Requirements is a comma-separated list of pip packages to install
    Code should be a string of Python code to run starting with def run(client, plan, project, task, api):
    '''
    # Fetch team key for authentication
    team_ = db.teams.find_one({ "_id": ObjectId(team) })
    team_key = team_.get('api_key')
    if not team_key:
        raise Exception("Team key not found")
    
    # Install requirements
    if not code:
        raise Exception("No code provided")
    
    venv_path = './venv_temp'
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    requirements = "requests, pymongo" + ("," + requirements if requirements is not None and requirements != "" else "")
    for req in requirements.split(','):
        req = req.strip()
        try:
            subprocess.check_call([f"{venv_path}/bin/pip", "install", req])
        except Exception as e:
            raise Exception("Error installing requirement: " + req + "\n" + str(e))
    
    # Create code file
    os.makedirs('./files', exist_ok=True)
    code_file_path = './files/temp_script.py'
    with open(code_file_path, 'w') as f:
                f.write(f'''
import pickle
import sys
import requests
from bson import ObjectId

class API:
    def __init__(self, team, team_key, automation_id):
        self.headers = {{
            "x-team-id": team,
            "x-team-key": team_key,
            "x-automation-id": automation_id
        }}
    
    def get(self, path):
        return requests.get(f"https://api.cx.stax.ai{{path}}", headers=self.headers)

    def post(self, path, data):
        return requests.post(f"https://api.cx.stax.ai{{path}}", headers=self.headers, json=data)
    
    def patch(self, path, data):
        return requests.patch(f"https://api.cx.stax.ai{{path}}", headers=self.headers, json=data)
    
    def delete(self, path):
        return requests.delete(f"https://api.cx.stax.ai{{path}}", headers=self.headers)
    
{code}

if __name__ == "__main__":
    variables_file_path = sys.argv[1]
    with open(variables_file_path, 'rb') as variables_file:
        variables = pickle.load(variables_file)
    
    api = API(f"{{variables['team']}}", f"{{variables['team_key']}}", f"{{variables['automation_id']}}")

    returned_value = run(
        client=variables['client'],
        plan=variables['plan'],
        project=variables['project'],
        task=variables['task'],
        api=api,
        **variables['function_params']
    )

    if returned_value is not None:
        with open('./files/returned_value.pkl', 'wb') as return_file:
            pickle.dump(returned_value, return_file)
                        ''')
    

    #variables to send to the code file
    variables = {
                "client": context.get('client'),
                "plan": context.get('plan'),
                "project": context.get('project'),
                "task": context.get('task'),
                "automation_id": automation_id,
                "team": team,
                "team_key": team_key,
                "function_params": function_params
            }

    variables_file_path = './files/variables.pkl'
    with open(variables_file_path, 'wb') as variables_file:
        pickle.dump(variables, variables_file)

     # Create a minimal set of environment variables
    env = {
        'PATH': f"{venv_path}/bin:" + os.environ['PATH'],
        'VIRTUAL_ENV': venv_path,
        'PYTHONHOME': '',
        'PYTHONPATH': ''
    }
    
    # Run the code
    try:
        subprocess.check_call([f"{venv_path}/bin/python", code_file_path, variables_file_path], env=env)
        if os.path.exists('./files/returned_value.pkl'):
            with open('./files/returned_value.pkl', 'rb') as return_file:
                returned_value = pickle.load(return_file)
            return returned_value
    except Exception as e:
        raise Exception("Error running code: " + str(e))
    finally:
        shutil.rmtree(venv_path)
        shutil.rmtree('./files')