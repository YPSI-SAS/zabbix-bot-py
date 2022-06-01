#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import time
from telegram.ext import *
from telegram import *
from action import (
    build_menu,
    display_object_button,
    display_host_characteristics,
    display_item_characteristics,
    display_trigger_characteristics,
    display_problem_characteristics,
    display_global_status,
    get_image_data,
    get_table_information_problem,
    get_table_information_maintenance,
    display_service_characteristics,
    get_table_last_values_host,
    get_table_sla_report,
)
from functools import wraps
import gettext
from emojiDict import telegramEmojiDict
import json
import yaml
import os
from report_service import ReportService
from report_host import ReportHost


from request_API import API

# log Management
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Global variables
START_OVER, ZABBIX_URL, API_VAR, TYPING, ZABBIX_BOT_USERNAME, ZABBIX_BOT_PASSWORD = map(chr, range(6))

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
    "main", localedir="locales", languages=[LANG])
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


def get_cancel_button():
    """Return cancel button in list"""
    cancel_button = list()
    cancel_button.append(
        InlineKeyboardButton(
            text=telegramEmojiDict["cross mark"] + _("Cancel"),
            callback_data=str(CANCEL),
        )
    )
    return cancel_button


def display_message_bot(update, context, message, reply_markup):
    """Display message and keyboard in conversation"""
    if context.user_data['AFTER_GRAPH'] == True:
        context.user_data['AFTER_GRAPH'] = False
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


