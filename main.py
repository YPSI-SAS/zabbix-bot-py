#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,ConversationHandler,MessageHandler,Filters,RegexHandler)
from telegram import InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardRemove,ChatAction,ReplyKeyboardMarkup,ParseMode
from action import build_menu, display_object_button, display_host_characteristics,display_item_characteristics, display_trigger_characteristics
from functools import wraps
import gettext
from emojiDict import telegramEmojiDict
import json
import yaml
import os
import time


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
HOST_MENU_NAME, NAME_HOST = map(chr, range(16,18))
HOST_MENU_TAG, TAG_HOST = map(chr, range(18,20))
HOST_GROUP_MENU, CHOOSE_HOSTGROUP = map(chr, range(20,22))
DISPLAY_ACTION = map(chr, range(22,23))
DISABLE_HOST, ENABLE_HOST, ITEM_MENU, TRIGGER_MENU, PROBLEM_MENU = map(chr, range(23,28))
CHOOSE_ITEM, DISABLE_ITEM, ENABLE_ITEM, GRAPH_MENU = map(chr,range(28,32))
DISPLAY_ACTION_ITEM = map(chr, range(32,33))
CHOOSE_TRIGGER, DISABLE_TRIGGER, ENABLE_TRIGGER, DISPLAY_ACTION_TRIGGER = map(chr, range(33,37))

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

#navigation_elements permits to navigate in the pages of elements 
@send_typing_action
def navigation_elements(update,context):
    ud = context.user_data
    if ud['TYPE_REQUEST'] == "all_host":
        elements_list= ud[API_VAR].get_list_hosts()
    elif ud['TYPE_REQUEST'] == "all_host_name":
        elements_list= ud[API_VAR].get_list_hosts_with_name(ud['NAME_HOST'])
    elif ud['TYPE_REQUEST'] == "all_host_tag":
        elements_list= ud[API_VAR].get_list_hosts_with_tag(ud['TAG_HOST'])
    elif ud['TYPE_REQUEST'] == "all_hostgroup":
        elements_list= ud[API_VAR].get_list_hostgroups()
    elif ud['TYPE_REQUEST'] == "all_host_hostgroup":
        elements_list= ud[API_VAR].get_list_hosts_with_hostgroup(ud['ID_HOSTGROUP'])
    elif ud['TYPE_REQUEST'] == "all_item":
        elements_list= ud[API_VAR].get_list_items(ud['ID_HOST'])
    elif ud['TYPE_REQUEST'] == "all_trigger_host":
        elements_list= ud[API_VAR].get_list_triggers_by_host(ud['ID_HOST'])
    elif ud['TYPE_REQUEST'] == "all_trigger_item":
        elements_list= ud[API_VAR].get_list_triggers_by_item(ud['ID_ITEM'])
    numberHostDisplay = 26
    numberPages = int(len(elements_list)/numberHostDisplay)
    if ud['NUMBER'] < numberPages:
        elements_list = elements_list[ud['NUMBER']*numberHostDisplay:(ud['NUMBER']+1)*numberHostDisplay]
    else:
        elements_list = elements_list[ud['NUMBER']*numberHostDisplay:]
    message, button_list = display_object_button(ud['OBJECT'],elements_list,LANG)
    
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
    ud['TYPE_REQUEST'] = 'all_host'
    ud['OBJECT'] = "host"
    ud['NUMBER']=0
    navigation_elements(update,context)
    return CHOOSE_HOST

#next permits to pass at the next page
def next(update,context):
    ud = context.user_data
    ud['NUMBER']=ud['NUMBER']+1    
    navigation_elements(update,context)
    return CHOOSE_HOST

#precedent permits to pass at the precedent page
def precedent(update,context):
    ud = context.user_data
    ud['NUMBER']=ud['NUMBER']-1
    navigation_elements(update,context)
    return CHOOSE_HOST

#get_name_host recovery the name enter by the user
def get_name_host(update,context):
    update.callback_query.edit_message_text(text=_('Okay, give me the name of the host'))
    context.user_data[START_OVER] = True
    return NAME_HOST

