import httplib2
import email
import base64
from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run


def GetGoogleService(user_id='me'):
    # Path to the client_secret.json file downloaded from the Developer Console
    CLIENT_SECRET_FILE = 'client_secret.json'

    # Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

    # Location of the credentials storage file
    STORAGE = Storage('gmail.storage')

    # Start the OAuth flow to retrieve credentials
    flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
    http = httplib2.Http()

    # Try to retrieve credentials from storage or run the flow to generate them
    credentials = STORAGE.get()
    if credentials is None or credentials.invalid:
      credentials = run(flow, STORAGE, http=http)

    # Authorize the httplib2.Http object with our credentials
    http = credentials.authorize(http)

    # Build the Gmail service from discovery
    gmail_service = build('gmail', 'v1', http=http)

    return gmail_service


def ListMessagesWithLabels(service, user_id, label_ids=[]):
    try:
        response = service.users().messages().list(userId=user_id,
                                                   labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,
                                                       labelIds=label_ids,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def GetMessage(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id,
                                                 id=msg_id,
                                                 format='raw').execute()

        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_string(msg_str)

        return mime_msg
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
