def hangouts_webhook_constructer(userid="",title="",subtitle="",topLabel="",
                                 content="",bottomLabel="",imageStyle="AVATAR",
                                 imageUrl=("https://avatars.slack-edge.com/"
                                           "2019-03-21/585452480903_"
                                           "b80d9b84e0b8cc06b80b_512.jpg")):

  return {"fulfillmentMessages": [
    {
      "payload": {
        "hangouts": {
          "header": {
             "title": title,
             "subtitle": subtitle,
             "imageStyle": "AVATAR",
             "imageUrl": imageUrl
          },
          "sections": [
            {
              "widgets": [
                {
                  "keyValue": {
                     "topLabel": topLabel,
                      "content": content,
                      "contentMultiline": True,
                      "bottomLabel": bottomLabel
                  }
                   
                  }
                
              ]
            }
          ]
        }
      },
      "platform": "HANGOUTS",
      "lang": "en"
    },
    {
      "text": {
        "text": []
      },
      "lang": "en"
    }
  ]}
  
def slack_webhook_constructer2(userid="",pretext="",text="",footer="",title="", 
                              author_icon=(
                              "https://avatars.slack-edge.com/2019-03-21/"
                              "585452480903_b80d9b84e0b8cc06b80b_512.jpg"),
                              color="#6CAFEE",footer_icon=(
                              "https://avatars.slack-edge.com/2019-03-21/"
                              "585452480903_b80d9b84e0b8cc06b80b_512.jpg")):
                                
    print "fufill title"

    return {"fulfillmentMessages": [
   {
      "payload": {
        "slack": {
          "text": "",
          "attachments": [
           {
            "fallback": "Collaby Slack Fufillment",
            "color": color,
            "pretext": pretext,
            "author_name": title,
            "author_icon": str(author_icon),
            "text": text,
            "footer": footer,
            "footer_icon": footer_icon
           }
           ]
        }
      },
      "platform": "SLACK",
      "lang": "en"
    },
    {
      "text": {
        "text": [
          "Good day! What can I do for you today?"
        ]
      },
      "lang": "en"
   }
  ]}
  
def slack_webhook_constructer(userid=" ",pretext=" ",text=" ",footer="",title=" ", 
                              author_icon=(
                              "https://avatars.slack-edge.com/2019-03-21/"
                              "585452480903_b80d9b84e0b8cc06b80b_512.jpg"),
                              text2=" ",
                              color="#6CAFEE",footer_icon=(
                              "https://avatars.slack-edge.com/2019-03-21/"
                              "585452480903_b80d9b84e0b8cc06b80b_512.jpg")):
                                
    print "fufill title"
    title = title
    return {"fulfillmentMessages": [
   {
      "payload": {
        "slack": {
          "text": "",
          "attachments": [
	        {
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": pretext
			}
		},
				{
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": author_icon,
					"alt_text": "profile pic"
				},
				{
					"type": "mrkdwn",
					"text": title
				}
			]
		},
		{
		  "type": "divider"
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": text
				},
				{
					"type": "mrkdwn",
					"text": text2
				}
			]
		},
		{
		  "type": "divider"
		}
	]
},
           {
            "footer": footer,
            "footer_icon": footer_icon
           }
           ]
        }
      },
      "platform": "SLACK",
      "lang": "en"
    },
    {
      "text": {
        "text": [
          "Good day! What can I do for you today?"
        ]
      },
      "lang": "en"
   }
  ]}
  
  
