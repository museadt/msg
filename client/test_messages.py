import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from network_client import MessageClient

config = {
    'client': {
        'server_host': 'localhost',
        'server_port': 5001,
        'reconnect_interval': 5
    },
    'logging': {
        'level': 'INFO',
        'file': 'app.log'
    }
}

client = MessageClient(config)
messages = client.get_messages()
print(f'Got {len(messages)} messages')
for msg in messages:
    print(f'Message ID: {msg.get("id")}, Title: {msg.get("title")}')