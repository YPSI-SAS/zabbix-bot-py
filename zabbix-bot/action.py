import gettext
from shutil import ExecError
from more_itertools import last
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
from textwrap import fill
import logging


logger = logging.getLogger(__name__)
ACK_MENU, CANCEL = map(chr, range(2))


def build_menu(buttons, n_cols, footer_buttons=None, cancel_button=None):
    """Create a menu with buttons"""
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if footer_buttons:
        menu.append(footer_buttons)
    if cancel_button:
        menu.append(cancel_button)
    return menu


def display_object_button(object, object_list, LANG, api):
    """Display all differents objects in the form of buttons"""
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
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
                if api.zabbix_version  >= 6:
                    status_host = host['interfaces'][0]['available']
                else:
                    status_host = host['available']
                button_list.append(InlineKeyboardButton(text=get_status_host_emoji(status_host)+host['name'],
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
    elif object == "service":  # Display service buttons
        if not object_list:
            message = _('I didn\'t find any services. Please cancel\n')
        else:
            if len(object_list) == 1:
                message = _(
                    'I found one service. Please choose a service or cancel\n')
            else:
                message = _(
                    'I found many services. Please choose one service or cancel\n')
            for service in object_list:
                button_list.append(InlineKeyboardButton(text=get_status_service_emoji(service['status'])+service['name'],
                                                        callback_data='{"SID":"'+service['serviceid']+'"}'))
    elif object == "sla":  # Display service buttons
        if not object_list:
            message = _(
                'I didn\'t find any SLA attached to this service. Please cancel\n')
        else:
            if len(object_list) == 1:
                message = _(
                    'I found one SLA. Please choose a SLA or cancel\n')
            else:
                message = _(
                    'I found many SLA. Please choose one SLA or cancel\n')
            for sla in object_list:
                button_list.append(InlineKeyboardButton(text=sla['name'],
                                                        callback_data='{"SLAID":"'+sla['slaid']+'"}'))
    return message, button_list


def get_status_service_emoji(status):
    """Convert status number of service to status emoji"""
    switcher = {
        "-1": telegramEmojiDict['green square'],
        "0": telegramEmojiDict['white large square'],
        "1": telegramEmojiDict['blue square'],
        "2": telegramEmojiDict['yellow square'],
        "3": telegramEmojiDict['orange square'],
        "4": telegramEmojiDict['brown square'],
        "5": telegramEmojiDict['red square'],
    }
    return switcher.get(status, "invalid status")


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
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    list_host = []
    #Recovery host ID
    Cdata = json.loads(ud['HOST_INFO'])
    hostID = Cdata['HID']
    try:
        #Get information about the host
        list_host = API_VAR.get_host_info(hostID)
        #Create message with host information
        for host in list_host:
            stateV = get_state_string(host['status'], _)
            if API_VAR.zabbix_version >=6:
                status_host = host['interfaces'][0]['available']
            else:
                status_host = host['available']
            availabilityV = get_status_string(status_host
                , _)
            message_tag = ""
            if API_VAR.zabbix_version >=5:
                message_tag = ('Tags:')
                for tag in host["tags"]:
                    message_tag = message_tag + '\n\t\t' + \
                        tag['tag']+' : ' + ('*%s*') % tag['value']
            message = _('Host *%s* is *%s*\nAvailability: *%s*\n%s') % (
                host['name'], stateV, availabilityV, message_tag)
    except Exception as e:
        logger.error("Error in get_host_info to display host characteristics")
        message = (_("*Error* in get\_host\_info"))  

    return message, list_host


def display_item_characteristics(context, LANG, API_VAR):
    """Recovery and create message of item selected by the user"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    list_item = []
    #Recovery item ID
    Cdata = json.loads(ud['ITEM_INFO'])
    itemID = Cdata['IID']
    try:
        #Get information about the item
        list_item = API_VAR.get_item_info(itemID)
        #Create message with item information
        for item in list_item:
            stateV = get_state_string(item['status'], _)
            message_tag=""
            if API_VAR.zabbix_version >=6:
                message_tag = ('Tags:')
                for tag in item["tags"]:
                    message_tag = message_tag + '\n\t\t' + \
                        tag['tag']+' : ' + ('*%s*') % tag['value']

            message = _('Host *%s*\nItem *%s* is *%s*\nLast value: *%s %s*\nLast check: *%s*\n %s') % (
                item['hosts'][0]['name'], item['name'], stateV, item['lastvalue'], item['units'], get_time(item['lastclock']), message_tag)
    except Exception as e:
        logger.error("Error in get_item_info to display item characteristics")
        message = (_("*Error* in get\_item\_info"))

    return message, list_item


def display_trigger_characteristics(context, LANG, API_VAR):
    """Recovery and create message of trigger selected by the user"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    list_trigger = []
    #Recovery trigger ID
    Cdata = json.loads(ud['TRIGGER_INFO'])
    triggerID = Cdata['TID']
    try:
        #Get information about the trigger
        list_trigger = API_VAR.get_trigger_info(triggerID)
        #Create message with trigger information
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
    except Exception as e:
        logger.error("Error in get_trigger_info to display trigger characteristics")
        message = (_("*Error* in get\_trigger\_info"))

    return message, list_trigger


def display_problem_characteristics(context, LANG, API_VAR):
    """Recovery and create message of problem selected by the user"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    list_problem = []
    #Recovery problem ID
    Cdata = json.loads(ud['PROBLEM_INFO'])
    problemID = Cdata['PID']
    try:
        #Get information about the problem
        list_problem = API_VAR.get_event_info(problemID)
        #Create message with problem information
        for problem in list_problem:
            severityV = get_severity_string(problem['severity'], _)
            acknowledgedV = get_acknowledged_emoji(problem['acknowledged'])
            message_tag = ('Tags:')
            for tag in problem["tags"]:
                message_tag = message_tag + '\n\t\t' + \
                    tag['tag']+' : ' + ('*%s*') % tag['value']
            message = _('Problem on *%s*\t\t*%s*\nSince: *%s*\nAcknowledged: *%s*\n%s') % (
                problem['hosts'][0]['name'], severityV, get_time(problem['clock']), acknowledgedV, message_tag)
    except Exception as e:
        logger.error("Error in get_event_info to display problem characteristics")
        message = (_("*Error* in get\_event\_info"))

    return message, list_problem


def display_service_characteristics(context, LANG, API_VAR):
    """Recovery and create message of service selected by the user"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    ud = context.user_data
    message = str()
    list_service = []
    #Recovery service ID
    Cdata = json.loads(ud['SERVICE_INFO'])
    serviceID = Cdata['SID']
    try:
        #Get information about the service
        list_service = API_VAR.get_service_info(serviceID)
        #Create message with service information
        for service in list_service:
            stateV = get_status_service_string(service['status'], _)
            message_tag = ('Tags:')
            for tag in service["tags"]:
                message_tag = message_tag + '\n\t\t' + \
                    tag['tag']+' : ' + ('*%s*') % tag['value']
            message_problem_tag = ('Problem tags:')
            for tag in service["problem_tags"]:
                if tag['operator'] == "0":
                    msg = tag['tag']+(' %s *%s*') % ("equals", tag['value'])
                elif tag['operator'] == "2":
                    msg = tag['tag']+(' %s *%s*') % ("like", tag['value'])
                else:
                    tag['tag']+' : ' + ('*%s*') % tag['value']
                message_problem_tag = message_problem_tag + '\n\t\t' + msg

            message = _('Service *%s* is *%s*\nCreated at: *%s*\n%s\n%s') % (
                service['name'], stateV, datetime.fromtimestamp(int(service['created_at'])), message_tag, message_problem_tag)
    except Exception as e:
        logger.error("Error in get_service_info to display service characteristics")
        message = (_("*Error* in get\_service\_info"))  

    return message, list_service


def get_status_service_string(status, _):
    """Convert status number of service to string"""
    switcher = {
        "-1": telegramEmojiDict['green square']+_("OK"),
        "0": telegramEmojiDict['white large square']+_("Not classified"),
        "1": telegramEmojiDict['blue square']+_("Information"),
        "2": telegramEmojiDict['yellow square']+_("Warning"),
        "3": telegramEmojiDict['orange square']+_("Average"),
        "4": telegramEmojiDict['brown square']+_("High"),
        "5": telegramEmojiDict['red square']+_("Disaster"),
    }
    return switcher.get(status, "invalid status")


def display_global_status(api, LANG):
    """Get all informations about a server"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext
    #Init state variables
    available_host = 0
    unavailable_host = 0
    unknown_host = 0
    not_classified_problem = 0
    information_problem = 0
    warning_problem = 0
    average_problem = 0
    high_problem = 0
    disaster_problem = 0
    try:
        #Get host information
        list_host = api.get_list_hosts()

        #Calculate number of host in each state
        for host in list_host:
            if api.zabbix_version >=6:
                status_host = host['interfaces'][0]['available']
            else:
                status_host = host['available']
            if status_host == "0":
                unknown_host = unknown_host+1
            elif status_host == "1":
                available_host = available_host+1
            elif status_host == "2":
                unavailable_host = unavailable_host+1

        #Get problem information
        list_problem = api.get_list_problems()

        #Calculate number of problem in each state
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
    except Exception as e:
        logger.error("Error to get global status")
        message = _("*Error* to get global information")
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
    return get_val_time(ecartSecond)


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
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext

    #Get values and time
    values = list()
    time = list()
    for val in data:
        time.append(str(datetime.fromtimestamp(int(val["clock"]))))
        values.append(float(val["value"]))

    values.reverse()
    time.reverse()

    #Create subplot
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

    #Change differents params of the graph
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
    if os.path.exists("../documents/images/"+str(list_item[0]["itemid"])+".png"):
        os.remove("../documents/images/"+str(list_item[0]["itemid"])+".png")
    plt.savefig("../documents/images/"+str(list_item[0]["itemid"])+".png")
    return "../documents/images/"+str(list_item[0]["itemid"])+".png"


def get_table_information_problem(api, LANG):
    """"Get problems information about Zabbix server"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext

    try:
        #Create table header
        table = pt.PrettyTable(
            [_('Host'), _('Severity-Problem'), _('Duration'), _('Ack')])
        table.align[_('Severity-Problem')] = 'l'
        table.align[_('Host')] = 'l'

        #Get problem list
        list_problem = api.get_list_problems()
        for problem in list_problem:
            #Get problem information
            host_info = api.get_event_info(problem['eventid'])
            severity_emoji = get_severity_emoji(problem['severity'])
            time = get_time(int(problem['clock']))
            acknowledged_emoji = get_acknowledged_emoji(problem['acknowledged'])
            table.add_row([fill(host_info[0]["hosts"][0]["name"], width=30), fill(
                severity_emoji+problem['name'], width=30), time, acknowledged_emoji])
        return table
    except Exception as e:
        logger.error("Error to get problem information")
        message = _("\nError to get problem information")
        return message


def get_table_information_maintenance(api, LANG):
    """"Get maintenances information about Zabbix server"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext

    try:
        #Create table header
        table = pt.PrettyTable(
            [_('Name'), _('Active since'), _('Active till'), _('State')])
        table.align[_('Name')] = 'l'
        table.align[_('State')] = 'l'
        now = datetime.now()
        
        #Get maintenance list
        list_maintenance = api.get_list_maintenances()
        for maintenance in list_maintenance:
            #Calculate if the maintenance is passed or not
            if now > datetime.fromtimestamp(int(maintenance['active_since'])) and now < datetime.fromtimestamp(int(maintenance['active_till'])):
                table.add_row([fill(maintenance['name'], width=30), datetime.fromtimestamp(int(maintenance['active_since'])),
                            datetime.fromtimestamp(int(maintenance['active_till'])), telegramEmojiDict['green square']+_("Active")])
            elif now > datetime.fromtimestamp(int(maintenance['active_till'])):
                table.add_row([fill(maintenance['name'], width=30), datetime.fromtimestamp(int(maintenance['active_since'])),
                            datetime.fromtimestamp(int(maintenance['active_till'])), telegramEmojiDict['red square']+_("Expired")])
            elif now < datetime.fromtimestamp(int(maintenance['active_since'])):
                table.add_row([fill(maintenance['name'], width=30), datetime.fromtimestamp(int(maintenance['active_since'])),
                            datetime.fromtimestamp(int(maintenance['active_till'])), telegramEmojiDict['orange square']+_("Approaching")])
        return table
    except Exception as e:
        logger.error("Error to get maintenance information")
        message = _("\nError to get maintenance information")
        return message


def get_table_last_values_host(LANG, element_items, host_name):
    """"Get all last values for host"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext

    #Get table header
    table = pt.PrettyTable(
        [_('Name'), _('Last check'), _('Last value')])
    table.align[_('Name')] = 'l'
    table.align[_('Last value')] = 'l'
    #Add value of items in table
    for item in element_items:
        last_value = item['lastvalue']
        if len(last_value) > 200:
            last_value = last_value[0:250] + "..."
        if "-" in last_value:
            last_value = last_value.replace('-', '\-')
        table.add_row([fill(item['name'], width=30), get_time(
            item['lastclock']), fill(last_value, width=50)])
    return table.get_string(title=host_name)


def get_table_sla_report(LANG, api, service_id, sla_id):
    """Get SLA report for service"""
    #Get translation
    lang_translations = gettext.translation(
        'action', localedir='../locales', languages=[LANG])
    lang_translations.install()
    _ = lang_translations.gettext

    table = pt.PrettyTable()
    
    try:
        #Get SLA information
        sla_report = api.get_sla_report_by_service(sla_id, service_id)
        sla_info = api.get_sla_by_service(sla_id=sla_id)
        sla_report_period = sla_report['periods']
        sla_report_period.reverse()
        sla_report_sli = list()
        for i in range(len(sla_report_period)):
            sla_report_sli.append(sla_report['sli'][i][0])
        sla_report_sli.reverse()

        #Create table header
        table = pt.PrettyTable([get_column_name(sla_info[0]['period'], _), _('SLO'), _('SLI'), _('Uptime'), _('Downtime'), _('Error budget')])

        # Limit to display in telegram
        number_max_val = 40
        if len(sla_report_period) < number_max_val:
            number_max_val = len(sla_report_period)

        #Add value of SLA in table
        for i in range(number_max_val):
            period = get_date_value_depending_period(
                sla_info[0]['period'], sla_report_period[i]['period_from'], sla_report_period[i]['period_to'])
            sli = float(np.round(sla_report_sli[i]['sli'], 4))
            uptime = get_val_time(sla_report_sli[i]['uptime'])
            downtime = get_val_time(sla_report_sli[i]['downtime'])
            error_budget = get_val_time(abs(sla_report_sli[i]['error_budget']))
            if sla_report_sli[i]['error_budget'] < 0:
                error_budget = "-" + error_budget
            table.add_row([period, sla_info[0]['slo'], sli,
                        uptime, downtime, error_budget])
        
        return table.get_string(title=sla_info[0]['name'])

    except Exception as e:
        logger.error("Error in get_sla_report")
        return _("\nError to get sla values")

def get_val_time(val_second):
    """Convert time to elapsed time until now"""
    minutes, seconds = divmod(int(val_second), 60)
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


def get_column_name(period, _):
    """Convert period to text"""
    switcher = {
        "0": _("Day"),
        "1": _("Week"),
        "2": _("Month"),
        "3": _("Quarter"),
        "4": _("Year")
    }
    return switcher.get(period, "invalid status")


def get_date_value_depending_period(period, period_from_timestamp, period_to_timestamp):
    """Get period of time depending SLA period"""
    period_from_timestamp = datetime.fromtimestamp(int(period_from_timestamp))
    period_to_timestamp = datetime.fromtimestamp(int(period_to_timestamp))

    if period == "0":
        return str(period_from_timestamp.year) + "-"+str(period_from_timestamp.month)+"-"+str(period_from_timestamp.day)
    elif period == "1":
        return str(period_from_timestamp.year) + "-"+str(period_from_timestamp.month)+"-"+str(period_from_timestamp.day)+" -- "+str(period_to_timestamp.month)+"-"+str(period_to_timestamp.day)
    elif period == "2":
        return str(period_from_timestamp.year) + "-"+str(period_from_timestamp.month)
    elif period == "3":
        return str(period_from_timestamp.year) + "-"+str(period_from_timestamp.month) + " -- "+str(period_to_timestamp.month-1)
    elif period == "4":
        return str(period_from_timestamp.year)
