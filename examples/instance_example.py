import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from instances.instance_manager import OneThingAIInstance
from instances.models import *


instance_manager = OneThingAIInstance(api_key="your_api_key")

ret = instance_manager.get_private_image_list()

for item in ret.data:
    print(item.app_image_id, item.image_name, item.image_status, item.region_id)

instance_config = InstanceConfigQuery(
    app_image_id="your_app_image_id",  # 私有镜像ID, item.app_image_id
    gpu_type="NVIDIA-GEFORCE-RTX-4090",  # 显卡类型
    region_id=6,  # 区域ID,  item.region_id
    gpu_num=1,  # 显卡数量
    bill_type=3,  # 计费类型 3 按量计费， 2 包月计费， 1 包天
    duration=0,  # 时长
    group_id="",  # 组ID
    custom_port=[CustomPort(local_port=7860, type="http")]
)

try:
    ret = instance_manager.create(instance_config)
    print(ret)
except Exception as e:
    print(e)


try:
    ret = instance_manager.get_instance_list(InstanceQuery(page=1, page_size=10))
    for item in ret.list:
        print(item.app_image_id, item.app_image_name, item.bill_type, item.app_id)
except Exception as e:
    print(e)

try:
    ret = instance_manager.stop("your_app_id")
    print(ret.msg)
except Exception as e:
    print(e)

try:
    ret = instance_manager.start("your_app_id")
    print(ret.msg)
except Exception as e:
    print(e)

try:
    ret = instance_manager.delete("your_app_id")
    print(ret.msg)
except Exception as e:
    print(e)