# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from .config import SparrowConfig
from transformers.models.bert.modeling_bert import BertAttention

# کلاس RouterAugmentedLinear بدون تغییر باقی می‌ماند (از پاسخ قبلی)

class RouterAugmentedAttention(nn.Module):
    """
    این کلاس یک بلوک BertAttention را می‌گیرد و آن را با یک مسیریاب هوشمند
    برای فعال‌سازی دینامیک سرهای توجه (Attention Heads) مجهز می‌کند.
    """
    def __init__(self, original_attention_module: BertAttention, config: SparrowConfig):
        super().__init__()
        self.original_attention = original_attention_module
        self.config = config

        # منجمد کردن تمام پارامترهای بلوک اصلی
        for param in self.original_attention.parameters():
            param.requires_grad = False
            
        # استخراج مشخصات از لایه اصلی
        self.num_heads = self.original_attention.self.num_attention_heads
        self.head_dim = self.original_attention.self.attention_head_size
        self.hidden_size = self.num_heads * self.head_dim

        # ساخت مسیریاب (با قابلیت داشتن لایه پنهان)
        router_output_size = self.num_heads
        if not self.config.router_hidden_layers:
            self.router = nn.Linear(self.hidden_size, router_output_size)
        else:
            # ساخت مسیریاب چندلایه
            layers = []
            last_size = self.hidden_size
            for hidden_dim in self.config.router_hidden_layers:
                layers.append(nn.Linear(last_size, hidden_dim))
                layers.append(nn.ReLU())
                last_size = hidden_dim
            layers.append(nn.Linear(last_size, router_output_size))
            self.router = nn.Sequential(*layers)
            
        self.last_sparsity_loss = 0.0

    def forward(self, hidden_states, attention_mask=None, **kwargs):
        # ۱. تولید امتیاز برای هر سر توجه
        router_input = hidden_states.mean(dim=1)
        router_logits = self.router(router_input)

        # ۲. انتخاب K درصد سرهای برتر
        num_heads_to_activate = int(self.num_heads * self.config.top_k_percent)
        k = max(1, num_heads_to_activate)

        _, top_k_indices = torch.topk(router_logits, k=k, dim=-1)
        
        # ۳. ایجاد ماسک برای انتخاب سرها
        head_mask = torch.zeros_like(router_logits).scatter_(-1, top_k_indices, 1)
        # اعمال STE Trick برای عبور گرادیان
        head_mask = head_mask + router_logits - router_logits.detach()
        # تغییر ابعاد ماسک برای ضرب در تنسورهای Q, K, V
        head_mask_expanded = head_mask.view(head_mask.size(0), 1, 1, self.num_heads, 1)

        # ۴. بازنویسی محاسبات داخلی توجه
        q = self.original_attention.self.query(hidden_states)
        k = self.original_attention.self.key(hidden_states)
        v = self.original_attention.self.value(hidden_states)

        # تغییر ابعاد برای جدا کردن سرها
        q_heads = q.view(q.size(0), q.size(1), self.num_heads, self.head_dim).permute(0, 3, 1, 2)
        k_heads = k.view(k.size(0), k.size(1), self.num_heads, self.head_dim).permute(0, 3, 1, 2)
        v_heads = v.view(v.size(0), v.size(1), self.num_heads, self.head_dim).permute(0, 3, 1, 2)

        # ۵. اعمال ماسک (خاموش کردن سرهای غیرفعال)
        q_heads = q_heads * head_mask_expanded
        k_heads = k_heads * head_mask_expanded
        v_heads = v_heads * head_mask_expanded

        # ۶. محاسبه امتیازات توجه
        attention_scores = torch.matmul(q_heads, k_heads.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.head_dim)
        if attention_mask is not None:
            attention_scores = attention_scores + attention_mask

        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        context_layer = torch.matmul(attention_probs, v_heads)

        # ۷. ترکیب خروجی سرها و لایه خروجی نهایی
        context_layer = context_layer.permute(0, 2, 3, 1).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.hidden_size,)
        context_layer = context_layer.view(new_context_layer_shape)
        
        # توجه: ما لایه خروجی attention.output را همواره فعال نگه می‌داریم
        attention_output = self.original_attention.output(context_layer, hidden_states)

        self.last_sparsity_loss = (head_mask > 0).float().mean()
        
        return (attention_output,)