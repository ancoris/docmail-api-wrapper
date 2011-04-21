from docmail import client
from docmail.appengine.client import Client

USERNAME = ''   # a valid docmail username
PASSWORD = ''   # a valid docmail password
SOURCE = ''     # a string to describe your app

# create a client ...
docmail_client = Client(USERNAME, PASSWORD, SOURCE)

# for further examples see example.py