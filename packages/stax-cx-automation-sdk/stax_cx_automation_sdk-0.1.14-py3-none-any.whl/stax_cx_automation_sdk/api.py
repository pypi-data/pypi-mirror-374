from os import getenv
from retry_requests import retry, RSession

API_URL = getenv('STAX_CX_API_URL', 'https://api.cx.stax.ai')

sess = retry(RSession(timeout=30), retries=3)

headers = {
        "x-internal-key": "",
        "x-automation-id": "",
        "x-team-id": ""
}
        
def get(url):
    return sess.get(f"{API_URL}{url}", headers=headers)

def post(url, data={}):
    return sess.post(f"{API_URL}{url}", headers=headers, json=data)

def patch(url, data={}):
    return sess.patch(f"{API_URL}{url}", headers=headers, json=data)

def delete(url):
    return sess.delete(f"{API_URL}{url}", headers=headers)
        
def init_api(team, aid, key):
    global headers
    headers["x-automation-id"] = aid
    headers["x-internal-key"] = key
    headers["x-team-id"] = team