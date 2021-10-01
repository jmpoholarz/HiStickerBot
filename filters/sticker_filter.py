import os

from telegram import Message
from telegram.ext import MessageFilter

class StickerFilter(MessageFilter):
    """ A filter to detect if a message is the sticker meme sticker """
    
    MEME_STICKER_FILE_UNIQUE_ID = os.environ['STICKER_FILE_UNIQUE_ID']

    def filter(self, message:Message):
        """ 
        Performs the logic check to see if the message is the sticker meme
        sticker or not

        message - the message to filter
        returns: True if the sticker is the meme sticker, false otherwise
        """
        if message.sticker is not None:
            if message.sticker.file_unique_id == \
                    self.MEME_STICKER_FILE_UNIQUE_ID:
                return True

        return False