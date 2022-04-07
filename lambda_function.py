import threading
from google_account_info import *
import json
import os
import os.path
import sys
import signal
import boto3
from webhook_message_builder import *


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    print "Timeout exception in lambda_function."

    raise TimeoutException


def lambda_handler(event, context):
    responsemessage = ''' [ERROR]: I do not understanding your request.
    Try typing *help* to get more info'''
    print event  # logs to cloudwatch for any troubleshooting

    action = event['queryResult']['parameters']['Action']

    bot_agent = event['originalDetectIntentRequest']['source']
    user = event['queryResult']['parameters']['targetuser']
    user = user + os.environ['domain'] if '@' not in user else user

    querytext = event['queryResult']['queryText']
    querytext = querytext.lower()

    # print statements for debucking in Cloudwatch
    print "the agent is"+bot_agent
    print "the action is {action}".format(action=action)

    # start 4 second timer to throw an error so the code doesn't run over
    # Dialog Flow's 5 second limit.
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(0)
    signal.alarm(4)

    # the below text when active will check if the user is authorized to use
    # this bot. So far this only works in Slack so I have it disabled for now.

    auth_user = event['originalDetectIntentRequest']['payload']['data']['event']['user']

    if (auth_user not in os.environ['authorized']):
        responsemessage = "`[ERROR]: You are not authorized to tell Collaby what to do. If you wish to request access than you can send your slack ID ({slackid}) to rsauosci@umich.edu to be added to the ACL.`".format(slackid=auth_user)

        return {'fulfillmentText': responsemessage}


# --------{ Show Forwarding for a target user}-------
    if (action == "forwarding"):

        # start a timer that will alert before Dialoflow's 5 second limit

        try:
            service = buildService(user)
            response = getForwarding(service, user, bot_agent)

        except TimeoutException:
            if bot_agent == 'slack':
                text = ("Collaby can only handle requests that take less than"
                        " 4 seconds to complete. For some reason gathering"
                        " forwarding settings for {user} took longer then 4"
                        " seconds to complete. Please wait 5 seconds and try"
                        " again. If you see this errormultiple times thene"
                        " please verify that all Google services ar running"
                        " properly by checking: \n"
                        "`https://www.google.com/appsstatus` \n if you "
                        " continue to see issues contact the Collaboration"
                        " Team (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)

                return slack_webhook_constructer(user, "*Timeout Error*",
                                                 text, footer, "Forwarding")

            elif bot_agent == 'hangouts':
                content = (
                        " <font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete."
                        " This means {user} likely has too many filters for"
                        " Collaby to handle or servers are slow. Please wait"
                        " 5 seconds and try again. If you see this error"
                        " multiple times then please verify that all Google"
                        " services are running properly by checking: \n \n"
                        " https://www.google.com/appsstatus \n\n if you"
                        " continue to see issues contact the Collaboration"
                        " Team to geta list of filters.").format(user=user)

                subtitle = ("Account: {user}").format(user=user)

                return hangouts_webhook_constructer(user, "Timeout Error",
                                                    subtitle, "", content, "")

            else:
                return uknownagent_text_formatter(userid, filters)
        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        return response
# --------------------------------------------------------

    if action == "enablegoogle" and querytext == "yes":

        try:
            print user
            service = buildDirectoryService(user)
            response = setUserStatus(service, user, bot_agent)
            return response
        except TimeoutException:
            if bot_agent == 'slack':
                text = ("Collaby can only handle requests that take less than"
                        " 4 seconds to complete. For some reason gathering"
                        " forwarding settings for {user} took longer then 4"
                        " seconds to complete. Please wait 5 seconds and try"
                        " again. If you see this errormultiple times thene"
                        " please verify that all Google services ar running"
                        " properly by checking: \n"
                        "`https://www.google.com/appsstatus` \n if you "
                        " continue to see issues contact the Collaboration"
                        " Team (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)

                return slack_webhook_constructer(user, "*Timeout Error*",
                                                 text, footer, "Forwarding")
												 




# -------{ Show SendAs settings for a Target User}--------
    elif (action == 'sendas'):

        try:
            service = buildService(user)
            response = getSendas(service, user, bot_agent)

        except TimeoutException:
            if bot_agent == 'slack':
                text = (
                     " Collaby can only handle requests that take less than 4"
                     " seconds to complete. For some reason gathering send-as"
                     " settings for {user} took longer then 4 seconds. Please"
                     " wait 5 seconds and try again. If you see this error"
                     " multiple times then please verify that all Google"
                     " services are running properly by checking: \n"
                     " \n if you continue to see issues contact the"
                     " Collaboration`https://www.google.com/appsstatus` Team "
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                # def slack_webhook_constructer(userid,pretext,text,
                # footer,footer_icon,color)

                footer = "Account: {user}".format(user=user)
                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text,
                                                 footer,
                                                 "Sendas setting")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete."
                        " {user} likely has too many filters for Collaby to "
                        " handle or This means servers are slow. Please wait"
                        " 5 seconds and try again. If yousee this error"
                        " multiple times then please verify that allGoogle"
                        " services are running properly by checking: \n \n"
                        " https://www.google.com/appsstatus \n\nif you"
                        " continue to see issues contact the Collaboration"
                        " Team to geta list of filters.").format(user=user)

                subtitle = "Account: {user}".format(user=user)

                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)

        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        return response

