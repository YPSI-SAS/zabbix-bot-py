import gettext
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,ConversationHandler,MessageHandler,Filters,RegexHandler)
from telegram import InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardRemove,ChatAction,ReplyKeyboardMarkup,ParseMode
from emojiDict import telegramEmojiDict
import json
from datetime import datetime, timedelta


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
                button_list.append (InlineKeyboardButton(text=get_status_emoji(host['status'])+host['name'], 
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
    elif object=="item":
        if not object_list:
            message = _('I didn\'t find any items. Please cancel\n')
        else:
            if len(object_list)==1:
                message = _('I found one item. Please choose a item or cancel\n')
            else:
                message = _('I found many items. Please choose one item or cancel\n')
            for item in object_list:
                button_list.append(InlineKeyboardButton(text=get_status_emoji(item['status'])+item['name'],
                callback_data='{"IID":"'+item['itemid']+'"}'))
    elif object=="trigger":
        if not object_list:
            message = _('I didn\'t find any triggers. Please cancel\n')
        else:
            if len(object_list)==1:
                message = _('I found one trigger. Please choose a trigger or cancel\n')
            else:
                message = _('I found many triggers. Please choose one trigger or cancel\n')
            for trigger in object_list:
                button_list.append(InlineKeyboardButton(text=get_status_emoji(trigger['status'])+trigger['description'],
                callback_data='{"TID":"'+trigger['triggerid']+'"}'))
    elif object=="problem":
        if not object_list:
            message = _('I didn\'t find any problems. Please cancel\n')
        else:
            if len(object_list)==1:
                message = _('I found one problem. Please choose a problem or cancel\n')
            else:
                message = _('I found many problems. Please choose one problem or cancel\n')
            for problem in object_list:
                button_list.append(InlineKeyboardButton(text=get_severity_emoji(problem['severity'])+get_acknowledged_emoji(problem['acknowledged'])+problem['name']+_(' since ')+get_time(problem['clock']),
                callback_data='{"PID":"'+problem['eventid']+'"}'))
    return message, button_list

#get_status_emoji converts the status number to the status emoji
def get_status_emoji(status):
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
        stateV=get_state_string(host['status'], _)
        message_tag = ('Tags:')
        for tag in host["tags"]:
            message_tag = message_tag + '\n\t\t' + tag['tag']+' : '+ ('*%s*') % tag['value']
        message = _('Host *%s* is *%s*\n %s') % (host['name'],stateV,message_tag)
    
    return message

#display_item_characteristics recovery the characteristics of item selected by the user
def display_item_characteristics(context,LANG,API_VAR):
    lang_translations = gettext.translation('action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    
    Cdata=json.loads(ud['ITEM_INFO'])
    itemID=Cdata['IID']
    list_item=API_VAR.get_item_info(itemID)
    for item in list_item:
        stateV=get_state_string(item['status'], _)
        message_tag = ('Tags:')
        for tag in item["tags"]:
            message_tag = message_tag + '\n\t\t' + tag['tag']+' : '+ ('*%s*') % tag['value']
        
        message = _('Host *%s*\nItem *%s* is *%s*\nLast value: *%s %s*\nLast check: *%s*\n %s') % (item['hosts'][0]['name'],item['name'],stateV,item['lastvalue'],item['units'],get_time(item['lastclock']),message_tag)
    
    return message

#display_trigger_characteristics recovery the characteristics of trigger selected by the user
def display_trigger_characteristics(context,LANG,API_VAR):
    lang_translations = gettext.translation('action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    
    Cdata=json.loads(ud['TRIGGER_INFO'])
    triggerID=Cdata['TID']
    list_trigger=API_VAR.get_trigger_info(triggerID)
    for trigger in list_trigger:
        stateV=get_state_string(trigger['status'], _)
        severityV=get_severity_string(trigger['priority'], _)
        valueV = get_value_string(trigger['value'],_)
        message_tag = ('Tags:')
        for tag in trigger["tags"]:
            message_tag = message_tag + '\n\t\t' + tag['tag']+' : '+ ('*%s*') % tag['value']
        message = _('Host *%s*\nTrigger *%s* is *%s*\nExpression: *%s*\nSeverity: *%s*\nValue: *%s* since *%s*\n %s') % (trigger['hosts'][0]['name'],trigger['description'],stateV,trigger['expression'],severityV,valueV,get_time(trigger['lastchange']),message_tag)
    return message

#display_problem_characteristics recovery the characteristics of problem selected by the user
def display_problem_characteristics(context,LANG,API_VAR):
    lang_translations = gettext.translation('action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    
    Cdata=json.loads(ud['PROBLEM_INFO'])
    problemID=Cdata['PID']
    list_problem=API_VAR.get_event_info(problemID)
    for problem in list_problem:
        severityV=get_severity_string(problem['severity'], _)
        acknowledgedV = get_acknowledged_emoji(problem['acknowledged'])
        message_tag = ('Tags:')
        for tag in problem["tags"]:
            message_tag = message_tag + '\n\t\t' + tag['tag']+' : '+ ('*%s*') % tag['value']
        message = _('Problem on *%s*\t\t*%s*\nSince: *%s*\nAcknowledged: *%s*\n%s') % (problem['hosts'][0]['name'],severityV,get_time(problem['clock']),acknowledgedV,message_tag)
    return message

#get_state_string converts the status number to the status text
def get_state_string(status, _):
    switcher = {
        "0": _("enabled"),
        "1": _("disabled")
    }
    return switcher.get(status,"invalid status")

#get_severity_string converts the severity number to the severity text
def get_severity_string(severity, _):
    switcher = {
        "0": telegramEmojiDict['white large square']+_("Not classified"),
        "1": telegramEmojiDict['blue square']+_("Information"),
        "2": telegramEmojiDict['yellow square']+_("Warning"),
        "3": telegramEmojiDict['orange square']+_("Average"),
        "4": telegramEmojiDict['brown square']+_("High"),
        "5": telegramEmojiDict['red square']+_("Disaster"),
    }
    return switcher.get(severity,"invalid severity")

#get_severity_emoji converts the severity number to the severity text
def get_severity_emoji(severity):
    switcher = {
        "0": telegramEmojiDict['white large square'],
        "1": telegramEmojiDict['blue square'],
        "2": telegramEmojiDict['yellow square'],
        "3": telegramEmojiDict['orange square'],
        "4": telegramEmojiDict['brown square'],
        "5": telegramEmojiDict['red square'],
    }
    return switcher.get(severity,"invalid severity")

#get_acknowledged_emoji converts the acknowledged number to the acknowledged text
def get_acknowledged_emoji(acknowledged):
    switcher = {
        "0": telegramEmojiDict['cross mark'],
        "1": telegramEmojiDict['check mark button'],
    }
    return switcher.get(acknowledged,"invalid acknowledged")

#get_value_string converts the value number to the value text
def get_value_string(value, _):
    switcher = {
        "0": telegramEmojiDict['green square']+_("OK"),
        "1": telegramEmojiDict['red square']+_("PROBLEM")
    }
    return switcher.get(value,"invalid value")

#get_time permits to convert a timestamp to a datetime
def get_time(timestamp):
    if timestamp==None:
        return "N/A"
    date = datetime.fromtimestamp(int(timestamp))
    now = datetime.now()
    ecartSecond = (now-date).total_seconds()
    minutes, seconds = divmod(int(ecartSecond), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    month,weeks = divmod(weeks,4)
    year, month = divmod(month,12)
    
    firstVal=""
    secondVal=""
    values = [year,month,weeks,days,hours,minutes,seconds]
    for i in range(len(values)):
      if values[i]!=0.0 and firstVal=="":
        firstVal= "%s%s" % (str(values[i]),get_unity(i))
        continue
      if values[i]!=0.0 and secondVal=="":
        secondVal= "{}{}".format(str(values[i]),get_unity(i))
        break
    return "{} {}".format(firstVal,secondVal)

#get_unity permits to obtain the unity of the time 
def get_unity(i):
    switcher = {
            0: 'y',
            1: 'M',
            2: 'w',
            3: 'd',
            4: 'h',
            5: 'm',
            6: 's'
    }
    return switcher.get(i,"invalid state")