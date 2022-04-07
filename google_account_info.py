import csv
import argparse
import sys
import os
import yaml
import json
import googleapiclient.discovery
from json import load
from httplib2 import Http
from oauth2client.client import SignedJwtAssertionCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from textformatter import *
from base64 import b64decode, b64encode
import boto3
import signal

BackoffError = ("HTTP Error 500.  Google APIs require a Backoff try again in 5"
                "seconds")
ENCRYPTED = os.environ['private_key']

# Decrypt code should run once and variables stored outside of the function
# handler so that these are decrypted once per container
DECRYPTED = boto3.client('kms').decrypt(
    CiphertextBlob=b64decode(ENCRYPTED),
    EncryptionContext={'LambdaFunctionName': os.environ[
                       'AWS_LAMBDA_FUNCTION_NAME']})['Plaintext']

def setUserStatus(service, userid, bot_agent):

    directoryservice = service
    print userid

    try:
        user = directoryservice.users().get(userKey=userid).execute()
        user['suspended'] = 'False'
        directoryservice.users().update(userKey=userid, body=user).execute()
        print "set user status"
        print userid
        print user
        if bot_agent == 'slack':
            return slack_message_formatter(userid,
                                           user,
                                           "userinfo")
            #return {'fulfillmentText': "enabled account {user} . To view status type ```get user info for {user}```".format(user=userid)}
        if bot_agent == 'hangouts':
            return {'fulfillmentText': "enabling account {user}".format(user=userid)}
        else:
            return uknownagent_text_formatter(userid, getuserinfo)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        if err.resp.status == 400:
            return {"fulfillmentText": "Invalid Grant"}
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)} 
 

