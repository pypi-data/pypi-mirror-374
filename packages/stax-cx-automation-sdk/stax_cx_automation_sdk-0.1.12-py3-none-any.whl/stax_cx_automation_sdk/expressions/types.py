from bson import ObjectId
from datetime import datetime

EXPANDABLES = {
    "User": "users",
    "Contact": "contacts",
    "File": "files",
    "Form": "forms",
    "EmailTemplate": "email_templates",
    "ProjectTemplate": "project_templates",
}


def castToType(x: str, type: str="Text"):
    '''
    Case x to the appropriate data type based on the type provided.
    
    Based on the following field types, the output datatypes must be:
     - User -> ObjectId (unless expanded using prop)
     - Contact -> ObjectId (unless expanded using prop)
     - Dropdown -> str
     - Date -> datetime
     - File -> ObjectId (unless expanded using prop)
     - Form -> ObjectId (unless expanded using prop)
     - EmailTemplate -> ObjectId (unless expanded using prop)
     - ProjectTemplate -> ObjectId (unless expanded using prop)
     - Field - str
     - Number - float
     - Text (default) - str
    '''
    
    if type in ["User", "Contact", "File", "Form", "EmailTemplate", "ProjectTemplate"]:
        try:
            return ObjectId(x)
        except:
            return None
    
    if type == "Date":
        try:
            return datetime.fromisoformat(str(x))
        except:
            return None
    
    if type == "Number":
        try:
            return float(x)
        except:
            return 0
    
    # Default
    if not x:
        return ""
    
    return str(x)