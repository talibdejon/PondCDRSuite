### Send a email notification with the attachement on any new file in the CDR folder 

import utils

CDR_FOLDER=""

# For any file in the CDR_FOLDER:
# Calculate hash = utils.calculate_hash(filename)
# Check is utils.get_hash(hash)
# If it returns True (file found in the database), skip it and go to the next file
# It it returns False (new file found):
#   1) Put it to the database with the Arrived status - utils.set_hash(filename, utils.FileStatus.ARRIVED) 
#   2) Send email - utils.send_email(filename)
#   3) Change status to Sent - utils.update_status(hash, utils.FileStatus.SENT)
#   4) Go to the next file