def getVacation(service, userid, bot_agent, action="vacation"):
    vacation = {}

    try:
        vacation = (service.users().settings().getVacation(
                    userId='{userid}'.format(userid=userid)).execute())

        print action
        print bot_agent

        if bot_agent == 'slack':
            return slack_message_formatter(userid, vacation, action)
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid, vacation, action)
        else:
            return uknownagent_text_formatter(userid, vacation)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                  user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getFilters(service, userid, bot_agent, action="filters"):
    filters = {}

    try:
        filters = service.users().settings().filters().list(
                  userId='{userid}'.format(userid=userid)).execute()
        if bot_agent == 'slack':
            return slack_message_formatter(userid, filters, "filters")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid, filters, "filters")
        else:
            return uknownagent_text_formatter(userid, filters)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getForwarding(service, userid, bot_agent):
    forwarding = {}

    try:
        forwarding2 = service.users().settings().getAutoForwarding(
                     userId='{userid}'.format(userid=userid)).execute()
        forwarding = service.users().settings().forwardingAddresses().list(
                  userId='{userid}'.format(userid=userid)).execute()

        print forwarding
        if bot_agent == 'slack':
            return slack_message_formatter(userid, forwarding, "forwarding")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid, forwarding, "forwarding")
        else:
            return uknownagent_text_formatter(userid, forwarding)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getSendas(service, userid, bot_agent):
    sendas = {}

    try:
        getsendas = service.users().settings().sendAs().list(
                    userId='{userid}'.format(userid=userid)).execute()
        if bot_agent == 'slack':
            return slack_message_formatter(userid, getsendas, "sendas")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid, getsendas, "sendas")
        else:
            return uknownagent_text_formatter(userid, getsendas)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getImap(service, userid, bot_agent):
    getimap = {}

    try:
        getimap = service.users().settings().getImap(userId=userid).execute()
        if bot_agent == 'slack':
            return slack_message_formatter(userid, getimap, "imap")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid, getimap, "imap")
        else:
            return uknownagent_text_formatter(userid, getimap)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getLabels(service, userid, bot_agent):
    getlabels = {}

    try:
        print "getting labels"
        getlabels = service.users().labels().list(userId='{userid}'.
                                                  format(userid=userid)
                                                  ).execute()
        if bot_agent == 'slack':
            return slack_message_formatter(userid, getlabels, "labels")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid, getlabels, "labels")
        else:
            return uknownagent_text_formatter(userid, getlabels)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getIsShared(service, userid, bot_agent):

    directoryservice = service

    try:
        getuserinfo = directoryservice.users().get(userKey=userid).execute()
        print "got user info"

        if bot_agent == 'slack':
            return slack_message_formatter(userid,
                                           getuserinfo,
                                           "userinfo")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid,
                                              getuserinfo,
                                              "userinfo")
        else:
            return uknownagent_text_formatter(userid, getuserinfo)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        if err.resp.status == 400:
            return {"fulfillmentText": "Invalid Grant"}
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getPop(service, userid, bot_agent):
    getpop = {}

    try:
        getpop = service.users().settings().getPop(userId='{userid}'.format(
                                                   userid=userid)).execute()
        if bot_agent == 'slack':
            return slack_message_formatter(userid, getpop, "pop")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid, getpop, "pop")
        else:
            return uknownagent_text_formatter(userid, getpop)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getDelegates(service, userid, bot_agent):
    getdelegates = {}

    try:
        getdelegates = service.users().settings().delegates().list(
                       userId='{userid}'.format(userid=userid)).execute()
        if bot_agent == 'slack':
            return slack_message_formatter(userid,
                                           getdelegates,
                                           "delegates")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid,
                                              getdelegates,
                                              "delegates")
        else:
            return uknownagent_text_formatter(userid, getdelegates)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        if err.resp.status == 400:
            return {"fulfillmentText": "Invalid Grant"}
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getSecurityChecklist(service, userid, bot_agent):
    securitychecklist = {}

    try:
        delegates_query = service.users().settings().delegates().list(
                          userId='{userid}'.format(userid=userid)).execute()
        print "delegates got"

        pop_query = service.users().settings().getPop(
                    userId='{userid}'.format(userid=userid)).execute()
        print "pop got"
        imap_query = service.users().settings().getImap(
                     userId=userid).execute()
        print "imap got"
        sendas_query = service.users().settings().sendAs().list(
                       userId='{userid}'.format(userid=userid)).execute()
        print "sends got"
        forwarding_query = service.users().settings().getAutoForwarding(
                           userId='{userid}'.format(userid=userid)).execute()
        print "forwarding got"
        if bot_agent == 'slack':
            return batch_slack_message_formatter(userid,
                                                 delegates_query,
                                                 imap_query,
                                                 forwarding_query,
                                                 sendas_query,
                                                 pop_query,
                                                 "security")
        if bot_agent == 'hangouts':
            return batch_hangouts_message_formatter(userid,
                                                    delegates_query,
                                                    imap_query,
                                                    forwarding_query,
                                                    sendas_query,
                                                    pop_query,
                                                    "security")
        else:
            print ("this is an unknown agent")
            return
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getUserInfo(service, userid, bot_agent):

    directoryservice = service

    try:
        getuserinfo = directoryservice.users().get(userKey=userid).execute()
        print "got user info"

        if bot_agent == 'slack':
            return slack_message_formatter(userid,
                                           getuserinfo,
                                           "userinfo")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid,
                                              getuserinfo,
                                              "userinfo")
        else:
            return uknownagent_text_formatter(userid, getuserinfo)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        if err.resp.status == 400:
            return {"fulfillmentText": "Invalid Grant"}
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getAuthorizedApps(service, userid, bot_agent):

    directoryservice = service

    try:
        getuserinfo = directoryservice.tokens().list(userKey=userid).execute()
        print "got user info"
        if bot_agent == 'slack':
            return slack_message_formatter(userid,
                                           getuserinfo,
                                           "getapps")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid,
                                              getuserinfo,
                                              "getapps")
        else:
            return uknownagent_text_formatter(userid, getuserinfo)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        if err.resp.status == 400:
            return {"fulfillmentText": "Invalid Grant"}
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def getUserUsage(service, userid, bot_agent):
    reportservice = service

    # Save this for reports action
    params = ('accounts:is_disabled,accounts:drive_used_quota_in_mb,'
              'accounts:gplus_photos_used_quota_in_mb,accounts:first_name,'
              'accounts:drive_used_quota_in_mb,'
              'accounts:is_less_secure_apps_access_allowed,accounts:last_name,'
              'accounts:num_authorized_apps,accounts:timestamp_creation,'
              'accounts:timestamp_last_login,accounts:timestamp_last_sso,'
              'accounts:total_quota_in_mb,accounts:used_quota_in_mb,'
              'accounts:used_quota_in_percentage,'
              'accounts:gmail_used_quota_in_mb')

    date = '2021-05-15'

    try:
        getuserinfo = service.userUsageReport().get(date=date, userKey=userid,
                                                    parameters=params
                                                    ).execute()
        print "got user info"

        if bot_agent == 'slack':
            return slack_message_formatter(userid,
                                           getuserinfo,
                                           "usagereport")
        if bot_agent == 'hangouts':
            return hangouts_message_formatter(userid,
                                              getuserinfo,
                                              "usagereport")
        else:
            return uknownagent_text_formatter(userid, getuserinfo)
    except HttpError as err:
        if err.resp.status == 500:
            return BackoffError
        if err.resp.status == 400:
            return {"fulfillmentText": "Invalid Grant"}
        elif err.resp.status == 404:
            print "404"
            return {"fulfillmentText": "> Sorry, {user} is not a valid "
                    "username in Google and no info could be found".format(
                                                                user=userid)}
        else:
            return {"fulfillmentText": "unkown error "
                    "{err}".format(err=err.resp.status)}


