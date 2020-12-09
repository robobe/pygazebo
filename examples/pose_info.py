import asyncio
import sys
sys.path.insert(0,'..')
from pygazebo import pygazebo

def cb(data):
    poses_stamped = pygazebo.msg.poses_stamped_pb2.PosesStamped()
    poses_stamped.ParseFromString(data)
    print(poses_stamped)

async def publish_loop():
    manager = await pygazebo.connect()
    subscriber = await manager.subscribe("/gazebo/default/pose/info", 
    'gazebo.msgs.PosesStamped', cb)
    while True:
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(publish_loop())