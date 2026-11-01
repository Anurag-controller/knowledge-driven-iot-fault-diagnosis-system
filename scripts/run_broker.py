import sys
from pathlib import Path
import asyncio
import logging
from amqtt.broker import Broker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import settings

port = settings.LOCAL_MQTT_PORT

config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': f'127.0.0.1:{port}',
        }
    },
    'sys_interval': 0,
    'auth': {
        'allow-anonymous': True,
    }
}

async def main():
    logging.basicConfig(level=logging.INFO)
    broker = Broker(config)
    await broker.start()
    print(f"Embedded MQTT Broker running on 127.0.0.1:{port}", flush=True)
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await broker.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
