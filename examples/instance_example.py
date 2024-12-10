from instances.models import (
    InstanceType,
    InstanceSize,
    create_instance_config
)
from instances.instance_manager import OneThingAIInstance

# Create instance configuration
config = create_instance_config(
    name="test-instance",
    instance_type=InstanceType.GPU,
    size=InstanceSize.SMALL,
    storage_size=100,
    gpu_count=1,
    tags={"environment": "development"}
)

# Initialize instance manager
instance_manager = OneThingAIInstance(api_key="your_api_key")

# Create instance
response = instance_manager.create(config)

if response.success:
    instance = response.data
    print(f"Instance created: {instance.id}")
    
    # Get metrics
    metrics_response = instance_manager.get_metrics(instance.id)
    if metrics_response.success:
        metrics = metrics_response.data
        print(f"CPU Usage: {metrics.cpu_usage}%")
else:
    print(f"Error: {response.message}") 