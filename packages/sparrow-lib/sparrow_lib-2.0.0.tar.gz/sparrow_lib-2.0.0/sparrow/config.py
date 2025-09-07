# sparrow/config.py

from typing import List, Type
import torch.nn as nn

class SparrowConfig:
    def __init__(
        self,
        # --- پارامترهای عمومی ---
        router_hidden_layers: List[int] = None,
        target_layers: List[Type[nn.Module]] = [nn.Linear],
        
        # --- پارامترهای استراتژی ---
        routing_strategy: str = "top_k_percent",
        
        # برای استراتژی top_k_percent
        top_k_percent: float = 0.2,
        
        # برای استراتژی adaptive_gate
        adaptive_sparsity_lambda: float = 0.001
    ):
        """
        کلاس تنظیمات برای کتابخانه sparrow.

        Args:
            router_hidden_layers (List[int], optional): لیستی از اندازه‌های لایه‌های پنهان مسیریاب.
            target_layers (List): لیستی از انواع لایه‌هایی که باید تقویت شوند.
            routing_strategy (str): استراتژی مسیریابی. گزینه‌ها: 'top_k_percent', 'adaptive_gate'.
            top_k_percent (float): برای استراتژی 'top_k_percent'، درصدی از نورون‌های برتر که فعال می‌شوند.
            adaptive_sparsity_lambda (float): برای استراتژی 'adaptive_gate'، ضریب جریمه برای بودجه محاسباتی.
        """
        self.router_hidden_layers = router_hidden_layers if router_hidden_layers else []
        self.target_layers = target_layers
        self.routing_strategy = routing_strategy
        self.adaptive_sparsity_lambda = adaptive_sparsity_lambda
        
        if top_k_percent and not (0 < top_k_percent <= 1):
            raise ValueError("top_k_percent must be between 0 and 1.")
        self.top_k_percent = top_k_percent