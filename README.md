# OneThingAI Python SDK

A Python SDK for managing GPU instances on the OneThingAI cloud platform.

## Features

- Instance lifecycle management (create, start, stop, delete)
- Private image management
- Resource availability checking
- Wallet and billing information
- Auto-scaling capabilities
- Robust error handling and retries

## Installation
```bash
pip install onethingai-pilot
```
## Quick Start

```python
from instances.instance_manager import OneThingAIInstance
from instances.models import InstanceConfigQuery, CustomPort
# Initialize the client
instance_manager = OneThingAIInstance(api_key="your_api_key")
# Create an instance
instance_config = InstanceConfigQuery(
    app_image_id="your_image_id",
    gpu_type="NVIDIA-GEFORCE-RTX-4090",
    region_id=6,
    gpu_num=1,
    bill_type=3, # Pay as you go
    duration=0,
    group_id="",
    custom_port=[CustomPort(local_port=7860, type="http")]
)

# Create instance
instance = instance_manager.create(instance_config)
print(f"Created instance: {instance.app_id}")
```

## Documentation

### Instance Management

```python
# List instances
instances = instance_manager.get_instance_list(InstanceQuery(page=1, page_size=10))

# Stop instance
instance_manager.stop(app_id="your_instance_id")

# Start instance
instance_manager.start(app_id="your_instance_id")

# Delete instance
instance_manager.delete(app_id="your_instance_id")
```

### Auto-scaling
WIP


## Development

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
```

These files provide a solid foundation for the project, including:
- Project metadata and dependencies
- Installation and build configuration
- Documentation of features and usage
- Development setup instructions
- Change tracking
- Licensing information

The configuration is based on modern Python packaging standards and includes all necessary dependencies identified from the codebase.