# ------------------------------------------------------

# -------{Show Imap settings for a Target User}---------
    elif (action == 'getimap'):

        try:
            service = buildService(user)
            response = getImap(service, user, bot_agent)

        except TimeoutException:
            if bot_agent == 'slack':
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. Gathering IMAP settings"
                     " for {user} took longer then 4 seconds. Please wait"
                     " and try again. If you see this error multiple times"
                     " verify all Google services by checking:\n"
                     " please verify that `https://www.google.com/appsstatus`"
                     "  \n if you continue to see issues contact the"
                     " Collaboration Team"
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)
                return slack_webhook_constructer(
                                                 user,
                                                 "*Timeout Error*",
                                                 text, footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete."
                        " {user} likely has too many filters or servers "
                        " are slow. Please wait 5 seconds and try again. If"
                        " you see this error multiple times please verify that"
                        " all Google services are running properly by"
                        " checking: \n \n https://www.google.com/appsstatus"
                        " \n\n if you continue to see issues contact the "
                        " Collaboration Team to get a full list"
                        " of filters.").format(user=user)

                subtitle = "Account: {user}".format(user=user)
                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle, "",
                                                    content, "")

            else:
                return uknownagent_text_formatter(userid, filters)
        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        return response
# ------------------------------------------------------

# --------{Show Filters for a Target User}--------------
    elif (action == 'filters'):

        try:
            service = buildService(user)
            response = getFilters(service, user, bot_agent)

        except TimeoutException:
            signal.alarm(0)
            if bot_agent == 'slack':
                text = (
                     "Collaby can only handle requests that take less than"
                     " 5 seconds to complete. This means {user} likely has too"
                     " many filters for Collaby to handle. Please wait and"
                     " try again. If you see this error multiple times"
                     " then please verify that all Google services are running"
                     " by checking: \n `https://www.google.com/appsstatus`"
                     " \n if you continue to see issues contact the"
                     " Collaboration Team (<#C6T3MEMC6|inf-collab>) to get a"
                     " list of filters.").format(user=user)

                footer = "Account: {user}".format(user=user)
                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text,
                                                 footer,
                                                 "Filters Timeout")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete."
                        " {user} likely has too many filters or servers are"
                        " slow. Please wait 5 seconds and try again. If you"
                        " ysee this error multiple times then verify that all"
                        " Google services are running properly by checking:"
                        " \n \n https://www.google.com/appsstatus \n\n if"
                        " you continue to see issues contact the"
                        " Collaboration Team to get a list of"
                        " filters.").format(user=user)

                subtitle = "Account: {user}".format(user=user)
                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)
        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        return response
# -----------------------------------------------------

