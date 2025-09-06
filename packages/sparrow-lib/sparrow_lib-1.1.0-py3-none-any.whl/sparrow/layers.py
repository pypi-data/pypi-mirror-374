# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from .config import SparrowConfig # وارد کردن کانفیگ

class RouterAugmentedLinear(nn.Module):
    """
    یک لایه خطی استاندارد را با یک مسیریاب داینامیک و قابل تنظیم مجهز می‌کند.
    """
    def __init__(self, original_layer: nn.Linear, config: SparrowConfig):
        super().__init__()
        self.original_layer = original_layer
        self.original_layer.weight = torch.nn.Parameter(self.original_layer.weight.contiguous())
        
        self.in_features = original_layer.in_features
        self.out_features = original_layer.out_features

        for param in self.original_layer.parameters():
            param.requires_grad = False

        # --- ساخت مسیریاب هوشمند بر اساس کانفیگ ---
        if not config.router_hidden_layers:
            # حالت ساده: مسیریاب تک‌لایه
            self.router = nn.Linear(self.in_features, self.out_features)
        else:
            # حالت پیشرفته: مسیریاب چندلایه (MLP)
            router_layers = []
            last_size = self.in_features
            # ایجاد لایه‌های پنهان
            for hidden_size in config.router_hidden_layers:
                router_layers.append(nn.Linear(last_size, hidden_size))
                router_layers.append(nn.ReLU())
                last_size = hidden_size
            # اضافه کردن لایه خروجی
            router_layers.append(nn.Linear(last_size, self.out_features))
            self.router = nn.Sequential(*router_layers)
        
        self.last_sparsity_loss = 0.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        router_logits = self.router(x)
        mask = F.gumbel_softmax(router_logits, tau=1.0, hard=True)
        self.last_sparsity_loss = mask.float().mean()
        original_output = self.original_layer(x)
        final_output = original_output * mask
        return final_output