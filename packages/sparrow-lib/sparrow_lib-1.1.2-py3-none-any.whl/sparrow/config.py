# sparrow/config.py

from typing import List, Type
import torch.nn as nn

class SparrowConfig:
    def __init__(
        self,
        sparsity_lambda: float = 0.0, # در این حالت معمولاً استفاده نمی‌شود
        router_hidden_layers: List[int] = None,
        routing_strategy: str = "top_k_percent",
        top_k_percent: float = 0.2 # <-- پارامتر جدید: ۲۰٪ نورون‌های برتر
    ):
        """
        کلاس تنظیمات برای کتابخانه sparrow.

        Args:
            sparsity_lambda (float): ضریب اهمیت صرفه‌جویی.
            router_hidden_layers (List[int], optional): لیستی از اندازه‌های لایه‌های پنهان مسیریاب.
            routing_strategy (str): استراتژی مسیریابی.
            top_k_percent (float): درصدی از نورون‌های برتر که باید فعال شوند (عددی بین 0 و 1).
        """
        self.sparsity_lambda = sparsity_lambda
        self.router_hidden_layers = router_hidden_layers if router_hidden_layers else []
        self.routing_strategy = routing_strategy
        
        if not (0 < top_k_percent <= 1):
            raise ValueError("top_k_percent must be between 0 and 1.")
        self.top_k_percent = top_k_percent