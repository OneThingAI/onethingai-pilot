import sys
from pathlib import Path
import time
sys.path.append(str(Path(__file__).parent.parent))

from onethingai_pilot.instances.instance_manager import OneThingAIInstance
from onethingai_pilot.instances.models import *

def stop_demo_instance(instance_manager, app_id):
    # 停止实例
    print(app_id, " 测试停止")
    if app_id:
        while True:
            ret = instance_manager.get_instance_list(QueryInstances(page=1, page_size=10))
            for item in ret.app_list:
                if item.app_id == app_id and item.status == InstanceStatus.RUNNING:
                    print("instance is running, stop it")
                    try:
                        ret = instance_manager.stop(app_id)
                        print(ret.msg)
                        return
                    except Exception as e:
                        print(f"stop instance failed {str(e)}")
                        return
                elif item.app_id == app_id:
                    print(f"skip this term, status is {item.status}")
                else:
                    pass
            print("sleep 10 seconds, wait for instance in running status")
            time.sleep(10)
    else:
        print("instance is not created by this demo, skip")


def start_demo_instance(instance_manager, app_id):
    # 启动已停止实例
    print(app_id, " 测试启动")
    if app_id:
        while True:
            ret = instance_manager.get_instance_list(QueryInstances(page=1, page_size=10))
            for item in ret.app_list:
                if item.app_id == app_id and item.status == InstanceStatus.STOPPED:
                    print("instance is stopped, start it")
                    try:
                        ret = instance_manager.start(app_id)
                        print(ret.msg)
                        return
                    except Exception as e:
                        print(f"start instance failed {str(e)}")
                        return
                elif item.app_id == app_id:
                    print(f"skip this term, status is {item.status}")
                else:
                    pass
            print("sleep 10 seconds, wait for instance in stopped status")
            time.sleep(10)
    else:
        print("instance is not created by this demo, skip")

def delete_demo_instance(instance_manager, app_id):
    # 删除实例
    print(app_id, " 测试删除")
    if app_id:
        while True:
            ret = instance_manager.get_instance_list(QueryInstances(page=1, page_size=10))
            for item in ret.app_list:
                if item.app_id == app_id and item.status == InstanceStatus.STOPPED:
                    print("instance is stopped, delete it")
                    try:
                        ret = instance_manager.delete(app_id)
                        print(ret.msg)
                        return
                    except Exception as e:
                        print(f"stop instance failed, or delete instance failed {str(e)}")
                        return
                elif item.app_id == app_id:
                    print(f"skip this term, status is {item.status}")
                else:
                    pass
            print("sleep 10 seconds, wait for instance in stopped status")
            time.sleep(10)
    else:
        print("instance is not created by this demo, skip")


def main():
    instance_manager = OneThingAIInstance(api_key="your_api_key")
    # 获取私有镜像列表
    ret = instance_manager.get_private_image_list(QueryPrivateImage(region_id=6))
    print(ret)
    instance_created_by_this_demo = None
    for item in ret.private_image_list:
        if item.region_id == 6 and item.app_image_status == PrivateImageStatus.SUCCESS:
            ret = instance_manager.get_available_resources(QueryResources(
                app_image_id=item.app_image_id,  # Convert to keyword argument
                region_id=6,
                gpu_type="NVIDIA-GEFORCE-RTX-4090"
            ))
            print(ret.resource_list)
            if ret.resource_list[0].max_gpu_num > 0: # 精确查找的资源返回数量大于0，则直接创建
                instance_config = InstanceConfig(
                    app_image_id=item.app_image_id,  # 私有镜像ID
                    gpu_type="NVIDIA-GEFORCE-RTX-4090",  # 显卡类型
                    region_id=6,  # 区域ID
                    gpu_num=1,  # 显卡数量
                    bill_type=BillType.PAY_AS_YOU_GO,  # 计费类型 
                    duration=0, 
                    group_id="",  
                    custom_port=[CustomPort(local_port=7860, type="http")]  # 端口转发
                )
                print(instance_config)
                try:
                    ret = instance_manager.create(instance_config)
                    print(ret.app_id, ret.group_id)
                    instance_created_by_this_demo = ret.app_id
                    break
                except Exception as e:
                    print(e)
                    print("create instance failed, try next image")
    # 获取实例列表
    try:
        ret = instance_manager.get_instance_list(QueryInstances(page=1, page_size=10))
        for item in ret.app_list:
            print(item.app_image_id, item.app_image_name, item.bill_type, item.app_id)
    except Exception as e:
        print(e)
    
    if instance_created_by_this_demo:
        stop_demo_instance(instance_manager, instance_created_by_this_demo)
        start_demo_instance(instance_manager, instance_created_by_this_demo)
        stop_demo_instance(instance_manager, instance_created_by_this_demo)
        delete_demo_instance(instance_manager, instance_created_by_this_demo)
    else:
        print("instance is not created by this demo, exit")

if __name__ == "__main__":
    main()