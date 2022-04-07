import json
from webhook_message_builder import *


def slack_message_formatter(userid, querydata, action="", querydata2={}):

    # NOTE: its imortant to have at least one blank space in the response data
    # otherwise Slack will not render the message.

    responsedata = " "
    responsedata2 = " "
    user_thumbnail = ("https://avatars.slack-edge.com/2019-03-21"
                      "/585452480903_b80d9b84e0b8cc06b80b_512.jpg")
    title = ""
    n = 1
    pretext = ""
    footer = ""

    print "This is an action in text formatter: " + action

    try:
        if (action == "filters"):
            if querydata:
                print "filters"
            else:
                print "NO FILTERS"

            pretext = ("Filter list for {user}:".
                       format(user=userid))

            title = ("*[Note]* Slack truncates any message length over 40k."
                     " This may not be the full list.")
            if querydata:
                for element in querydata['filter']:

                    # only gather 20 filters otherwise the script could timeout
                    if n == 21:
                        break

                    if (n % 2) == 0:

                        responsedata2 += ("_#{n}_\n *Criteria:* \n"
                                          " _{criteria}_ \n \n *Action*:\n "
                                          "_{action}_ \n \n".format(
                                                            action=str(
                                                                json.dumps(
                                                                    element[
                                                                      'action'
                                                                    ])),
                                                            n=n,
                                                            criteria=str(
                                                                json.dumps(
                                                                    element[
                                                                     'criteria'
                                                                        ]))))

                    else:
                        responsedata += ("_#{n}_\n *Criteria:* \n"
                                         " _{criteria}_ \n"
                                         "\n *Action*:\n"
                                         " _{action}_ "
                                         "\n \n".format(
                                                        action=str(
                                                          json.dumps(element[
                                                              'action'])),
                                                        n=n,
                                                        criteria=str(
                                                                    json.dumps(
                                                                     element[
                                                                      'crite'
                                                                      'ria']))
                                                                      ))
                    n += 1
            else:
                responsedata = ("{user} does *not* appear to have any "
                                "filters.".format(user=userid))

        elif (action == "labels"):
            # NOTE:  Everyone has at least one mail label

            title = ("*[Note]* Results reflect only the first 50 labels."
                     " This may not be the full list.")

            responsedata = "*Name:* \n"
            responsedata2 = "*Type:* \n"

            print querydata

            for element in querydata['labels']:

                if n == 50:
                    break

                pretext = ("Label list for {user}:".
                           format(user=userid))

                responsedata = responsedata + (
                               "_{name}_ \n".
                               format(name=element.get('name')))

                responsedata2 = responsedata2 + (
                               " _{type}_ \n".
                               format(type=element.get('type')))
                n += 1

        elif (action == "forwarding"):

            pretext = "Forwarding settings for {user}:".format(user=userid)
            title = "{user}'s forwarding settings:".format(user=userid)

            if querydata:

                for element in querydata['forwardingAddresses']:

                    if (n % 2) == 0:
                        responsedata2 = responsedata2 + (
                                        "\n {n}. *Email:* {email} \n     "
                                        "*Enabled:* {enabled}\n".format(
                                            n=n,
                                            email=element.get(
                                                'forwardingEmail'),
                                            enabled=element.get(
                                                'verificationStatus')))
                    else:
                        responsedata = responsedata + (
                                        "\n {n}. *Email:* {email} \n     "
                                        "*Enabled:* {enabled}\n".format(
                                            n=n,
                                            email=element.get(
                                                'forwardingEmail'),
                                            enabled=element.get(
                                                    'verificationStatus')))
                    n += 1
            else:

                responsedata = ("{user} has *no* forwarding addresses"
                                "in GMail".format(user=userid))

        elif (action == "sendas"):
            pretext = ("Send-As settings for {user}:".
                       format(user=userid))
            title = "{user}'s sendAs settings:".format(user=userid)

            for element in querydata['sendAs']:

                responsedata = responsedata + ("\n _{n}_. *Email:* "
                                               "{email}\n*     Display Name:*"
                                               " {name}"
                                               "\n".
                                               format(
                                                n=n,
                                                name=element.get(
                                                 'displayName'),
                                                email=element.get(
                                                 'sendAsEmail')))
                n += 1

        elif (action == "imap"):

            pretext = "The IMAP settings for {user}:".format(user=userid)
            title = "{user}'s IMAP settings:".format(user=userid)

            responsedata = ("*Enabled:*"
                            " _{enabled}_\n*Expunge Behavior:* _{expunge}_\n"
                            "*Auto Expunge:* _{auto}_ \n".
                            format(expunge=querydata.get('expungeBehavior'),
                                   enabled=querydata.get('enabled'),
                                   auto=querydata.get('autoExpunge')))

        elif (action == "vacation"):

            element = querydata
            pretext = "The Vacation settings for {user}:".format(user=userid)
            title = "{user}'s Vacation settings:".format(user=userid)

            if (element.get('enableAutoReply')):
                print "autoreply"
                responsedata = ("*Enabled:* _True_ \n"
                                "*Subject:* _{subject}_ \n"
                                "*Text:* _{text}_ \n"
                                .format(
                                    subject=element.get('responseSubject'),
                                    text=element.get('responseBodyPlainText')))
            else:
                responsedata = ("{user} has *no* Vacation settings configured"
                                " in GMail".format(user=userid))

        elif (action == "delegates"):

            title = "{user}'s delegates:".format(user=userid)

            if (querydata.get('delegates')):
                pretext = ("Here is a list of delegates for {user}:".
                           format(user=userid))

                for element in querydata['delegates']:
                    responsedata = responsedata + (
                                   "_{n}_. *Email:* _{email}_\n"
                                   "*      Status:* _{verification}_"
                                   "\n\n".format(
                                    n=n, email=element.get('delegateEmail'),
                                    verification=element.get(
                                     'verificationStatus')))
                    n += 1
            else:
                pretext = ("{user} has no delegates authorized".format(
                                                                user=userid))
                responsedata = (" *Delegates:* _none_"
                                "\n".format(user=userid))

        elif (action == "pop"):
            element = querydata
            pretext = "POP settings for {user}:".format(user=userid)
            footer = "Account: {user}".format(user=userid)
            title = "{user}'s POP settings:".format(user=userid)

            responsedata = ("*Status:* _{accesswindow}_"
                            "\n*Behavior:* _{disposition}_".
                            format(accesswindow=element.get('accessWindow'),
                                   disposition=element.get('disposition')))

        elif (action == "userinfo"):

            print "at userinfo"

            element = querydata

            emailstring = ""
            departmental = "False"
            user_fullname = ""
            user_disabled = ""
            user_primaryemail = ""
            user_mailboxsetup = ""
            user_otheremails = ""
            user_lastlogin = ""
            user_suspensionreason = ""
            user_thumbnailphotourl = ""
            user_creationtime = ""
            user_orgunitpath = ""

            user_fullname = element['name'].get('fullName')
            user_disabled = element.get('suspended')
            user_primaryemail = element.get('primaryEmail')
            user_mailboxsetup = element.get('isMailboxSetup')

            if (element.get('thumbnailPhotoUrl')):
                user_thumbnail = element.get('thumbnailPhotoUrl')

            user_otheremails = element.get('emails')
            user_lastlogin = element.get('lastLoginTime')
            user_suspensionreason = element.get('suspensionReason')
            user_thumbnailphotourl = element.get('thumbnailPhotoUrl')
            user_creationtime = element.get('creationTime')

            if (element.get('orgUnitPath') == '/Department accounts'):
                pretext = ("{user} is a Shared Departmental "
                           "Account".format(user=userid))
            else:
                pretext = ("{user} is a user account:".format(user=userid))

            user_orgunitpath = element.get('orgUnitPath')

            for emails in user_otheremails:
                emailstring = emailstring + emails['address'] + ", "
                print emailstring

            print "before response"
            title = ("{full}'s Google Info".format(full=user_fullname))
            responsedata = ("*Full Name:* _{full}_\n"
                            "*Suspended:* _{susp}_\n"
                            "*Email:* _{email}_ \n"
                            "*Mailbox Setup:* _{mailbox}_\n\n"
                            "*Other Emails:*\n{otheremails}"
                            "\n".format(full=user_fullname,
                                        susp=user_disabled,
                                        email=user_primaryemail,
                                        mailbox=user_mailboxsetup,
                                        otheremails=emailstring))

            responsedata2 = ("*Lastlogin:* {lastlogin}\n"
                             "*Org:* {org}\n"
                             "*Creation:* {creation}\n"
                             "*Suspension Reason:* {reason}").format(
                                            lastlogin=user_lastlogin,
                                            org=user_orgunitpath,
                                            creation=user_creationtime,
                                            reason=user_suspensionreason)
        elif (action == "getapps"):
            title = ("Google Workplace Apps Authorized by "
                     "{user}".format(user=userid))
            pretext = "{user}'s Authorized Google Apps".format(user=userid)
            print "at getaps"
            app_name = ""

            responsedata = "*Name:* \n"

            element = querydata['items']

            for item in querydata['items']:
                name = item.get('displayText')
                responsedata += ("_{n}._ {name} \n".format(n=n, name=name))
                n += 1

        elif (action == "usagereport"):
            element = querydata

            account_type = ""
            account_drivespace = ""
            account_firstname = ""
            account_photospace = ""
            account_lesssecure = ""
            account_lastname = ""
            account_authorized = ""
            account_creation = ""
            account_total_quota = ""
            account_used_quota = ""
            account_used_quota_percet = ""
            account_gmail_quota = ""

            print "at usage info"
            print element

            account_type = element['usageReports'][0]['entity']
            account_type = account_type.get('type')

            account_drivespace = (element['usageReports'][0]['parameters'][1]
                                  ['intValue'])
            print (account_drivespace)
            account_gmail_quota = (element['usageReports'][0] ['parameters'][3]
                                  ['intValue'])
            print (account_gmail_quota)
            account_firstname = (element['usageReports'][0]['parameters'][2]
                                 ['stringValue'])
            account_photospace = (element['usageReports'][0]['parameters'][4]
                                  ['intValue'])
            account_lesssecure = (element['usageReports'][0]['parameters'][5]
                                  ['boolValue'])
            account_lastname = (element['usageReports'][0]['parameters'][6]
                                ['stringValue'])
            account_authorized = (element['usageReports'][0]['parameters'][7]
                                  ['intValue'])
            account_creation = (element['usageReports'][0]['parameters'][8]
                                ['datetimeValue'])
            account_total_quota = (element['usageReports'][0]['parameters'][11]
                                   ['intValue'])
            account_used_quota = (element['usageReports'][0]['parameters'][12]
                                  ['intValue'])
            account_used_quota_percent = (element['usageReports'][0]
                                          ['parameters'][13]['intValue'])


            title = "Email: {userid}".format(userid=userid)
            pretext = ("The Usage information for {first} {last}:").format(
                                                    first=account_firstname,
                                                    last=account_lastname)

            print account_gmail_quota

            responsedata = ("*Full Name:* {first} {last}\n"
                            "*Account Type:* {account}\n"
                            "*Creation Date:* {creation}\n"
                            "*Less Secure Apps:* {lesssecure}\n"
                            "*Drive Used in MB:* {drivespace}"
                            "\n".format(first=account_firstname,
                                        last=account_lastname,
                                        account=account_type,
                                        creation=account_creation,
                                        lesssecure=account_lesssecure,
                                        drivespace=account_drivespace))

            responsedata2 = ("*Photos stored in MB:* {photospace}\n"
                             "*Gmail used in MB:* {gmailspace}\n" 
                             "*Number of Authorized Apps:* {authorized}\n"
                             "*Total Quota:* {quota}\n"
                             "*Total Quota Used:* {quotaused}\n"
                             "*Quota Percent used:* {quotapercent}".format(
                                    photospace=account_photospace,
                                    authorized=account_authorized,
                                    quota=account_total_quota,
                                    gmailspace=account_gmail_quota,
                                    quotaused=account_used_quota,
                                    quotapercent=account_used_quota_percent))

        else:
            responsedata = str(json.dumps(querydata, indent=0))
    except Exception, e:
        return {"fulfillmentText": ">  *_Invalid User:_* Unable to find info "
                "for {user}. Check the formatting of the uniqname and try "
                "again.".format(user=userid)}
        pass

    # changing footer icon or collor will override Collaby's defaults
    # def slack_webhook_constructer
    # (userid,pretext,text,footer,footer_icon,color)

    print "right before return"
    return slack_webhook_constructer(userid, pretext, responsedata, footer,
                                     title, user_thumbnail, responsedata2)


