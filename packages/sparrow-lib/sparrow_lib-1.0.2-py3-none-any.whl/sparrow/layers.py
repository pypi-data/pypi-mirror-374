# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F

class RouterAugmentedLinear(nn.Module):
    def __init__(self, original_layer: nn.Linear):
        super().__init__()
        self.original_layer = original_layer
        
        # --- خط جدید اینجاست ---
        # ما مطمئن می‌شویم که تنسور وزن‌ها در حافظه یکپارچه است
        self.original_layer.weight = torch.nn.Parameter(self.original_layer.weight.contiguous())
        
        self.in_features = original_layer.in_features
        self.out_features = original_layer.out_features

        for param in self.original_layer.parameters():
            param.requires_grad = False

        self.router = nn.Linear(self.in_features, self.out_features)
        self.last_sparsity_loss = 0.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # ... بقیه کد forward بدون تغییر باقی می‌ماند ...
        router_logits = self.router(x)
        mask = F.gumbel_softmax(router_logits, tau=1.0, hard=True)
        self.last_sparsity_loss = mask.float().mean()
        original_output = self.original_layer(x)
        final_output = original_output * mask
        return final_output