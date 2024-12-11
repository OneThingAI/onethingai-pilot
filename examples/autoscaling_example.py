import logging
import time
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from instances.instance_manager import OneThingAIInstance
from onethingai_pilot.scaling_policy import AutoscalingPolicy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d'
)
logger = logging.getLogger("AutoscalingExample")

def run_autoscaling_example():
    # Configuration
    API_KEY = "your_api_key_here"
    INSTANCE_CONFIG = {
        "name": "auto-scaled-instance",
        "type": "gpu",
        "size": "small",
        # Add other configuration parameters as needed
    }

    # Initialize instance manager and policy
    instance_manager = OneThingAIInstance(API_KEY)
    policy = AutoscalingPolicy()

    try:
        # Create initial instance
        instance = instance_manager.create(INSTANCE_CONFIG)
        instance_id = instance["id"]
        logger.info(f"Created instance: {instance_id}")

        # Monitor and apply autoscaling policies
        monitoring_duration = 3600  # 1 hour
        start_time = time.time()

        while time.time() - start_time < monitoring_duration:
            try:
                # Get current metrics
                metrics = instance_manager.get_metrics(instance_id)
                
                # Evaluate scaling policies
                if policy.should_scale_up(metrics):
                    new_instance = instance_manager.create(INSTANCE_CONFIG)
                    logger.info(f"Scaled up: Created new instance {new_instance['id']}")
                
                elif policy.should_scale_down(metrics):
                    instance_manager.stop(instance_id)
                    logger.info(f"Scaled down: Stopped instance {instance_id}")
                    # Optional: Delete the instance after stopping
                    instance_manager.delete(instance_id)
                    logger.info(f"Deleted instance {instance_id}")
                    break

                time.sleep(60)  # Wait for 1 minute before next check

            except Exception as e:
                logger.error(f"Error during monitoring: {str(e)}")
                break

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    
    finally:
        # Cleanup: Ensure instance is deleted
        try:
            instance_manager.delete(instance_id)
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    run_autoscaling_example() 