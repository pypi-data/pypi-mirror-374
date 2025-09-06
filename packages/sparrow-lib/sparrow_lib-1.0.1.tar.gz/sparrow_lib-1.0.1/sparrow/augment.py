# sparrow/augment.py

import torch.nn as nn
from .layers import RouterAugmentedLinear
from .config import SparrowConfig # این import را اضافه کنید

def add_routers_to_model(model: nn.Module, config: SparrowConfig) -> nn.Module:
    """
    مدل را بر اساس تنظیمات ارائه شده، با مسیریاب‌ها تقویت می‌کند.
    """
    # ... کد این تابع بدون تغییر باقی می‌ماند ...
    for name, module in model.named_modules():
        if any(isinstance(module, layer_type) for layer_type in config.target_layers):
            if 'query' in name or 'key' in name or 'value' in name or 'dense' in name:
                parent_name, child_name = name.rsplit('.', 1)
                parent_module = model.get_submodule(parent_name)
                
                new_layer = RouterAugmentedLinear(module)
                setattr(parent_module, child_name, new_layer)
    return model

# --- این تابع احتمالاً جا مانده است ---
def collect_sparsity_losses(model: nn.Module) -> float:
    """
    در مدل پیمایش کرده و مجموع زیان‌های پراکندگی ذخیره شده در هر لایه
    RouterAugmentedLinear را جمع‌آوری می‌کند.
    """
    total_loss = 0.0
    num_layers = 0
    for module in model.modules():
        if isinstance(module, RouterAugmentedLinear):
            total_loss += module.last_sparsity_loss
            num_layers += 1
    
    return total_loss / num_layers if num_layers > 0 else 0.0