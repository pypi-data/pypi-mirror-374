# See LICENSE.md file in project root directory

from json import loads
from bson import ObjectId
from re import sub, findall

from ..db import db
from .js import evaluateJSWithContext
from .types import castToType, EXPANDABLES

def evaluate(context: dict, x, type: str="Text", prop: str="_id", add_equals: bool=True):
    '''
    Populate the field value with any context references if provided and evaluate to get the final value of the right type.
    If the expression requires fetching additional information, it will be fetched, expanded as needed, and cached in the context.
    '''

    if add_equals and isinstance(x, str) and not x.startswith('=') and x.startswith("@@{"):
        # If the expression does not start with '=', add it
        x = f"={x}"
    
    # If the expression is not a string or if the first character is not '=', return it as is
    if not isinstance(x, str) or not x.startswith('='):
        return castToType(x, type) # It may be None or a literal value
    
    # Remove the '=' from the expression
    x = x[1:]
    
    try:
        # Find all patterns that match @@...@@ and replace it with the JS-evaluated results
        x = sub(r'@@(.*?)@@', lambda m: evaluateSingle(context, m.group(1), type, prop), x)        
        
        # Convert to the appropriate data type if prop is _id
        return castToType(x, type if prop=="_id" else "Text")
        
    except Exception as e:
        raise Exception(f"Failed evaluating expression '${x}': {str(e)}")
        
        
