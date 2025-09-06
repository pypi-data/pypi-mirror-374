# sparrow/augment.py (به‌روزرسانی شده)
from .config import SparrowConfig
from .layers import RouterAugmentedLinear
import torch.nn as nn

def add_routers_to_model(model: nn.Module, config: SparrowConfig) -> nn.Module:
    """
    مدل را بر اساس تنظیمات ارائه شده، با مسیریاب‌ها تقویت می‌کند.
    """
    for name, module in model.named_modules():
        if any(isinstance(module, layer_type) for layer_type in config.target_layers):
            if 'query' in name or 'key' in name or 'value' in name or 'dense' in name:
                parent_name, child_name = name.rsplit('.', 1)
                parent_module = model.get_submodule(parent_name)
                
                # اینجا می‌توانیم بر اساس config.routing_strategy لایه‌های مختلفی بسازیم
                new_layer = RouterAugmentedLinear(module)
                setattr(parent_module, child_name, new_layer)
    return model