#get_tag_host recovery the tag enter by the user
def get_tag_host(update,context):
    update.callback_query.edit_message_text(text=_('Okay, give me the tag of the host (NAME=VALUE)'))
    context.user_data[START_OVER] = True
    return TAG_HOST

#list_host_with_name display the list of host which contains the name of the host enter by the user
def list_host_with_name(update, context):
    ud = context.user_data
    ud['NAME_HOST']=update.message.text
    ud['TYPE_REQUEST'] = "all_host_name"
    ud['OBJECT'] = "host"
    ud['NUMBER']=0
    navigation_elements(update,context)    
    return CHOOSE_HOST

#list_host_with_tag display the list of host which contains the tag of the host enter by the user
def list_host_with_tag(update, context):
    ud = context.user_data
    ud['TAG_HOST']=update.message.text
    ud['TYPE_REQUEST'] = "all_host_tag"
    ud['OBJECT'] = "host"
    ud['NUMBER']=0
    navigation_elements(update,context)    
    return CHOOSE_HOST

#list_item display the list of item of the host selected by the user
def list_item(update, context):
    ud = context.user_data
    ud['TYPE_REQUEST'] = "all_item"
    Cdata=json.loads(ud['HOST_INFO'])
    ud['ID_HOST']=Cdata['HID']
    ud['OBJECT'] = "item"
    ud['NUMBER']=0
    navigation_elements(update,context)    
    return CHOOSE_ITEM

#list_hostgroups permits to recovery and display hostgroups
def list_hostgroups(update,context):
    ud = context.user_data
    ud['TYPE_REQUEST'] = "all_hostgroup"
    ud['OBJECT'] = "HG"
    ud['NUMBER']=0
    navigation_elements(update,context) 
    return CHOOSE_HOSTGROUP 

#list_trigger_by_host display the list of trigger of the host selected by the user
def list_trigger_by_host(update, context):
    ud = context.user_data
    ud['TYPE_REQUEST'] = "all_trigger_host"
    Cdata=json.loads(ud['HOST_INFO'])
    ud['ID_HOST']=Cdata['HID']
    ud['OBJECT'] = "trigger"
    ud['NUMBER']=0
    navigation_elements(update,context)    
    return CHOOSE_TRIGGER

#list_trigger_by_item display the list of trigger of the item selected by the user
def list_trigger_by_item(update, context):
    ud = context.user_data
    ud['TYPE_REQUEST'] = "all_trigger_item"
    Cdata=json.loads(ud['ITEM_INFO'])
    ud['ID_ITEM']=Cdata['IID']
    ud['OBJECT'] = "trigger"
    ud['NUMBER']=0
    navigation_elements(update,context)    
    return CHOOSE_TRIGGER

#select_hostgroups permits to display host belonging to hostgroup
def select_hostgroups(update,context):
    ud = context.user_data
    ud['HOSTGROUP_INFO']=update.callback_query.data
    Cdata=json.loads(ud['HOSTGROUP_INFO'])
    ud['ID_HOSTGROUP'] = Cdata['HGID']
    ud['TYPE_REQUEST'] = "all_host_hostgroup"
    ud['OBJECT'] = "host"
    ud['NUMBER']=0
    navigation_elements(update,context) 
    return CHOOSE_HOST

#display_action_host return a list of buttons for make the sub-menu
def display_action_host(context):
    ud = context.user_data
    button_list = list()
    Cdata=json.loads(ud['HOST_INFO'])
    hostID=Cdata['HID']
    list_host=ud[API_VAR].get_host_info(hostID)
    list_host_problems=ud[API_VAR].get_host_problem(hostID)

    for host in list_host:
         #Display active checks or not
        if host["status"]=='0':
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['prohibited']+_('Disable'),callback_data=str(DISABLE_HOST)))
        else:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['check mark button']+_('Enable'), callback_data=str(ENABLE_HOST)))
    
        if len(host["items"])!=0:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['spiral notepad']+_('Items'),callback_data=str(ITEM_MENU)))
        if len(host["triggers"])!=0:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['vertical traffic light']+_('Triggers'),callback_data=str(TRIGGER_MENU)))
        if len(list_host_problems)!=0:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['police car light']+_('Problems'),callback_data=str(PROBLEM_MENU)))
    
    cancel_button = get_cancel_button()
    return button_list,cancel_button

