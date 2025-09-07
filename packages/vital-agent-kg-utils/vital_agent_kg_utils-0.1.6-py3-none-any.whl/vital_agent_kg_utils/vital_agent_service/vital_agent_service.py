
class VitalAgentService:
    pass

# interface and handler for websocket messages to/from service which cover
# searching for agents, such as when an agent needs to find another agent for help

# covers searching and getting from service db

# this should implement some new functions on AIMPMessageHandlerInf
# to provide a handler for websocket messages which would include replies to requests

# agent should then extend this instead of AIMPMessageHandlerInf to pick up this
# functionality

# this is implemented here because agent definitions use the KG domain
# and not only the AIMP domain

