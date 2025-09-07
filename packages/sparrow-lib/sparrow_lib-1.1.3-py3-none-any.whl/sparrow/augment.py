# sparrow/augment.py

import torch.nn as nn
from .layers import RouterAugmentedLinear
from .config import SparrowConfig

def add_routers_to_model(model: nn.Module, config: SparrowConfig) -> nn.Module:
    """
    مدل را بر اساس تنظیمات ارائه شده، با مسیریاب‌ها تقویت می‌کند.
    """
    for name, module in model.named_modules():
        if any(isinstance(module, layer_type) for layer_type in config.target_layers):
            # فقط لایه‌های کلیدی ترنسفورمرها را هدف قرار می‌دهیم
            if 'query' in name or 'key' in name or 'value' in name or 'dense' in name:
                parent_name, child_name = name.rsplit('.', 1)
                parent_module = model.get_submodule(parent_name)
                
                # --- تغییر اینجاست: پاس دادن کانفیگ به لایه ---
                new_layer = RouterAugmentedLinear(module, config)
                setattr(parent_module, child_name, new_layer)
    return model

def collect_sparsity_losses(model: nn.Module) -> float:
    # این تابع بدون تغییر باقی می‌ماند
    total_loss = 0.0
    num_layers = 0
    for module in model.modules():
        if isinstance(module, RouterAugmentedLinear):
            total_loss += module.last_sparsity_loss
            num_layers += 1
    return total_loss / num_layers if num_layers > 0 else 0.0