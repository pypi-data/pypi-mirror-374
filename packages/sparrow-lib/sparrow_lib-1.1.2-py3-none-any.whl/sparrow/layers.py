# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from .config import SparrowConfig

class RouterAugmentedLinear(nn.Module):
    # متد __init__ همان کدی است که در نسخه قبلی نوشتیم (که مسیریاب چندلایه می‌سازد)
    # ...

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        router_logits = self.router(x)

        if self.config.routing_strategy == "top_k_percent":
            # --- منطق جدید اینجاست ---
            # محاسبه داینامیک k بر اساس درصد
            num_neurons_to_activate = int(self.out_features * self.config.top_k_percent)
            
            # اطمینان از اینکه حداقل یک نورون فعال می‌شود
            k = max(1, num_neurons_to_activate)
            
            # بقیه منطق Top-K مانند قبل است
            top_k_values, top_k_indices = torch.topk(router_logits, k=k, dim=-1)
            mask = torch.zeros_like(router_logits).scatter_(-1, top_k_indices, 1)
            mask = mask + router_logits - router_logits.detach() # STE Trick

        else:
            # اینجا می‌توانید منطق استراتژی‌های دیگر را در آینده اضافه کنید
            raise ValueError(f"Unknown routing strategy: {self.config.routing_strategy}")

        # در این استراتژی، زیان پراکندگی همیشه برابر با درصد انتخابی است
        self.last_sparsity_loss = torch.tensor(self.config.top_k_percent)
        
        original_output = self.original_layer(x)
        final_output = original_output * mask
        
        return final_output