# --------{is the this a shared account?}--------------------
    elif (action == 'isshared'):

        try:
            service = buildDirectoryService(user)
            response = getIsShared(service, user, bot_agent)

        except TimeoutException:
            if bot_agent == 'slack':
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. For gathering Email settigns"
                     " for {user} took longer then 4 seconds. Please wait"
                     " and try again. If you see this error multiple times"
                     " please verify that all Google services are running"
                     " by checking: \n `https://www.google.com/appsstatus`"
                     " \n if you continue to see issues contact the"
                     " Collaboration Team (<#C6T3MEMC6|inf-collab>)."
                     ).format(user=user)

                footer = "Account: {user}".format(user=user)
                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text, footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete."
                        " {user} likely has too many filters. Please wait 5"
                        " seconds and try again. If you see this error"
                        " multiple times then please verify that all Google "
                        " services are running properly by checking: \n \n"
                        " https://www.google.com/appsstatus \n\n if you "
                        " continue to see issues contact the Collaboration "
                        " Team to get a list of filters.").format(user=user)

                subtitle = "Account: {user}".format(user=user)

                return hangouts_webhook_constructer(
                                                    user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")

            else:
                return uknownagent_text_formatter(userid, filters)
        except HttpError as err:
            return {'fulfillmentText': err}
        except Exception as err:
            print err
            if service.status == 401:
                print "error made it to here"
            return {'fulfillmentText': "not a shared account"}
        finally:
            signal.alarm(0)

        return response
# -----------------------------------------------------------

# --------{Show labels for a target user}--------------------
    elif (action == 'labels'):

        try:
            service = buildService(user)
            response = getLabels(service, user, bot_agent)

        except TimeoutException:
            if bot_agent == 'slack':
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. It is likely that {user} has"
                     " too many labels to gather within the time limit."
                     " Please wait and try again. If you see this error"
                     " multiple times then please verify that all Google"
                     " services are running properly by checking:"
                     " \n`https://www.google.com/appsstatus` \n if you "
                     " continue to see issues contact the Collaboration Team"
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)
                return slack_webhook_constructer(
                                                 user,
                                                 "*Timeout Error*",
                                                 text, footer,
                                                 "Labels Timeout")
            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to resolve."
                        " This means {user} likely has too many filters for"
                        " Collaby to handle or servers are slow. Please wait"
                        " 5 seconds and try again. If you see this error"
                        " multiple times then please verify that all Google "
                        " services are running properly by checking: \n \n"
                        " https://www.google.com/appsstatus \n\n you continue"
                        " to see issues contact the Collaboration Team to"
                        " get a list of filters.").format(user=user)

                subtitle = "Account: {user}".format(user=user)

                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)
        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)
        return response
# -----------------------------------------------------

# --------{Show pop settings}--------------------------
    elif (action == 'pop'):

        try:
            service = buildService(user)
            response = getPop(service, user, bot_agent)

        except TimeoutException:
            if bot_agent == 'slack':
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. Gathering POP settings"
                     " for {user} took longer then 4 seconds. Please wait"
                     " and try again. If you see this error multiple times "
                     " please verify that all Google services are running "
                     " properly by checking: \n "
                     " `https://www.google.com/appsstatus` \n if you continue "
                     " to see issues contact the Collaboration Team"
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)

                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text, footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle "
                        " requests that take less than 5 seconds to complete."
                        " means {user} likely has too many filters for Collaby"
                        " or servers are slow. Please wait 5 seconds and try"
                        " again. If you see this error multiple times then"
                        " verify that all Google services are running properly"
                        " by checking: \n \n"
                        " https://www.google.com/appss tatus \n\n if you"
                        " https://www.google.com/appsstatus \n\n if"
                        " Team to get a list of filters.").format(user=user)

                subtitle = "Account: {user}".format(user=user)
                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)
        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        return response
# -----------------------------------------------------

