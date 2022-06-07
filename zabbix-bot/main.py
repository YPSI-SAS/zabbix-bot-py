#! /usr/bin/python3
# -*- coding: utf-8 -*-
from distutils.command.build import build
import logging
from telegram.ext import *
from telegram import *
from action import *
from functools import wraps
import gettext
from emojiDict import telegramEmojiDict
import json
import yaml
import os
from reports.report_service import ReportService
from reports.report_host import ReportHost
from command import Command
from display_information import DisplayInformation

from request_API import API

# log Management
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename='zabbix-bot.log'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global variables
START_OVER, ZABBIX_URL, API_VAR, TYPING, ZABBIX_BOT_USERNAME, ZABBIX_BOT_PASSWORD, DISPLAY_INFORMATION = map(chr, range(7))

DISPLAY_ACTION_SERVICE = "display_action_service"
CHOOSE_SERVICE = "choose_service"
DISPLAY_ACTION_GRAPH = "display_action_graph"
MESSAGE = "message"
DISPLAY_ACTION_PROBLEM = "display_action_problem"
CHOOSE_PROBLEM = "choose_problem"
DISPLAY_ACTION_TRIGGER = "display_action_trigger"
CHOOSE_TRIGGER = "choose_trigger"
DISPLAY_ACTION_ITEM = "display_action_item"
CHOOSE_ITEM = "choose_item"
DISPLAY_ACTION = "display_action"
CHOOSE_HOSTGROUP = "choose_hostgroup"
TAG_HOST = "tag_host"
NAME_HOST = "name_host"
CHOOSE_HOST = "choose_host"
STOPPING = "stopping"
SERVER = "server"
CHOOSE_LANG = "choose_lang"
CHOOSE_MODE_LOGGER = "choose_mode_logger"
CHOOSE_SETTING = "choose_setting"
CANCEL = "cancel"
ACTION_START = "action_start"
DIPLAY_ACTION_VALUE = "display_action_value"
LAST_VALUE = "last_value"
SERVICE_MENU = "service_menu"
CHANGE_SEVERITY = "change_severity"
MESSAGE_MENU = "message_menu"
CHANGE_SEVERITY_MENU = "change_severity_menu"
UNACKNOWLEDGE = "unacknowledge"
ACKNOWLEDGE = "acknowledge"
ENABLE_TRIGGER = "enable_trigger"
DISABLE_TRIGGER = "disable_trigger"
GRAPH_MENU = "graph_menu"
ENABLE_ITEM = "enable_item"
DISABLE_ITEM = "disable_item"
PROBLEM_MENU = "problem_menu"
TRIGGER_MENU = "trigger_menu"
ITEM_MENU = "item_menu"
ENABLE_HOST = "enable_host"
DISABLE_HOST = "disable_host"
HOST_GROUP_MENU = "host_group_menu"
PRECEDENT_VALUES = "precedent_values"
NEXT_VALUES = "next_values"
SETTING_MENU = "setting_menu"
ALL_MENU = "all_menu"
PRECEDENT = "precedent"
NEXT = "next"
HOST_MENU_NAME = "host_menu_name"
HOST_MENU_TAG = "host_menu_tag"
LOCATION_MENU = "location_menu"
DIPLAY_ACTION_LOCATION = "display_action_location"
SLA_MENU = "sla_menu"
CHOOSE_SLA = "choose_sla"
DISPLAY_ACTION_SLA = "display_action_sla"
PDF_MENU = "pdf_menu"
DISPLAY_ACTION_PDF = "display_action_pdf"
END_SERVICE = "end_service"

LANG = "en"
NAME_SERVER = ""

lang_translations = gettext.translation(
    "main", localedir="../locales", languages=[LANG])
lang_translations.install()
_ = lang_translations.gettext

END = ConversationHandler.END


def send_typing_action(func):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return command_func


def send_document_action(func):
    """Sends document action while processing func command."""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_DOCUMENT
        )
        return func(update, context, *args, **kwargs)

    return command_func


def send_photo_action(func):
    """Sends photo action while processing func command."""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_PHOTO
        )
        return func(update, context, *args, **kwargs)

    return command_func


