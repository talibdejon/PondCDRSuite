### Declare the supplementary methods

from enum import Enum
import database

HASH_LENGTH = ""
EMAIL_TO_SEND= ""
SMTP_SERVER= ""
SMTP_PORT= ""

class FileStatus(Enum):
    ARRIVED = "Arrived"
    SENT = "Sent" 
    DELIVERED = "Delivered"
    REMOVED = "Removed"

def calculate_hash(filename): 
    """ 
    Accept a filename and return a hash  
    """
    pass
    return ""

def get_hash(hash):
    """ 
    Accept a filename and return its hash from the database 
    """ 
    pass
    return None 

def set_hash(filename, FileStatus):
    """ 
    Accept a filename and add its hash to the database 
    """
    pass
    id = 0
    return id

def update_status(hash, FileStatus):
    """
    Accept a hash and a new status. Return True by success
    """
    pass
    return True

def send_email(filename):
    """ 
    Accept a filename and send a email with the file attached. Return True by success
    """
    pass
    return True
    