def evaluateSingle(context: dict, x, type: str="Text", prop: str="_id"):
    '''
    Evaluate a single expression and return the result.
    '''
    if not x:
        return ""
    
    # If the expression is a JSON string, fetch the key and evaluate it
    if isinstance(x, str) and x.startswith('{') and x.endswith('}'):
        try:
            y = loads(x)
            if not isinstance(y, dict):
                raise Exception(f"{x} could not be parsed as a JSON object")
            
            if not y.get("key"):
                raise Exception(f"{x} must have a valid 'key'")
            
            x = y["key"]
            
        except:
            raise Exception(f"{x} must be a valid JSON object")
        
    # Find all data references and ensure we have them all in the context
    # Sample data references:
    #  - client.data['{READABLE KEY}']
    #  - plan.data['{READABLE KEY}']
    #  - project.data['{READABLE KEY}']
    #  - client.data["{READABLE KEY}"]
    #  - plan.data["{READABLE KEY}"]
    #  - project.data["{READABLE KEY}"]
    # Use regex to find all data references and extract the keys
    for ref in [ "client", "plan", "project" ]:
        if not context.get(ref) or not context["fields"].get(ref) or not context[ref].get("data") or not context[ref].get("data_val"):
            continue
        
        for match in findall(rf"{ref}\.data(_val)?\[['\"](.*?)['\"]\]", x):
            # Get the key type from context.fields
            key = match[1]
            ftype = context["fields"][ref].get(key)
            if not ftype:
                ftype = "Text"
                
            # If not expandable, skip
            if ftype not in EXPANDABLES:
                continue
            
            # If we don't have the data value to expand, skip
            if not context[ref]["data_val"].get(key):
                continue
            
            # IF the prop to fetch is not _id, we need to replace data_val['{KEY}'] with data['{KEY}']['{prop}']
            if prop != "_id":
                x = sub(rf"{ref}\.data_val\[['\"]{key}['\"]\]", f"{ref}.data['{key}']['{prop}']", x)
            
            # Skip if it's already expanded in context
            try:
                context[ref]["data"].get(key) and context[ref]["data"][key].get(prop)
                continue
            except:            
                collection = db.get_collection(EXPANDABLES[ftype])
                context[ref]["data"][key] = collection.find_one({
                    "_id": ObjectId(context[ref]["data_val"][key]),
                    "deleted_at": None,
                    "team": context.get("team")
                })

    # Expanding project lead        
    if context.get("project"):
        # Skip if it's already expanded in context
            if context['project']['lead'] and isinstance(context['project']['lead'], ObjectId):
                context['project']['lead'] = db.users.find_one({"_id": ObjectId(context['project']['lead']), "deleted_at": None}, {"email": 1, "name": 1})
                # We need to add the prop to project.lead references
            if prop:
                x = sub(r"project\.lead", f"project.lead['{prop}']", x)

    # Expanding task assignee
    if context.get("task"):
        if context['task']['assignee'] and isinstance(context['task']['assignee'], ObjectId):
            context["task"]["assignee"] = db.users.find_one({"_id": ObjectId(context["task"]["assignee"]), "deleted_at": None}, {"email": 1, "name": 1})
            # We need to add the prop to task.assignee references
        if prop:
            x = sub(r"task\.assignee", f"task.assignee['{prop}']", x)
    
    
    # Expanding deal owner, stage
    if context.get("deal"):
        if context['deal']['owner'] and isinstance(context['deal']['owner'], ObjectId):
            context['deal']['owner'] = db.users.find_one({"_id": ObjectId(context['deal']['owner']), "deleted_at": None}, {"email": 1, "name": 1})
        # We need to add the prop to deal.owner references
        if prop:
            x = sub(r"deal\.owner", f"deal.owner['{prop}']", x)

        if context['deal']['funnel'] and isinstance(context['deal']['funnel'], ObjectId):
            context['deal']['funnel'] = db.funnels.find_one({"_id": ObjectId(context['deal']['funnel']), "deleted_at": None})
        # We need to add the prop to deal.funnel references
        if prop:
            x = sub(r"deal\.funnel", f"deal.funnel['{prop}']", x)
        
        if context['deal']['stage'] and isinstance(context['deal']['stage'], ObjectId):
            funnel = db.funnels.find_one({"_id": ObjectId(context['deal']['funnel'].get('_id')), "deleted_at": None})
            for stage in funnel['stages']:
                if str(stage['_id']) == str(context['deal']['stage']):
                    context['deal']['stage'] = stage
                    break
        # We need to add the prop to deal.stage references
        if prop:
            x = sub(r"deal\.stage", f"deal.stage['{prop}']", x)
        


    # We have to do something very similar for client contacts, external, and assignees
    if context.get("client"):
        # Sample contact references
        # - client.contacts['{ROLE}'] --> Contact
        # - client.external["{ROLE}"] --> Contact
        # - client.assignees["{ROLE}"] --> User
        for ref in [ "contacts", "external", "assignees" ]:
            if not context["client"].get(ref):
                continue
            
            for match in findall(rf"client\.{ref}\[['\"](.*?)['\"]\](.)?", x):
                role = match[0]
                try:
                    context["client"][ref].get(role) and context["client"][ref][role].get(prop)
                    # If there is not group 2 (. after the role), we need to append the prop to the reference
                    if not match[1]:
                        x = sub(rf"client\.{ref}\[['\"]{role}['\"]\]", f"client.{ref}['{role}']['{prop}']", x)
                    continue # We already have this loaded correctly
                
                except:
                    collection = db.get_collection("users" if ref=="assignees" else "contacts")
                    context["client"][ref][role] = collection.find_one({
                        "_id": ObjectId(context["client"][ref][role]),
                        "deleted_at": None,
                        **({ "team": context.get("team") } if ref!="assignees" else {})
                    })

                    if 'email' in context["client"][ref][role] and isinstance(context['client'][ref][role]['email'], list):
                        if len(context["client"][ref][role]['email'])>0:
                            context["client"][ref][role]['email'] = context["client"][ref][role]['email'][0]
                        else:
                            context["client"][ref][role]['email'] = ""
                    
                    # If there is not group 2 (. after the role), we need to append the prop to the reference
                    if not match[1]:
                        x = sub(rf"client\.{ref}\[['\"]{role}['\"]\]", f"client.{ref}['{role}']['{prop}']", x)
                    
    # Now that we have all the required context (and since it's mutable, we can use it again for other applications in the same service/automation!!), evaluate the expression
    return str(evaluateJSWithContext(x, context))