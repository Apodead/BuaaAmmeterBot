import json

def read_config():
    global bot_token
    global base_url
    global db_filename
    def default_get(s, default):
        #nonlocal conf
        if conf.get(s) is None:
            if default is None:
                raise ValueError('Config Error:{} is not set'
                        ' and does not have a default value'.format(s))
            else :
                return default
        else:
            return conf.get(s)
    with open('config.json') as f:
        conf = json.load(f)
        bot_token = default_get('BotToken', None)
        base_url = default_get('BaseURL', 'https://api.telegram.org/bot')
        #bot_api = default_get('BotAPI', api + 'bot')
        db_filename = default_get('DBFile', 'data.sqlite3')

bot_token = None
base_url = None
db_filename = None
read_config()