def help_msg(update, context):
    """Display help message"""
    message = _(
        "Commands:\n /start - Start a conversation\n /stop - Stop a current action and return to start menu\n /maintenances *nameServer* - Get all maintenance periods\n /problems *nameServer* - Get all problems on Zabbix server\n /global\_status *nameServer* - Get the global information of Zabbix server. You must specify nameServer arguments or environments variables ZABBIX\_BOT\_USERNAME, ZABBIX\_BOT\_PASSWORD and ZABBIX\_URL if you don't pass argument."
    )
    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(
            text=message, parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
    context.user_data[START_OVER] = False


def global_status(update, context):
    """Diplay all global informations about Zabbix server"""
    servFind = False
    server_name = ""
    if len(context.args) != 0:
        server_name = context.args[0]
    if server_name == "" and os.getenv("ZABBIX_URL") != None and os.getenv("ZABBIX_BOT_USERNAME") != None and os.getenv("ZABBIX_BOT_PASSWORD") != None:
        server_name = os.getenv("ZABBIX_URL")
        servFind = True
        context.user_data[str(ZABBIX_URL)] = os.getenv("ZABBIX_URL")
        context.user_data[str(ZABBIX_BOT_USERNAME)] = os.getenv("ZABBIX_BOT_USERNAME")
        context.user_data[str(ZABBIX_BOT_PASSWORD)] = os.getenv("ZABBIX_BOT_PASSWORD")
    elif server_name != "":
        with open("config.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
        for __, doc in data_loaded.items():
            for i in range(len(data_loaded["servers"])):
                if server_name == doc[i]["server"]:
                    servFind = True
                    context.user_data[str(ZABBIX_URL)] = doc[i]["url"]
                    context.user_data[str(ZABBIX_BOT_USERNAME)] = doc[i]["username"]
                    context.user_data[str(ZABBIX_BOT_PASSWORD)] = doc[i]["password"]

    if servFind == False and server_name == "":
        message = _(
            "Can you set environments variables (ZABBIX\_URL, ZABBIX\_BOT\_USERNAME and ZABBIX\_BOT\_PASSWORD) to use this command with any argument."
        )
    elif servFind == False and server_name != "":
        message = _("The server *%s* was not found in config.yaml file.") % (
            server_name
        )
    else:
        api = API(
            context.user_data[str(ZABBIX_URL)], context.user_data[str(ZABBIX_BOT_USERNAME)],context.user_data[str(ZABBIX_BOT_PASSWORD)]
        )
        message = _("The server use is *%s*\n") % (server_name)
        message = message + display_global_status(api, LANG)

    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(
            text=message, parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
    context.user_data[START_OVER] = False


def show_problem(update, context):
    """Get all problems on Zabbix server"""
    servFind = False
    server_name = ""
    if len(context.args) != 0:
        server_name = context.args[0]
    if server_name == "" and os.getenv("ZABBIX_URL") != None and os.getenv("ZABBIX_BOT_USERNAME") != None and os.getenv("ZABBIX_BOT_PASSWORD") != None:
        server_name = os.getenv("ZABBIX_URL")
        servFind = True
        context.user_data[str(ZABBIX_URL)] = os.getenv("ZABBIX_URL")
        context.user_data[str(ZABBIX_BOT_USERNAME)] = os.getenv("ZABBIX_BOT_USERNAME")
        context.user_data[str(ZABBIX_BOT_PASSWORD)] = os.getenv("ZABBIX_BOT_PASSWORD")
    elif server_name != "":
        with open("config.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
        for __, doc in data_loaded.items():
            for i in range(len(data_loaded["servers"])):
                if server_name == doc[i]["server"]:
                    servFind = True
                    context.user_data[str(ZABBIX_URL)] = doc[i]["url"]
                    context.user_data[str(ZABBIX_BOT_USERNAME)] = doc[i]["username"]
                    context.user_data[str(ZABBIX_BOT_PASSWORD)] = doc[i]["password"]

    if servFind == False and server_name == "":
        message = _(
            "Can you set environments variables (ZABBIX\_URL, ZABBIX\_BOT\_USERNAME and ZABBIX\_BOT\_PASSWORD) to use this command with any argument."
        )
        update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
    elif servFind == False and servFind != "":
        message = _("The server *%s* was not found in config.yaml file.") % (
            server_name
        )
        update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
    else:
        api = API(
            context.user_data[str(ZABBIX_URL)], context.user_data[str(ZABBIX_BOT_USERNAME)],context.user_data[str(ZABBIX_BOT_PASSWORD)]
        )
        table = get_table_information_problem(api, LANG)
        update.message.reply_text(
            f'```{table}```', parse_mode=ParseMode.MARKDOWN_V2)


def show_maintenance(update, context):
    """Get all maintenances on Zabbix server"""
    servFind = False
    server_name = ""
    if len(context.args) != 0:
        server_name = context.args[0]
    if server_name == "" and os.getenv("ZABBIX_URL") != None and os.getenv("ZABBIX_BOT_USERNAME") != None and os.getenv("ZABBIX_BOT_PASSWORD") != None:
        server_name = os.getenv("ZABBIX_URL")
        servFind = True
        context.user_data[str(ZABBIX_URL)] = os.getenv("ZABBIX_URL")
        context.user_data[str(ZABBIX_BOT_USERNAME)] = os.getenv("ZABBIX_BOT_USERNAME")
        context.user_data[str(ZABBIX_BOT_PASSWORD)] = os.getenv("ZABBIX_BOT_PASSWORD")
    elif server_name != "":
        with open("config.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
        for __, doc in data_loaded.items():
            for i in range(len(data_loaded["servers"])):
                if server_name == doc[i]["server"]:
                    servFind = True
                    context.user_data[str(ZABBIX_URL)] = doc[i]["url"]
                    context.user_data[str(ZABBIX_BOT_USERNAME)] = doc[i]["username"]
                    context.user_data[str(ZABBIX_BOT_PASSWORD)] = doc[i]["password"]

    if servFind == False and server_name == "":
        message = _(
            "Can you set environments variables (ZABBIX\_URL, ZABBIX\_BOT\_USERNAME and ZABBIX\_BOT\_PASSWORD) to use this command with any argument."
        )
        update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
    elif servFind == False and servFind != "":
        message = _("The server *%s* was not found in config.yaml file.") % (
            server_name
        )
        update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
    else:
        api = API(
            context.user_data[str(ZABBIX_URL)], context.user_data[str(ZABBIX_BOT_USERNAME)],context.user_data[str(ZABBIX_BOT_PASSWORD)]
        )
        table = get_table_information_maintenance(api, LANG)
        update.message.reply_text(
            f'```{table}```', parse_mode=ParseMode.MARKDOWN_V2)


@send_typing_action
def navigation_elements(update, context):
    """Navigate in differents pages of elements"""
    ud = context.user_data
    # Get the correct list of objects depending to type request
    if ud["TYPE_REQUEST"] == "all_host":
        elements_list = ud[API_VAR].get_list_hosts()
    elif ud["TYPE_REQUEST"] == "all_host_name":
        elements_list = ud[API_VAR].get_list_hosts_with_name(ud["NAME_HOST"])
    elif ud["TYPE_REQUEST"] == "all_host_tag":
        elements_list = ud[API_VAR].get_list_hosts_with_tag(ud["TAG_HOST"])
    elif ud["TYPE_REQUEST"] == "all_hostgroup":
        elements_list = ud[API_VAR].get_list_hostgroups()
    elif ud["TYPE_REQUEST"] == "all_host_hostgroup":
        elements_list = ud[API_VAR].get_list_hosts_with_hostgroup(
            ud["ID_HOSTGROUP"])
    elif ud["TYPE_REQUEST"] == "all_item":
        elements_list = ud[API_VAR].get_list_items(ud["ID_HOST"])
    elif ud["TYPE_REQUEST"] == "all_trigger_host":
        elements_list = ud[API_VAR].get_list_triggers_by_host(ud["ID_HOST"])
    elif ud["TYPE_REQUEST"] == "all_trigger_item":
        elements_list = ud[API_VAR].get_list_triggers_by_item(ud["ID_ITEM"])
    elif ud["TYPE_REQUEST"] == "all_problem_host":
        elements_list = ud[API_VAR].get_list_problems_by_host(ud["ID_HOST"])
    elif ud["TYPE_REQUEST"] == "all_problem_trigger":
        elements_list = ud[API_VAR].get_list_problems_by_trigger(
            ud["ID_TRIGGER"])
    elif ud["TYPE_REQUEST"] == "all_service":
        elements_list = ud[API_VAR].get_list_services()
    elif ud["TYPE_REQUEST"] == "all_service_parent":
        elements_list = ud[API_VAR].get_list_services_parent_child(
            ud["PARENT_CHILD_ID"])
    elif ud["TYPE_REQUEST"] == "all_problem_service":
        elements_list = ud[API_VAR].get_list_problems_by_service(
            ud["PROBLEM_ID"])
    elif ud["TYPE_REQUEST"] == "all_sla_service":
        elements_list = ud[API_VAR].get_sla_by_service(
            service_id=ud['ID_SERVICE'])
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

    # Create footer elements
    footer_buttons = list()
    if ud["NUMBER"] > 0:
        footer_buttons.append(
            InlineKeyboardButton(text="<<", callback_data=str(PRECEDENT))
        )
    text_button = _("Page %s") % (str(ud["NUMBER"] + 1))
    footer_buttons.append(
        InlineKeyboardButton(text=text_button, callback_data=str(ud["NUMBER"]))
    )
    if ud["NUMBER"] < numberPages:
        footer_buttons.append(InlineKeyboardButton(
            text=">>", callback_data=str(NEXT)))

    # Create cancel button
    cancel_button = get_cancel_button()
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


def list_host(update, context):
    """Display all hosts"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_host"
    ud["OBJECT"] = "host"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
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
    ud["TYPE_REQUEST"] = "all_host_name"
    ud["OBJECT"] = "host"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_HOST


def list_host_with_tag(update, context):
    """Display the list of host which contains the tag of the host enter by the user"""
    ud = context.user_data
    ud["TAG_HOST"] = update.message.text
    ud["TYPE_REQUEST"] = "all_host_tag"
    ud["OBJECT"] = "host"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_HOST


def list_item(update, context):
    """Display the list of item for the host selected by the user"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_item"
    Cdata = json.loads(ud["HOST_INFO"])
    ud["ID_HOST"] = Cdata["HID"]
    ud["OBJECT"] = "item"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_ITEM


def list_sla_service(update, context):
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_sla_service"
    Cdata = json.loads(ud["SERVICE_INFO"])
    ud["ID_SERVICE"] = Cdata["SID"]
    ud["OBJECT"] = "sla"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_SLA


def list_hostgroups(update, context):
    """Display all hostgroups"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_hostgroup"
    ud["OBJECT"] = "HG"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_HOSTGROUP


def list_services(update, context):
    """Display all services"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_service"
    ud["OBJECT"] = "service"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
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
    value = ud[API_VAR].get_service_info(Cdata['PARID'])
    ud["PARENT_CHILD_ID"] = concatenate_id(
        value[0], "parents", "serviceid")
    ud["TYPE_REQUEST"] = "all_service_parent"
    ud["OBJECT"] = "service"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_SERVICE


def list_service_child(update, context):
    """Display all children services"""
    ud = context.user_data
    Cdata = json.loads(update.callback_query.data)
    value = ud[API_VAR].get_service_info(Cdata["CHILDID"])
    ud["PARENT_CHILD_ID"] = concatenate_id(
        value[0], "children", "serviceid")
    ud["TYPE_REQUEST"] = "all_service_parent"
    ud["OBJECT"] = "service"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_SERVICE


def list_problem_by_service(update, context):
    """Display the list of problem for the service selected by the user"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_problem_service"
    Cdata = json.loads(update.callback_query.data)
    value = ud[API_VAR].get_service_info(Cdata["PROID"])
    ud["PROBLEM_ID"] = concatenate_id(
        value[0], "problem_events", "eventid")
    ud["OBJECT"] = "problem"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_PROBLEM


def list_trigger_by_host(update, context):
    """Display the list of trigger for the host selected by the user"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_trigger_host"
    Cdata = json.loads(ud["HOST_INFO"])
    ud["ID_HOST"] = Cdata["HID"]
    ud["OBJECT"] = "trigger"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_TRIGGER


def list_trigger_by_item(update, context):
    """Display the list of trigger for the item selected by the user"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_trigger_item"
    Cdata = json.loads(ud["ITEM_INFO"])
    ud["ID_ITEM"] = Cdata["IID"]
    ud["OBJECT"] = "trigger"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_TRIGGER


def select_hostgroups(update, context):
    """Display host belonging to hostgroup"""
    ud = context.user_data
    ud["HOSTGROUP_INFO"] = update.callback_query.data
    Cdata = json.loads(ud["HOSTGROUP_INFO"])
    ud["ID_HOSTGROUP"] = Cdata["HGID"]
    ud["TYPE_REQUEST"] = "all_host_hostgroup"
    ud["OBJECT"] = "host"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_HOST


def list_problem_by_host(update, context):
    """Display the list of problem for the host selected by the user"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_problem_host"
    Cdata = json.loads(ud["HOST_INFO"])
    ud["ID_HOST"] = Cdata["HID"]
    ud["OBJECT"] = "problem"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_PROBLEM


def list_problem_by_trigger(update, context):
    """Display the list of problem for the trigger selected by the user"""
    ud = context.user_data
    ud["TYPE_REQUEST"] = "all_problem_trigger"
    Cdata = json.loads(ud["TRIGGER_INFO"])
    ud["ID_TRIGGER"] = Cdata["TID"]
    ud["OBJECT"] = "problem"
    ud["NUMBER"] = 0
    navigation_elements(update, context)
    return CHOOSE_PROBLEM


def display_action_host(context):
    """Return buttons list for create host menu"""
    ud = context.user_data
    button_list = list()
    Cdata = json.loads(ud["HOST_INFO"])
    hostID = Cdata["HID"]
    list_host = ud[API_VAR].get_host_info(hostID)
    list_host_problems = ud[API_VAR].get_host_problem(hostID)

    for host in list_host:
        # Display enable or not
        if host["status"] == "0":
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["prohibited"] + _("Disable"),
                    callback_data=str(DISABLE_HOST),
                )
            )
        else:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["check mark button"] + _("Enable"),
                    callback_data=str(ENABLE_HOST),
                )
            )

        # Display items button if it has item
        if len(host["items"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["spiral notepad"] + _("Items"),
                    callback_data=str(ITEM_MENU),
                )
            )
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["memo"] + _("Last values"),
                    callback_data=str(LAST_VALUE),
                )
            )

        # Display triggers button if it has trigger
        if len(host["triggers"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["vertical traffic light"] +
                    _("Triggers"),
                    callback_data=str(TRIGGER_MENU),
                )
            )

        # Display groups button if it has group
        if len(host["groups"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["laptop"]
                    + telegramEmojiDict["laptop"] +
                    _("Back to group"),
                    callback_data='{"HGID":"' +
                    host['groups'][0]['groupid']+'"}',
                )
            )

        # Display problems button if it has problem
        if len(list_host_problems) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["police car light"] + _("Problems"),
                    callback_data=str(PROBLEM_MENU),
                )
            )
        if type(host['inventory']) != list and host['inventory']['location_lat'] != "" and host['inventory']['location_lon'] != "":
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["world map"] + _("Location"),
                    callback_data=str(LOCATION_MENU),
                )
            )

        button_list.append(
            InlineKeyboardButton(
                text=telegramEmojiDict["page with curl"] +
                _("Report PDF"),
                callback_data=str(PDF_MENU),
            )
        )

    cancel_button = get_cancel_button()
    return button_list, cancel_button