def display_message_bot(update, context, message, reply_markup):
    """Display message and keyboard in conversation"""
    if context.user_data['AFTER_BOT_SEND'] == True:
        context.user_data['AFTER_BOT_SEND'] = False
        context.bot.send_message(update.effective_chat.id, text=message,
                                 parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        context.user_data[START_OVER] = False
        return
    if not context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(
            text=message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    else:
        update.message.reply_markdown(text=message, reply_markup=reply_markup)
    context.user_data[START_OVER] = False


@send_typing_action
def navigation_elements(update, context):
    """Navigate in differents pages of elements"""
    ud = context.user_data
    # Get the correct list of objects depending to type request
    try:
        if ud["TYPE_REQUEST"] == "get_list_hosts":
            elements_list = ud[API_VAR].get_list_hosts()
        elif ud["TYPE_REQUEST"] == "get_list_hosts_with_name":
            elements_list = ud[API_VAR].get_list_hosts_with_name(ud["NAME_HOST"])
        elif ud["TYPE_REQUEST"] == "get_list_hosts_with_tag":
            elements_list = ud[API_VAR].get_list_hosts_with_tag(ud["TAG_HOST"])
        elif ud["TYPE_REQUEST"] == "get_list_hostgroups":
            elements_list = ud[API_VAR].get_list_hostgroups()
        elif ud["TYPE_REQUEST"] == "get_list_hosts_with_hostgroup":
            elements_list = ud[API_VAR].get_list_hosts_with_hostgroup(
                ud["ID_HOSTGROUP"])
        elif ud["TYPE_REQUEST"] == "get_list_items":
            elements_list = ud[API_VAR].get_list_items(ud["ID_HOST"])
        elif ud["TYPE_REQUEST"] == "get_list_triggers_by_host":
            elements_list = ud[API_VAR].get_list_triggers_by_host(ud["ID_HOST"])
        elif ud["TYPE_REQUEST"] == "get_list_triggers_by_item":
            elements_list = ud[API_VAR].get_list_triggers_by_item(ud["ID_ITEM"])
        elif ud["TYPE_REQUEST"] == "get_list_problems_by_host":
            elements_list = ud[API_VAR].get_list_problems_by_host(ud["ID_HOST"])
        elif ud["TYPE_REQUEST"] == "get_list_problems_by_trigger":
            elements_list = ud[API_VAR].get_list_problems_by_trigger(
                ud["ID_TRIGGER"])
        elif ud["TYPE_REQUEST"] == "get_list_services":
            elements_list = ud[API_VAR].get_list_services()
        elif ud["TYPE_REQUEST"] == "get_list_services_parent_child":
            elements_list = ud[API_VAR].get_list_services_parent_child(
                ud["PARENT_CHILD_ID"])
        elif ud["TYPE_REQUEST"] == "get_list_problems_by_service":
            elements_list = ud[API_VAR].get_list_problems_by_service(
                ud["PROBLEM_ID"])
        elif ud["TYPE_REQUEST"] == "get_sla_by_service":
            elements_list = ud[API_VAR].get_sla_by_service(
                service_id=ud['ID_SERVICE'])

        logger.info("Request %s executed", ud["TYPE_REQUEST"])
        
        if ud['OBJECT'] == 'problem':
            numberHostDisplay = 15
        else:
            numberHostDisplay = 26  # Max number of objects by pages
        numberPages = int(len(elements_list) / numberHostDisplay)

        # Get correct elements depending the selected page
        if ud["NUMBER"] < numberPages:
            elements_list = elements_list[
                ud["NUMBER"] * numberHostDisplay: (ud["NUMBER"] + 1) * numberHostDisplay
            ]
        else:
            elements_list = elements_list[ud["NUMBER"] * numberHostDisplay:]

        # Get elements in button_list
        message, button_list = display_object_button(
            ud["OBJECT"], elements_list, LANG)

        display_information = DisplayInformation(LANG, ud[API_VAR])
        # Create footer elements
        footer_buttons = list()
        if ud["NUMBER"] > 0:
            display_information.add_button_in_list(footer_buttons, "<<", str(PRECEDENT))
        
        text_button = _("Page %s") % (str(ud["NUMBER"] + 1))
        display_information.add_button_in_list(footer_buttons, text_button, str(ud["NUMBER"]))

        if ud["NUMBER"] < numberPages:
            display_information.add_button_in_list(footer_buttons, ">>", str(NEXT))
            
        # Create cancel button
        cancel_button = display_information.get_cancel_button()
        if ud["OBJECT"] == "problem":
            reply_markup = InlineKeyboardMarkup(
                build_menu(
                    button_list,
                    n_cols=1,
                    footer_buttons=footer_buttons,
                    cancel_button=cancel_button,
                )
            )
        else:
            reply_markup = InlineKeyboardMarkup(
                build_menu(
                    button_list,
                    n_cols=2,
                    footer_buttons=footer_buttons,
                    cancel_button=cancel_button,
                )
            )
        display_message_bot(update, context, message, reply_markup)
    except Exception as e:
        logger.error("Error in "+ud["TYPE_REQUEST"])
        return True

def create_user_data_to_list_element(context, type_request, object, number):
    ud = context.user_data
    ud["TYPE_REQUEST"] = type_request
    ud["OBJECT"] = object
    ud["NUMBER"] = number

def list_host(update, context):
    """Display all hosts"""
    create_user_data_to_list_element(context, "get_list_hosts", "host", 0)
    error = navigation_elements(update, context)
    if error :
        context.user_data[START_OVER] = True
        message_update = _("*Error* to list all hosts\n\n")
        start(update, context, message_update)
        return END
    return CHOOSE_HOST


def next(update, context):
    """Pass at the next page"""
    ud = context.user_data
    ud["NUMBER"] = ud["NUMBER"] + 1
    navigation_elements(update, context)
    if ud['OBJECT'] == "host":
        return CHOOSE_HOST
    elif ud['OBJECT'] == "HG":
        return CHOOSE_HOSTGROUP
    elif ud['OBJECT'] == "item":
        return CHOOSE_ITEM
    elif ud['OBJECT'] == "trigger":
        return CHOOSE_TRIGGER
    elif ud['OBJECT'] == "problem":
        return CHOOSE_PROBLEM
    elif ud['OBJECT'] == "service":
        return CHOOSE_SERVICE
    elif ud['OBJECT'] == "sla":
        return CHOOSE_SLA


def precedent(update, context):
    """Pass at the precedent page"""
    ud = context.user_data
    ud["NUMBER"] = ud["NUMBER"] - 1
    navigation_elements(update, context)
    if ud['OBJECT'] == "host":
        return CHOOSE_HOST
    elif ud['OBJECT'] == "HG":
        return CHOOSE_HOSTGROUP
    elif ud['OBJECT'] == "item":
        return CHOOSE_ITEM
    elif ud['OBJECT'] == "trigger":
        return CHOOSE_TRIGGER
    elif ud['OBJECT'] == "problem":
        return CHOOSE_PROBLEM
    elif ud['OBJECT'] == "service":
        return CHOOSE_SERVICE
    elif ud['OBJECT'] == "sla":
        return CHOOSE_SLA


def get_name_host(update, context):
    """Ask people to enter host name"""
    update.callback_query.edit_message_text(
        text=_("Okay, give me the name of the host")
    )
    context.user_data[START_OVER] = True
    return NAME_HOST


def get_tag_host(update, context):
    """Ask people to enter tag values"""
    update.callback_query.edit_message_text(
        text=_("Okay, give me the tag of the host (NAME=VALUE)")
    )
    context.user_data[START_OVER] = True
    return TAG_HOST


def list_host_with_name(update, context):
    """Display the list of host which contains the name of the host enter by the user"""
    ud = context.user_data
    ud["NAME_HOST"] = update.message.text
    create_user_data_to_list_element(context, "get_list_hosts_with_name", "host", 0)
    error = navigation_elements(update, context)
    if error :
        context.user_data[START_OVER] = False
        message_update = _("*Error* to list host with name\n\n")
        start(update, context, message_update)
        return END
    return CHOOSE_HOST


def list_host_with_tag(update, context):
    """Display the list of host which contains the tag of the host enter by the user"""
    ud = context.user_data
    ud["TAG_HOST"] = update.message.text
    create_user_data_to_list_element(context, "get_list_hosts_with_tag", "host", 0)
    error = navigation_elements(update, context)
    if error :
        context.user_data[START_OVER] = False
        message_update = _("*Error* to list host with tag\n\n")
        start(update, context, message_update)
        return END
    return CHOOSE_HOST


def list_item(update, context):
    """Display the list of item for the host selected by the user"""
    ud = context.user_data
    create_user_data_to_list_element(context, "get_list_items", "item", 0)
    Cdata = json.loads(ud["HOST_INFO"])
    ud["ID_HOST"] = Cdata["HID"]
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list items\n\n")
        display_information = DisplayInformation(LANG, ud[API_VAR])
        display_information.reply_host(update, context, message_update)
        return DISPLAY_ACTION
    return CHOOSE_ITEM


def list_sla_service(update, context):
    """Display the list of SLA for the service selected by the user"""
    ud = context.user_data
    create_user_data_to_list_element(context, "get_sla_by_service", "sla", 0)
    Cdata = json.loads(ud["SERVICE_INFO"])
    ud["ID_SERVICE"] = Cdata["SID"]
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list SLA\n\n")
        reply_service(update, context, message_update)
        return DISPLAY_ACTION_SERVICE
    return CHOOSE_SLA


def list_hostgroups(update, context):
    """Display all hostgroups"""
    create_user_data_to_list_element(context, "get_list_hostgroups", "HG", 0)
    error = navigation_elements(update, context)
    if error :
        context.user_data[START_OVER] = True
        message_update = _("*Error* to list hostgroups\n\n")
        start(update, context, message_update)
        return END
    return CHOOSE_HOSTGROUP


def list_services(update, context):
    """Display all services"""
    create_user_data_to_list_element(context, "get_list_services", "service", 0)
    error = navigation_elements(update, context)
    if error :
        context.user_data[START_OVER] = True
        message_update = _("*Error* to list services\n\n")
        start(update, context, message_update)
        return END
    return CHOOSE_SERVICE


def concatenate_id(value, filter, filterid):
    eventid = ""
    for val in value[filter]:
        eventid = eventid+";"+val[filterid]
    return eventid


def list_service_parent(update, context):
    """Display all parents services"""
    ud = context.user_data
    Cdata = json.loads(update.callback_query.data)
    try:
        value = ud[API_VAR].get_service_info(Cdata['PARID'])
    except Exception as e:
        message_update = _("*Error* to list parents service\n\n")
        reply_service(update, context, message_update)
        return DISPLAY_ACTION_SERVICE

    ud["PARENT_CHILD_ID"] = concatenate_id(value[0], "parents", "serviceid")
    create_user_data_to_list_element(context, "get_list_services_parent_child", "service", 0)
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list parents service\n\n")
        reply_service(update, context, message_update)
        return DISPLAY_ACTION_SERVICE
    
    return CHOOSE_SERVICE


def list_service_child(update, context):
    """Display all children services"""
    ud = context.user_data
    Cdata = json.loads(update.callback_query.data)
    try:
        value = ud[API_VAR].get_service_info(Cdata["CHILDID"])
    except Exception as e:
        message_update = _("*Error* to list children service\n\n")
        reply_service(update, context, message_update)
        return DISPLAY_ACTION_SERVICE

    ud["PARENT_CHILD_ID"] = concatenate_id(value[0], "children", "serviceid")
    create_user_data_to_list_element(context, "get_list_services_parent_child", "service", 0)
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list children service\n\n")
        reply_service(update, context, message_update)
        return DISPLAY_ACTION_SERVICE
    return CHOOSE_SERVICE


def list_problem_by_service(update, context):
    """Display the list of problem for the service selected by the user"""
    ud = context.user_data
    Cdata = json.loads(update.callback_query.data)

    try:
        value = ud[API_VAR].get_service_info(Cdata["PROID"])
    except Exception as e:
        message_update = _("*Error* to list problems\n\n")
        reply_service(update, context, message_update)
        return DISPLAY_ACTION_SERVICE

    ud["PROBLEM_ID"] = concatenate_id(value[0], "problem_events", "eventid")
    create_user_data_to_list_element(context, "get_list_problems_by_service", "problem", 0)
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list problems\n\n")
        reply_service(update, context, message_update)
        return DISPLAY_ACTION_SERVICE
    return CHOOSE_PROBLEM


def list_trigger_by_host(update, context):
    """Display the list of trigger for the host selected by the user"""
    ud = context.user_data
    create_user_data_to_list_element(context, "get_list_triggers_by_host", "trigger", 0)
    Cdata = json.loads(ud["HOST_INFO"])
    ud["ID_HOST"] = Cdata["HID"]
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list triggers\n\n")
        display_information = DisplayInformation(LANG, ud[API_VAR])
        display_information.reply_host(update, context, message_update)
        return DISPLAY_ACTION
    return CHOOSE_TRIGGER


def list_trigger_by_item(update, context):
    """Display the list of trigger for the item selected by the user"""
    ud = context.user_data
    create_user_data_to_list_element(context, "get_list_triggers_by_item", "trigger", 0)
    Cdata = json.loads(ud["ITEM_INFO"])
    ud["ID_ITEM"] = Cdata["IID"]
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list triggers\n\n")
        display_information = DisplayInformation(LANG, ud[API_VAR])
        display_information.reply_item(update, context, message_update)
        return DISPLAY_ACTION_ITEM
    return CHOOSE_TRIGGER


def select_hostgroups(update, context):
    """Display host belonging to hostgroup"""
    ud = context.user_data
    create_user_data_to_list_element(context, "get_list_hosts_with_hostgroup", "host", 0)
    ud["HOSTGROUP_INFO"] = update.callback_query.data
    Cdata = json.loads(ud["HOSTGROUP_INFO"])
    ud["ID_HOSTGROUP"] = Cdata["HGID"]
    error = navigation_elements(update, context)
    if error :
        context.user_data[START_OVER] = True
        message_update = _("*Error* to select hosts in hostgroup\n\n")
        start(update, context, message_update)
        return END
    logger.info("Request select host in hostgroup executed")
    return CHOOSE_HOST


def list_problem_by_host(update, context):
    """Display the list of problem for the host selected by the user"""
    ud = context.user_data
    create_user_data_to_list_element(context, "get_list_problems_by_host", "problem", 0)
    Cdata = json.loads(ud["HOST_INFO"])
    ud["ID_HOST"] = Cdata["HID"]
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list problems\n\n")
        display_information = DisplayInformation(LANG, ud[API_VAR])
        display_information.reply_host(update, context, message_update)
        return DISPLAY_ACTION
    return CHOOSE_PROBLEM


def list_problem_by_trigger(update, context):
    """Display the list of problem for the trigger selected by the user"""
    ud = context.user_data
    create_user_data_to_list_element(context, "get_list_problems_by_trigger", "problem", 0)
    Cdata = json.loads(ud["TRIGGER_INFO"])
    ud["ID_TRIGGER"] = Cdata["TID"]
    error = navigation_elements(update, context)
    if error:
        message_update = _("*Error* to list problems\n\n")
        display_information = DisplayInformation(LANG, ud[API_VAR])
        display_information.reply_trigger(update, context, message_update)
        return DISPLAY_ACTION_TRIGGER
    return CHOOSE_PROBLEM

def get_host(update, context):
    """Go back to host after last values"""
    ud = context.user_data
    ud["HOST_INFO"] = update.callback_query.data
    ud['OBJECT'] = 'host'
    display_information = DisplayInformation(LANG, ud[API_VAR])
    message, list_host = display_host_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_information.display_action_host(context, list_host)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request get host executed")
    return END


@send_typing_action
def select_host(update, context):
    """Display all informations and button about host selected"""
    ud = context.user_data
    ud["HOST_INFO"] = update.callback_query.data
    ud['OBJECT'] = 'host'
    display_information = DisplayInformation(LANG, ud[API_VAR])
    message, list_host = display_host_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_information.display_action_host(context, list_host)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request select host executed")
    return DISPLAY_ACTION


@send_typing_action
def select_item(update, context):
    """Display all informations and button about item selected"""
    ud = context.user_data
    ud["ITEM_INFO"] = update.callback_query.data
    display_information = DisplayInformation(LANG, ud[API_VAR])
    message, list_item = display_item_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_information.display_action_item(list_item)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request select item executed")
    return DISPLAY_ACTION_ITEM


@send_typing_action
def select_trigger(update, context):
    """Display all informations and button about trigger selected"""
    ud = context.user_data
    ud["TRIGGER_INFO"] = update.callback_query.data
    display_information = DisplayInformation(LANG, ud[API_VAR])
    message, list_trigger = display_trigger_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_information.display_action_trigger(context,list_trigger)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request select trigger executed")
    return DISPLAY_ACTION_TRIGGER


@send_typing_action
def select_problem(update, context):
    """Display all informations and button about problem selected"""
    ud = context.user_data
    ud["PROBLEM_INFO"] = update.callback_query.data
    display_information = DisplayInformation(LANG, ud[API_VAR])
    message,list_problem = display_problem_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_information.display_action_problem(list_problem)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request select problem executed")
    return DISPLAY_ACTION_PROBLEM


@send_typing_action
def select_service(update, context):
    """Display all informations and button about service selected"""
    ud = context.user_data
    ud["SERVICE_INFO"] = update.callback_query.data
    reply_service(update, context, "")
    logger.info("Request select service executed")
    return DISPLAY_ACTION_SERVICE


@send_typing_action
def select_sla(update, context):
    """Display all informations and button about sla selected"""
    ud = context.user_data
    ud["SLA_INFO"] = update.callback_query.data
    ud = context.user_data
    Cdata = json.loads(ud['SERVICE_INFO'])
    serviceID = Cdata['SID']
    Cdata = json.loads(ud['SLA_INFO'])
    slaID = Cdata['SLAID']
    message = get_table_sla_report(LANG, ud[API_VAR], serviceID, slaID)
    display_information = DisplayInformation(LANG, ud[API_VAR])
    cancel_button = display_information.get_cancel_button()
    button_list = list()
    display_information.add_button_in_list(button_list, telegramEmojiDict["level slider"] +_("Back to service"), '{"SID":"' +serviceID + '"}')

    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    update.callback_query.edit_message_text(
        text=f'```{message}```',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )
    logger.info("Request select SLA executed")
    return DISPLAY_ACTION_SLA

@send_typing_action
def enable_host(update, context):
    """Enable host selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    try:
        ud[API_VAR].update_host_status(host_ID, 0)
        message_update = _("Host enabled OK\n")
    except Exception as e:
        logger.error("Error to enable host")
        message_update = _("*Error* to enable host\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    display_information.reply_host(update, context, message_update)
    logger.info("Request enable host executed")

@send_typing_action
def disable_host(update, context):
    """Disable host selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    try:
        ud[API_VAR].update_host_status(host_ID, 1)
        message_update = _("Host disabled OK\n")
    except Exception as e:
        logger.error("Error to disable host")
        message_update = _("*Error* to disable host\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    display_information.reply_host(update, context, message_update)
    logger.info("Request disable host executed")

@send_typing_action
def enable_item(update, context):
    """Enable item selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["ITEM_INFO"])
    item_ID = Cdata["IID"]
    try:
        ud[API_VAR].update_item_status(item_ID, 0)
        message_update = _("Item enabled OK\n")
    except Exception as e:
        logger.error("Error to enable item")
        message_update = _("*Error* to enable item\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    display_information.reply_item(update, context, message_update)
    logger.info("Request enable item executed")

@send_typing_action
def disable_item(update, context):
    """Disable item selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["ITEM_INFO"])
    item_ID = Cdata["IID"]
    try:
        ud[API_VAR].update_item_status(item_ID, 1)
        message_update = _("Item disabled OK\n")
    except Exception as e:
        logger.error("Error to disable item")
        message_update = _("*Error* to disable item\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    display_information.reply_item(update, context, message_update)
    logger.info("Request disable item executed")

@send_typing_action
def enable_trigger(update, context):
    """Enable trigger selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["TRIGGER_INFO"])
    trigger_ID = Cdata["TID"]
    try:
        ud[API_VAR].update_trigger_status(trigger_ID, 0)
        message_update = _("Trigger enabled OK\n")
    except Exception as e:
        logger.error("Error to enable trigger")
        message_update = _("*Error* to enable trigger\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    display_information.reply_trigger(update, context, message_update)
    logger.info("Request enable trigger executed")


@send_typing_action
def disable_trigger(update, context):
    """Disable trigger selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["TRIGGER_INFO"])
    trigger_ID = Cdata["TID"]
    try:
        ud[API_VAR].update_trigger_status(trigger_ID, 1)
        message_update = _("Trigger disabled OK\n")
    except Exception as e:
        logger.error("Error to disable trigger")
        message_update = _("*Error* to disable trigger\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    display_information.reply_trigger(update, context, message_update)
    logger.info("Request disable trigger executed")



@send_typing_action
def acknowledge_problem(update, context):
    """Acknowledge problem selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["PROBLEM_INFO"])
    problem_ID = Cdata["PID"]
    try:
        ud[API_VAR].action_event(problem_ID, 2)
        message_update = _("Problem acknowledged OK\n")
    except Exception as e:
        logger.error("Error to acknowledge problem")
        message_update = _("*Error* to acknowledge problem\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    display_information.reply_problem(update, context, message_update)
    logger.info("Request acknowledge problem executed")


@send_typing_action
def unacknowledge_problem(update, context):
    """Unaknowledge problem selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["PROBLEM_INFO"])
    problem_ID = Cdata["PID"]
    try:
        ud[API_VAR].action_event(problem_ID, 16)
        message_update = _("Problem unacknowledged OK\n")
    except Exception as e:
        logger.error("Error to unacknowledge problem")
        message_update = _("*Error* to unacknowledge problem\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    display_information.reply_problem(update, context, message_update)
    logger.info("Request unacknowledge problem executed")

@send_typing_action
def show_location_host(update, context):
    """Display location of host"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    try:
        information_host = ud[API_VAR].get_host_info(host_ID)
        button_list = list()
        display_information = DisplayInformation(LANG, ud[API_VAR])
        display_information.add_button_in_list(button_list, telegramEmojiDict["laptop"] + _("Back to host"), '{"HID":"' + host_ID + '"}')
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2)
        )
        context.bot.sendLocation(
            chat_id=update.effective_chat.id, latitude=float(information_host[0]['inventory']['location_lat']), longitude=float(information_host[0]['inventory']['location_lon']), reply_markup=reply_markup
        )
        ud['AFTER_BOT_SEND'] = True
    except Exception as e:
        logger.error("Error to get location")
        message_update = _("*Error* to get location\n\n")
        display_information = DisplayInformation(LANG, ud[API_VAR])
        display_information.reply_host(update, context, message_update)
        return END
    logger.info("Request show host location executed")
    return DIPLAY_ACTION_LOCATION


def delete_image_after(list_images):
    for image in list_images:
        if os.path.exists(image):
            os.remove(image)


@send_document_action
def send_pdf(update, context):
    ud = context.user_data
    display_information = DisplayInformation(LANG, ud[API_VAR])
    try:
        if ud['OBJECT'] == "host":
            Cdata = json.loads(ud["HOST_INFO"])
            host_ID = Cdata["HID"]
            report_host = ReportHost(
                api=ud[API_VAR], host_id=host_ID, LANG=LANG)
            file, list_images = report_host.create_report()
            button_list = list()
            display_information.add_button_in_list(button_list, telegramEmojiDict["laptop"] + _("Back to host"), '{"HID":"'+host_ID+'"}')
        elif ud['OBJECT'] == 'service':
            Cdata = json.loads(ud["SERVICE_INFO"])
            service_ID = Cdata["SID"]
            report_service = ReportService(
                api=ud[API_VAR], service_id=service_ID, LANG=LANG)
            file, list_images = report_service.create_report()
            button_list = list()
            display_information.add_button_in_list(button_list, telegramEmojiDict["level slider"] + _("Back to service"), '{"SID":"'+service_ID+'"}')
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2)
        )
        # send the pdf doc
        context.bot.sendDocument(
            chat_id=update.effective_chat.id, document=open(file, 'rb'), reply_markup=reply_markup, timeout=100)
        ud['AFTER_BOT_SEND'] = True
        delete_image_after(list_images=list_images)

    except Exception as e:
        if ud['OBJECT']=='host':
            logger.error("Error to generate host report")
            message_update = _("*Error* to generate host report\n\n")
            display_information = DisplayInformation(LANG, ud[API_VAR])
            display_information.reply_host(update, context, message_update)
            return END
        elif ud['OBJECT'] == 'service':
            logger.error("Error to generate service report")
            message_update = _("*Error* to generate service report\n\n")
            reply_service(update, context, message_update)
            return END_SERVICE
    logger.info("Request send PDF executed")
    return DISPLAY_ACTION_PDF

def reply_service(update, context, message_update):
    ud = context.user_data
    display_information = DisplayInformation(LANG, ud[API_VAR])
    message, list_service = display_service_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_information.display_action_service(context, list_service)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update=update, context=context, message=message_update+message, reply_markup=reply_markup)

def get_service(update, context):
    """Go back to service after last values"""
    ud = context.user_data
    ud["SERVICE_INFO"] = update.callback_query.data
    reply_service(update, context, "")
    logger.info("Request get service executed")
    return END_SERVICE


@send_typing_action
def show_last_value_host(update, context):
    """Display last value of each items"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    ud['NUMBER_VALUES'] = 0
    navigation_last_values(update=update, context=context, host_ID=host_ID)
    logger.info("Request show last value host executed")
    return DIPLAY_ACTION_VALUE


@send_typing_action
def navigation_last_values(update, context, host_ID):
    """Navigate in differents pages of last values"""
    ud = context.user_data
    numberValueDisplay = 15  # Max number of objects by pages
    table_last_values = ud[API_VAR].get_host_info(host_ID)
    elements_list = table_last_values[0]['items']
    numberPages = int(len(elements_list) / numberValueDisplay)
    # Get correct elements depending the selected page
    if ud["NUMBER_VALUES"] < numberPages:
        elements_list = elements_list[
            ud["NUMBER_VALUES"] * numberValueDisplay: (ud["NUMBER_VALUES"] + 1) * numberValueDisplay
        ]
    else:
        elements_list = elements_list[ud["NUMBER_VALUES"]
                                      * numberValueDisplay:]

    display_information = DisplayInformation(LANG, ud[API_VAR])
    # Get elements in button_list
    button_list = list()
    display_information.add_button_in_list(button_list, telegramEmojiDict["laptop"] + _("Back to host"), '{"HID":"' + host_ID + '"}')

    # Create footer elements
    footer_buttons = list()
    if ud["NUMBER_VALUES"] > 0:
        display_information.add_button_in_list(footer_buttons, "<<", str(PRECEDENT_VALUES))
    
    text_button = _("Page %s") % (str(ud["NUMBER_VALUES"] + 1))
    display_information.add_button_in_list(footer_buttons, text_button, str(ud["NUMBER_VALUES"]))
    
    if ud["NUMBER_VALUES"] < numberPages:
        display_information.add_button_in_list(footer_buttons, ">>", str(NEXT_VALUES))

    # Create cancel button
    reply_markup = InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=2,
            footer_buttons=footer_buttons,
        )
    )
    table_last_values_msg = get_table_last_values_host(LANG=LANG,
                                                       element_items=elements_list, host_name=table_last_values[0]['name'])
    update.callback_query.edit_message_text(
        text=f'```{table_last_values_msg}```',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )


def next_values(update, context):
    """Pass at the next page of values"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    ud["NUMBER_VALUES"] = ud["NUMBER_VALUES"] + 1
    navigation_last_values(update, context, host_ID)
    return DIPLAY_ACTION_VALUE


def precedent_values(update, context):
    """Pass at the precedent page of values"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    ud["NUMBER_VALUES"] = ud["NUMBER_VALUES"] - 1
    navigation_last_values(update, context, host_ID)
    return DIPLAY_ACTION_VALUE


def get_message(update, context):
    """Ask message to user"""
    update.callback_query.edit_message_text(
        text=_("Okay, give me the message"))
    return MESSAGE


@send_typing_action
def send_message(update, context):
    """Send message for problem selected by the user"""
    ud = context.user_data
    ud["MESSAGE_INFO"] = update.message.text
    Cdata = json.loads(ud["PROBLEM_INFO"])
    problem_ID = Cdata["PID"]
    try:
        ud[API_VAR].action_event(problem_ID, 4, ud["MESSAGE_INFO"])
        message_update = _("Send message to problem OK\n")
    except Exception as e:
        logger.error("Error to send message")
        message_update = _("*Error* to send message\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    message_object, list_problem = display_problem_characteristics(
        context, LANG, ud[API_VAR])
    button_list, cancel_button = display_information.display_action_problem(list_problem)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    update.message.reply_markdown(
        text=message_update + message_object, reply_markup=reply_markup
    )
    logger.info("Request send message on problem executed")
    return END


def choose_severity(update, context):
    """Display keyboard with differents severity"""
    msg = _("Choose new severity")
    button_list = list()
    button_list.append(
        KeyboardButton(
            telegramEmojiDict["white large square"] + _("Not classified"))
    )
    button_list.append(
        KeyboardButton(telegramEmojiDict["blue square"] + _("Information"))
    )
    button_list.append(
        KeyboardButton(telegramEmojiDict["yellow square"] + _("Warning"))
    )
    button_list.append(
        KeyboardButton(telegramEmojiDict["orange square"] + _("Average"))
    )
    button_list.append(KeyboardButton(
        telegramEmojiDict["brown square"] + _("High")))
    button_list.append(KeyboardButton(
        telegramEmojiDict["red square"] + _("Disaster")))

    reply_kb_markup = ReplyKeyboardMarkup(
        build_menu(button_list, n_cols=2), resize_keyboard=True, one_time_keyboard=True
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=msg, reply_markup=reply_kb_markup
    )
    logger.info("Request choose severity executed")
    return CHANGE_SEVERITY


@send_typing_action
def change_severity(update, context):
    """Change severty on problem"""
    ud = context.user_data
    text = update.message.text
    if telegramEmojiDict["white large square"] + _("Not classified") in text:
        severity = 0
    elif telegramEmojiDict["blue square"] + _("Information") in text:
        severity = 1
    elif telegramEmojiDict["yellow square"] + _("Warning") in text:
        severity = 2
    elif telegramEmojiDict["orange square"] + _("Average") in text:
        severity = 3
    elif telegramEmojiDict["brown square"] + _("High") in text:
        severity = 4
    elif telegramEmojiDict["red square"] + _("Disaster") in text:
        severity = 5
    Cdata = json.loads(ud["PROBLEM_INFO"])
    problem_ID = Cdata["PID"]
    try:
        ud[API_VAR].action_event(problem_ID, 8, severity=severity)
        message_update = _("Severity change to problem OK\n")
    except Exception as e:
        logger.error("Error to change severity")
        message_update = _("*Error* to change severity\n\n")
    display_information = DisplayInformation(LANG, ud[API_VAR])
    message_object, list_problem = display_problem_characteristics(
        context, LANG, ud[API_VAR])
    button_list, cancel_button = display_information.display_action_problem(list_problem)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    update.message.reply_markdown(
        text=message_update + message_object, reply_markup=reply_markup
    )
    logger.info("Request change severity executed")
    return END


@send_photo_action
def display_graph(update, context):
    """Display graph for item"""
    ud = context.user_data
    Cdata = json.loads(ud["ITEM_INFO"])
    CdataH = json.loads(ud["HOST_INFO"])
    host_id = CdataH["HID"]
    item_id = Cdata["IID"]
    try:
        list_item = ud[API_VAR].get_item_info(item_id)
        data = ud[API_VAR].get_list_history_item(
            item_id, list_item[0]['value_type'])
        name_file = get_image_data(data, list_item, LANG)
        display_information = DisplayInformation(LANG, ud[API_VAR])
        button_list = list()
        display_information.add_button_in_list(button_list, telegramEmojiDict["spiral notepad"] + _("Back to item"), '{"IID":"' + item_id + '"}')
        display_information.add_button_in_list(button_list, telegramEmojiDict["laptop"] + _("Back to host"), '{"HID":"' + host_id + '"}')
        reply_markup = InlineKeyboardMarkup(build_menu(
            button_list, n_cols=2))
        context.bot.send_photo(update.effective_chat.id, photo=open(
            name_file, 'rb'), reply_markup=reply_markup)
        ud['AFTER_BOT_SEND'] = True
        delete_image_after(list_images=[name_file])
    except Exception as e:
        logger.error("Error to display graph")
        message_update = _("*Error* to display graph\n\n")
        display_information = DisplayInformation(LANG, ud[API_VAR])
        display_information.reply_item(update, context, message_update)
        return DISPLAY_ACTION_ITEM
    logger.info("Request display graph executed")
    return DISPLAY_ACTION_GRAPH


def start(update, context, message_update=""):
    """start display the start message"""
    context.user_data['AFTER_BOT_SEND'] = False
    button_list = list()
    findServ = False
    bot = context.bot
    # If information of server are in environment variables
    if NAME_SERVER == "" and os.getenv("ZABBIX_URL") != None and os.getenv("ZABBIX_BOT_USERNAME") != None and os.getenv("ZABBIX_BOT_PASSWORD") != None:
        findServ = True
        context.user_data[str(ZABBIX_URL)] = os.getenv("ZABBIX_URL")
        context.user_data[str(ZABBIX_BOT_USERNAME)] = os.getenv("ZABBIX_BOT_USERNAME")
        context.user_data[str(ZABBIX_BOT_PASSWORD)] = os.getenv("ZABBIX_BOT_PASSWORD")
        message = _(
            "Hey, I'm %s !\nI will help you to handle Zabbix problems !\nI'm connected to the server : *%s*"
        ) % (bot.get_me().first_name, os.getenv("ZABBIX_URL"))
    elif NAME_SERVER != "":  # If server already set
        with open("config.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
        for __, doc in data_loaded.items():
            for i in range(len(data_loaded["servers"])):
                if NAME_SERVER == doc[i]["server"]:
                    findServ = True
                    context.user_data[str(ZABBIX_URL)] = doc[i]["url"]
                    context.user_data[str(ZABBIX_BOT_USERNAME)] = doc[i]["username"]
                    context.user_data[str(ZABBIX_BOT_PASSWORD)] = doc[i]["password"]
        message = _(
            "Hey, I'm %s !\nI will help you to handle Zabbix problems !\nI'm connected to the server : *%s*"
        ) % (bot.get_me().first_name, NAME_SERVER)
    else:  # If server not set, get the first on configuration file
        if os.path.exists("config.yaml"):
            with open("config.yaml", "r") as stream:
                data_loaded = yaml.safe_load(stream)
            for __, doc in data_loaded.items():
                findServ = True
                context.user_data[str(ZABBIX_URL)] = doc[0]["url"]
                context.user_data[str(ZABBIX_BOT_USERNAME)] = doc[0]["username"]
                context.user_data[str(ZABBIX_BOT_PASSWORD)] = doc[0]["password"]
            message = _(
                "Hey, I'm %s !\nI will help you to handle Zabbix problems !\nI'm connected to the server : *%s*"
            ) % (bot.get_me().first_name, doc[0]["server"])

    # Create initial message:
    if findServ == True:
        display_information = DisplayInformation(LANG, None)
        display_information.add_button_in_list(button_list, telegramEmojiDict["magnifying glass tilted"]+ telegramEmojiDict["laptop"]+ _("Search host name"), str(HOST_MENU_NAME))
        display_information.add_button_in_list(button_list, telegramEmojiDict["magnifying glass tilted left"]+ telegramEmojiDict["laptop"]+ _("Search host tag"), str(HOST_MENU_TAG))
        display_information.add_button_in_list(button_list, telegramEmojiDict["laptop"]+ telegramEmojiDict["laptop"]+ _("Hostgroups"), str(HOST_GROUP_MENU))
        display_information.add_button_in_list(button_list, telegramEmojiDict["large blue diamond"] +_("All Hosts"), str(ALL_MENU))
        display_information.add_button_in_list(button_list, telegramEmojiDict["level slider"]+ _("Services"), str(SERVICE_MENU))
        footer_buttons = list()
        display_information.add_button_in_list(footer_buttons, telegramEmojiDict["gear"] + _("Settings"), str(SETTING_MENU))
        display_information.add_button_in_list(footer_buttons, telegramEmojiDict["waving hand"] + _("Done"), str(END))
            
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2, footer_buttons=footer_buttons)
        )
        try:
            context.user_data[API_VAR] = API(
                context.user_data[str(ZABBIX_URL)], context.user_data[str(ZABBIX_BOT_USERNAME)],context.user_data[str(ZABBIX_BOT_PASSWORD)]
            )
            message = message + "\n" + \
            display_global_status(context.user_data[API_VAR], LANG)
            message = message + _("\n\nType /help to show all commands\n   Choose an option:")
        except Exception as e:
            message = ("%s - %s") % (e, context.user_data[str(ZABBIX_URL)])
            display_information.add_button_in_list(button_list, telegramEmojiDict["gear"] + _("Settings"), str(SETTING_MENU))
            display_information.add_button_in_list(button_list, telegramEmojiDict["waving hand"] + _("Done"), str(END))
            
            reply_markup = InlineKeyboardMarkup(
                build_menu(button_list, n_cols=2)
            )

    else:
        message = _("The server is incorrect. Please change the name in setting.")
        display_information.add_button_in_list(button_list, telegramEmojiDict["gear"] + _("Settings"), str(SETTING_MENU))
        display_information.add_button_in_list(button_list, telegramEmojiDict["waving hand"] + _("Done"), str(END))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2)
        )

    #Send initial message
    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(
            text=message_update+message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_markdown(text=message_update+message, reply_markup=reply_markup)
    context.user_data[START_OVER] = False
    logger.info("Request start executed")
    return ACTION_START


def list_setting(update, context):
    """Create buttons for actions in menu setting"""
    ud = context.user_data
    display_information = DisplayInformation(LANG, ud[API_VAR])
    button_list = list()
    display_information.add_button_in_list(button_list, telegramEmojiDict["white flag"] + _("Change language"), "language")
    display_information.add_button_in_list(button_list, telegramEmojiDict["electric plug"] + _("Change server"), "server")
    display_information.add_button_in_list(button_list, telegramEmojiDict["construction"] +_("Change level logger"), "mode_logger")
    cancel_button = display_information.get_cancel_button()

    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message = _("Choose what you want to change")
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request list setting executed")
    return CHOOSE_SETTING


def select_lang(update, context):
    """Create buttons for select languages"""
    button_list = list()
    display_information = DisplayInformation(LANG, context.user_data[API_VAR])
    display_information.add_button_in_list(button_list, "🇬🇧 English", "en")
    display_information.add_button_in_list(button_list, "🇫🇷 French", "fr")
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    message = _("Please choose your language")
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request select language executed")
    return CHOOSE_LANG


def choose_lang(update, context):
    """Get the language choose by the user and change the language of the bot"""
    context.user_data["LANG"] = update.callback_query.data
    global LANG, lang_translations, _
    LANG = context.user_data["LANG"]
    lang_translations = gettext.translation(
        "main", localedir="../locales", languages=[LANG]
    )
    lang_translations.install()
    _ = lang_translations.gettext
    context.user_data[START_OVER] = True
    start(update, context)
    logger.info("Request choose language executed")
    return END

def select_mode_logger(update, context):
    """Create buttons for select logger level"""
    display_information = DisplayInformation(LANG, context.user_data[API_VAR])
    button_list = list()
    display_information.add_button_in_list(button_list, telegramEmojiDict["blue circle"] +"DEBUG", "debug")
    display_information.add_button_in_list(button_list, telegramEmojiDict["green circle"] +"INFO", "info")
    display_information.add_button_in_list(button_list, telegramEmojiDict["yellow circle"] +"WARNING", "warning")
    display_information.add_button_in_list(button_list, telegramEmojiDict["orange circle"] +"ERROR", "error")
    display_information.add_button_in_list(button_list, telegramEmojiDict["red circle"] +"CRITICAL", "critical")
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    message = _("Please choose your level logger")
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request select mode logger executed")
    return CHOOSE_MODE_LOGGER

def choose_mode_logger(update, context):
    """Get the mode logger choose by the user and change the logging level"""
    context.user_data["MODE_LOGGER"] = update.callback_query.data
    level = context.user_data["MODE_LOGGER"]
    if level == "info":
        logging.getLogger().setLevel(logging.INFO)
    elif level == "debug":
        logging.getLogger().setLevel(logging.DEBUG)
    elif level == "warning":
        logging.getLogger().setLevel(logging.WARNING)
    elif level == "error":
        logging.getLogger().setLevel(logging.ERROR)
    elif level == "critical":
        logging.getLogger().setLevel(logging.CRITICAL)
    context.user_data[START_OVER] = True
    start(update, context)
    logger.info("Request choose mode logger executed")
    return END


def get_name_server(update, context):
    """Create buttons list for each server in configuration file"""
    ud = context.user_data
    display_information = DisplayInformation(LANG, ud[API_VAR])
    button_list = list()
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
            for __, doc in data_loaded.items():
                for i in range(len(data_loaded["servers"])):
                    display_information.add_button_in_list(button_list, doc[i]["server"], '{"SE":"' + doc[i]["server"] + '"}')
        message = _("Choose one server or cancel")
    else:
        message = _(
            "The file *config.yaml* doesn't exists. Create file or use environment variables."
        )
    cancel_button = display_information.get_cancel_button()
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    logger.info("Request display name server executed")
    return SERVER


def change_server(update, context):
    """Get the server that the user has choose"""
    global NAME_SERVER
    Cdata = json.loads(update.callback_query.data)
    NAME_SERVER = Cdata["SE"]
    context.user_data[START_OVER] = True
    start(update, context)
    logger.info("Request change server executed")
    return STOPPING


def cancel(update, context):
    """Stop the conversation and display the main menu"""
    context.user_data[START_OVER] = True
    start(update, context)
    logger.info("Request cancel executed")
    return STOPPING


def stop(update, context):
    """End Conversation by command."""
    context.user_data.clear()
    update.message.reply_text(_("Okay, bye."))
    logger.info("Request stop executed")
    return END


def stop_nested(update, context):
    """End conversation child and return to start menu"""
    context.user_data[START_OVER] = False
    update.message.reply_text("STOP okay.")
    start(update, context)
    logger.info("Request stop executed")
    return STOPPING


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    context.user_data.clear()
    update.callback_query.edit_message_text(text=_("See you !"))
    logger.info("Request end executed")
    return END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv("BOT_TOKEN"), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler for change severity
    change_severity_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                choose_severity, pattern="^" + str(CHANGE_SEVERITY_MENU) + "$"
            )
        ],
        states={CHANGE_SEVERITY: [MessageHandler(
            Filters.text, change_severity)]},
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={STOPPING: STOPPING, END: DISPLAY_ACTION_PROBLEM},
    )

    # Add conversation handler for send message
    message_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                get_message, pattern="^" + str(MESSAGE_MENU) + "$")
        ],
        states={MESSAGE: [MessageHandler(
            Filters.regex(r"^[^\/]"), send_message)]},
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={STOPPING: STOPPING, END: DISPLAY_ACTION_PROBLEM},
    )

    # Add conversation handler for send last values
    last_value_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                show_last_value_host, pattern="^" + str(LAST_VALUE) + "$"
            ),
        ],
        states={DIPLAY_ACTION_VALUE: [
            CallbackQueryHandler(
                get_host, pattern='^{"HID*'),
            CallbackQueryHandler(
                precedent_values, pattern="^" + str(PRECEDENT_VALUES) + "$"),
            CallbackQueryHandler(
                next_values, pattern="^" + str(NEXT_VALUES) + "$"),
        ]},
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={STOPPING: STOPPING, END: DISPLAY_ACTION},
    )

    # Add conversation handler for send location
    location_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                show_location_host, pattern="^" + str(LOCATION_MENU) + "$"
            ),
        ],
        states={DIPLAY_ACTION_LOCATION: [
            CallbackQueryHandler(
                get_host, pattern='^{"HID*'),
        ]},
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={STOPPING: STOPPING, END: DISPLAY_ACTION},
    )

    # Add conversation handler for send PDF
    pdf_conv_host = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                send_pdf, pattern="^" + str(PDF_MENU) + "$"
            ),
        ],
        states={DISPLAY_ACTION_PDF: [
            CallbackQueryHandler(
                get_host, pattern='^{"HID*'),
            CallbackQueryHandler(
                get_service, pattern='^{"SID*'),
        ]},
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={STOPPING: STOPPING, END: DISPLAY_ACTION,
                       END_SERVICE: DISPLAY_ACTION_SERVICE},
    )

    states_list = {DISPLAY_ACTION: [
        CallbackQueryHandler(
            list_item, pattern="^" + str(ITEM_MENU) + "$"),
        CallbackQueryHandler(
            list_trigger_by_host, pattern="^" + str(TRIGGER_MENU) + "$"
        ),
        CallbackQueryHandler(
            list_problem_by_host, pattern="^" + str(PROBLEM_MENU) + "$"
        ),
        CallbackQueryHandler(
            enable_host, pattern="^" + str(ENABLE_HOST) + "$"),
        CallbackQueryHandler(
            disable_host, pattern="^" + str(DISABLE_HOST) + "$"
        ),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(select_hostgroups, pattern='^{"HGID*'),
        last_value_conv,
        location_conv,
        pdf_conv_host,
    ],
        CHOOSE_HOST: [
        CallbackQueryHandler(select_host, pattern='^{"HID*'),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(
            precedent, pattern="^" + str(PRECEDENT) + "$"),
        CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
    ],
        CHOOSE_ITEM: [
        CallbackQueryHandler(select_item, pattern='^{"IID*'),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(
            precedent, pattern="^" + str(PRECEDENT) + "$"),
        CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
    ],
        DISPLAY_ACTION_ITEM: [
        CallbackQueryHandler(select_host, pattern='^{"HID*'),
        CallbackQueryHandler(
            list_trigger_by_item, pattern="^" + str(TRIGGER_MENU) + "$"
        ),
        CallbackQueryHandler(
            enable_item, pattern="^" + str(ENABLE_ITEM) + "$"),
        CallbackQueryHandler(
            disable_item, pattern="^" + str(DISABLE_ITEM) + "$"
        ),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(
            display_graph, pattern="^" + str(GRAPH_MENU) + "$"),
    ],
        DISPLAY_ACTION_GRAPH: [
        CallbackQueryHandler(
            select_item, pattern='^{"IID*'),
        CallbackQueryHandler(select_host, pattern='^{"HID*'),
    ],
        CHOOSE_TRIGGER: [
        CallbackQueryHandler(select_trigger, pattern='^{"TID*'),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(
            precedent, pattern="^" + str(PRECEDENT) + "$"),
        CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
    ],
        DISPLAY_ACTION_TRIGGER: [
        CallbackQueryHandler(select_host, pattern='^{"HID*'),
        CallbackQueryHandler(select_item, pattern='^{"IID*'),
        CallbackQueryHandler(
            list_problem_by_trigger, pattern="^" +
            str(PROBLEM_MENU) + "$"
        ),
        CallbackQueryHandler(
            enable_trigger, pattern="^" + str(ENABLE_TRIGGER) + "$"
        ),
        CallbackQueryHandler(
            disable_trigger, pattern="^" + str(DISABLE_TRIGGER) + "$"
        ),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
    ],
        CHOOSE_PROBLEM: [
        CallbackQueryHandler(select_problem, pattern='^{"PID*'),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(
            precedent, pattern="^" + str(PRECEDENT) + "$"),
        CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
    ],
        DISPLAY_ACTION_PROBLEM: [
        CallbackQueryHandler(select_host, pattern='^{"HID*'),
        CallbackQueryHandler(select_trigger, pattern='^{"TID*'),
        CallbackQueryHandler(
            unacknowledge_problem, pattern="^" +
            str(UNACKNOWLEDGE) + "$"
        ),
        CallbackQueryHandler(
            acknowledge_problem, pattern="^" + str(ACKNOWLEDGE) + "$"
        ),
        message_conv,
        change_severity_conv,
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
    ]}

    # Add conversation handler for host
    host_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_host, pattern='^{"HID*')],
        states=states_list,
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={
            STOPPING: STOPPING,
        },
    )

    # Add conversation handler for change server
    change_server_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            get_name_server, pattern="^server")],
        states={
            SERVER: [
                CallbackQueryHandler(change_server, pattern='^{"SE*'),
                CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
            ]
        },
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={STOPPING: STOPPING, END: STOPPING},
    )

    # Add conversation handler for all menu
    all_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            list_host, pattern="^" + str(ALL_MENU) + "$")],
        states={
            CHOOSE_HOST: [
                host_conv,
                CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
                CallbackQueryHandler(
                    precedent, pattern="^" + str(PRECEDENT) + "$"),
                CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
            ]
        },
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={END: ACTION_START, STOPPING: ACTION_START},
    )

    # Add conversation handler for search host menu with name
    search_host_name_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                get_name_host, pattern="^" + str(HOST_MENU_NAME) + "$")
        ],
        states={
            NAME_HOST: [MessageHandler(Filters.regex(r"^[^\/]"), list_host_with_name)],
            CHOOSE_HOST: [
                host_conv,
                CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
                CallbackQueryHandler(
                    precedent, pattern="^" + str(PRECEDENT) + "$"),
                CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
            ],
        },
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={END: ACTION_START, STOPPING: ACTION_START},
    )

    # Add conversation handler for search host menu with tag
    search_host_tag_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                get_tag_host, pattern="^" + str(HOST_MENU_TAG) + "$")
        ],
        states={
            TAG_HOST: [
                MessageHandler(
                    Filters.regex(r"^[a-zA-Z0-9\-]+=[a-zA-Z0-9\-]+$"),
                    list_host_with_tag,
                )
            ],
            CHOOSE_HOST: [
                host_conv,
                CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
                CallbackQueryHandler(
                    precedent, pattern="^" + str(PRECEDENT) + "$"),
                CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
            ],
        },
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={END: ACTION_START, STOPPING: ACTION_START},
    )

    # Add conversation handler for host group menu
    host_group_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                list_hostgroups, pattern="^" + str(HOST_GROUP_MENU) + "$")
        ],
        states={
            CHOOSE_HOSTGROUP: [
                CallbackQueryHandler(select_hostgroups, pattern='^{"HGID*'),
                CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
                CallbackQueryHandler(
                    precedent, pattern="^" + str(PRECEDENT) + "$"),
                CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
            ],
            CHOOSE_HOST: [
                host_conv,
                CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
                CallbackQueryHandler(
                    precedent, pattern="^" + str(PRECEDENT) + "$"),
                CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
            ],
        },
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={END: ACTION_START, STOPPING: ACTION_START},
    )

    # Add conversation handler for setting menu
    setting_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            list_setting, pattern="^" + str(SETTING_MENU) + "$")],
        states={
            CHOOSE_SETTING: [
                CallbackQueryHandler(select_lang, pattern="^lang"),
                CallbackQueryHandler(select_mode_logger, pattern="^mode_logger$"),
                change_server_conv,
                CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
            ],
            CHOOSE_LANG: [CallbackQueryHandler(choose_lang)],
            CHOOSE_MODE_LOGGER: [CallbackQueryHandler(choose_mode_logger)]
        },
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={END: ACTION_START, STOPPING: ACTION_START},
    )

    states_list[CHOOSE_SERVICE] = [
        CallbackQueryHandler(select_service, pattern='^{"SID*'),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(
            precedent, pattern="^" + str(PRECEDENT) + "$"),
        CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
    ]
    states_list[DISPLAY_ACTION_SERVICE] = [
        CallbackQueryHandler(list_service_parent, pattern='^{"PARID*'),
        CallbackQueryHandler(list_service_child,
                             pattern='^{"CHILDID*'),
        CallbackQueryHandler(list_problem_by_service,
                             pattern='^{"PROID*'),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(
            list_sla_service, pattern="^" + str(SLA_MENU) + "$"
        ),
        pdf_conv_host,
    ]
    states_list[CHOOSE_SLA] = [
        CallbackQueryHandler(select_sla, pattern='^{"SLAID*'),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
        CallbackQueryHandler(
            precedent, pattern="^" + str(PRECEDENT) + "$"),
        CallbackQueryHandler(next, pattern="^" + str(NEXT) + "$"),
    ]
    states_list[DISPLAY_ACTION_SLA] = [
        CallbackQueryHandler(select_service, pattern='^{"SID*'),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
    ]

    # Add conversation handler for service menu
    service_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                list_services, pattern="^"+str(SERVICE_MENU)+"$")
        ],
        states=states_list,
        fallbacks=[CommandHandler("stop", stop_nested)],
        map_to_parent={END: ACTION_START, STOPPING: ACTION_START},
    )

    # Add conversation handler for Start Menu:
    start_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ACTION_START: [
                search_host_name_conv,
                search_host_tag_conv,
                host_group_conv,
                all_conv,
                service_conv,
                setting_conv,
                CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
            ],
            END:[CallbackQueryHandler(stop)]
        },
        fallbacks=[CommandHandler("stop", stop)],
    )
    command = Command(START_OVER=START_OVER, _=_, LANG=LANG)
    dp.add_handler(CommandHandler("help", command.help_msg))
    dp.add_handler(start_conv)
    dp.add_handler(CommandHandler("global_status", command.global_status))
    dp.add_handler(CommandHandler("problems", command.show_problem))
    dp.add_handler(CommandHandler("maintenances", command.show_maintenance))

    # Log all errors:
    dp.add_error_handler(error)

    # Start DisAtBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    updater.idle()


if __name__ == "__main__":
    logger.info("Zabbix Bot Start.")

    main()
