from gladier import GladierBaseTool


def choose_topic(data):
    import random
    topics = [
        'cats',
        'dragons',
        'zoom meetings',
        'goto lines',
        'badly written code modules',
        'european swallows',
        'african swallows',
    ]
    random_topic = random.randint(0, len(topics))
    return data.get('topic') or topics[random_topic]


def agree_with_topic(data):
    import random
    responses = [
        '{topic} are great!',
        "{topic} are the reason I'm the programmer I am today.",
        'I would never have graduated collage if not for {topic}.',
        'I have never encountered {topic}, but I have herd good things.'
    ]
    random_response = random.randint(0, len(responses) - 1)
    topic = data.get('topic', 'awkward silences')
    response = responses[random_response]
    return response.format(topic=topic)


def disagree_with_topic(data):
    import random
    responses = [
        '{topic} are stupid.',
        'If not for {topic}, my code would be bug free!',
        'My life was carefree before {topic}, but now they\'re the reason I need therapy.'
    ]
    random_response = random.randint(0, len(responses) - 1)
    topic = data.get('topic', 'awkward silences')
    response = responses[random_response]
    return response.format(topic=topic)


class HelloConversation(GladierBaseTool):

    flow_definition = {
        'Comment': 'Hello Gladier with a few different flow states.',
        'StartAt': 'ChooseTopic',
        'States': {
            'ChooseTopic': {
                'Comment': 'Say something to start the conversation',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'ExceptionOnActionFailure': False,
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': '$.input.choose_topic_funcx_id',
                        'payload': {
                            'topic.$': '$.input.topic',
                        }
                    }]
                },
                'ResultPath': '$.ChooseTopic',
                'WaitTime': 300,
                'Next': 'AgreeWithTopic',
            },
            'AgreeWithTopic': {
                'Comment': 'Agree with the topic',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'ExceptionOnActionFailure': False,
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': '$.input.agree_with_topic_funcx_id',
                        'payload': {
                            'topic.$': '$.ChooseTopic.details.result',
                        }
                    }]
                },
                'ResultPath': '$.AgreeWithTopic',
                'WaitTime': 300,
                'Next': 'DisagreeWithTopic',
            },
            'DisagreeWithTopic': {
                'Comment': 'Disagree with the topic.',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'ExceptionOnActionFailure': False,
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': '$.input.disagree_with_topic_funcx_id',
                        'payload': {
                            'topic.$': '$.ChooseTopic.details.result',
                        }
                    }]
                },
                'ResultPath': '$.DisagreeWithTopic',
                'WaitTime': 300,
                'End': True,
            },
        }
    }

    required_input = [
        'topic',
        'funcx_endpoint_non_compute'
    ]

    flow_input = {
        'topic': '',
    }

    funcx_functions = [
        choose_topic,
        agree_with_topic,
        disagree_with_topic,
    ]
