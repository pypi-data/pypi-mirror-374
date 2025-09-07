# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from .config import SparrowConfig

class RouterAugmentedLinear(nn.Module):
    def __init__(self, original_layer: nn.Linear, config: SparrowConfig):
        super().__init__()
        # ... (کد init بدون تغییر باقی می‌ماند) ...
        self.config = config # ذخیره کانفیگ

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        router_logits = self.router(x)

        if self.config.routing_strategy == "gumbel_softmax":
            mask = F.gumbel_softmax(router_logits, tau=1.0, hard=True)
        
        elif self.config.routing_strategy == "top_k":
            # انتخاب k نورون برتر بر اساس امتیازشان
            k = self.config.k
            top_k_values, top_k_indices = torch.topk(router_logits, k=k, dim=-1)
            
            # ایجاد یک ماسک پراکنده
            mask = torch.zeros_like(router_logits).scatter_(-1, top_k_indices, 1)
            
            # این یک ترفند برای اجازه دادن به گرادیان برای عبور از انتخاب top-k است
            # ما با این کار انتخاب را برای backpropagation به یک فرآیند "نرم" تبدیل می‌کنیم
            mask = mask + router_logits - router_logits.detach()

        else:
            raise ValueError(f"Unknown routing strategy: {self.config.routing_strategy}")

        self.last_sparsity_loss = mask.float().mean()
        original_output = self.original_layer(x)
        final_output = original_output * mask
        
        return final_output