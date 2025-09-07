# sparrow/integrations.py (فایل جدید)

from transformers import Trainer
from .augment import collect_sparsity_losses
from .config import SparrowConfig

class SparrowTrainer(Trainer):
    """
    یک Trainer سفارشی که به طور خودکار زیان پراکندگی را به زیان اصلی اضافه می‌کند.
    """
    def __init__(self, *args, sparrow_config: SparrowConfig, **kwargs):
        super().__init__(*args, **kwargs)
        self.sparrow_config = sparrow_config

    def compute_loss(self, model, inputs, return_outputs=False):
        # محاسبه زیان اصلی (مثلاً CrossEntropy) توسط Trainer والد
        outputs = model(**inputs)
        classification_loss = outputs.loss
        
        # جمع‌آوری زیان پراکندگی از تمام لایه‌های sparrow
        sparsity_loss = collect_sparsity_losses(model)
        
        # محاسبه زیان نهایی با استفاده از لاندای تعریف شده در config
        total_loss = classification_loss + self.sparrow_config.sparsity_lambda * sparsity_loss
        
        return (total_loss, outputs) if return_outputs else total_loss