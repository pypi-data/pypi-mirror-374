# sparrow/config.py

from typing import List, Type
import torch.nn as nn

class SparrowConfig:
    def __init__(
        self,
        sparsity_lambda: float = 0.0,
        router_hidden_layers: List[int] = None,
        routing_strategy: str = "top_k_percent",
        top_k_percent: float = 0.2,
        target_layers: List[Type[nn.Module]] = [nn.Linear]
    ):
        self.sparsity_lambda = sparsity_lambda
        self.router_hidden_layers = router_hidden_layers if router_hidden_layers else []
        self.routing_strategy = routing_strategy
        self.target_layers = target_layers
        
        if not (0 < top_k_percent <= 1):
            raise ValueError("top_k_percent must be between 0 and 1.")
        self.top_k_percent = top_k_percent