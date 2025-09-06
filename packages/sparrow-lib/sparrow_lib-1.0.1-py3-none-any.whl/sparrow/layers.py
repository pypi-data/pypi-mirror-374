# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F

class RouterAugmentedLinear(nn.Module):
    """
    یک لایه خطی استاندارد (nn.Linear) را می‌گیرد و آن را با یک مسیریاب
    دینامیک مجهز می‌کند. وزن‌های لایه اصلی منجمد باقی می‌مانند و فقط
    مسیریاب آموزش می‌بیند.
    """
    def __init__(self, original_layer: nn.Linear):
        super().__init__()
        self.original_layer = original_layer
        
        # استخراج ابعاد از لایه اصلی
        self.in_features = original_layer.in_features
        self.out_features = original_layer.out_features

        # منجمد کردن پارامترهای لایه اصلی
        for param in self.original_layer.parameters():
            param.requires_grad = False

        # تعریف مسیریاب که کاملاً قابل آموزش است
        self.router = nn.Linear(self.in_features, self.out_features)
        
        # متغیری برای ذخیره زیان پراکندگی در هر بار اجرا
        self.last_sparsity_loss = 0.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 1. گرفتن امتیازها از مسیریاب
        router_logits = self.router(x)

        # 2. ایجاد ماسک باینری با Gumbel-Softmax
        # hard=True تضمین می‌کند که خروجی 0 یا 1 باشد اما گرادیان جریان دارد
        mask = F.gumbel_softmax(router_logits, tau=1.0, hard=True)
        
        # 3. محاسبه و ذخیره زیان پراکندگی
        # این مقدار میانگین درصد نورون‌های فعال شده در این بچ است
        self.last_sparsity_loss = mask.float().mean()

        # 4. اجرای لایه اصلی و اعمال ماسک
        original_output = self.original_layer(x)
        final_output = original_output * mask
        
        # فقط خروجی اصلی برگردانده می‌شود تا ساختار مدل به هم نریزد
        return final_output