def display_action_item(context):
    """Return buttons list for create item menu"""
    ud = context.user_data
    button_list = list()
    Cdata = json.loads(ud["ITEM_INFO"])
    itemID = Cdata["IID"]
    list_item = ud[API_VAR].get_item_info(itemID)

    for item in list_item:
        # Display enable or not
        if item["status"] == "0":
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["prohibited"] + _("Disable"),
                    callback_data=str(DISABLE_ITEM),
                )
            )
        else:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["check mark button"] + _("Enable"),
                    callback_data=str(ENABLE_ITEM),
                )
            )

        # Display graph button if his value type in unsigned or float
        if item["value_type"] == "0" or item["value_type"] == "3":
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["chart decreasing"] + _("Graph"),
                    callback_data=str(GRAPH_MENU),
                )
            )

        # Display triggers button if it has trigger
        if len(item["triggers"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["vertical traffic light"] +
                    _("Triggers"),
                    callback_data=str(TRIGGER_MENU),
                )
            )

        # Display host button if it has one
        if len(item["hosts"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["laptop"] + _("Host"),
                    callback_data='{"HID":"' +
                    item["hosts"][0]["hostid"] + '"}',
                )
            )

    cancel_button = get_cancel_button()
    return button_list, cancel_button


def display_action_trigger(context):
    """Return buttons list for create trigger menu"""
    ud = context.user_data
    button_list = list()
    Cdata = json.loads(ud["TRIGGER_INFO"])
    triggerID = Cdata["TID"]
    list_trigger = ud[API_VAR].get_trigger_info(triggerID)
    list_trigger_problems = ud[API_VAR].get_trigger_problem(triggerID)

    for trigger in list_trigger:
        # Display enable or not
        if trigger["status"] == "0":
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["prohibited"] + _("Disable"),
                    callback_data=str(DISABLE_TRIGGER),
                )
            )
        else:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["check mark button"] + _("Enable"),
                    callback_data=str(ENABLE_TRIGGER),
                )
            )

        # Display items button if it has item
        if len(trigger["items"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["spiral notepad"] + _("Item"),
                    callback_data='{"IID":"' +
                    trigger["items"][0]["itemid"] + '"}',
                )
            )

        # Display host button if it has one
        if len(trigger["hosts"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["laptop"] + _("Host"),
                    callback_data='{"HID":"' +
                    trigger["hosts"][0]["hostid"] + '"}',
                )
            )

        # Display problems button if it has problem
        if len(list_trigger_problems) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["police car light"] + _("Problems"),
                    callback_data=str(PROBLEM_MENU),
                )
            )

    cancel_button = get_cancel_button()
    return button_list, cancel_button


