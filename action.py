import gettext
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,ConversationHandler,MessageHandler,Filters,RegexHandler)
from telegram import InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardRemove,ChatAction,ReplyKeyboardMarkup,ParseMode
from emojiDict import telegramEmojiDict

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
                callback_data='{"HI":"'+host['hostid']+'"}'))

    return message, button_list

#get_status_emoji_host converts the status number to the status text
def get_status_emoji_host(status):
    switcher = {
        "0": telegramEmojiDict['green square'],
        "1": telegramEmojiDict['red square']
    }
    return switcher.get(status,"invalid status")