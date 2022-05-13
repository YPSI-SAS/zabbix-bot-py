#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,ConversationHandler,MessageHandler,Filters,RegexHandler)
from telegram import InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardRemove,ChatAction,ReplyKeyboardMarkup,ParseMode
from action import build_menu, display_object_button
from functools import wraps
import gettext
from emojiDict import telegramEmojiDict
import json
import yaml
import os

from request_API import API

#log Management
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

#Global variables
ACTION_START, START_OVER, ZABBIX_URL, ZABBIX_TOKEN, API_VAR, TYPING, CANCEL = map(chr, range(7))
SETTING,CHOOSE_SETTING,CHOOSE_LANG, SERVER, STOPPING = map(chr,range(7,12))
ALL_MENU, CHOOSE_HOST = map(chr, range(12,14))
PRECEDENT, NEXT = map(chr, range(14,16))

LANG = 'en'
NAME_SERVER=""

lang_translations = gettext.translation('main', localedir='locales', languages=[LANG])
lang_translations.install()
_ = lang_translations.gettext

END = ConversationHandler.END

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

#get_cancel_button return the button cancel in a list
def get_cancel_button():
    cancel_button=list()
    cancel_button.append(InlineKeyboardButton(text=telegramEmojiDict['cross mark']+_('Cancel'), callback_data=str(CANCEL)))
    return cancel_button

#display_message_bot display message en keyboard to conversation
def display_message_bot(update,context,message,reply_markup):
    if not context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(text=message ,parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup)
    else:
        update.message.reply_markdown(text=message, reply_markup=reply_markup)
    context.user_data[START_OVER] = False


#help_msg display the help message
def help_msg(update,context):
    message = _('Commands:\n /start - Start a conversation\n /stop - Stop a current action and return to start menu')
    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(text=message, parse_mode=ParseMode.MARKDOWN)
    else: 
        update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
    context.user_data[START_OVER]= False

#navigation_host permits to navigate in the pages of hosts 
@send_typing_action
def navigation_host(update,context):
    ud = context.user_data
    host_list= ud[API_VAR].get_list_hosts()
    numberHostDisplay = 26
    numberPages = int(len(host_list)/numberHostDisplay)
    if ud['NUMBER'] < numberPages:
        host_list = host_list[ud['NUMBER']*numberHostDisplay:(ud['NUMBER']+1)*numberHostDisplay]
    else:
        host_list = host_list[ud['NUMBER']*numberHostDisplay:]
    message, button_list = display_object_button("host",host_list,LANG)
    
    footer_buttons =list()
    if ud['NUMBER']>0:
        footer_buttons.append(InlineKeyboardButton(text='<<', callback_data=str(PRECEDENT)))
    
    text_button=_('Page %s') % (str(ud['NUMBER']+1))
    footer_buttons.append(InlineKeyboardButton(text=text_button, callback_data=str(ud['NUMBER'])))

    if ud['NUMBER']<numberPages:
        footer_buttons.append(InlineKeyboardButton(text='>>', callback_data=str(NEXT)))

    cancel_button = get_cancel_button()
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,footer_buttons=footer_buttons,cancel_button=cancel_button))
    display_message_bot(update,context,message,reply_markup)

#list_host display a page of hosts
def list_host(update, context):
    ud = context.user_data
    ud['NUMBER']=0
    navigation_host(update,context)
    return CHOOSE_HOST

#next_host permits to pass at the next page
def next_host(update,context):
    ud = context.user_data
    ud['NUMBER']=ud['NUMBER']+1
    
    navigation_host(update,context)
    return CHOOSE_HOST

#precedent_host permits to pass at the precedent page
def precedent_host(update,context):
    ud = context.user_data
    ud['NUMBER']=ud['NUMBER']-1
    
    navigation_host(update,context)
    return CHOOSE_HOST

