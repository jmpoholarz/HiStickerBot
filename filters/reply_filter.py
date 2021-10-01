import os

from telegram import Message
from telegram.ext import MessageFilter

class ReplyFilter(MessageFilter):
    """ A filter to detect if the message was a reply to HiStickerBot """
    
    MEME_STICKER_FILE_UNIQUE_ID = os.environ['STICKER_FILE_UNIQUE_ID']

    def filter(self, message:Message):
        """ 
        TODO

        message - the message to filter
        returns: 
        """
        #if message.sticker is not None:
        #    if message.sticker.file_unique_id == \
        #            self.MEME_STICKER_FILE_UNIQUE_ID:
        #        return True

        return False