def hangouts_message_formatter(userid, querydata, action=""):
    n = 1
    responsedata = ""
    topLabel = ""
    bottomLabel = ""
    title = ""
    subtitle = "Account: {user}".format(user=userid)

    try:
        if (action == "filters"):
            title = "Email Filters:"
            topLabel = "Top of filter list for {user}".format(user=userid)
            bottomLabel = "End of filter list for {user}".format(user=userid)
            for element in querydata['filter']:

                responsedata = responsedata + (
                 "\n <i>#{n}</i> \n<b>Criteria:</b>\n<i>{criteria}</i>\n \n"
                 "<b>Action:</b>\n<i>{action}</i>\n \n-----------------\n".
                 format(n=n, criteria=str(json.dumps(element['criteria'])),
                        action=str(json.dumps(element['action']))))

                n += 1

        elif (action == "labels"):
            title = "GMail labels:"
            topLabel = "Top of label list for {user}".format(user=userid)
            bottomLabel = "End of label list for {user}".format(user=userid)
            for element in querydata['labels']:

                responsedata = responsedata + (
                               "\n <i>#{n}</i> \n<b>name:</b> <i>{name}</i>"
                               "\n<b>type:</b> <i>{type}</i>"
                               "\n-----------------".format(
                                n=n, name=element.get('name'),
                                type=element.get('type')))
                n += 1

        elif (action == "forwarding"):
            title = "Forwarding settings:"
            element = querydata

            if (element.get('enabled')):

                responsedata = ("\n<b>Email Address:</b> <i>{email}</i>\n"
                                "<b>Enabled:</b> <i>{enabled}</i>\n"
                                "<b>Disposition:</b> <i>{disposition}</i> "
                                "\n \n".format(
                                 email=element.get('emailAddress'),
                                 enabled=element.get('enabled'),
                                 disposition=element.get('disposition')))
            else:
                responsedata = "<b>Forwarding:</b> <i>disabled</i>"

        elif (action == "sendas"):
            title = "SendAs settings:"
            for element in querydata['sendAs']:

                responsedata = responsedata + (
                               "\n<i>#{n}</i> \n<b>Email:</b> "
                               "<i>{email}</i>\n"
                               "<b>Display Name:</b> "
                               "<i>{name}</i>"
                               "\n-----------------".
                               format(n=n, name=element.get('displayName'),
                                      email=element.get('sendAsEmail')))

                n += 1

        elif (action == "pop"):
            title = "POP Settings:"
            element = querydata

            responsedata = ("<b>Enabled status:</b><i>{accesswindow}</i>\n"
                            "<b>Behavior:</b><i>{disposition}</i>".
                            format(accesswindow=element.get('accessWindow'),
                                   disposition=element.get('disposition')))

        elif (action == "imap"):
            title = "IMAP settings:"
            element = querydata

            responsedata = ("<b>Enabled:</b> <i>{enabled}</i>\n"
                            "<b>Expunge Behavior:</b> <i>{expunge}</i>\n"
                            "<b>Auto Expunge:</b> <i>{auto}</i>".
                            format(expunge=element.get('expungeBehavior'),
                                   enabled=element.get('enabled'),
                                   auto=element.get('autoExpunge')))

        elif (action == "vacation"):
            title = "GMail Vacation Settings:"
            element = querydata

            if (element.get('enableAutoReply')):
                responsedata = ("<b>Enabled:</b> <i>True</i> \n"
                                "<b>Subject:</b> <i>{subject}</i> \n"
                                "<b>Text:</b> <i>{text}</i>"
                                .format(
                                    subject=element.get('responseSubject'),
                                    text=element.get('responseBodyPlainText')))
            else:
                responsedata = ("GMail Vacation Settings for {user} are"
                                " <b>disabled</b>".format(user=userid))

        elif (action == "delegates"):
            title = "Delegates:"
            if (querydata.get('delegates')):
                for element in querydata['delegates']:

                    responsedata = responsedata + (
                     "<i>#{n}</i> \n<b>Delegate Email:</b><i>{email}</i>\n"
                     "<b>Verification Status:</b> <i>{verification}</i>\n"
                     "-----------------".format(
                      n=n, email=element.get('delegateEmail'),
                      verification=element.get('verificationStatus')))

                    n += 1
            else:
                responsedata = "\n<b>Delegates:</b> <i>none</i>.\n \n"

        elif (action == "isshared"):
            title = "Shared Account?"
            element = querydata
            response = "Account: {user}".format(user=userid)
            subtitle = "Exists as personal or shared"

            responsedata = ("<b>Email:</b><i>{email}</i>\n"
                            "<b>Message Total:</b> <i>{messages}</i>".format(
                             messages=element.get('messagesTotal'),
                             email=element.get('emailAddress')))

        else:
            responsedata = str(json.dumps(querydata, indent=0))
    except Exception, e:
        print e
        pass

    content = "<font color='#6CAFEE'>{data}".format(data=responsedata)

    # setting imageURL and imageStyle will override Collaby's defaults
    # hangouts_webhook_constructer(title="",subtitle="",topLabel="",
	#                              content="",bottomLabel="",
    #                              imageStyle,imageUrl")

    return hangouts_webhook_constructer(userid, title, subtitle,
                                        topLabel, content, bottomLabel)


