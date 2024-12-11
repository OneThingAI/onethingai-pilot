import time
from typing import Dict

class AutoscalingPolicy:
    """Defines and evaluates autoscaling policies."""
    
    def __init__(self, 
                 cpu_threshold: float = 80.0,
                 memory_threshold: float = 80.0,
                 scale_up_cooldown: int = 300,  # 5 minutes
                 scale_down_cooldown: int = 300):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.scale_up_cooldown = scale_up_cooldown
        self.scale_down_cooldown = scale_down_cooldown
        self.last_scale_up_time = 0
        self.last_scale_down_time = 0

    def should_scale_up(self, metrics: Dict) -> bool:
        """Evaluate if scaling up is needed based on metrics."""
        current_time = time.time()
        if current_time - self.last_scale_up_time < self.scale_up_cooldown:
            return False

        cpu_usage = metrics.get("cpu_usage", 0)
        memory_usage = metrics.get("memory_usage", 0)

        if cpu_usage > self.cpu_threshold or memory_usage > self.memory_threshold:
            self.last_scale_up_time = current_time
            return True
        return False

    def should_scale_down(self, metrics: Dict) -> bool:
        """Evaluate if scaling down is needed based on metrics."""
        current_time = time.time()
        if current_time - self.last_scale_down_time < self.scale_down_cooldown:
            return False

        cpu_usage = metrics.get("cpu_usage", 0)
        memory_usage = metrics.get("memory_usage", 0)

        if cpu_usage < self.cpu_threshold/2 and memory_usage < self.memory_threshold/2:
            self.last_scale_down_time = current_time
            return True
        return False 