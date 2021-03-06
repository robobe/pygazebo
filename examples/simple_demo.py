import asyncio
import sys
sys.path.insert(0,'..')
from pygazebo import pygazebo


def cb(data):
    message = pygazebo.msg.gz_string_pb2.GzString.FromString(data)
    print('Received message:', message.data)

async def publish_loop():
    manager = await pygazebo.connect()

    publisher = await manager.advertise(
        'test/hello',
        'gazebo.msgs.GzString')

    subscriber = await manager.subscribe("/gazebo/default/my_pub", 
    'gazebo.msgs.GzString', cb)
        
    message = pygazebo.msg.gz_string_pb2.GzString()
    message.data = "helllllllllllllllllllll"
    
    while True:
        await publisher.publish(message)
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(publish_loop())