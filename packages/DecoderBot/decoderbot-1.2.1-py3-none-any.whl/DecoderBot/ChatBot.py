import difflib
import random
import re
import datetime

class ChatBot:

    class ResponseTypeError(Exception):
        pass

    def __init__(self, name="My ChatBot", threshold=0.2):
        self.name = name
        self.nameResponse = f"My name is {self.name}"

        # Default responses
        self._responses = {
            "hello": ["Hey there, how are you?", "Howdy! How's your day going?", "Hello there!", "What's up?"],
            "bye": ["Goodbye! You can come here whenever you want.", "See you later!", "Take care!", "Bye bye!"]
        }

        # Important responses that always stay
        self._imp_responses = {
            "name": [self.nameResponse]
        }

        self.threshold = threshold

        # Merge important responses
        self._responses.update(self._imp_responses)

        # Optional synonyms (can expand)
        self.synonyms = {
            "hi": "hello",
            "hey": "hello",
            "yo": "hello",
            "goodbye": "bye",
            "see you": "bye",
            "later": "bye",
            "thx": "thanks",
            "thank u": "thanks"
        }

    # normalize keys, safe for strings only
    def normalize(self, text):
        if isinstance(text, str):
            text = text.lower().strip()
            return re.sub(r"[^\w\s]", "", text)
        return text

    # Train single message
    def train_for(self, message, reply):
        key = self.normalize(message)
        self._responses[key] = reply if isinstance(reply, list) else [reply]

    # Train from a dictionary
    def set_training(self, responses):
        if not isinstance(responses, dict):
            raise self.ResponseTypeError("set_training requires a dictionary")

        self._responses = {}
        for message, reply in responses.items():
            key = self.normalize(message)
            self._responses[key] = reply if isinstance(reply, list) else [reply]

        self._responses.update(self._imp_responses)

    # Add/update dictionary without clearing existing
    def train(self, responses):
        if not isinstance(responses, dict):
            raise self.ResponseTypeError("train requires a dictionary")

        for message, reply in responses.items():
            key = self.normalize(message)
            self._responses[key] = reply if isinstance(reply, list) else [reply]

    # Get Current Time
    def get_time(self):
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')}."

    # Exact response with random choice if list
    def get_response(self, message, m="Sorry, I can't give the answer to that message right now"):
        key = self.normalize(message)

        # Check if user asked about time anywhere in the message
        if "time" in key:
            return self.get_time()

        # Check synonyms first
        key = self.synonyms.get(message.lower(), key)
        resp = self._responses.get(key)
        if not resp:
            return m
        return random.choice(resp)

    # Closest match for typos
    def get_closest_response(self, message, m="Sorry, I can't give the answer to that message right now"):
        key = self.normalize(message)
        if "time" in key:
            return self.get_time()
        key = self.synonyms.get(message.lower(), key)
        a = difflib.get_close_matches(key, self._responses.keys(), n=1, cutoff=self.threshold)
        if a:
            resp = self._responses[a[0]]
            return random.choice(resp)
        return m

    # Reset training
    def reset_training(self):
        self._responses = {}
        self._responses.update(self._imp_responses)

    # Reset entire bot
    def reset_bot(self, name="My ChatBot", threshold=0.2):
        self.__init__(name=name, threshold=threshold)




class Data:
    def __init__(self):
        self.conversations = {
            "hello": ["Hey there!", "Hi!", "Hello! 👋", "Hey, how’s it going?"],
            "hi": ["Hello!", "Hi there!", "Hey!"],
            "hey": ["Hi!", "Hey there!", "What’s up?"],
            "yo": ["Yo! 👊", "What’s up?", "Hey!"],
            "good morning": ["Good morning to you!", "Morning! 🌞", "Have a great day ahead!"],
            "good afternoon": ["Good afternoon!", "Hope your day is going well!"],
            "good evening": ["Good evening!", "Evening! How was your day?"],
            "how are you": ["I’m just a bot, but I’m doing great!", "All good here, thanks for asking!", "I’m functioning as expected!"],
            "what's up": ["Just waiting for your message!", "Not much, what about you?", "Same old, same old 😅"],
        }

        self.thanks_and_bye = {
            "thank you": ["You're welcome!", "No problem!", "Anytime!", "Glad to help!"],
            "thanks": ["Sure thing!", "Happy to help!", "No worries!"],
            "bye": ["Goodbye! Take care!", "See you soon!", "Bye! Come back anytime!"],
            "see you": ["See you later!", "Catch you soon!"],
            "later": ["Later!", "Catch you later!", "See ya!"]
        }

        self.famous_people = {
            "who is elon musk": [
                "CEO of Tesla and SpaceX.",
                "The guy who makes rockets and electric cars 😅",
                "Founder of SpaceX, Tesla, and a few more companies."
            ],
            "who is bill gates": [
                "Co-founder of Microsoft.",
                "One of the richest people on Earth.",
                "Now mostly a philanthropist."
            ],
            "who is albert einstein": [
                "One of the greatest physicists ever.",
                "Famous for the theory of relativity.",
                "The E = mc² guy 😉"
            ],
        }

        self.brands = {
            "what is apple": [
                "A tech company known for iPhones, iPads, and Macs.",
                "Makers of iPhone and Mac.",
                "A company founded by Steve Jobs, Steve Wozniak, and Ronald Wayne."
            ],
            "what is google": [
                "The world's biggest search engine.",
                "Also owns YouTube, Android, and more.",
                "Basically the answer to everything online."
            ],
            "what is microsoft": [
                "Creators of Windows, Office, and Xbox.",
                "Tech giant founded by Bill Gates and Paul Allen.",
                "Makers of the Windows OS."
            ]
        }
        self.small_talk = {
            "how's your day": ["It's going great, thanks!", "All good here! How about you?", "Pretty good!"],
            "what's your favorite color": ["I like blue.", "Green is nice.", "I don't have eyes, but I like the idea of purple 😅"],
            "do you like music": ["I love all kinds of music!", "Yes! Music is amazing.", "I listen to data beats 😎"],
            "tell me a joke": ["Why did the scarecrow win an award? Because he was outstanding in his field!", "I told my computer I needed a break, and now it won't stop sending me Kit-Kat ads."],
            "what's your favorite movie": ["I love all kinds of movies!", "Yes! Movies are amazing.", "I watch data flicks 😎"],
            "what's your favorite book": ["I love all kinds of books!", "Yes! Books are amazing.", "I read data stories 😎"],
            "what's your favorite food": ["I don't eat, but I hear pizza is great!", "I love the idea of data sandwiches!", "Food is fuel, right?"],
            "tell me a fact": ["Did you know? Honey never spoils.", "Here's a fun fact: Bananas are berries, but strawberries aren't!", "Did you know? Octopuses have three hearts."],
            "tell me something interesting": ["Did you know? A group of flamingos is called a 'flamboyance.'", "Here's something cool: Honey never spoils.", "Did you know? Bananas are berries, but strawberries aren't!"],
            "what's the weather": ["I can't see outside, but I hope it's sunny! ☀️", "Looks like rain... in my data! 🌧️", "Cloudy with a chance of algorithms! ☁️🤖"]
        }

        # Merge all
        self.all_data = {}
        self.all_data.update(self.conversations)
        self.all_data.update(self.thanks_and_bye)
        self.all_data.update(self.famous_people)
        self.all_data.update(self.brands)
        self.all_data.update(self.small_talk)