def uknownagent_text_formatter(userid, querydata, response):

    print "unknown agent"

    querydata = querydata
    querydata = str(json.dumps(querydata, indent=2))

    querydata = querydata.replace('{', ' ')
    querydata = querydata.replace('}', ' ')
    querydata = querydata.replace(',', '')
    querydata = querydata.replace('"', '')
    querydata = querydata.replace('[', ' ')
    querydata = querydata.replace(']', ' ')

    unknownagentresponse = "{response} {querydata}".format(response=response,
                                                           querydata=querydata)

    return {"fulfillmentText": unknownagentresponse}


def batch_hangouts_message_formatter(userid, delegates_query, imap_query,
                                     forwarding_query, sendas_query, pop_query,
                                     action=""):

    # for when you want to combine more than one call into one output.
    delegatesresponse = ""
    imapresponse = ""
    forwardingresponse = ""
    sendasresponse = ""

    if (action == "security"):

        print "security"
        element = delegates_query
        if (element.get('delegates')):
            for element in delegates_query['delegates']:

                delegatesresponse += (
                            "<i>Delegate Settings:</i>\n------------\n"
                            "<b>Delegate Email:</b><i>{email}</i>\n"
                            "<b>Verification Status:</b> <i>{verification}</i>"
                            "\n------------\n".format(
                             user=userid,
                             email=element.get('delegateEmail'),
                             verification=element.get('verificationStatus')))

        else:
            response = ("{user} has no Delegate addresses setup within their "
                        "account:".format(user=userid))

            delegatesresponse = ("<i>Delegate Settings:\n------------\n "
                                 "<b>Delegates:</b> <i>none</i>"
                                 "\n------------\n".format(user=userid))

        element = forwarding_query
        if (element.get('enabled')):
            print "forwarding got"

            forwardingresponse = (
                               "<i>Forwarding Settings:</i>\n------------\n"
                               "<b>Email Address:</b><i>{email}</i>\n"
                               "<b>Enabled:</b><i>{enabled}</i>\n"
                               "<b>Disposition:</b> <i>{disposition}</i>"
                               "\n------------\n\n".
                               format(
                                user=userid,
                                email=element.get('emailAddress'),
                                enabled=element.get('enabled'),
                                disposition=element.get('disposition')))
        else:
            forwardingresponse = ("<i>Forwarding Settings:</i>\n------------\n"
                                  "<b>Forwarding:</b><i>disabled</i>"
                                  "\n------------\n".format(user=userid))

        for element in sendas_query['sendAs']:

            sendasresponse += ("<i>Send-as Settings:</i>\n------------\n"
                               "<b>Email:</b> <i>{email}</i>\n"
                               "<b>Display Name:</b><i>{name}</i>"
                               "\n------------\n".
                               format(user=userid,
                                      name=element.get('displayName'),
                                      email=element.get('sendAsEmail')))

        element = pop_query

        popresponse = ("<i>POP Settings:</i>\n------------\n<b>"
                       "Enable status:</b><i>{accesswindow}</i>\n"
                       "<b>Behavior:</b><i>{disposition}</i>\n------------\n".
                       format(accesswindow=element.get('accessWindow'),
                              disposition=element.get('disposition')))

        element = imap_query

        imapresponse = ("<i>IMAP Settings:</i>\n------------\n<b>Enabled:</b>"
                        "<i>{enabled}</i>\n<b>Expunge Behavior:</b>"
                        "<i>{expunge}</i>\n<b>Auto Expunge:</b><i>{auto}</i>"
                        "\n------------\n ".format(
                                       user=userid,
                                       expunge=element.get('expungeBehavior'),
                                       enabled=element.get('enabled'),
                                       auto=element.get('autoExpunge')))

    title = "Security Checklist"
    subtitle = "Account: {user}".format(user=userid)

    content = ("<font color='#6CAFEE'>{delegatesresponse}\n{imapresponse}\n"
               "{popresponse}\n{sendasresponse}\n{forwardingresponse}</font>"
               "<font color='#DCDCDC'>--------------------------------------"
               "---------------------------------\n</font>"
               "<font color='#006400'>[note] To verify filters paste:\n<b>"
               "<i>get filters for {user}</font>".format(
                                   popresponse=popresponse, user=userid,
                                   forwardingresponse=forwardingresponse,
                                   delegatesresponse=delegatesresponse,
                                   imapresponse=imapresponse,
                                   sendasresponse=sendasresponse))

    topLabel = ""
    bottomLabel = ""

    # setting imageURL and imageStyle will override Collaby's defaults
    # hangouts_webhook_constructer(userid="",title="",subtitle="",topLabel="",
    # content="",bottomLabel="",imageStyle="AVATAR",
    # imageUrl="dest")

    return hangouts_webhook_constructer(userid, title, subtitle,
                                        topLabel, content, bottomLabel)