def display_action_problem(context):
    """Return buttons list for create problem menu"""
    ud = context.user_data
    button_list = list()
    Cdata = json.loads(ud["PROBLEM_INFO"])
    problemID = Cdata["PID"]
    list_problem = ud[API_VAR].get_event_info(problemID)
    for problem in list_problem:
        # Display trigger buttons if problem is bind to trigger
        if problem["object"] == "0":
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["vertical traffic light"] +
                    _("Trigger"),
                    callback_data='{"TID":"' + problem["objectid"] + '"}',
                )
            )

        # Display host button if it has one
        if len(problem["hosts"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["laptop"] + _("Host"),
                    callback_data='{"HID":"' +
                    problem["hosts"][0]["hostid"] + '"}',
                )
            )

        # Display acknowledge or unacknowledge button
        if problem["acknowledged"] == "0":
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["check mark button"] +
                    _("Acknowledge"),
                    callback_data=str(ACKNOWLEDGE),
                )
            )
        else:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["cross mark"] + _("Unacknowledge"),
                    callback_data=str(UNACKNOWLEDGE),
                )
            )

        # Display send messsage button
        button_list.append(
            InlineKeyboardButton(
                text=telegramEmojiDict["speech balloon"] + _("Send message"),
                callback_data=str(MESSAGE_MENU),
            )
        )

        # Display change severity button
        button_list.append(
            InlineKeyboardButton(
                text=telegramEmojiDict["horizontal traffic light"]
                + _("Change severity"),
                callback_data=str(CHANGE_SEVERITY_MENU),
            )
        )

    cancel_button = get_cancel_button()
    return button_list, cancel_button


