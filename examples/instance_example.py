import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from instances.instance_manager import OneThingAIInstance
from instances.models import *
instance_manager = OneThingAIInstance(api_key="97ad8bccd51ab247f7535d9c788ef949")

ret = instance_manager.get_private_image_list()

for item in ret.data:
    print(item.image_name)

ret = instance_manager.get_available_resources(ResourceQuery(app_image_id=1, gpu_type="NVIDIA-GEFORCE-RTX-4090"))
for item in ret.resource:
    print(item.gpu_type, item.region_id, item.max_gpu_num)