def batch_slack_message_formatter(userid, delegates_query, imap_query,
                                  forwarding_query, sendas_query,
                                  pop_query, action=""):

    delegatesresponse = ""
    imapresponse = ""
    forwardingresponse = ""
    sendasresponse = ""
    popresponse = ""
    response = ""
    responsedata = ""
    title = ""
    responsedata2 = ""
    thumbnail = ("https://avatars.slack-edge.com/2019-03-21/"
                 "585452480903_b80d9b84e0b8cc06b80b_512.jpg")
    n = 0

    print "batch"
    if (action == "security"):
        print action
        element = delegates_query
        if (element.get('delegates')):
            for element in delegates_query['delegates']:
                print element.get('verificationStatus')

                delegatesresponse += (
                    "\n *Delegate Settings:* \n"
                    "_Email:_ {email}\n"
                    "_Status:_ {verification}"
                    "\n".format(
                     user=userid, email=element.get('delegateEmail'),
                     verification=element.get('verificationStatus')))

        else:

            delegatesresponse = ("*Delegate Settings:* \n"
                                 "_Delegates:_ none \n".
                                 format(user=userid))

        element = forwarding_query
        if (element.get('enabled')):

            forwardingresponse = (
                "*Forwarding Settings:* \n"
                "_Email_ {email} \n _Enabled:_ {enabled}\n"
                "_Disposition:_ {disposition}\n".
                format(user=userid, email=element.get('emailAddress'),
                       enabled=element.get('enabled'),
                       disposition=element.get('disposition')))

        else:

            forwardingresponse = ("*Forwarding Settings:* \n"
                                  "_Forwarding:_ _disabled_\n".
                                  format(user=userid))

        element = pop_query

        popresponse = ("*POP Settings:* \n _Status:_ "
                       "{accesswindow} \n _Behavior:_  {disposition}"
                       "\n".format(
                        accesswindow=element.get('accessWindow'),
                        disposition=element.get('disposition')))
        n = 0
        for element in sendas_query['sendAs']:
            n += 1
            sendasresponse += ("*Send-as Settings {n}:* \n _Email:_"
                               " {email} \n _Display Name:_ {name} \n"
                               "\n".format(n=n,
                                           user=userid,
                                           name=element.get('displayName'),
                                           email=element.get('sendAsEmail')))

        element = imap_query

        imapresponse = ("*IMAP Settings:* \n"
                        "_Enabled:_  {enabled}"
                        "\n_Behavior:_ {expunge}\n"
                        "_Auto Expunge:_ {auto}\n".
                        format(user=userid,
                               expunge=element.get('expungeBehavior'),
                               enabled=element.get('enabled'),
                               auto=element.get('autoExpunge')))

    pretext = "Security Checklist for: {user}".format(user=userid)

    responsedata = ("{delegatesresponse}\n{popresponse}"
                    "\n{forwardingresponse}".format(
                                        popresponse=popresponse,
                                        forwardingresponse=forwardingresponse,
                                        delegatesresponse=delegatesresponse))

    responsedata2 = ("{imapresponse}\n{sendasresponse}\n".format(
                        imapresponse=imapresponse,
                        sendasresponse=sendasresponse))

    footer = ("[note] To verify filters paste: *_get filters for {user}_*"
              .format(user=userid))

    # changing footer icon or collor will override Collaby's defaults
    # slack_webhook_constructer(userid="", pretext="",text="", footer="",
    # footer_icon="destination", color="#6CAFEE")

    title = pretext

    return slack_webhook_constructer(userid, pretext, responsedata,
                                     footer, title, thumbnail, responsedata2)
