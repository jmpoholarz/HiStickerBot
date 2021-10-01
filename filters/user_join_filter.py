import os

from telegram import Message
from telegram.ext import MessageFilter

class UserJoinFilter(MessageFilter):
    """ A filter to detect if a new user has joined the chat """
    
    MEME_STICKER_FILE_UNIQUE_ID = os.environ['STICKER_FILE_UNIQUE_ID']

    def filter(self, message:Message):
        """ 
        Checks if the message refers to new users joining

        message - the message to filter
        returns: True if a new user(s) have joined, false otherwise
        """
        if message.new_chat_members is not None and \
                len(message.new_chat_members) > 0:
            return True

        return False