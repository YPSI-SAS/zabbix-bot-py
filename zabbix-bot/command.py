from telegram.ext import *
from telegram import *
import os
import yaml
from action import get_table_information_problem, display_global_status,get_table_information_maintenance
from request_API import API
import gettext


class Command:
    """This class contains all methods used to create a command in conversation"""

    def __init__(self, START_OVER, _, LANG) -> None:
        self.START_OVER = START_OVER
        self.LANG= LANG
        lang_translations = gettext.translation(
            "command", localedir="../locales", languages=[LANG])
        lang_translations.install()
        self._ = lang_translations.gettext
        self.ZABBIX_BOT_PASSWORD = ""
        self.ZABBIX_BOT_USERNAME = ""
        self.ZABBIX_URL = ""


    def help_msg(self, update, context):
        """Display help message"""
        message = self._(
            "Commands:\n /start - Start a conversation\n /stop - Stop a current action and return to start menu\n /maintenances *nameServer* - Get all maintenance periods\n /problems *nameServer* - Get all problems on Zabbix server\n /global\_status *nameServer* - Get the global information of Zabbix server. You must specify nameServer arguments or environments variables ZABBIX\_BOT\_USERNAME, ZABBIX\_BOT\_PASSWORD and ZABBIX\_URL if you don't pass argument."
        )
        if context.user_data.get(self.START_OVER):
            update.callback_query.edit_message_text(
                text=message, parse_mode=ParseMode.MARKDOWN
            )
        else:
            update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
        self.START_OVER = False

    def search_server(self, context):
        server_find = False
        server_name = ""
        message = ""
        if len(context.args) != 0:
            server_name = context.args[0]
        if server_name == "" and os.getenv("ZABBIX_URL") != None and os.getenv("ZABBIX_BOT_USERNAME") != None and os.getenv("ZABBIX_BOT_PASSWORD") != None:
            server_name = os.getenv("ZABBIX_URL")
            server_find = True
            self.ZABBIX_URL = os.getenv("ZABBIX_URL")
            self.ZABBIX_BOT_USERNAME = os.getenv("ZABBIX_BOT_USERNAME")
            self.ZABBIX_BOT_PASSWORD = os.getenv("ZABBIX_BOT_PASSWORD")
        elif server_name != "":
            with open("config.yaml", "r") as stream:
                data_loaded = yaml.safe_load(stream)
            for __, doc in data_loaded.items():
                for i in range(len(data_loaded["servers"])):
                    if server_name == doc[i]["server"]:
                        server_find = True
                        self.ZABBIX_URL = doc[i]["url"]
                        self.ZABBIX_BOT_USERNAME = doc[i]["username"]
                        self.ZABBIX_BOT_PASSWORD = doc[i]["password"]

        if server_find == False and server_name == "":
            message = self._(
                "Can you set environments variables (ZABBIX\_URL, ZABBIX\_BOT\_USERNAME and ZABBIX\_BOT\_PASSWORD) to use this command with any argument."
            )
        elif server_find == False and server_name != "":
            message = self._("The server *%s* was not found in config.yaml file.") % (
                server_name
            )

        return message, server_name

    def show_problem(self, update, context):
        """Get all problems on Zabbix server"""
        message, server_name = self.search_server(context)
            
        if message =="":
            try:
                api = API(
                    self.ZABBIX_URL, self.ZABBIX_BOT_USERNAME,self.ZABBIX_BOT_PASSWORD
                )
                table = get_table_information_problem(api, self.LANG)
                update.message.reply_text(
                f'```{table}```', parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                message = self._("Incorrect user name or password or account is temporarily blocked for server %s") % (self.ZABBIX_URL)
                update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
        else:
            update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)

    def global_status(self,update, context):
        """Diplay all global informations about Zabbix server"""
        message, server_name = self.search_server(context)

        if message == "":
            try:
                api = API(
                    self.ZABBIX_URL, self.ZABBIX_BOT_USERNAME,self.ZABBIX_BOT_PASSWORD
                )
                message = self._("The server use is *%s*\n") % (server_name)
                message = message + display_global_status(api, self.LANG)
            except Exception as e:
                message = self._("Incorrect user name or password or account is temporarily blocked for server %s") % (self.ZABBIX_URL)
            

        update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
        self.START_OVER = False

    def show_maintenance(self,update, context):
        """Get all maintenances on Zabbix server"""
        message, server_name = self.search_server(context)

        if message =="":
            try:
                api = API(
                    self.ZABBIX_URL, self.ZABBIX_BOT_USERNAME,self.ZABBIX_BOT_PASSWORD
                )
                table = get_table_information_maintenance(api, self.LANG)
                update.message.reply_text(
                    f'```{table}```', parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                message = self._("Incorrect user name or password or account is temporarily blocked for server %s") % (self.ZABBIX_URL)
                update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
        else:
            update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
