import json, os
FILE_PATH = os.path.join(os.path.dirname(__file__), 'postgres.json')

class DatabaseConfig:
    def __init__(self):
        self.load_settings()
    def load_settings(self):
        data = json.load(open(FILE_PATH))
        net = data['NETWORK_SETTINGS']
        db  = data['DATABASE_SETTINGS']
        self.IP_ADDRESS        = net['IP_ADDRESS']
        self.PORT_NUMBER       = net['PORT_NUMBER']
        self.RECONNECT_ATTEMPTS = net['RECONNECT_ATTEMPTS']
        self.RECONNECT_INTERVAL = net['RECONNECT_INTERVAL']
        self.DB_USER    = db['DB_USER']
        self.DB_PASSWORD= db['DB_PASSWORD']
        self.DB_NAME    = db['DB_NAME']
