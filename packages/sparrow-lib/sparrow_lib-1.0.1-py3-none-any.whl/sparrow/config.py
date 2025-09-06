# sparrow/config.py (فایل جدید)

from typing import List, Type
import torch.nn as nn

class SparrowConfig:
    def __init__(
        self,
        sparsity_lambda: float = 0.01,
        target_layers: List[Type[nn.Module]] = [nn.Linear],
        # در آینده می‌توان استراتژی‌های دیگری اضافه کرد
        routing_strategy: str = "gumbel_softmax" 
    ):
        """
        کلاس تنظیمات برای کتابخانه sparrow.

        Args:
            sparsity_lambda (float): ضریب اهمیت صرفه‌جویی در تابع زیان.
            target_layers (List): لیستی از انواع لایه‌هایی که باید مجهز به مسیریاب شوند.
            routing_strategy (str): استراتژی مسیریابی (در حال حاضر فقط 'gumbel_softmax').
        """
        self.sparsity_lambda = sparsity_lambda
        self.target_layers = target_layers
        self.routing_strategy = routing_strategy