def buildService(user):
    TargetUser = user

    # sanitize owner
    TargetUser = (user + os.enviorn['domain']
                  if '@' not in TargetUser else TargetUser)

    privatekey = DECRYPTED
    privatekey = str(privatekey).replace('\\n', '\n')
    #clientemail = str(DECRYPTED_CEMAIL.encode('ascii'))
    clientemail = os.environ['client_email']

    credentials = SignedJwtAssertionCredentials(
        clientemail,
        privatekey,
        'https://mail.google.com/', sub=TargetUser)

    # Create an HTTP object or the Folder Owner, then feed it our credentials.
    http = Http()
    credentials.authorize(http)

    # Now that we're ready, build the folder owner 'service'
	# and the 'AdminServce'.
    try:
        print "building service"
        service = build('gmail', 'v1', http=http)
        print ("service built")
        return service
    except HttpError as err:
        print "error in build 1"
        return err
    except Exception as err:
        if err.status == 401:
            print "401 error!"
        return err
    except Exception as err:
        print err
        return err
    except:
        print "Error in build"
        return


def buildAdminService(user):
    TargetUser = user

    # sanitize owner
    TargetUser = (user + os.enviorn['domain']
                  if '@' not in TargetUser else TargetUser)

    privatekey = DECRYPTED
    privatekey = str(privatekey).replace('\\n', '\n')
    clientemail = os.environ['client_email']
   # clientemail = str(DECRYPTED_CEMAIL.encode('ascii'))

    # clientemail = os.environ['client_email']
    scopes = ('https://www.googleapis.com/auth/admin.reports.usage.readonly')

    credentials = SignedJwtAssertionCredentials(
        clientemail,
        privatekey,
        scopes,
        sub='admin-mgoogle@umich.edu')

    # Create an HTTP object or the Folder Owner, then feed it our credentials.
    http = Http()
    credentials.authorize(http)

    # Now that we're ready, build the folder owner 'service'
    # and the 'AdminServce'.
    try:
        print "building service"
        service = build('admin', 'reports_v1', http=http)
        print ("service built")
        return service
    except HttpError as err:
        print "error in build 1"
        return err
    except Exception as err:
        if err.status == 401:
            print "401 error!"
        return err
    except Exception as err:
        print err
        return err
    except:
        print "Error in build"
        return


def buildDirectoryService(user):
    TargetUser = user

    # sanitize owner
    TargetUser = (user + os.enviorn['domain']
                  if '@' not in TargetUser else TargetUser)

    privatekey = DECRYPTED
    privatekey = str(privatekey).replace('\\n', '\n')
    clientemail = os.environ['client_email']
    scopes = ('https://www.googleapis.com/auth/admin.directory.user.security '
              'https://www.googleapis.com/auth/admin.directory.user.readonly '
              'https://www.googleapis.com/auth/admin.directory.user')

    credentials = SignedJwtAssertionCredentials(
        clientemail,
        privatekey,
        scopes,
        sub='admin-mgoogle@umich.edu')

    # Create an HTTP object or the Folder Owner, then feed it our credentials.
    http = Http()
    credentials.authorize(http)

    # Now that we're ready, build the folder owner 'service'
    # and the 'AdminServce'.
    try:
        print "building service"
        service = build('admin', 'directory_v1', http=http)
        print ("service built")
        return service
    except HttpError as err:
        print "error in build 1"
        return err
    except Exception as err:
        if err.status == 401:
            print "401 error!"
        return err
    except Exception as err:
        print err
        return err
    except:
        print "Error in build"
        return

def main():
    # leaving arg parse for local testing.

    global logger
    global logpath
    global config

    # parser = argparse.ArgumentParser()
    # parser.add_argument("Action", help="Action the script will be taking.")
    # parser.add_argument("TargetUser", help="")

    # parser.add_argument("-c","--config",
    # help="The GAK congig to use.", default="/etc/google-admin-kit.yml")
    # env=parser.parse_args()

    # config = {}

    # service = buildService ('local-config.yml', env.TargetUser)
    # getForwarding (service, env.TargetUser)


if __name__ == '__main__':
    main()