def display_action_service(context):
    """Return buttons list for create service menu"""
    ud = context.user_data
    button_list = list()
    Cdata = json.loads(ud["SERVICE_INFO"])
    serviceID = Cdata["SID"]
    list_service = ud[API_VAR].get_service_info(serviceID)
    list_sla = ud[API_VAR].get_sla_by_service(serviceID)
    for service in list_service:

        # Display parent button if it has one
        if len(service["parents"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["level slider"] +
                    telegramEmojiDict["baby"] +
                    _("Parents service"),
                    callback_data='{"PARID":"' +
                    service['serviceid'] + '"}',
                )
            )

        # Display children button if it has one
        if len(service["children"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["level slider"] +
                    telegramEmojiDict["older person"] +
                    _("Children service"),
                    callback_data='{"CHILDID":"' +
                    service['serviceid'] + '"}',
                )
            )

        # Display problem button if it has one
        if len(service["problem_events"]) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["police car light"] +
                    _("Problems"),
                    callback_data='{"PROID":"' +
                    service['serviceid'] + '"}',
                )
            )

        # Display sla button
        if len(list_sla) != 0:
            button_list.append(
                InlineKeyboardButton(
                    text=telegramEmojiDict["bar chart"] +
                    _("SLA"),
                    callback_data=str(SLA_MENU),
                )
            )

        button_list.append(
            InlineKeyboardButton(
                text=telegramEmojiDict["page with curl"] +
                _("Report PDF"),
                callback_data=str(PDF_MENU),
            )
        )

    cancel_button = get_cancel_button()
    return button_list, cancel_button


