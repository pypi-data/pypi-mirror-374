from ..db import db
from datetime import datetime
from bson import ObjectId
from copy import deepcopy

# It is very expensive to pre-expand all possible related resources for small populates, therefore, we will only expand resources
# that are explicitly requested by the user. This will allow for a more efficient use of resources.
# A shared 'context' variable is to be passed in with the following structure:
# {
#   'team': ID,
#   'fields': { 'client': {}, 'plan': {}, 'project': {} }, # Types for all custom fields by resource
#   'client': { ...expanded },
#   'plan': { ...expanded },
#   'project': { ...expanded },
#   'task': { ...expanded },
#   'deal': { ...expanded },
#   'email': { to: { name, first_name, last_name, email }, from: { name, first_name, last_name, email } }
# }

# A client has contacts, assignees, and external contacts - all of which will contain the roles as keys and IDs as values
# Clients, plans, and projects have fields which are expanded as well under 'data_val' with the value (in correct type).
# If an object is referenced (eg. User, Contact, EmailTemplate, Form, etc.), it will be expanded on demand under the 'data' key property for the same key.
# For example:
# client.data_val['Email Template'] = ObjectId('5f3b3b4e1d5b4f0001d7e6d7')
# client.data['Email Template'] = { name, subject, body }

def createInitialContext(team: ObjectId, task: ObjectId=None, project: ObjectId=None, client: ObjectId=None, plan: ObjectId=None, deal: ObjectId=None) -> (dict):
    '''
    Create the initial context reference for the expression evaluation. This should be passed in (as mutable) to all populate function calls
    '''
    context = { "team": team }
    filter = { "team": team, "deleted_at": None }
    
    # Load all fields for client, plan, and project
    context["fields"] = { "client": {}, "plan": {}, "project": {} }
    for f in db['fields'].find({ **filter }, { "key": 1, "on_type": 1, "type": 1 }):
        if not f.get('key') or not f.get('on_type') or not f.get('type'):
            continue
        
        if f["on_type"] not in ["client", "plan", "project"]:
            continue
        
        context["fields"][f["on_type"]][f["key"]] = f["type"]
            
    
    # Re-usable function to unpack fields from array to dictionary
    def unpack_fields(fields_array: list) -> (dict):
        fields_dict = {}
        if not fields_array:
            return fields_dict
        
        for f in fields_array:
            if not f.get('key') or not f.get('value'):
                continue
            
            v = f['value']
            
            # Convert datetime to Javascript Date object string (for eval_js)
            if isinstance(f['value'], datetime):
                v = f"new Date('{v.isoformat()}')"
                
            fields_dict[f['key']] = v
            
        return fields_dict
    
    
    # Load task, project, plan, and client based on IDs provided
    if task:
        context["task"] = db['tasks'].find_one({ **filter, "_id": task })
        if not context["task"]:
            raise Exception("Task not found.")
        
    # Attempt to find project ID from task if not provided
    if not project and context.get("task"):
        project = context["task"].get("project")
        
    if project:
        context["project"] = db['projects'].find_one({ **filter, "_id": project })
        if not context["project"]:
            raise Exception("Project not found.")
        
        context["project"]["data_val"] = unpack_fields(context["project"].get("fields", []))
        context["project"]["data"] = deepcopy(context["project"]["data_val"]) # Copy for now - we'll replace with expanded data when we expand it on demand
        
    # Attempt to find plan ID from proejct and then task if not provided
    if not plan and context.get("project"):
        plan = context["project"].get("plan")
        
    if not plan and context.get("task"):
        plan = context["task"].get("plan")
        
    if plan:
        context["plan"] = db['plans'].find_one({ **filter, "_id": plan })
        if not context["plan"]:
            raise Exception("Plan not found.")
        
        context["plan"]["data_val"] = unpack_fields(context["plan"].get("fields", []))
        context["plan"]["data"] = deepcopy(context["plan"]["data_val"])
    
    if deal:
        context["deal"] = db['deals'].find_one({ **filter, "_id": deal })
        if not context["deal"]:
            raise Exception("Deal not found.")
        
        
    # Attempt to find client ID from plan, project, deal, and then task (in that order) if not provided
    if not client and context.get("plan"):
        client = context["plan"].get("client")
        
    if not client and context.get("project"):
        client = context["project"].get("client")

    if not client and context.get("deal"):
        client = context["deal"].get("client")
        
    if not client and context.get("task"):
        client = context["task"].get("client")
        
    if client:
        context["client"] = db['clients'].find_one({ **filter, "_id": client })
        if not context["client"]:
            raise Exception("Client not found.")
        
        context["client"]["data_val"] = unpack_fields(context["client"].get("fields", []))
        context["client"]["data"] = deepcopy(context["client"]["data_val"])
        
        # Clients also have contacts we need to unpack into dictionaries
        contact_map = {} 
        if context["client"].get("contacts"):
            for c in context["client"].get("contacts", []): 
                if not c.get('role') or not c.get('contact'): 
                    continue 
                
                if c.get('plan', None) and context.get("plan", None) and str(c["plan"]) != str(context["plan"].get('_id')): 
                    continue 

                contact_map[c['role']] = c['contact'] 

        external_map = {} 
        if context["client"].get("external"):
            for c in context["client"].get("external", []): 
                if not c.get('role') or not c.get('contact'): 
                    continue 
                
                if c.get('plan', None) and context.get("plan", None) and str(c["plan"]) != str(context["plan"].get('_id')): 
                    continue 

                external_map[c['role']] = c['contact']

        assignee_map = {}    
        if context["client"].get("assignees"):
            for a in context["client"].get("assignees", []): 
                if not a.get('role') or not a.get('user'): 
                    continue 
                
                if a.get('plan', None) and context.get("plan", None) and str(a["plan"]) != str(context["plan"].get('_id')): 
                    continue 

                assignee_map[a['role']] = a['user']
        
        context["client"]["contacts"] = contact_map
        context["client"]["external"] = external_map
        context["client"]["assignees"] = assignee_map
        
    return context