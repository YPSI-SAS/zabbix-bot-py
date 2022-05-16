import gettext
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,ConversationHandler,MessageHandler,Filters,RegexHandler)
from telegram import InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardRemove,ChatAction,ReplyKeyboardMarkup,ParseMode
from emojiDict import telegramEmojiDict
import json


ACK_MENU, CANCEL = map(chr, range(2))
#build_menu build a menu with buttons
def build_menu(buttons,
               n_cols,footer_buttons=None,cancel_button=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if footer_buttons:
        menu.append(footer_buttons)
    if cancel_button:
        menu.append(cancel_button)
    return menu

#display_object_buttons display all objects in the form of buttons
def display_object_button(object, object_list,LANG):
    lang_translations = gettext.translation('action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    button_list = list()
    message =str()
    if object=="host":
        if not object_list:
            message = _('I didn\'t find any hosts. Please cancel\n')
        else :
            if len(object_list)==1:
                message = _('I found one host. Please choose a host or cancel\n')
            else:
                message = _('I found many hosts. Please choose one host or cancel\n')
            for host in object_list:
                button_list.append (InlineKeyboardButton(text=get_status_emoji_host(host['status'])+host['name'], 
                callback_data='{"HID":"'+host['hostid']+'"}'))
    elif object=="HG":
        if not object_list:
            message = _('I didn\'t find any hostgroups. Please cancel\n')
        else:
            if len(object_list)==1:
                message = _('I found one hostgroup. Please choose a hostgroup or cancel\n')
            else:
                message = _('I found many hostgroups. Please choose one hostgroup or cancel\n')
            for hostgroup in object_list:
                button_list.append(InlineKeyboardButton(text=hostgroup['name'],
                callback_data='{"HGID":"'+hostgroup['groupid']+'"}'))

    return message, button_list

#get_status_emoji_host converts the status number to the status emoji
def get_status_emoji_host(status):
    switcher = {
        "0": telegramEmojiDict['green square'],
        "1": telegramEmojiDict['red square']
    }
    return switcher.get(status,"invalid status")

#display_host_characteristics recovery the characteristics of host selected by the user
def display_host_characteristics(context,LANG,API_VAR):
    lang_translations = gettext.translation('action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    
    Cdata=json.loads(ud['HOST_INFO'])
    hostID=Cdata['HID']
    list_host=API_VAR.get_host_info(hostID)
    for host in list_host:
        stateV=get_state_string_host(host['status'], _)
        message_tag = ('Tags:')
        for tag in host["tags"]:
            message_tag = message_tag + '\n\t\t' + tag['tag']+' : '+ ('*%s*') % tag['value']
        message = _('Host *%s* is *%s*\n %s') % (host['name'],stateV,message_tag)
    
    return message

#get_state_string_host converts the status number to the status text
def get_state_string_host(status, _):
    switcher = {
        "0": _("enabled"),
        "1": _("disabled")
    }
    return switcher.get(status,"invalid status")