# --------{Show delegate settings}---------------------
    elif (action == 'delegates'):

        try:
            service = buildService(user)
            print ("service sort of built")
            response = getDelegates(service, user, bot_agent)

        except TimeoutException:
            if bot_agent == 'slack':
                text = (
                     " Collaby can only handle requests that take less than"
                     " 4 seconds to complete. Gathering IMAP settings"
                     " for {user} took longer then 4 seconds. Please wait"
                     " and try again. If you see this error multiple times"
                     " please verify that all Google services are running"
                     " by checking: \n`https://www.google.com/appsstatus`"
                     " \n if you continue to see issues contact the "
                     " Collaboration Team "
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)

                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text,
                                                 footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete."
                        " {user} likely has too many filters for Collaby"
                        " or servers are slow. Please wait and try again. If"
                        " you see this error multiple times please verify that"
                        " all Google services are running by checking: \n \n"
                        " https://www.google.com/appsstatus \n\n if you"
                        " continue tosee issues contact the Collaboration Team"
                        "  to get a list of filters.").format(user=user)

                subtitle = "Account: {user}".format(user=user)

                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)

        except HttpError as err:
            if err.resp.status == 400:
                return {'fulfillmentText': "Invalid Grant"}
            else:
                return {'fulfillmentText': "Error!: {err}".format(err=err)}
        except Exception, e:
            print "error: {e}".format(e=str(e))
            if str(e) == "invalid_grant: Invalid email or User ID":
                print "invalid grant"
                return {'fulfillmentText': " {user} is  not a valid email"
                                           " or user is"
                                           " disabled".format(user=user)}
        finally:
            signal.alarm(0)

        return response
# -----------------------------------------------------

# --------{Show security settings}---------------------
    elif (action == 'security'):

        try:
            service = buildService(user)
            response = getSecurityChecklist(service, user, bot_agent)

        except TimeoutException:
            print "Security timeout"
            if bot_agent == 'slack':
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. For some reason gathering IMAP"
                     " settings for {user} took longer then 4 seconds. Please "
                     " wait and try again. If you see this error multiple"
                     " times please verify that all Google services are"
                     " running properly by checking:"
                     " \n `https://www.google.com/appsstatus` \n"
                     " if you continue to see issues contact the"
                     " Collaboration Team"
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)
                print text
                footer = "Account: {user}".format(user=user)
                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text,
                                                 footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete. "
                        " This means {user} likely has too many filters"
                        " to handle or servers are slow. Please wait and try"
                        " again. If you see this error multiple times please"
                        " verify that all Google services are running by"
                        " checking: \n \n https://www.google.com/appsstatus"
                        " \n\n if you continue to see issues contact the"
                        " Collaboration Team to get a list of"
                        " filters.").format(user=user)

                subtitle = ("Account: {user}").format(user=user)

                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)
        return response

# --------{Show vacatiom settings}---------------------
    elif (action == 'vacation'):

        try:
            service = buildService(user)
            response = getVacation(service, user, bot_agent)
            print response
        except TimeoutException:

            if bot_agent == 'slack':
                print "vacation timeout"
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. For some reason gathering "
                     " settings for {user} took longer then 4 seconds. Please "
                     " wait and try again. If you see this error multiple"
                     " times please verify that all Google services are"
                     " running properly by checking:"
                     " \n `https://www.google.com/appsstatus` \n"
                     " if you continue to see issues contact the"
                     " Collaboration Team"
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)

                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text,
                                                 footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete. "
                        " This means {user} For some reason gaterhing vacation"
                        " settings for {user} took longer than 4 seconds. "
                        " Wait and try again. If you see this error multiple"
                        " times please verify that all Google services are"
                        " running properly by checking:"
                        " \n `https://www.google.com/appsstatus` \n"
                        " if you continue to see issues contact the"
                        " Collaboration Team"
                        ).format(user=user)

                subtitle = ("Account: {user}").format(user=user)

                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)

        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        return response
# -----------------------------------------

