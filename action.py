import gettext
from telegram import InlineKeyboardButton
from emojiDict import telegramEmojiDict
import json
from datetime import datetime
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import prettytable as pt

ACK_MENU, CANCEL = map(chr, range(2))


def build_menu(buttons, n_cols, footer_buttons=None, cancel_button=None):
    """Create a menu with buttons"""
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if footer_buttons:
        menu.append(footer_buttons)
    if cancel_button:
        menu.append(cancel_button)
    return menu


def display_object_button(object, object_list, LANG):
    """Display all differents objects in the form of buttons"""
    lang_translations = gettext.translation(
        'action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    button_list = list()
    message = str()
    if object == "host":  # Display host buttons
        if not object_list:
            message = _('I didn\'t find any hosts. Please cancel\n')
        else:
            if len(object_list) == 1:
                message = _(
                    'I found one host. Please choose a host or cancel\n')
            else:
                message = _(
                    'I found many hosts. Please choose one host or cancel\n')
            for host in object_list:
                button_list.append(InlineKeyboardButton(text=get_status_host_emoji(host['interfaces'][0]['available'])+host['name'],
                                                        callback_data='{"HID":"'+host['hostid']+'"}'))
    elif object == "HG":  # Display host group buttons
        if not object_list:
            message = _('I didn\'t find any hostgroups. Please cancel\n')
        else:
            if len(object_list) == 1:
                message = _(
                    'I found one hostgroup. Please choose a hostgroup or cancel\n')
            else:
                message = _(
                    'I found many hostgroups. Please choose one hostgroup or cancel\n')
            for hostgroup in object_list:
                button_list.append(InlineKeyboardButton(text=hostgroup['name'],
                                                        callback_data='{"HGID":"'+hostgroup['groupid']+'"}'))
    elif object == "item":  # Display item buttons
        if not object_list:
            message = _('I didn\'t find any items. Please cancel\n')
        else:
            if len(object_list) == 1:
                message = _(
                    'I found one item. Please choose a item or cancel\n')
            else:
                message = _(
                    'I found many items. Please choose one item or cancel\n')
            for item in object_list:
                button_list.append(InlineKeyboardButton(text=get_status_emoji(item['status'])+item['name'],
                                                        callback_data='{"IID":"'+item['itemid']+'"}'))
    elif object == "trigger":  # Display trigger buttons
        if not object_list:
            message = _('I didn\'t find any triggers. Please cancel\n')
        else:
            if len(object_list) == 1:
                message = _(
                    'I found one trigger. Please choose a trigger or cancel\n')
            else:
                message = _(
                    'I found many triggers. Please choose one trigger or cancel\n')
            for trigger in object_list:
                button_list.append(InlineKeyboardButton(text=get_status_emoji(trigger['status'])+trigger['description'],
                                                        callback_data='{"TID":"'+trigger['triggerid']+'"}'))
    elif object == "problem":  # Display problem buttons
        if not object_list:
            message = _('I didn\'t find any problems. Please cancel\n')
        else:
            if len(object_list) == 1:
                message = _(
                    'I found one problem. Please choose a problem or cancel\n')
            else:
                message = _(
                    'I found many problems. Please choose one problem or cancel\n')
            for problem in object_list:
                button_list.append(InlineKeyboardButton(text=get_severity_emoji(problem['severity'])+get_acknowledged_emoji(problem['acknowledged'])+problem['name']+_(' since ')+get_time(problem['clock']),
                                                        callback_data='{"PID":"'+problem['eventid']+'"}'))
    return message, button_list


def get_status_host_emoji(status):
    """Convert status number of host to status emoji"""
    switcher = {
        "0": telegramEmojiDict['white large square'],
        "1": telegramEmojiDict['green square'],
        "2": telegramEmojiDict['red square']
    }
    return switcher.get(status, "invalid status")


def get_status_emoji(status):
    """Convert status number of object to status emoji"""
    switcher = {
        "0": telegramEmojiDict['green square'],
        "1": telegramEmojiDict['red square']
    }
    return switcher.get(status, "invalid status")


def display_host_characteristics(context, LANG, API_VAR):
    """Recovery and create message of host selected by the user"""
    lang_translations = gettext.translation(
        'action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()

    Cdata = json.loads(ud['HOST_INFO'])
    hostID = Cdata['HID']
    list_host = API_VAR.get_host_info(hostID)
    for host in list_host:
        stateV = get_state_string(host['status'], _)
        availabilityV = get_status_string(
            host['interfaces'][0]['available'], _)
        message_tag = ('Tags:')
        for tag in host["tags"]:
            message_tag = message_tag + '\n\t\t' + \
                tag['tag']+' : ' + ('*%s*') % tag['value']
        message = _('Host *%s* is *%s*\nAvailability: *%s*\n%s') % (
            host['name'], stateV, availabilityV, message_tag)

    return message


def display_item_characteristics(context, LANG, API_VAR):
    """Recovery and create message of item selected by the user"""
    lang_translations = gettext.translation(
        'action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()

    Cdata = json.loads(ud['ITEM_INFO'])
    itemID = Cdata['IID']
    list_item = API_VAR.get_item_info(itemID)
    for item in list_item:
        stateV = get_state_string(item['status'], _)
        message_tag = ('Tags:')
        for tag in item["tags"]:
            message_tag = message_tag + '\n\t\t' + \
                tag['tag']+' : ' + ('*%s*') % tag['value']

        message = _('Host *%s*\nItem *%s* is *%s*\nLast value: *%s %s*\nLast check: *%s*\n %s') % (
            item['hosts'][0]['name'], item['name'], stateV, item['lastvalue'], item['units'], get_time(item['lastclock']), message_tag)

    return message


def display_trigger_characteristics(context, LANG, API_VAR):
    """Recovery and create message of trigger selected by the user"""
    lang_translations = gettext.translation(
        'action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()

    Cdata = json.loads(ud['TRIGGER_INFO'])
    triggerID = Cdata['TID']
    list_trigger = API_VAR.get_trigger_info(triggerID)
    for trigger in list_trigger:
        stateV = get_state_string(trigger['status'], _)
        severityV = get_severity_string(trigger['priority'], _)
        valueV = get_value_string(trigger['value'], _)
        message_tag = ('Tags:')
        for tag in trigger["tags"]:
            message_tag = message_tag + '\n\t\t' + \
                tag['tag']+' : ' + ('*%s*') % tag['value']
        message = _('Host *%s*\nTrigger *%s* is *%s*\nExpression: *%s*\nSeverity: *%s*\nValue: *%s* since *%s*\n %s') % (
            trigger['hosts'][0]['name'], trigger['description'], stateV, trigger['expression'], severityV, valueV, get_time(trigger['lastchange']), message_tag)
    return message


def display_problem_characteristics(context, LANG, API_VAR):
    """Recovery and create message of problem selected by the user"""
    lang_translations = gettext.translation(
        'action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()

    Cdata = json.loads(ud['PROBLEM_INFO'])
    problemID = Cdata['PID']
    list_problem = API_VAR.get_event_info(problemID)
    for problem in list_problem:
        severityV = get_severity_string(problem['severity'], _)
        acknowledgedV = get_acknowledged_emoji(problem['acknowledged'])
        message_tag = ('Tags:')
        for tag in problem["tags"]:
            message_tag = message_tag + '\n\t\t' + \
                tag['tag']+' : ' + ('*%s*') % tag['value']
        message = _('Problem on *%s*\t\t*%s*\nSince: *%s*\nAcknowledged: *%s*\n%s') % (
            problem['hosts'][0]['name'], severityV, get_time(problem['clock']), acknowledgedV, message_tag)
    return message


def display_global_status(api, LANG):
    """Get all informations about a server"""
    lang_translations = gettext.translation(
        'action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    available_host = 0
    unavailable_host = 0
    unknown_host = 0
    not_classified_problem = 0
    information_problem = 0
    warning_problem = 0
    average_problem = 0
    high_problem = 0
    disaster_problem = 0

    list_host = api.get_list_hosts()
    list_problem = api.get_list_problems()

    for host in list_host:
        status_host = host['interfaces'][0]['available']
        if status_host == "0":
            unknown_host = unknown_host+1
        elif status_host == "1":
            available_host = available_host+1
        elif status_host == "2":
            unavailable_host = unavailable_host+1

    for problem in list_problem:
        status_problem = problem['severity']
        if status_problem == "0":
            not_classified_problem = not_classified_problem+1
        elif status_problem == "1":
            information_problem = information_problem+1
        elif status_problem == "2":
            warning_problem = warning_problem+1
        elif status_problem == "3":
            average_problem = average_problem+1
        elif status_problem == "4":
            high_problem = high_problem+1
        elif status_problem == "5":
            disaster_problem = disaster_problem+1

    message = _('*Host availability*\n%s : %d\n%s : %d\n%s : %d\nTOTAL: %d\n\n*Problems by severity*\n%s : %d\n%s : %d\n%s : %d\n%s : %d\n%s : %d\n%s : %d\nTOTAL: %d') % (telegramEmojiDict['green square']+_("Available"), available_host, telegramEmojiDict['red square']+_("Not available"), unavailable_host, telegramEmojiDict['white large square']+_("Unknown"), unknown_host, len(list_host), telegramEmojiDict['red square']+_(
        "Disaster"), disaster_problem, telegramEmojiDict['brown square']+_("High"), high_problem, telegramEmojiDict['orange square']+_("Average"), average_problem, telegramEmojiDict['yellow square']+_("Warning"), warning_problem, telegramEmojiDict['blue square']+_("Information"), information_problem, telegramEmojiDict['white large square']+_("Not classified"), not_classified_problem, len(list_problem))
    return message


def get_state_string(status, _):
    """Convert status number to status text"""
    switcher = {
        "0": _("enabled"),
        "1": _("disabled")
    }
    return switcher.get(status, "invalid status")


def get_status_string(status, _):
    """Convert status number of host to status text"""
    switcher = {
        "0": telegramEmojiDict['white large square']+_("Unknown"),
        "1": telegramEmojiDict['green square']+_("Available"),
        "2": telegramEmojiDict['red square']+_("Not available")
    }
    return switcher.get(status, "invalid status")


def get_severity_string(severity, _):
    """Convert severity number to severity text"""
    switcher = {
        "0": telegramEmojiDict['white large square']+_("Not classified"),
        "1": telegramEmojiDict['blue square']+_("Information"),
        "2": telegramEmojiDict['yellow square']+_("Warning"),
        "3": telegramEmojiDict['orange square']+_("Average"),
        "4": telegramEmojiDict['brown square']+_("High"),
        "5": telegramEmojiDict['red square']+_("Disaster"),
    }
    return switcher.get(severity, "invalid severity")


def get_severity_emoji(severity):
    """Convert severity number to severity emoji"""
    switcher = {
        "0": telegramEmojiDict['white large square'],
        "1": telegramEmojiDict['blue square'],
        "2": telegramEmojiDict['yellow square'],
        "3": telegramEmojiDict['orange square'],
        "4": telegramEmojiDict['brown square'],
        "5": telegramEmojiDict['red square'],
    }
    return switcher.get(severity, "invalid severity")


def get_acknowledged_emoji(acknowledged):
    """Convert acknowledged number to the acknowledged text"""
    switcher = {
        "0": telegramEmojiDict['cross mark'],
        "1": telegramEmojiDict['check mark button'],
    }
    return switcher.get(acknowledged, "invalid acknowledged")


def get_value_string(value, _):
    """Convert value number for problem to value text"""
    switcher = {
        "0": telegramEmojiDict['green square']+_("OK"),
        "1": telegramEmojiDict['red square']+_("PROBLEM")
    }
    return switcher.get(value, "invalid value")


def get_time(timestamp):
    """Convert timestamp to a datetime for know duration"""
    if timestamp == None:
        return "N/A"
    date = datetime.fromtimestamp(int(timestamp))
    now = datetime.now()
    ecartSecond = (now-date).total_seconds()
    minutes, seconds = divmod(int(ecartSecond), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    month, weeks = divmod(weeks, 4)
    year, month = divmod(month, 12)

    firstVal = ""
    secondVal = ""
    values = [year, month, weeks, days, hours, minutes, seconds]
    for i in range(len(values)):
        if values[i] != 0.0 and firstVal == "":
            firstVal = "%s%s" % (str(values[i]), get_unity(i))
            continue
        if values[i] != 0.0 and secondVal == "":
            secondVal = "{}{}".format(str(values[i]), get_unity(i))
            break
    return "{} {}".format(firstVal, secondVal)


def get_unity(i):
    """Obtain the unity of the time"""
    switcher = {
        0: 'y',
        1: 'M',
        2: 'w',
        3: 'd',
        4: 'h',
        5: 'm',
        6: 's'
    }
    return switcher.get(i, "invalid state")


def get_image_data(data, list_item, LANG):
    """Create graph for item and save at image"""
    lang_translations = gettext.translation(
        'action', localedir='locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext

    values = list()
    time = list()
    for val in data:
        time.append(str(datetime.fromtimestamp(int(val["clock"]))))
        values.append(float(val["value"]))

    values.reverse()
    time.reverse()

    __, ax = plt.subplots(figsize=(12, 6))
    ax.plot(time, values, label=list_item[0]['units'])

    # Check if there are values or not
    if len(values) == 0:
        plt.ylim(0, 1)
        plt.figtext(
            0.5,
            0.5,
            _("No values"),
            horizontalalignment="center",
            fontsize=35,
            fontweight="bold",
        )

    # Display the point if there are one value
    if len(values) == 1:
        plt.scatter(time, values)

    # Change the scale of the x axis to see the values
    start, end = ax.get_xlim()
    if len(time) > 30:
        ax.xaxis.set_ticks(np.arange(start, end, len(time) / 30))

    plt.title(list_item[0]['name'])
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.30)
    if list_item[0]['units'] != "":
        plt.legend(
            loc="best", fancybox=True, shadow=True
        )

    # plt.tight_layout()
    plt.grid()

    # Save the graph to image
    if os.path.exists("image.png"):
        os.remove("image.png")
    plt.savefig("image.png")


def get_table_information_problem(api):
    """"Get problems information about Zabbix server"""
    table = pt.PrettyTable(['Host', 'Severity-Problem', 'Duration', 'Ack'])
    table.align['Severity-Problem'] = 'l'
    table.align['Host'] = 'l'
    list_problem = api.get_list_problems()
    for problem in list_problem:
        host_info = api.get_event_info(problem['eventid'])
        severity_emoji = get_severity_emoji(problem['severity'])
        time = get_time(int(problem['clock']))
        acknowledged_emoji = get_acknowledged_emoji(problem['acknowledged'])
        table.add_row([host_info[0]["hosts"][0]["name"],
                      severity_emoji+problem['name'], time, acknowledged_emoji])
    return table


def get_table_information_maintenance(api):
    """"Get maintenances information about Zabbix server"""
    table = pt.PrettyTable(['Name', 'Active since', 'Active till', 'State'])
    table.align['Name'] = 'l'
    table.align['State'] = 'l'
    now = datetime.now()
    list_maintenance = api.get_list_maintenances()
    for maintenance in list_maintenance:
        if now > datetime.fromtimestamp(int(maintenance['active_since'])) and now < datetime.fromtimestamp(int(maintenance['active_till'])):
            table.add_row([maintenance['name'], datetime.fromtimestamp(int(maintenance['active_since'])),
                           datetime.fromtimestamp(int(maintenance['active_till'])), telegramEmojiDict['green square']+"Active"])
        elif now > datetime.fromtimestamp(int(maintenance['active_till'])):
            table.add_row([maintenance['name'], datetime.fromtimestamp(int(maintenance['active_since'])),
                           datetime.fromtimestamp(int(maintenance['active_till'])), telegramEmojiDict['red square']+"Expired"])
        elif now < datetime.fromtimestamp(int(maintenance['active_since'])):
            table.add_row([maintenance['name'], datetime.fromtimestamp(int(maintenance['active_since'])),
                           datetime.fromtimestamp(int(maintenance['active_till'])), telegramEmojiDict['orange square']+"Approaching"])
    return table
