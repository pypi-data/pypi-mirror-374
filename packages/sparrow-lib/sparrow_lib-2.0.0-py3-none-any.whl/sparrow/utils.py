# sparrow/utils.py (فایل جدید)

import pandas as pd
from .layers import RouterAugmentedLinear
import torch.nn as nn

def get_sparsity_report(model: nn.Module) -> pd.DataFrame:
    """
    یک گزارش دقیق از میزان فعالیت نورون‌ها در هر لایه مجهز به مسیریاب تولید می‌کند.
    این تابع باید بعد از اجرای مدل روی داده‌ها فراخوانی شود.
    """
    report_data = []
    for name, module in model.named_modules():
        if isinstance(module, RouterAugmentedLinear):
            # last_sparsity_loss همان میانگین فعالیت نورون‌ها است
            activation_percentage = module.last_sparsity_loss * 100
            report_data.append({
                "Layer Name": name,
                "Activation (%)": f"{activation_percentage:.2f}%",
                "Active Neurons": f"{int(module.out_features * module.last_sparsity_loss)} / {module.out_features}"
            })
    
    if not report_data:
        print("هیچ لایه‌ای با مسیریاب در مدل یافت نشد.")
        return pd.DataFrame()
        
    return pd.DataFrame(report_data)