def get_host(update, context):
    """Go back to host after last values"""
    ud = context.user_data
    ud["HOST_INFO"] = update.callback_query.data
    ud['OBJECT'] = 'host'
    message = display_host_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_action_host(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    return END


@send_typing_action
def select_host(update, context):
    """Display all informations and button about host selected"""
    ud = context.user_data
    ud["HOST_INFO"] = update.callback_query.data
    ud['OBJECT'] = 'host'
    message = display_host_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_action_host(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    return DISPLAY_ACTION


@send_typing_action
def select_item(update, context):
    """Display all informations and button about item selected"""
    ud = context.user_data
    ud["ITEM_INFO"] = update.callback_query.data
    message = display_item_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_action_item(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)

    return DISPLAY_ACTION_ITEM


@send_typing_action
def select_trigger(update, context):
    """Display all informations and button about trigger selected"""
    ud = context.user_data
    ud["TRIGGER_INFO"] = update.callback_query.data
    message = display_trigger_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_action_trigger(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    return DISPLAY_ACTION_TRIGGER


@send_typing_action
def select_problem(update, context):
    """Display all informations and button about problem selected"""
    ud = context.user_data
    ud["PROBLEM_INFO"] = update.callback_query.data
    message = display_problem_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_action_problem(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    return DISPLAY_ACTION_PROBLEM


@send_typing_action
def select_service(update, context):
    """Display all informations and button about service selected"""
    ud = context.user_data
    ud["SERVICE_INFO"] = update.callback_query.data
    message = display_service_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_action_service(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
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
    cancel_button = get_cancel_button()
    button_list = list()
    button_list.append(
        InlineKeyboardButton(
            text=telegramEmojiDict["level slider"] +
            _("Back to service"),
            callback_data='{"SID":"' +
            serviceID + '"}',
        )
    )
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    update.callback_query.edit_message_text(
        text=f'```{message}```',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )
    return DISPLAY_ACTION_SLA


@send_typing_action
def enable_host(update, context):
    """Enable host selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    ud[API_VAR].update_host_status(host_ID, 0)
    message_update = _("Host enabled OK\n")
    button_list, cancel_button = display_action_host(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_host_characteristics(context, LANG, ud[API_VAR])
    update.callback_query.edit_message_text(
        text=message_update + message_object,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )


@send_typing_action
def disable_host(update, context):
    """Disable host selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    ud[API_VAR].update_host_status(host_ID, 1)
    message_update = _("Host disabled OK\n")
    button_list, cancel_button = display_action_host(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_host_characteristics(context, LANG, ud[API_VAR])
    update.callback_query.edit_message_text(
        text=message_update + message_object,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )


@send_typing_action
def enable_item(update, context):
    """Enable item selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["ITEM_INFO"])
    item_ID = Cdata["IID"]
    ud[API_VAR].update_item_status(item_ID, 0)
    message_update = _("Item enabled OK\n")
    button_list, cancel_button = display_action_item(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_item_characteristics(context, LANG, ud[API_VAR])
    update.callback_query.edit_message_text(
        text=message_update + message_object,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )


@send_typing_action
def disable_item(update, context):
    """Disable item selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["ITEM_INFO"])
    item_ID = Cdata["IID"]
    ud[API_VAR].update_item_status(item_ID, 1)
    message_update = _("Item disabled OK\n")
    button_list, cancel_button = display_action_item(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_item_characteristics(context, LANG, ud[API_VAR])
    update.callback_query.edit_message_text(
        text=message_update + message_object,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )


@send_typing_action
def enable_trigger(update, context):
    """Enable trigger selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["TRIGGER_INFO"])
    trigger_ID = Cdata["TID"]
    ud[API_VAR].update_trigger_status(trigger_ID, 0)
    message_update = _("Trigger enabled OK\n")
    button_list, cancel_button = display_action_trigger(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_trigger_characteristics(
        context, LANG, ud[API_VAR])
    update.callback_query.edit_message_text(
        text=message_update + message_object,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )


@send_typing_action
def disable_trigger(update, context):
    """Disable trigger selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["TRIGGER_INFO"])
    trigger_ID = Cdata["TID"]
    ud[API_VAR].update_trigger_status(trigger_ID, 1)
    message_update = _("Trigger disabled OK\n")
    button_list, cancel_button = display_action_trigger(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_trigger_characteristics(
        context, LANG, ud[API_VAR])
    update.callback_query.edit_message_text(
        text=message_update + message_object,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )


@send_typing_action
def acknowledge_problem(update, context):
    """Acknowledge problem selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["PROBLEM_INFO"])
    problem_ID = Cdata["PID"]
    ud[API_VAR].action_event(problem_ID, 2)
    message_update = _("Problem acknowledged OK\n")
    button_list, cancel_button = display_action_problem(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_problem_characteristics(
        context, LANG, ud[API_VAR])
    update.callback_query.edit_message_text(
        text=message_update + message_object,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )


@send_typing_action
def unacknowledge_problem(update, context):
    """Unaknowledge problem selected by user"""
    ud = context.user_data
    Cdata = json.loads(ud["PROBLEM_INFO"])
    problem_ID = Cdata["PID"]
    ud[API_VAR].action_event(problem_ID, 16)
    message_update = _("Problem unacknowledged OK\n")
    button_list, cancel_button = display_action_problem(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_problem_characteristics(
        context, LANG, ud[API_VAR])
    update.callback_query.edit_message_text(
        text=message_update + message_object,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )


@send_typing_action
def show_location_host(update, context):
    """Display location of host"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    information_host = ud[API_VAR].get_host_info(host_ID)
    button_list = list()
    button_list.append(
        InlineKeyboardButton(
            text=telegramEmojiDict["laptop"] +
            _("Back to host"),
            callback_data='{"HID":"' +
            host_ID + '"}',
        )
    )
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2)
    )
    context.bot.sendLocation(
        chat_id=update.effective_chat.id, latitude=float(information_host[0]['inventory']['location_lat']), longitude=float(information_host[0]['inventory']['location_lon']), reply_markup=reply_markup
    )
    ud['AFTER_GRAPH'] = True
    return DIPLAY_ACTION_LOCATION


def delete_image_after(list_images):
    for image in list_images:
        if os.path.exists(image):
            os.remove(image)


@send_document_action
def send_pdf(update, context):
    ud = context.user_data
    if ud['OBJECT'] == "host":
        Cdata = json.loads(ud["HOST_INFO"])
        host_ID = Cdata["HID"]
        report_host = ReportHost(
            api=ud[API_VAR], host_id=host_ID, LANG=LANG)
        file, list_images = report_host.create_report()
        button_list = list()
        button_list.append(
            InlineKeyboardButton(
                text=telegramEmojiDict["laptop"] +
                _("Back to host"),
                callback_data='{"HID":"'+host_ID+'"}',
            )
        )
    elif ud['OBJECT'] == 'service':
        Cdata = json.loads(ud["SERVICE_INFO"])
        service_ID = Cdata["SID"]
        report_service = ReportService(
            api=ud[API_VAR], service_id=service_ID, LANG=LANG)
        file, list_images = report_service.create_report()
        button_list = list()
        button_list.append(
            InlineKeyboardButton(
                text=telegramEmojiDict["level slider"] +
                _("Back to service"),
                callback_data='{"SID":"'+service_ID+'"}',
            )
        )
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2)
    )
    # send the pdf doc
    context.bot.sendDocument(
        chat_id=update.effective_chat.id, document=open(file, 'rb'), reply_markup=reply_markup, timeout=100)
    ud['AFTER_GRAPH'] = True
    delete_image_after(list_images=list_images)
    return DISPLAY_ACTION_PDF


def get_service(update, context):
    """Go back to service after last values"""
    ud = context.user_data
    ud["SERVICE_INFO"] = update.callback_query.data
    message = display_service_characteristics(context, LANG, ud[API_VAR])
    button_list, cancel_button = display_action_service(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    return END_SERVICE


@send_typing_action
def show_last_value_host(update, context):
    """Display last value of each items"""
    ud = context.user_data
    Cdata = json.loads(ud["HOST_INFO"])
    host_ID = Cdata["HID"]
    ud['NUMBER_VALUES'] = 0
    navigation_last_values(update=update, context=context, host_ID=host_ID)
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

    # Get elements in button_list
    button_list = list()
    button_list.append(
        InlineKeyboardButton(
            text=telegramEmojiDict["laptop"] +
            _("Back to host"),
            callback_data='{"HID":"' +
            host_ID + '"}',
        )
    )

    # Create footer elements
    footer_buttons = list()
    if ud["NUMBER_VALUES"] > 0:
        footer_buttons.append(
            InlineKeyboardButton(
                text="<<", callback_data=str(PRECEDENT_VALUES))
        )
    text_button = _("Page %s") % (str(ud["NUMBER_VALUES"] + 1))
    footer_buttons.append(
        InlineKeyboardButton(
            text=text_button, callback_data=str(ud["NUMBER_VALUES"]))
    )
    if ud["NUMBER_VALUES"] < numberPages:
        footer_buttons.append(InlineKeyboardButton(
            text=">>", callback_data=str(NEXT_VALUES)))

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
    ud[API_VAR].action_event(problem_ID, 4, ud["MESSAGE_INFO"])
    message_update = _("Send message to problem OK\n")
    button_list, cancel_button = display_action_problem(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_problem_characteristics(
        context, LANG, ud[API_VAR])
    update.message.reply_markdown(
        text=message_update + message_object, reply_markup=reply_markup
    )
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
    ud[API_VAR].action_event(problem_ID, 8, severity=severity)
    message_update = _("Severity change to problem OK\n")
    button_list, cancel_button = display_action_problem(context)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    message_object = display_problem_characteristics(
        context, LANG, ud[API_VAR])
    update.message.reply_markdown(
        text=message_update + message_object, reply_markup=reply_markup
    )
    return END


@send_photo_action
def display_graph(update, context):
    """Display graph for item"""
    ud = context.user_data
    Cdata = json.loads(ud["ITEM_INFO"])
    CdataH = json.loads(ud["HOST_INFO"])
    host_id = CdataH["HID"]
    item_id = Cdata["IID"]
    list_item = ud[API_VAR].get_item_info(item_id)
    data = ud[API_VAR].get_list_history_item(
        item_id, list_item[0]['value_type'])
    name_file = get_image_data(data, list_item, LANG)
    button_list = list()
    button_list.append(
        InlineKeyboardButton(
            text=telegramEmojiDict["spiral notepad"] + _("Back to item"),
            callback_data='{"IID":"' + item_id + '"}',
        )
    )
    button_list.append(
        InlineKeyboardButton(
            text=telegramEmojiDict["laptop"] + _("Back to host"),
            callback_data='{"HID":"' + host_id + '"}',
        )
    )
    reply_markup = InlineKeyboardMarkup(build_menu(
        button_list, n_cols=2))
    context.bot.send_photo(update.effective_chat.id, photo=open(
        name_file, 'rb'), reply_markup=reply_markup)
    ud['AFTER_GRAPH'] = True
    delete_image_after(list_images=[name_file])
    return DISPLAY_ACTION_GRAPH


def start(update, context):
    """start display the start message"""
    context.user_data['AFTER_GRAPH'] = False
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
        buttons = [
            [
                InlineKeyboardButton(
                    text=telegramEmojiDict["magnifying glass tilted"]
                    + telegramEmojiDict["laptop"]
                    + _("Search host name"),
                    callback_data=str(HOST_MENU_NAME),
                ),
                InlineKeyboardButton(
                    text=telegramEmojiDict["magnifying glass tilted left"]
                    + telegramEmojiDict["laptop"]
                    + _("Search host tag"),
                    callback_data=str(HOST_MENU_TAG),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=telegramEmojiDict["laptop"]
                    + telegramEmojiDict["laptop"]
                    + _("Hostgroups"),
                    callback_data=str(HOST_GROUP_MENU),
                ),
                InlineKeyboardButton(
                    text=telegramEmojiDict["large blue diamond"] +
                    _("All Hosts"),
                    callback_data=str(ALL_MENU),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=telegramEmojiDict["level slider"]
                    + _("Services"),
                    callback_data=str(SERVICE_MENU),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=telegramEmojiDict["gear"] + _("Settings"),
                    callback_data=str(SETTING_MENU),
                ),
                InlineKeyboardButton(
                    text=telegramEmojiDict["waving hand"] + _("Done"),
                    callback_data=str(END),
                ),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.user_data[API_VAR] = API(
            context.user_data[str(ZABBIX_URL)], context.user_data[str(ZABBIX_BOT_USERNAME)],context.user_data[str(ZABBIX_BOT_PASSWORD)]
        )
        message = message + "\n" + \
            display_global_status(context.user_data[API_VAR], LANG)
        message = message + \
            _("\n\nType /help to show all commands\n   Choose an option:")

    else:
        message = _(
            "The server is incorrect. Please change the name in setting.")
        buttons = [
            [
                InlineKeyboardButton(
                    text=telegramEmojiDict["gear"] + _("Settings"),
                    callback_data=str(SETTING_MENU),
                )
            ],
            [
                InlineKeyboardButton(
                    text=telegramEmojiDict["waving hand"] + _("Done"),
                    callback_data=str(END),
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(
            text=message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_markdown(text=message, reply_markup=reply_markup)
    context.user_data[START_OVER] = False
    return ACTION_START


def list_setting(update, context):
    """Create buttons for actions in menu setting"""
    button_list = list()
    button_list.append(
        InlineKeyboardButton(
            text=telegramEmojiDict["white flag"] + _("Change language"),
            callback_data="language",
        )
    )
    button_list.append(
        InlineKeyboardButton(
            text=telegramEmojiDict["electric plug"] + _("Change server"),
            callback_data="server",
        )
    )
    cancel_button = get_cancel_button()
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=3, cancel_button=cancel_button)
    )
    message = _("Choose what you want to change")
    display_message_bot(update, context, message, reply_markup)
    return CHOOSE_SETTING


def select_lang(update, context):
    """Create buttons for select languages"""
    button_list = list()
    button_list.append(InlineKeyboardButton(
        text="🇬🇧 English", callback_data="en"))
    button_list.append(InlineKeyboardButton(
        text="🇫🇷 French", callback_data="fr"))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    message = _("Please choose your language")
    display_message_bot(update, context, message, reply_markup)
    return CHOOSE_LANG


def choose_lang(update, context):
    """Get the language choose by the user and change the language of the bot"""
    context.user_data["LANG"] = update.callback_query.data
    global LANG, lang_translations, _
    LANG = context.user_data["LANG"]
    lang_translations = gettext.translation(
        "main", localedir="locales", languages=[LANG]
    )
    lang_translations.install()
    _ = lang_translations.gettext
    context.user_data[START_OVER] = True
    start(update, context)
    return END


def get_name_server(update, context):
    """Create buttons list for each server in configuration file"""
    button_list = list()
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
            for __, doc in data_loaded.items():
                for i in range(len(data_loaded["servers"])):
                    button_list.append(
                        InlineKeyboardButton(
                            text=doc[i]["server"],
                            callback_data='{"SE":"' + doc[i]["server"] + '"}',
                        )
                    )
        message = _("Choose one server or cancel")
    else:
        message = _(
            "The file *config.yaml* doesn't exists. Create file or use environment variables."
        )
    cancel_button = get_cancel_button()
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2, cancel_button=cancel_button)
    )
    display_message_bot(update, context, message, reply_markup)
    return SERVER


def change_server(update, context):
    """Get the server that the user has choose"""
    global NAME_SERVER
    Cdata = json.loads(update.callback_query.data)
    NAME_SERVER = Cdata["SE"]
    context.user_data[START_OVER] = True
    start(update, context)
    return STOPPING


def cancel(update, context):
    """Stop the conversation and display the main menu"""
    context.user_data[START_OVER] = True
    start(update, context)
    return STOPPING


def stop(update, context):
    """End Conversation by command."""
    context.user_data.clear()
    update.message.reply_text(_("Okay, bye."))
    return END


def stop_nested(update, context):
    """End conversation child and return to start menu"""
    context.user_data[START_OVER] = False
    update.message.reply_text("STOP okay.")
    start(update, context)
    return STOPPING


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    context.user_data.clear()
    update.callback_query.edit_message_text(text=_("See you !"))
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
                change_server_conv,
                CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$"),
            ],
            CHOOSE_LANG: [CallbackQueryHandler(choose_lang)],
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
            ]
        },
        fallbacks=[CommandHandler("stop", stop)],
    )

    dp.add_handler(CommandHandler("help", help_msg))
    dp.add_handler(start_conv)
    dp.add_handler(CommandHandler("global_status", global_status))
    dp.add_handler(CommandHandler("problems", show_problem))
    dp.add_handler(CommandHandler("maintenances", show_maintenance))

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