#start display the start message
def start(update,context):
    #Start function. Displayed whenever the /start command is called.
    findServ=False
    bot=context.bot
    if NAME_SERVER=="" and os.getenv('URL')!=None and os.getenv('TOKEN')!=None:
        findServ=True
        context.user_data[str(ZABBIX_URL)]=os.getenv('URL')
        context.user_data[str(ZABBIX_TOKEN)]=os.getenv('TOKEN')
        message = _('Hey, I\'m %s !\nI will help you to handle Zabbix problems !\nI\'m connected to the server : *%s*\nType /help to show all commands\n   Choose an option:') % (bot.get_me().first_name,os.getenv('URL'))
    elif NAME_SERVER!="":
        with open("config.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        for __, doc in data_loaded.items():
            for i in range(len(data_loaded["servers"])):
                if NAME_SERVER==doc[i]["server"]:
                    findServ=True
                    context.user_data[str(ZABBIX_URL)]=doc[i]["url"]
                    context.user_data[str(ZABBIX_TOKEN)]=doc[i]["token"]
        message = _('Hey, I\'m %s !\nI will help you to handle Zabbix problems !\nI\'m connected to the server : *%s*\nType /help to show all commands\n   Choose an option:') % (bot.get_me().first_name,NAME_SERVER)
    else:
        if os.path.exists("config.yaml"):
            with open("config.yaml", 'r') as stream:
                data_loaded = yaml.safe_load(stream)
            for __, doc in data_loaded.items():
                findServ=True
                context.user_data[str(ZABBIX_URL)]=doc[0]["url"]
                context.user_data[str(ZABBIX_TOKEN)]=doc[0]["token"]
            message = _('Hey, I\'m %s !\nI will help you to handle Zabbix problems !\nI\'m connected to the server : *%s*\nType /help to show all commands\n   Choose an option:') % (bot.get_me().first_name,doc[0]["server"])
       

    # Create initial message:
    if findServ==True:
        buttons = [[
            InlineKeyboardButton(text=telegramEmojiDict['large blue diamond']+_('All Hosts'), callback_data=str(ALL_MENU)),
        ],
            [
            InlineKeyboardButton(text=telegramEmojiDict['gear']+_('Settings'), callback_data=str(SETTING)),
            InlineKeyboardButton(text=telegramEmojiDict['waving hand']+_('Done'), callback_data=str(END))
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.user_data[API_VAR] = API(context.user_data[str(ZABBIX_URL)], context.user_data[str(ZABBIX_TOKEN)])

    else:
        message = _('The server is incorrect. Please change the name in setting.')
        buttons = [[
            InlineKeyboardButton(text=telegramEmojiDict['gear']+_('Settings'), callback_data=str(SETTING))
        ],[
            InlineKeyboardButton(text=telegramEmojiDict['waving hand']+_('Done'), callback_data=str(END))
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else: 
        update.message.reply_markdown(text=message, reply_markup=reply_markup)
    context.user_data[START_OVER]= False
    return ACTION_START

#list_setting display the action possible in the menu setting
def list_setting(update,context):
    button_list =list()
    button_list.append(InlineKeyboardButton(text=telegramEmojiDict['white flag']+_('Change language'),callback_data="language"))
    button_list.append(InlineKeyboardButton(text=telegramEmojiDict['electric plug']+_('Change server'),callback_data="server"))
    cancel_button = get_cancel_button()
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=3,cancel_button=cancel_button))
    message=_('Choose what you want to change')
    display_message_bot(update,context,message,reply_markup)
    return CHOOSE_SETTING

#select_lang display the possibles languages 
def select_lang(update,context):
    button_list =list()
    button_list.append(InlineKeyboardButton(text="🇬🇧 English",callback_data="en"))
    button_list.append(InlineKeyboardButton(text="🇫🇷 French",callback_data="fr"))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=3))
    message=_('Please choose your language')
    display_message_bot(update,context,message,reply_markup)
    return CHOOSE_LANG

#choose_lang recovery the language choose by the user and change the language of the bot
def choose_lang(update,context):
    context.user_data['LANG']=update.callback_query.data
    global LANG,lang_translations,_
    LANG=context.user_data['LANG']
    lang_translations = gettext.translation('main', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    context.user_data[START_OVER]=True
    start(update,context)
    return END

#get_name_server recovery the name of the server enter by the user
def get_name_server(update,context):
    button_list=list()
    if os.path.exists("config.yaml"):
        with open("config.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            for __, doc in data_loaded.items():
                for i in range(len(data_loaded["servers"])):
                    button_list.append(InlineKeyboardButton(text=doc[i]["server"],callback_data='{"SE":"'+doc[i]["server"]+'"}'))
        message=_("Choose one server or cancel")
    else:
        message=_('The file *config.yaml* doesn\'t exists. Create file or use environment variables.')
    cancel_button = get_cancel_button()
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button))
    display_message_bot(update,context,message,reply_markup)
    return SERVER

#change_server change the server where the bot is connected
def change_server(update,context):
    global NAME_SERVER
    Cdata=json.loads(update.callback_query.data)
    NAME_SERVER=Cdata['SE']
    context.user_data[START_OVER]=True
    start(update,context)
    return STOPPING

#cancel stop the conversation and display the main menu
def cancel(update,context):
    context.user_data[START_OVER]=True
    start(update,context)
    return STOPPING

#stop stop all conversations
def stop(update, context):
    """End Conversation by command."""
    context.user_data.clear()
    update.message.reply_text(_('Okay, bye.'))
    return END

#stop_nested end conversation child and return to start menu
def stop_nested(update,context):
    context.user_data[START_OVER]=False
    update.message.reply_text('STOP okay.')
    start(update,context)
    return STOPPING

#end stop all conversations
def end(update, context):
    """End conversation from InlineKeyboardButton."""
    context.user_data.clear()
    update.callback_query.edit_message_text(text=_('See you !'))
    return END

#error log the errors that the bot meet
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('BOT_TOKEN'),use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    # Add conversation handler for change server
    change_server_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(get_name_server, pattern='^server')],
        states={
            SERVER:[
                CallbackQueryHandler(change_server, pattern='^{"SE*'),
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
            ]
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            STOPPING: STOPPING,
            END: STOPPING
        }
    )

    # Add conversation handler for all menu
    all_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(list_host, pattern='^' + str(ALL_MENU))],
        states={
            CHOOSE_HOST:[
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
                CallbackQueryHandler(precedent_host, pattern='^' + str(PRECEDENT) + '$'),
                CallbackQueryHandler(next_host, pattern='^' + str(NEXT) + '$'),
            ]
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            END: ACTION_START,
            STOPPING: ACTION_START
        }
    )

    # Add conversation handler for setting menu
    setting_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(list_setting, pattern='^'+str(SETTING))],
        states={
            CHOOSE_SETTING:[
                CallbackQueryHandler(select_lang, pattern='^lang'),
                change_server_conv,
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
            ],
            CHOOSE_LANG:[
                CallbackQueryHandler(choose_lang)
            ]
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            END: ACTION_START,
            STOPPING: ACTION_START
        }
    )

    # Add conversation handler for Start Menu:
    start_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ACTION_START: [
                all_conv,
                setting_conv,
                CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
            ]
          
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    
    dp.add_handler(CommandHandler("help",help_msg))
    dp.add_handler(start_conv)

    # Log all errors:
    dp.add_error_handler(error)

    # Start DisAtBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    updater.idle()


if __name__ == '__main__':
    logger.info("Zabbix Bot Start.")

    main()