#display_action_item return a list of buttons for make the sub-menu
def display_action_item(context):
    ud = context.user_data
    button_list = list()
    Cdata=json.loads(ud['ITEM_INFO'])
    itemID=Cdata['IID']
    list_item=ud[API_VAR].get_item_info(itemID)

    for item in list_item:
         #Display active checks or not
        if item["status"]=='0':
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['prohibited']+_('Disable'),callback_data=str(DISABLE_ITEM)))
        else:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['check mark button']+_('Enable'), callback_data=str(ENABLE_ITEM)))
    
        if item['value_type']=='0' or item['value_type']=='3':
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['chart decreasing']+_('Graphs'),callback_data=str(GRAPH_MENU)))
        if len(item["triggers"])!=0:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['vertical traffic light']+_('Triggers'),callback_data=str(TRIGGER_MENU)))
        if len(item['hosts'])!=0:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['laptop']+_('Host'),callback_data='{"HID":"'+item['hosts'][0]['hostid']+'"}'))
    
    cancel_button = get_cancel_button()
    return button_list,cancel_button

#display_action_trigger return a list of buttons for make the sub-menu
def display_action_trigger(context):
    ud = context.user_data
    button_list = list()
    Cdata=json.loads(ud['TRIGGER_INFO'])
    triggerID=Cdata['TID']
    list_trigger=ud[API_VAR].get_trigger_info(triggerID)
    list_trigger_problems=ud[API_VAR].get_trigger_problem(triggerID)

    for trigger in list_trigger:
         #Display active checks or not
        if trigger["status"]=='0':
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['prohibited']+_('Disable'),callback_data=str(DISABLE_TRIGGER)))
        else:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['check mark button']+_('Enable'), callback_data=str(ENABLE_TRIGGER)))
    
        if len(trigger["items"])!=0:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['spiral notepad']+_('Item'),callback_data='{"IID":"'+trigger['items'][0]['itemid']+'"}'))
        if len(trigger['hosts'])!=0:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['laptop']+_('Host'),callback_data='{"HID":"'+trigger['hosts'][0]['hostid']+'"}'))
        if len(list_trigger_problems)!=0:
            button_list.append(InlineKeyboardButton(text=telegramEmojiDict['police car light']+_('Problems'),callback_data=str(PROBLEM_MENU)))

    cancel_button = get_cancel_button()
    return button_list,cancel_button

