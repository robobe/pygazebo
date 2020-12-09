import asyncio
import sys
sys.path.insert(0,'..')
from pygazebo import pygazebo

def cb(data):
    poses_stamped = pygazebo.msg.imu_pb2.IMU()
    poses_stamped.ParseFromString(data)
    print(poses_stamped)

async def publish_loop():
    manager = await pygazebo.connect()
    subscriber = await manager.subscribe("/gazebo/default/heavy_base/imu_base/imu/imu", 
    'gazebo.msgs.IMU', cb)
    while True:
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(publish_loop())