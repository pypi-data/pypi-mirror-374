# sparrow/augment.py
import torch.nn as nn
from transformers.models.bert.modeling_bert import BertAttention
from .layers import RouterAugmentedLinear, RouterAugmentedAttention
from .config import SparrowConfig

def add_routers_to_model(model: nn.Module, config: SparrowConfig) -> nn.Module:
    # یک لیست از ماژول‌ها برای جایگزینی تهیه می‌کنیم تا در حین پیمایش، ساختار مدل تغییر نکند
    modules_to_replace = []
    for name, module in model.named_modules():
        if isinstance(module, BertAttention):
            modules_to_replace.append((name, module))

    # جایگزینی بلوک‌های Attention با نسخه تقویت‌شده
    for name, module in modules_to_replace:
        parent_name, child_name = name.rsplit('.', 1)
        parent_module = model.get_submodule(parent_name)
        new_layer = RouterAugmentedAttention(module, config)
        setattr(parent_module, child_name, new_layer)

    # تقویت لایه‌های FFN (که خارج از بلوک Attention هستند)
    for name, module in model.named_modules():
        if isinstance(module, BertAttention) or isinstance(module, RouterAugmentedAttention):
            continue # از این بلوک‌ها و محتویاتشان رد می‌شویم

        if any(isinstance(module, layer_type) for layer_type in config.target_layers):
            if 'dense' in name and 'attention' not in name: # فقط لایه‌های FFN
                parent_name, child_name = name.rsplit('.', 1)
                parent_module = model.get_submodule(parent_name)
                new_layer = RouterAugmentedLinear(module, config)
                setattr(parent_module, child_name, new_layer)
                
    return model

# تابع collect_sparsity_losses بدون تغییر باقی می‌ماند

def collect_sparsity_losses(model: nn.Module) -> float:
    total_loss = 0.0
    num_layers = 0
    for module in model.modules():
        if isinstance(module, RouterAugmentedLinear):
            total_loss += module.last_sparsity_loss
            num_layers += 1
    return total_loss / num_layers if num_layers > 0 else 0.0