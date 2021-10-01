import random

from telegram import Message
from telegram.ext import MessageFilter

import user_store

class RandomMessageFilter(MessageFilter):
    """ A filter that randomly selects messages """
    
    BASE_PROBABILITY = 0.50

    user_map = {}
    allowed_groups = []

    def __init__(self, user_map, allowed_groups):
        self.user_map = user_map
        self.allowed_groups = allowed_groups

    def filter(self, message:Message):
        """ 
        Selects messages based on a random number being larger than a
        computed probability.  Users are stickered based on:
            1. They're a brand new user
            2. They've sent at least 10 messages since the last sticker
            3. A random probability, chances increase the more messages
                that have been sent since their last sticker
        The formula used is (500/(x+400)) where x is the number of messages
        since the last stickered message.
        Alternate formulas considered were:
            probability = 0.0000001*x*x*x - 0.000001*x*x + math.sqrt(.5*x) - 10
            probability = 1 -900000/(x+850)^2

        message - the message to filter
        returns: True if the random number selector chooses the message
        """
        # Log the group the message was from
        if message.chat.title is not None:
            print(str(message.chat.id) + " " + message.chat.title)
        elif message.chat.username is not None:
            print(str(message.chat.id) + " " + message.chat.username)
        

        for user in self.user_map:
            us = self.user_map[user]
            print("uid:" + str(us.get_user_id()) + " : " + str(us.get_username()) + " : " + str(us.get_count_since_last_stickered()))


        # Check if this is a new user
        if message.from_user.id not in self.user_map:
            # User is new, add them to the map
            user_id = message.from_user.id
            username = message.from_user.username
            us = user_store.UserStore(user_id=user_id, username=username)
            us.set_id_last_message_stickered(message.message_id)
            us.set_count_since_last_stickered(0)
            self.user_map[user_id] = us
            # And sticker them
            return False
        
        # User is known, get information about them
        us = self.user_map[message.from_user.id]
        id_last_stickered = us.get_id_last_message_stickered()
        count_since_stickered = us.get_count_since_last_stickered()

        # Check how many messages since last stickered
        if count_since_stickered < 10:
            # Haven't sent enough, do not sticker
            us.set_count_since_last_stickered(count_since_stickered + 1)
            us.set_id_last_message_sent(message.message_id)
            return False

        # Get count of messages since user's last message
        count_since_last_message = \
            message.message_id - us.get_id_last_message_stickered()
        # Calulate probability of stickering
        probability = (500 / (count_since_last_message + 400))
        # Sticker if probability is high enough
        random_number = random.random()
        print("rmf:mid:" + str(message.message_id))
        print("rmf:idlms:" + str(us.get_id_last_message_stickered()))
        print("rmf:P:" + str(probability))
        if random_number > probability:
            us.set_count_since_last_stickered(0)
            us.set_id_last_message_stickered(message.message_id)
            return True

        # Increment count of non-stickered messages if not high enough
        us.set_count_since_last_stickered(count_since_stickered + 1)
        us.set_id_last_message_sent(message.message_id)
        return False