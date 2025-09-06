# sparrow/config.py

from typing import List, Type
import torch.nn as nn

class SparrowConfig:
    def __init__(
        self,
        sparsity_lambda: float = 0.01,
        target_layers: List[Type[nn.Module]] = [nn.Linear],
        router_hidden_layers: List[int] = None,
        routing_strategy: str = "gumbel_softmax"
    ):
        """
        کلاس تنظیمات برای کتابخانه sparrow.

        Args:
            sparsity_lambda (float): ضریب اهمیت صرفه‌جویی در تابع زیان.
            target_layers (List): لیستی از انواع لایه‌هایی که باید مجهز به مسیریاب شوند.
            router_hidden_layers (List[int], optional): لیستی از اندازه‌های لایه‌های پنهان برای
                مسیریاب. اگر None باشد، یک مسیریاب تک‌لایه ساده ساخته می‌شود.
                مثال: [32, 64] یک مسیریاب با دو لایه پنهانی می‌سازد.
            routing_strategy (str): استراتژی مسیریابی (برای نسخه‌های آینده).
        """
        self.sparsity_lambda = sparsity_lambda
        self.target_layers = target_layers
        self.router_hidden_layers = router_hidden_layers if router_hidden_layers else []
        self.routing_strategy = routing_strategy