
class KGraphUtils:

    @staticmethod
    def create_message_tuples(messages):
        objects = []
        i = 0
        while i < len(messages):
            if messages[i]['type'] == 'http://vital.ai/ontology/haley-ai-kg#KGChatUserMessage':
                objects.append(messages[i])
            if messages[i]['type'] == 'http://vital.ai/ontology/haley-ai-kg#KGChatBotMessage':
                objects.append(messages[i])
            i += 1
        tuples = []
        i = 0
        while i < len(objects):
            user_msg = ""
            bot_msg = ""
            if objects[i]['type'] == 'http://vital.ai/ontology/haley-ai-kg#KGChatUserMessage':
                user_msg = objects[i].get('http://vital.ai/ontology/haley-ai-kg#hasKGChatMessageText')
                i += 1
                if i < len(objects):
                    if objects[i]['type'] == 'http://vital.ai/ontology/haley-ai-kg#KGChatBotMessage':
                        bot_msg = objects[i].get('http://vital.ai/ontology/haley-ai-kg#hasKGChatMessageText')
                        tuples.append((user_msg, bot_msg))
                    else:
                        tuples.append((user_msg, bot_msg))
            elif objects[i]['type'] == 'http://vital.ai/ontology/haley-ai-kg#KGChatBotMessage':
                bot_msg = objects[i].get('http://vital.ai/ontology/haley-ai-kg#hasKGChatMessageText')
                tuples.append((user_msg, bot_msg))
            i += 1
        return tuples
