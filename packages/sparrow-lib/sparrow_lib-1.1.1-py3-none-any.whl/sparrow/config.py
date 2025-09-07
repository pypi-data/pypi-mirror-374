# sparrow/config.py

class SparrowConfig:
    def __init__(
        self,
        # ... (پارامترهای دیگر) ...
        routing_strategy: str = "top_k", # <-- تغییر پیش‌فرض به top_k
        k: int = 4 # <-- پارامتر جدید: تعداد نورون‌هایی که باید فعال شوند
    ):
        # ... (کد init) ...
        self.routing_strategy = routing_strategy
        self.k = k