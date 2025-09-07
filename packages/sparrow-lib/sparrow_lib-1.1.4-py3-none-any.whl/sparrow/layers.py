# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from .config import SparrowConfig

class RouterAugmentedLinear(nn.Module):
    def __init__(self, original_layer: nn.Linear, config: SparrowConfig):
        super().__init__()
        self.original_layer = original_layer
        self.config = config

        # اطمینان از یکپارچگی وزن‌ها
        self.original_layer.weight = torch.nn.Parameter(self.original_layer.weight.contiguous())
        
        self.in_features = original_layer.in_features
        self.out_features = original_layer.out_features

        # منجمد کردن وزن‌های لایه اصلی
        for param in self.original_layer.parameters():
            param.requires_grad = False

        # ساخت مسیریاب بر اساس کانفیگ
        if not self.config.router_hidden_layers:
            self.router = nn.Linear(self.in_features, self.out_features)
        else:
            router_layers = []
            last_size = self.in_features
            for hidden_size in self.config.router_hidden_layers:
                router_layers.append(nn.Linear(last_size, hidden_size))
                router_layers.append(nn.ReLU())
                last_size = hidden_size
            router_layers.append(nn.Linear(last_size, self.out_features))
            self.router = nn.Sequential(*router_layers)
        
        self.last_sparsity_loss = 0.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        router_logits = self.router(x)

        if self.config.routing_strategy == "top_k_percent":
            num_neurons_to_activate = int(self.out_features * self.config.top_k_percent)
            k = max(1, num_neurons_to_activate)
            
            _, top_k_indices = torch.topk(router_logits, k=k, dim=-1)
            mask = torch.zeros_like(router_logits).scatter_(-1, top_k_indices, 1)
            # STE Trick for differentiability
            mask = mask + router_logits - router_logits.detach()
        else:
            raise ValueError(f"Unknown routing strategy: {self.config.routing_strategy}")

        self.last_sparsity_loss = torch.tensor(self.config.top_k_percent)
        
        original_output = self.original_layer(x)
        final_output = original_output * mask
        
        return final_output