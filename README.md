# Hi Sticker Bot

A Telegram bot which randomly replies to chat responses with a configured
Telegram sticker.

Users are stickered according to the following:
1. They're a brand new user
2. They've sent at least 10 messages since the last time they've been stickered
3. A random probability: chances increase the more messages that have been sent since their last sticker

The formula used:
    
    P(stickered) = 1 - (500/(x+400)) 
where x is the number of messages since the last stickered message.  
This means that in a busy chat, a user will not be stickered for at 
least 100 messages.


## Tech Stack
The bot has been programmed in python using the Telegram python library.
It is hosted on Heroku, utilizing their free tier of hosting.

Data is stored using Heroku's Postgres database plugin.

Heroku Dashboard: https://dashboard.heroku.com/apps/histickerbotapp/


## Limitations

1. The user information does not currently store message ids for multiple
chats, only for a single chat.  This means if the same user is in
multiple chats with the bot, the message IDs from the different chats
would override each other, breaking the math for how often they should
be stickered.

This could be addressed by reworking the database to include the chat ID
as part of the key for the row.

2. Due to app persistence limitations of Heroku, all data has to be stored
in a database to not be lost on Heroku host shutdown.  Otherwise, in an
inactive chat, the bot would forget the last time users sent messages
and would sticker them each time it woke up.

## Resources
The initial tutorial for setting up the bot on Heroku goes to https://blog.usejournal.com/part-2-deploying-telegram-bot-for-free-on-heroku-3defe5a6c0e8 which was
very helpful in figuring out where to start.

### Python Telegram Bot API: 
https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#reply-to-a-message

https://python-telegram-bot.org/

### Python Telegram Bot API Docs:
https://python-telegram-bot.readthedocs.io/en/latest/telegram.html

Message Class: https://python-telegram-bot.readthedocs.io/en/latest/telegram.message.html

Send Sticker Function: https://python-telegram-bot.readthedocs.io/en/latest/telegram.bot.html#telegram.Bot.send_sticker

Chat Class: https://python-telegram-bot.readthedocs.io/en/latest/telegram.chat.html

Sticker Class: https://python-telegram-bot.readthedocs.io/en/latest/telegram.sticker.html#telegram.Sticker



