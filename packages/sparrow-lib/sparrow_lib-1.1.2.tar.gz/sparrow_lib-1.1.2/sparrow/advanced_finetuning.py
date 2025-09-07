# examples/advanced_finetuning.py

from transformers import BertForSequenceClassification, AutoTokenizer, TrainingArguments
from sparrow.config import SparrowConfig
from sparrow.augment import add_routers_to_model
from sparrow.integrations import SparrowTrainer
from sparrow.utils import get_sparsity_report

# ۱. تعریف تنظیمات
sparrow_config = SparrowConfig(sparsity_lambda=0.01)

# ۲. بارگذاری و تقویت مدل
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
model = add_routers_to_model(model, config=sparrow_config)

# ... آماده‌سازی داده‌ها ...

# ۳. استفاده از Trainer سفارشی
training_args = TrainingArguments(output_dir="test_trainer", num_train_epochs=1)

trainer = SparrowTrainer(
    model=model,
    args=training_args,
    sparrow_config=sparrow_config, # ارسال تنظیمات به Trainer
    # ... train_dataset, eval_dataset ...
)

# ۴. شروع آموزش
trainer.train()

# ۵. گرفتن گزارش پراکندگی بعد از آموزش
# ابتدا مدل را روی داده‌های ارزیابی اجرا می‌کنیم
trainer.evaluate() 
report = get_sparsity_report(model)
print("\n--- Sparsity Report ---")
print(report)