# --------{Show User settings}---------------------
    elif (action == 'userinfo'):

        try:
            service = buildDirectoryService(user)
            print "at response"
            response = getUserInfo(service, user, bot_agent)

        except TimeoutException:

            if bot_agent == 'slack':
                print "Userinfo Timeout"
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. For some reason gathering "
                     " settings for {user} took longer then 4 seconds. Please "
                     " wait and try again. If you see this error multiple"
                     " times please verify that all Google services are"
                     " running properly by checking:"
                     " \n `https://www.google.com/appsstatus` \n"
                     " if you continue to see issues contact the"
                     " Collaboration Team"
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)

                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text,
                                                 footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete. "
                        " This means {user} For some reason gaterhing vacation"
                        " settings for {user} took longer than 4 seconds. "
                        " Wait and try again. If you see this error multiple"
                        " times please verify that all Google services are"
                        " running properly by checking:"
                        " \n `https://www.google.com/appsstatus` \n"
                        " if you continue to see issues contact the"
                        " Collaboration Team"
                        ).format(user=user)

                subtitle = ("Account: {user}").format(user=user)

                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)

        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        print "final return"
        return response


# --------{Show user's Authorized apps}---------------------
    elif (action == 'getapps'):

        try:
            service = buildDirectoryService(user)
            print "at response"
            response = getAuthorizedApps(service, user, bot_agent)

        except TimeoutException:

            if bot_agent == 'slack':
                print "Userinfo Timeout"
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. For some reason gathering "
                     " settings for {user} took longer then 4 seconds. Please "
                     " wait and try again. If you see this error multiple"
                     " times please verify that all Google services are"
                     " running properly by checking:"
                     " \n `https://www.google.com/appsstatus` \n"
                     " if you continue to see issues contact the"
                     " Collaboration Team"
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)

                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text,
                                                 footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete. "
                        " This means {user} For some reason gaterhing vacation"
                        " settings for {user} took longer than 4 seconds. "
                        " Wait and try again. If you see this error multiple"
                        " times please verify that all Google services are"
                        " running properly by checking:"
                        " \n `https://www.google.com/appsstatus` \n"
                        " if you continue to see issues contact the"
                        " Collaboration Team"
                        ).format(user=user)

                subtitle = ("Account: {user}").format(user=user)

                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)

        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        print "final return"
        return response

    elif (action == 'usagereport'):
        signal.signal(signal.SIGALRM, timeout_handler)
        # start a 3 second timer that throws an exception if it takes too long
        signal.alarm(8)

        try:
            service = buildAdminService(user)
            print "at response"
            response = getUserUsage(service, user, bot_agent)

        except TimeoutException:

            if bot_agent == 'slack':
                print "Userinfo Timeout"
                text = (
                     "Collaby can only handle requests that take less than"
                     " 4 seconds to complete. For some reason gathering "
                     " settings for {user} took longer then 4 seconds. Please "
                     " wait and try again. If you see this error multiple"
                     " times please verify that all Google services are"
                     " running properly by checking:"
                     " \n `https://www.google.com/appsstatus` \n"
                     " if you continue to see issues contact the"
                     " Collaboration Team"
                     " (<#C6T3MEMC6|inf-collab>).").format(user=user)

                footer = "Account: {user}".format(user=user)

                return slack_webhook_constructer(user,
                                                 "*Timeout Error*",
                                                 text,
                                                 footer,
                                                 "#8B0000")

            elif bot_agent == 'hangouts':
                content = (
                        "<font color = '#8B0000'>Collaby can only handle"
                        " requests that take less than 5 seconds to complete. "
                        " This means {user} For some reason gaterhing vacation"
                        " settings for {user} took longer than 4 seconds. "
                        " Wait and try again. If you see this error multiple"
                        " times please verify that all Google services are"
                        " running properly by checking:"
                        " \n `https://www.google.com/appsstatus` \n"
                        " if you continue to see issues contact the"
                        " Collaboration Team"
                        ).format(user=user)

                subtitle = ("Account: {user}").format(user=user)

                return hangouts_webhook_constructer(user,
                                                    "Timeout Error",
                                                    subtitle,
                                                    "",
                                                    content,
                                                    "")
            else:
                return uknownagent_text_formatter(userid, filters)

        except HttpError as err:
            return {'fulfillmentText': err}
        finally:
            signal.alarm(0)

        print "final return"
        
        return response
