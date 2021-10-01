#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

# Credit to https://blog.usejournal.com/part-2-deploying-telegram-
# bot-for-free-on-heroku-3defe5a6c0e8 for the initial tutorial

# > heroku logs -t
# To see the bot's logs from the heroku host

# To push a commit to the hosted bot:
# git push heroku master

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

Note: Bot will need to be added as a bot admin and/or have acces to read
messages in order to function properly!
(https://core.telegram.org/bots#privacy-mode for details)
"""

import atexit
import logging
import os
import sys
from threading import Timer
import time
import traceback

from telegram import Bot, Update, Sticker, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.helpers import mention_html

import filters.user_join_filter as user_join_filter
import filters.sticker_filter as sticker_filter
import filters.random_message_filter as random_message_filter
import filters.debug_command_filter as debug_command_filter
import serialization
import user_store


# Telegram generated token to connect to the bot
TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
# Where the app is hosted on heroku
APP_NAME = "https://histickerbotapp.herokuapp.com/"
# The port the app is hosted on
PORT = int(os.environ.get('PORT', '8443'))
# List of users to send error messages to
ADMINS = [os.environ['ADMIN_USER']]
DEVS = [int(os.environ['DEV_USER'])]
# Meme sticker to send
STICKER = os.environ['STICKER']

# Map to store information about users in the bot's channel
user_map = serialization.load_user_map_from_db()

# List of groups the bot should process counts in
allowed_groups = []
allowed_groups.append(int(os.environ['DEV_USER']))
for group in os.environ.get('GROUPS').split(sep=","):
    int_group = int(group) * -1 #All groups have negative IDs
    allowed_groups.append(int_group)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Helper thread to reduce frequency of outputting to file in busy chats
save_timer = None



def wait_then_save_users(time_in_seconds=15):
    """ Sleeps for a given amount of time and then serializes user_map """
    print("Starting 5 minute wait to write user data...")
    time.sleep(time_in_seconds)
    print("Finished wait.  Writing user data to file.")
    serialization.write_user_map_to_db(user_map)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def handler_print_debug_user_map(update:Update, context:CallbackContext):
    """ Responds with a formatted message of users in the user_map """
    debug_message = "Users:\n"
    for user in user_map:
        us = user_map[user]
        count = update.message.message_id - us.get_id_last_message_stickered()
        probability = 1 - (500 / (count + 400))
        #if (us.get_count_since_last_stickered < 10 or probability < 0):
        #    probability = 0
        print("mid:" + str(update.message.message_id))
        print("idlms:" + str(us.get_id_last_message_stickered()))
        print("P:" + str(probability))
        debug_message += us.get_username() + \
            " : " + str(count) + \
            " : " + str(int(probability*100)) + "%\n"
    update.message.reply_text(debug_message)


def handler_send_sticker(update:Update, context:CallbackContext):
    """ Responds with just the meme sticker """
    update.message.reply_sticker(STICKER)


def handler_send_sticker_and_greeting(update:Update, context:CallbackContext):
    """ Reponds with the meme sticker and a hello message """
    update.message.reply_sticker(STICKER)
    hi_message = "Hi, @" + update.message.from_user.username + "!"
    update.message.reply_text(hi_message)


def handler_send_errors_to_admins(update:Update, context:CallbackContext):
    """ Sends errors to users in the admin list array """
    # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ""
    # normally, we always have an user. If not, its either a channel or a poll update.
    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
    # there are more situations when you don't get a chat
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
           f"</code>"
    # and send it to the dev(s)
    #for dev_id in devs:
    #    context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    
    for user in DEVS:
        context.bot.send_message(user, text, parse_mode=ParseMode.HTML)

    # we raise the error again, so the logger module catches it.
    raise


def handler_refresh_save_task(update:Update, context:CallbackContext):
    """ Resets the timer that controls when to save the user_map to a file """
    global save_timer #use bot.py's save_task obj
    global user_map #use boy.py's user_map obj
    if save_timer is not None:
        save_timer.cancel()
        print("save_timer cancelled")
        save_timer.join()
        print("save timer joined")
    save_timer = Timer(60.0, serialization.write_user_map_to_db, [user_map])
    save_timer.start()
    print("save_timer started")
    
    


def main():
    """Start the bot."""

    # Creates the Updater which takes the bot's token.
    # use_context=True to use the new context based callbacks
    # (will no longer be necessary Post version 12)
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    #dp.add_handler(CommandHandler("help", help))


    # Send meme sticker when a new user joins the chat
    join_fil = MessageHandler(
        user_join_filter.UserJoinFilter(),
        handler_send_sticker
    )
    dp.add_handler(join_fil)
    # Send meme sticker when message is meme sticker
    #sticker_fil = MessageHandler(
    #    sticker_filter.StickerFilter(), 
    #    handler_send_sticker
    #)
    #dp.add_handler(sticker_fil)
    # Send meme sticker and hello for random messages
    random_fil = MessageHandler(
        random_message_filter.RandomMessageFilter(user_map, allowed_groups), 
        handler_send_sticker_and_greeting
    )
    dp.add_handler(random_fil)

    # Output debug information when an admin sends $$chances
    debug_fil = MessageHandler(
        debug_command_filter.DebugCommandFilter(DEVS),
        handler_print_debug_user_map
    )
    dp.add_handler(debug_fil)

    # On any activity, refresh the snooze timer
    activity_fil = MessageHandler(
        Filters.all,
        handler_refresh_save_task
    )
    dp.add_handler(activity_fil)

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)
    # Send errors to admins
    dp.add_error_handler(handler_send_errors_to_admins)

    # Start the Bot
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN
    )
    # updater.bot.set_webhook(url=settings.WEBHOOK_URL)
    updater.bot.set_webhook(APP_NAME + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()