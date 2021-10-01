import random

from telegram import Message
from telegram.ext import MessageFilter

import user_store

class DebugCommandFilter(MessageFilter):
    """ A filter that randomly selects messages """

    admins = []

    def __init__(self, admins):
        self.admins = admins

    def filter(self, message:Message):
        """ 
        Prints out debug information for matching debug commands from admin
        users
        """
        # Check if user is an admin
        if message.from_user.id not in self.admins:
            return False
        # Check if the message matches valid commands
        if message.text == "$$chances":
            return True
            
        return False