#select_host permits to display the informations and the sub-menu for the host selected
@send_typing_action
def select_host(update,context):
    ud = context.user_data
    ud['HOST_INFO']=update.callback_query.data
    message=display_host_characteristics(context,LANG, ud[API_VAR])
    button_list, cancel_button = display_action_host(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    display_message_bot(update,context,message,reply_markup)
    return DISPLAY_ACTION

#select_item permits to display the informations and the sub-menu for the item selected
@send_typing_action
def select_item(update,context):
    ud = context.user_data
    ud['ITEM_INFO']=update.callback_query.data
    message=display_item_characteristics(context,LANG, ud[API_VAR])
    button_list, cancel_button = display_action_item(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    display_message_bot(update,context,message,reply_markup)
    return DISPLAY_ACTION_ITEM

#select_trigger permits to display the informations and the sub-menu for the trigger selected
@send_typing_action
def select_trigger(update,context):
    ud = context.user_data
    ud['TRIGGER_INFO']=update.callback_query.data
    message=display_trigger_characteristics(context,LANG, ud[API_VAR])
    button_list, cancel_button = display_action_trigger(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    display_message_bot(update,context,message,reply_markup)
    return DISPLAY_ACTION_TRIGGER

#enable_host permits to enable the host selected
@send_typing_action
def enable_host(update,context):
    ud = context.user_data
    Cdata=json.loads(ud['HOST_INFO'])
    host_ID=Cdata['HID']
    ud[API_VAR].update_host_status(host_ID, 0)
    message_update = _('Host enabled OK\n')
    button_list, cancel_button = display_action_host(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    message_object=display_host_characteristics(context,LANG, ud[API_VAR])
    update.callback_query.edit_message_text(text=message_update+message_object,parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup)

#disable_host permits to disable the host selected
@send_typing_action
def disable_host(update,context):
    ud = context.user_data
    Cdata=json.loads(ud['HOST_INFO'])
    host_ID=Cdata['HID']
    ud[API_VAR].update_host_status(host_ID, 1)
    message_update = _('Host disabled OK\n')
    button_list, cancel_button = display_action_host(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    message_object=display_host_characteristics(context,LANG, ud[API_VAR])
    update.callback_query.edit_message_text(text=message_update+message_object,parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup)

#enable_item permits to enable the item selected
@send_typing_action
def enable_item(update,context):
    ud = context.user_data
    Cdata=json.loads(ud['ITEM_INFO'])
    item_ID=Cdata['IID']
    ud[API_VAR].update_item_status(item_ID, 0)
    message_update = _('Item enabled OK\n')
    button_list, cancel_button = display_action_item(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    message_object=display_item_characteristics(context,LANG, ud[API_VAR])
    update.callback_query.edit_message_text(text=message_update+message_object,parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup)

#disable_item permits to disable the item selected
@send_typing_action
def disable_item(update,context):
    ud = context.user_data
    Cdata=json.loads(ud['ITEM_INFO'])
    item_ID=Cdata['IID']
    ud[API_VAR].update_item_status(item_ID, 1)
    message_update = _('Item disabled OK\n')
    button_list, cancel_button = display_action_item(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    message_object=display_item_characteristics(context,LANG, ud[API_VAR])
    update.callback_query.edit_message_text(text=message_update+message_object,parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup)


#enable_trigger permits to enable the trigger selected
@send_typing_action
def enable_trigger(update,context):
    ud = context.user_data
    Cdata=json.loads(ud['TRIGGER_INFO'])
    trigger_ID=Cdata['TID']
    ud[API_VAR].update_trigger_status(trigger_ID, 0)
    message_update = _('Trigger enabled OK\n')
    button_list, cancel_button = display_action_trigger(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    message_object=display_trigger_characteristics(context,LANG, ud[API_VAR])
    update.callback_query.edit_message_text(text=message_update+message_object,parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup)

#disable_trigger permits to disable the trigger selected
@send_typing_action
def disable_trigger(update,context):
    ud = context.user_data
    Cdata=json.loads(ud['TRIGGER_INFO'])
    trigger_ID=Cdata['TID']
    ud[API_VAR].update_trigger_status(trigger_ID, 1)
    message_update = _('Trigger disabled OK\n')
    button_list, cancel_button = display_action_trigger(context)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=2,cancel_button=cancel_button)) 
    message_object=display_trigger_characteristics(context,LANG, ud[API_VAR])
    update.callback_query.edit_message_text(text=message_update+message_object,parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup)

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
        buttons = [
            [
                InlineKeyboardButton(text=telegramEmojiDict['magnifying glass tilted']+telegramEmojiDict['laptop']+_('Search host name'), callback_data=str(HOST_MENU_NAME)),
                InlineKeyboardButton(text=telegramEmojiDict['magnifying glass tilted left']+telegramEmojiDict['laptop']+_('Search host tag'), callback_data=str(HOST_MENU_TAG)),
            ],
            [
                InlineKeyboardButton(text=telegramEmojiDict['laptop']+telegramEmojiDict['laptop']+_('Hostgroups'), callback_data=str(HOST_GROUP_MENU)),
                InlineKeyboardButton(text=telegramEmojiDict['large blue diamond']+_('All Hosts'), callback_data=str(ALL_MENU)),
            ],
            [
                InlineKeyboardButton(text=telegramEmojiDict['gear']+_('Settings'), callback_data=str(SETTING)),
                InlineKeyboardButton(text=telegramEmojiDict['waving hand']+_('Done'), callback_data=str(END))
            ]
        ]
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

    #Add conversation handler for host
    host_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_host, pattern='^{"HID*')],
        states={
            DISPLAY_ACTION:[
                CallbackQueryHandler(list_item, pattern='^' + str(ITEM_MENU) + '$'),
                CallbackQueryHandler(list_trigger_by_host, pattern='^' + str(TRIGGER_MENU) + '$'),
                CallbackQueryHandler(enable_host, pattern='^' + str(ENABLE_HOST) + '$'),
                CallbackQueryHandler(disable_host, pattern='^' + str(DISABLE_HOST) + '$'),
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
            ],
            CHOOSE_ITEM:[
                CallbackQueryHandler(select_item, pattern='^{"IID*'),
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
            ],
            DISPLAY_ACTION_ITEM:[
                CallbackQueryHandler(select_host, pattern='^{"HID*'),
                CallbackQueryHandler(list_trigger_by_item, pattern='^' + str(TRIGGER_MENU) + '$'),
                CallbackQueryHandler(enable_item, pattern='^' + str(ENABLE_ITEM) + '$'),
                CallbackQueryHandler(disable_item, pattern='^' + str(DISABLE_ITEM) + '$'),
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
            ],
            CHOOSE_TRIGGER:[
                CallbackQueryHandler(select_trigger, pattern='^{"TID*'),
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
            ],
            DISPLAY_ACTION_TRIGGER:[
                CallbackQueryHandler(select_host, pattern='^{"HID*'),
                CallbackQueryHandler(select_item, pattern='^{"IID*'),
                CallbackQueryHandler(enable_trigger, pattern='^' + str(ENABLE_TRIGGER) + '$'),
                CallbackQueryHandler(disable_trigger, pattern='^' + str(DISABLE_TRIGGER) + '$'),
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
            ]
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            STOPPING: STOPPING,
        }
    )

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
                host_conv,
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
                CallbackQueryHandler(precedent, pattern='^' + str(PRECEDENT) + '$'),
                CallbackQueryHandler(next, pattern='^' + str(NEXT) + '$'),
            ]
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            END: ACTION_START,
            STOPPING: ACTION_START
        }
    )

    # Add conversation handler for search host menu with name
    search_host_name_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(get_name_host, pattern='^'+str(HOST_MENU_NAME))],
        states={
            NAME_HOST:[MessageHandler(Filters.regex(r'^[^\/]'), list_host_with_name)],
            CHOOSE_HOST:[
                host_conv,
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
                CallbackQueryHandler(precedent, pattern='^' + str(PRECEDENT) + '$'),
                CallbackQueryHandler(next, pattern='^' + str(NEXT) + '$'),
            ]
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            END: ACTION_START,
            STOPPING: ACTION_START
        }
    )

    # Add conversation handler for search host menu with tag
    search_host_tag_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(get_tag_host, pattern='^'+str(HOST_MENU_TAG))],
        states={
            TAG_HOST:[MessageHandler(Filters.regex(r'^[a-zA-Z0-9\-]+=[a-zA-Z0-9\-]+$'), list_host_with_tag)],
            CHOOSE_HOST:[
                host_conv,
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
                CallbackQueryHandler(precedent, pattern='^' + str(PRECEDENT) + '$'),
                CallbackQueryHandler(next, pattern='^' + str(NEXT) + '$'),
            ]
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            END: ACTION_START,
            STOPPING: ACTION_START
        }
    )

    # Add conversation handler for host group menu
    host_group_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(list_hostgroups, pattern='^'+str(HOST_GROUP_MENU))],
        states={
            CHOOSE_HOSTGROUP:[
                CallbackQueryHandler(select_hostgroups, pattern='^{"HGID*'),
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
                CallbackQueryHandler(precedent, pattern='^' + str(PRECEDENT) + '$'),
                CallbackQueryHandler(next, pattern='^' + str(NEXT) + '$'),
            ],
            CHOOSE_HOST:[
                host_conv,
                CallbackQueryHandler(cancel, pattern='^' + str(CANCEL) + '$'),
                CallbackQueryHandler(precedent, pattern='^' + str(PRECEDENT) + '$'),
                CallbackQueryHandler(next, pattern='^' + str(NEXT) + '$'),
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
                search_host_name_conv,
                search_host_tag_conv,
                host_group_conv,
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