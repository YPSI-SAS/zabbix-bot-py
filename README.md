# Zabbix-Bot-Py

## Environment variables
The variable BOT_TOKEN is obligatory for know the bot.
The variables URL, TOKEN are obligatory if you won't use the config file and manage only one server

## Config file
The config file is essential for manage many server
<br/>For declare a server use the configuration below by replacing capitalized words

* `NAMESERVER` it's the name of the server that you will use in the flag --server. <span style="color: #FF0000"> WARNING </span> : The name of the server must be unique
* `URL` it's the url at use for access to your zabbix server. Its format is **https://monserveurzabbix.fr** and you replace **monserveurzabbix.fr** by the server. <span style="color: #FF0000"> WARNING </span> : remember to put **http** if your url is not a secure url
* `TOKEN` it's the token that you have generate in Zabbix interface in Administration > General > API Tokens

```yaml
servers:
   - server: "NAMESERVER"
     url: "URL" 
     token: "TOKEN"
   - server: "NAMESERVER2"
     url: "URL" 
     token: "TOKEN"
```

