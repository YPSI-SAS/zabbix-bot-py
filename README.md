# Zabbix-Bot-Py

## Environment variables
The variable BOT_TOKEN is obligatory for know the bot.
The variables ZABBIX_URL, ZABBIX_TOKEN are obligatory if you won't use the config file and manage only one server

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
docker run --env BOT_TOKEN= --env ZABBIX_URL= --env ZABBIX_TOKEN= zabbix-bot
```