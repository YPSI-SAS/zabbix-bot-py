import logging
import json
from telegram.ext import *
from telegram import *
from emojiDict import telegramEmojiDict
from action import *
import gettext

logger = logging.getLogger(__name__)

class DisplayInformation:
    """This class contains all methods used to display action and reply for element"""

    def __init__(self, LANG, api) -> None:
        self.LANG = LANG
        lang_translations = gettext.translation(
            "displayInformation", localedir="../locales", languages=[LANG])
        lang_translations.install()
        self._ = lang_translations.gettext
        self.api = api

    def add_button_in_list(self, button_list, text, callback):
        button_list.append(
            InlineKeyboardButton(
                text=text,
                callback_data=callback
            )
        )

    def get_cancel_button(self):
        """Return cancel button in list"""
        cancel_button = list()
        text = telegramEmojiDict["cross mark"] + self._("Cancel")
        self.add_button_in_list(cancel_button, text, "cancel")
        return cancel_button 

    def display_action_host(self, context, list_host):
        """Return buttons list for create host menu"""
        ud = context.user_data
        button_list = list()
        Cdata = json.loads(ud["HOST_INFO"])
        hostID = Cdata["HID"]

        try:
            list_host_problems = self.api.get_host_problem(hostID)
        except Exception as e:
            logger.error("Error in get_host_problem for display action host")
            list_host_problems = []

        for host in list_host:
            # Display enable or not
            if host["status"] == "0":
                text=telegramEmojiDict["prohibited"] + self._("Disable")
                self.add_button_in_list(button_list, text, "disable_host")
            else:
                text=telegramEmojiDict["check mark button"] + self._("Enable")
                self.add_button_in_list(button_list, text, "enable_host")

            # Display items button if it has item
            if len(host["items"]) != 0:
                text=telegramEmojiDict["spiral notepad"] + self._("Items")
                self.add_button_in_list(button_list, text, "item_menu")
                text=telegramEmojiDict["memo"] + self._("Last values")
                self.add_button_in_list(button_list, text, "last_value")
                
            # Display triggers button if it has trigger
            if len(host["triggers"]) != 0:
                text=telegramEmojiDict["vertical traffic light"] + self._("Triggers")
                self.add_button_in_list(button_list, text, "trigger_menu")
                
            # Display groups button if it has group
            if len(host["groups"]) != 0:
                text=telegramEmojiDict["laptop"]+ telegramEmojiDict["laptop"] +self._("Back to group")
                self.add_button_in_list(button_list, text, '{"HGID":"' +host['groups'][0]['groupid']+'"}')
                
            # Display problems button if it has problem
            if len(list_host_problems) != 0:
                text=telegramEmojiDict["police car light"] + self._("Problems")
                self.add_button_in_list(button_list, text, "problem_menu")
            
            if type(host['inventory']) != list and host['inventory']['location_lat'] != "" and host['inventory']['location_lon'] != "":
                text=telegramEmojiDict["world map"] + self._("Location")
                self.add_button_in_list(button_list, text, "location_menu")
                
            text=telegramEmojiDict["page with curl"] +self._("Report PDF")
            self.add_button_in_list(button_list, text, "pdf_menu")
            
        logger.info("Request display action host executed")
        cancel_button = self.get_cancel_button()
        return button_list, cancel_button

    def display_action_item(self, list_item):
        """Return buttons list for create item menu"""
        button_list = list()

        for item in list_item:
            # Display enable or not
            if item["status"] == "0":
                text=telegramEmojiDict["prohibited"] + self._("Disable")
                self.add_button_in_list(button_list, text, "disable_item")
            else:
                text=telegramEmojiDict["check mark button"] + self._("Enable")
                self.add_button_in_list(button_list, text, "enable_item")
                
            # Display graph button if his value type in unsigned or float
            if item["value_type"] == "0" or item["value_type"] == "3":
                text=telegramEmojiDict["chart decreasing"] + self._("Graph")
                self.add_button_in_list(button_list, text, "graph_menu")
                
            # Display triggers button if it has trigger
            if len(item["triggers"]) != 0:
                text=telegramEmojiDict["vertical traffic light"] +self._("Triggers")
                self.add_button_in_list(button_list, text, "trigger_menu")

            # Display host button if it has one
            if len(item["hosts"]) != 0:
                text=telegramEmojiDict["laptop"] + self._("Host")
                self.add_button_in_list(button_list, text, '{"HID":"' +item["hosts"][0]["hostid"] + '"}')
                
        logger.info("Request display action item executed")
        cancel_button = self.get_cancel_button()
        return button_list, cancel_button

    def display_action_trigger(self, context,list_trigger):
        """Return buttons list for create trigger menu"""
        ud = context.user_data
        button_list = list()
        Cdata = json.loads(ud["TRIGGER_INFO"])
        triggerID = Cdata["TID"]

        try:
            list_trigger_problems = self.api.get_list_problems_by_trigger(triggerID)
        except Exception as e:
            logger.error("Error in get_list_problems_by_trigger for display action trigger")
            list_trigger_problems = []

        for trigger in list_trigger:
            # Display enable or not
            if trigger["status"] == "0":
                text=telegramEmojiDict["prohibited"] + self._("Disable")
                self.add_button_in_list(button_list, text, "disable_trigger")
            else:
                text=telegramEmojiDict["check mark button"] + self._("Enable")
                self.add_button_in_list(button_list, text, "enable_trigger")

            # Display items button if it has item
            if len(trigger["items"]) != 0:
                text=telegramEmojiDict["spiral notepad"] + self._("Item")
                self.add_button_in_list(button_list, text, '{"IID":"' +trigger["items"][0]["itemid"] + '"}')

            # Display host button if it has one
            if len(trigger["hosts"]) != 0:
                text=telegramEmojiDict["laptop"] + self._("Host")
                self.add_button_in_list(button_list, text,'{"HID":"' +trigger["hosts"][0]["hostid"] + '"}')
                
            # Display problems button if it has problem
            if len(list_trigger_problems) != 0:
                text=telegramEmojiDict["police car light"] + self._("Problems")
                self.add_button_in_list(button_list, text, "problem_menu")
        logger.info("Request display action trigger executed")
        cancel_button = self.get_cancel_button()
        return button_list, cancel_button

    def display_action_problem(self, list_problem):
        """Return buttons list for create problem menu"""
        button_list = list()
        
        for problem in list_problem:
            # Display trigger buttons if problem is bind to trigger
            if problem["object"] == "0":
                text=telegramEmojiDict["vertical traffic light"] +self._("Trigger")
                self.add_button_in_list(button_list, text, '{"TID":"' + problem["objectid"] + '"}')
                
            # Display host button if it has one
            if len(problem["hosts"]) != 0:
                text=telegramEmojiDict["laptop"] + self._("Host")
                self.add_button_in_list(button_list, text, '{"HID":"' +problem["hosts"][0]["hostid"] + '"}')

            # Display acknowledge or unacknowledge button
            if problem["acknowledged"] == "0":
                text=telegramEmojiDict["check mark button"] +self._("Acknowledge")
                self.add_button_in_list(button_list, text, "acknowledge")
            elif problem["acknowledged"] == "1" and self.api.zabbix_version >=5:
                text=telegramEmojiDict["cross mark"] + self._("Unacknowledge")
                self.add_button_in_list(button_list, text, "unacknowledge")
                
            # Display send messsage button
            text=telegramEmojiDict["speech balloon"] + self._("Send message")
            self.add_button_in_list(button_list, text, "message_menu")
            
            # Display change severity button
            text=telegramEmojiDict["horizontal traffic light"]+ self._("Change severity")
            self.add_button_in_list(button_list, text, "change_severity_menu")
        logger.info("Request display action problem executed")
        cancel_button = self.get_cancel_button()
        return button_list, cancel_button


    def display_action_service(self,context, list_service):
        """Return buttons list for create service menu"""
        ud = context.user_data
        button_list = list()
        Cdata = json.loads(ud["SERVICE_INFO"])
        serviceID = Cdata["SID"]
        try:
            list_sla = self.api.get_sla_by_service(serviceID)
        except Exception as e:
            logger.error("Error in get_sla_by_service for display action service")
            list_sla = []

        for service in list_service:

            # Display parent button if it has one
            if len(service["parents"]) != 0:
                text=telegramEmojiDict["level slider"] +telegramEmojiDict["baby"] +self._("Parents service")
                self.add_button_in_list(button_list, text, '{"PARID":"' +service['serviceid'] + '"}')
               
            # Display children button if it has one
            if len(service["children"]) != 0:
                text=telegramEmojiDict["level slider"] + telegramEmojiDict["older person"] + self._("Children service")
                self.add_button_in_list(button_list, text, '{"CHILDID":"' + service['serviceid'] + '"}')
                
            # Display problem button if it has one
            if len(service["problem_events"]) != 0:
                text=telegramEmojiDict["police car light"] + self._("Problems")
                self.add_button_in_list(button_list, text, '{"PROID":"' + service['serviceid'] + '"}')
                
            # Display sla button
            if len(list_sla) != 0:
                text=telegramEmojiDict["bar chart"] + self._("SLA")
                self.add_button_in_list(button_list, text, "sla_menu")
            
            text=telegramEmojiDict["page with curl"] + self._("Report PDF")
            self.add_button_in_list(button_list, text, "pdf_menu")
        logger.info("Request display action service executed")
        cancel_button = self.get_cancel_button()
        return button_list, cancel_button

    def reply_host(self, update, context, message_update):
        message_object, list_host = display_host_characteristics(context, self.LANG, self.api)
        button_list, cancel_button = self.display_action_host(context, list_host)
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2, cancel_button=cancel_button)
        )
        update.callback_query.edit_message_text(
            text=message_update + message_object,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )

    def reply_item(self, update, context, message_update):
        message_object, list_item = display_item_characteristics(context, self.LANG, self.api)
        button_list, cancel_button = self.display_information.display_action_item(list_item)
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2, cancel_button=cancel_button)
        )
        update.callback_query.edit_message_text(
            text=message_update + message_object,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )

    def reply_trigger(self, update, context, message_update):
        message_object,list_trigger = display_trigger_characteristics(
            context, self.LANG, self.api)
        button_list, cancel_button = self.display_action_trigger(context,list_trigger)
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2, cancel_button=cancel_button)
        )
        update.callback_query.edit_message_text(
            text=message_update + message_object,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )
    def reply_problem(self, update, context, message_update):
        message_object, list_problem = display_problem_characteristics(
            context, self.LANG, self.api)
        button_list, cancel_button = self.display_action_problem(list_problem)
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2, cancel_button=cancel_button)
        )
        update.callback_query.edit_message_text(
            text=message_update + message_object,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )