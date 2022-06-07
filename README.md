# Zabbix-Bot-Py

Zabbix Bot is a Telegram bot compatible Zabbix version 4, 5 and 6.

## Environment variables
The variable BOT_TOKEN is obligatory for know the bot.
The variables ZABBIX_URL, ZABBIX_BOT_USERNAME, ZABBIX_BOT_PASSWORD are obligatory if you won't use the config file and manage only one server

## Config file
The config file is essential for manage many server. His name is config.yaml and it must be located in zabbix-bot directory.
<br/>For declare a server use the configuration below by replacing capitalized words

* `NAMESERVER` it's the name of the server that you will use in the flag --server. <span style="color: #FF0000"> WARNING </span> : The name of the server must be unique
* `URL` it's the url at use for access to your zabbix server. Its format is **https://monserveurzabbix.fr** and you replace **monserveurzabbix.fr** by the server. <span style="color: #FF0000"> WARNING </span> : remember to put **http** if your url is not a secure url
* `USERNAME` it's the username that you use to connect
* `PASSWORD` it's the password that you use to connect

```yaml
servers:
   - server: "NAMESERVER"
     url: "URL" 
     username: "USERNAME"
     password: "PASSWORD"
   - server: "NAMESERVER2"
     url: "URL" 
     username: "USERNAME"
     password: "PASSWORD"
```

## DockerFile
To use a Zabbix Bot in container use a Dockerfile. Let's start by build an image :
```sh
docker build -t zabbix-bot .
```

Next, you can create container, but you must specify BOT_TOKEN in environment variable. Moreover, if your image doesn't contain à config.yaml file, you must pass ZABBIX_URL and ZABBIX_TOKEN environment variables. <span style="color: #FF0000"> WARNING </span> : your container must be access to your zabbix server. 
With config.yaml file in image:
```sh
docker run --env BOT_TOKEN= zabbix-bot
```

Without config.yaml file in image:
```sh
docker run --env BOT_TOKEN= --env ZABBIX_URL= --env ZABBIX_BOT_USERNAME= --env ZABBIX_BOT_PASSWORD= zabbix-bot
```

## Make translation
### Update existing translations
For update existing translations, you must be in main directory zabbix-bot-py :
```sh
xgettext -d main -o locales/main.pot zabbix-bot/main.py
msgmerge --update locales/en/LC_MESSAGES/main.po locales/main.pot
msgmerge --update locales/fr/LC_MESSAGES/main.po locales/main.pot

xgettext -d command -o locales/command.pot zabbix-bot/command.py
msgmerge --update locales/en/LC_MESSAGES/command.po locales/command.pot
msgmerge --update locales/fr/LC_MESSAGES/command.po locales/command.pot

xgettext -d action -o locales/action.pot zabbix-bot/action.py
msgmerge --update locales/en/LC_MESSAGES/action.po locales/action.pot
msgmerge --update locales/fr/LC_MESSAGES/action.po locales/action.pot

xgettext -d report -o locales/report.pot zabbix-bot/reports/report*
msgmerge --update locales/en/LC_MESSAGES/report.po locales/report.pot
msgmerge --update locales/fr/LC_MESSAGES/report.po locales/report.pot

xgettext -d displayInformation -o locales/displayInformation.pot zabbix-bot/display_information.py
msgmerge --update locales/en/LC_MESSAGES/displayInformation.po locales/displayInformation.pot
msgmerge --update locales/fr/LC_MESSAGES/displayInformation.po locales/displayInformation.pot
```

After, add new translations in each po files. For this, you can use Poedit which generate mo files automatically when you save your new translations.
<br/>Or edit each po files manually and run these commands to generate mo files:
```sh
msgfmt -o locales/fr/LC_MESSAGES/main.mo locales/fr/LC_MESSAGES/main
msgfmt -o locales/en/LC_MESSAGES/main.mo locales/en/LC_MESSAGES/main

msgfmt -o locales/fr/LC_MESSAGES/command.mo locales/fr/LC_MESSAGES/command
msgfmt -o locales/en/LC_MESSAGES/command.mo locales/en/LC_MESSAGES/command

msgfmt -o locales/fr/LC_MESSAGES/action.mo locales/fr/LC_MESSAGES/action
msgfmt -o locales/en/LC_MESSAGES/action.mo locales/en/LC_MESSAGES/action

msgfmt -o locales/fr/LC_MESSAGES/report.mo locales/fr/LC_MESSAGES/report
msgfmt -o locales/en/LC_MESSAGES/report.mo locales/en/LC_MESSAGES/report

msgfmt -o locales/fr/LC_MESSAGES/displayInformation.mo locales/fr/LC_MESSAGES/displayInformation
msgfmt -o locales/en/LC_MESSAGES/displayInformation.mo locales/en/LC_MESSAGES/displayInformation
```
### Add new translations
For my example, I choose to make spanish translation (es). To make for other language change es by acronyme of the language. 
<br/>Start by creating a new directory in locales
```sh
mkdir -p locales/es/LC_MESSAGES
```

Copy all pot files and change exension:
```sh
cp locales/main.pot locales/es/LC_MESSAGES/main.po
cp locales/command.pot locales/es/LC_MESSAGES/command.po
cp locales/action.pot locales/es/LC_MESSAGES/action.po
cp locales/report.pot locales/es/LC_MESSAGES/report.po
cp locales/displayInformation.pot locales/es/LC_MESSAGES/displayInformation.po
```

After, add new translations in each po files. For this, you can use Poedit which generate mo files automatically when you save your new translations.
<br/>Or edit each po files manually and run these commands to generate mo files:
```sh
msgfmt -o locales/es/LC_MESSAGES/main.mo locales/es/LC_MESSAGES/main
msgfmt -o locales/es/LC_MESSAGES/command.mo locales/es/LC_MESSAGES/command
msgfmt -o locales/es/LC_MESSAGES/action.mo locales/es/LC_MESSAGES/action
msgfmt -o locales/es/LC_MESSAGES/report.mo locales/es/LC_MESSAGES/report
msgfmt -o locales/es/LC_MESSAGES/displayInformation.mo locales/es/LC_MESSAGES/displayInformation
```