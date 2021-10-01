

class UserStore:
    """ 
    Stores information about a given user that the bot may find useful
    when calculating when to appropriately sticker them
    """

    # unique id number to represent a user on telegram
    _user_id = -1
    # username for the user on telegram
    _username = "Undefined"
    # The message_id of the most recent message sent by this user
    _id_last_message_sent = -1
    # The message_id of the most recent message stickered by the bot
    _id_last_message_stickered = -1
    # The number of messages sent by the user since they were last stickered
    _count_since_last_stickered = -1
    # Whether the user has been stored in the database
    _is_new_user = True


    def __init__(self, user_id=None, username=None, data_dict=None):
        if user_id is not None and username is not None:
            """ Create a new UserStore object for the given user_id, username """
            self._user_id = user_id
            self._username = username
            self._id_last_message_sent = -1
            self._id_last_message_stickered = -1
            self._count_since_last_stickered = -1
            self._is_new_user = True
        elif data_dict is not None:
            """ Create a new UserStore object from a dictionary representation """
            self._user_id = data_dict["user_id"]
            self._username = data_dict["username"]
            self._id_last_message_sent = data_dict["id_last_message_sent"]
            self._id_last_message_stickered = data_dict["id_last_message_stickered"]
            self._count_since_last_stickered = data_dict["count_since_last_stickered"]
            self._is_new_user = False

    def get_user_id(self):
        return self._user_id
    
    def get_username(self):
        return self._username

    def set_id_last_message_sent(self, value):
        self._id_last_message_sent = value
    
    def get_id_last_message_sent(self):
        return self._id_last_message_sent
    
    def set_id_last_message_stickered(self, value):
        self._id_last_message_stickered = value
    
    def get_id_last_message_stickered(self):
        return self._id_last_message_stickered
    
    def set_count_since_last_stickered(self, value):
        self._count_since_last_stickered = value
    
    def get_count_since_last_stickered(self):
        return self._count_since_last_stickered
    
    def get_is_new_user(self):
        return self._is_new_user
    
    def set_is_new_user(self, value):
        self._is_new_user = value
    
    def to_dict(self):
        """ Converted a UserStore into a dict for easy writing to json """
        data = {
            "user_id" : self._user_id,
            "username" : self._username,
            "id_last_message_sent" : self._id_last_message_sent,
            "id_last_message_stickered" : self._id_last_message_stickered,
            "count_since_last_stickered" : self._count_since_last_stickered,
            "is_new_user" : self._is_new_user
        }
        return data
