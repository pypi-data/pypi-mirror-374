# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from .config import SparrowConfig
from transformers.models.bert.modeling_bert import BertAttention

class RouterAugmentedLinear(nn.Module):
    def __init__(self, original_layer: nn.Linear, config: SparrowConfig):
        super().__init__()
        self.original_layer = original_layer
        self.config = config
        self.original_layer.weight = torch.nn.Parameter(self.original_layer.weight.contiguous())
        
        self.in_features = original_layer.in_features
        self.out_features = original_layer.out_features

        for param in self.original_layer.parameters():
            param.requires_grad = False

        router_output_size = self.out_features
        if self.config.routing_strategy == "adaptive_gate":
            router_output_size += 1

        if not self.config.router_hidden_layers:
            self.router = nn.Linear(self.in_features, router_output_size)
        else:
            router_layers = []
            last_size = self.in_features
            for hidden_size in self.config.router_hidden_layers:
                router_layers.append(nn.Linear(last_size, hidden_size))
                router_layers.append(nn.ReLU())
                last_size = hidden_size
            router_layers.append(nn.Linear(last_size, router_output_size))
            self.router = nn.Sequential(*router_layers)
        
        self.last_sparsity_loss = 0.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        router_output = self.router(x)
        mask = None
        
        if self.config.routing_strategy == "top_k_percent":
            num_neurons_to_activate = int(self.out_features * self.config.top_k_percent)
            k = max(1, num_neurons_to_activate)
            
            _, top_k_indices = torch.topk(router_output, k=k, dim=-1)
            mask = torch.zeros_like(router_output).scatter_(-1, top_k_indices, 1)
            mask = mask + router_output - router_output.detach()
            self.last_sparsity_loss = torch.tensor(self.config.top_k_percent)
        
        elif self.config.routing_strategy == "adaptive_gate":
            is_3d = x.dim() == 3
            router_logits = router_output[:, :, :-1] if is_3d else router_output[:, :-1]
            budget_logit = router_output[:, :, -1] if is_3d else router_output[:, -1]

            probs = torch.sigmoid(router_logits)
            mask = (torch.rand_like(probs) < probs).float() if self.training else (probs > 0.5).float()
            mask = mask - probs.detach() + probs
            
            actual_sparsity = mask.mean()
            predicted_sparsity = torch.sigmoid(budget_logit).mean()
            
            sparsity_loss = torch.pow(predicted_sparsity - actual_sparsity, 2)
            budget_penalty = self.config.adaptive_sparsity_lambda * predicted_sparsity
            self.last_sparsity_loss = sparsity_loss + budget_penalty
        
        else:
            raise ValueError(f"Unknown routing strategy: {self.config.routing_strategy}")

        original_output = self.original_layer(x)
        final_output = original_output * mask
        return final_output

# sparrow/layers.py

# ... (کلاس RouterAugmentedLinear بدون تغییر باقی می‌ماند) ...

# sparrow/layers.py


# کلاس RouterAugmentedLinear بدون تغییر از نسخه صحیح قبلی باقی می‌ماند.

class RouterAugmentedAttention(nn.Module):
    """
    این کلاس یک بلوک BertAttention را در بر می‌گیرد و آن را با یک مسیریاب هوشمند
    برای فعال‌سازی پویا سرهای توجه (attention heads) مجهز می‌کند.
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

        # ساخت مسیریاب (ساده یا چندلایه)
        router_output_size = self.num_heads
        if not self.config.router_hidden_layers:
            self.router = nn.Linear(self.hidden_size, router_output_size)
        else:
            layers = []
            last_size = self.hidden_size
            for hidden_dim in self.config.router_hidden_layers:
                layers.append(nn.Linear(last_size, hidden_dim))
                layers.append(nn.ReLU())
                last_size = hidden_dim
            layers.append(nn.Linear(last_size, router_output_size))
            self.router = nn.Sequential(*layers)
            
        self.last_sparsity_loss = 0.0

    # --- رفع کلیدی اینجاست ---
    # امضای متد اکنون به درستی آرگومان‌های اضافی را با **kwargs می‌پذیرد.
    def forward(self, hidden_states, attention_mask=None, **kwargs):
        # ۱. تولید امتیاز برای هر سر توجه
        router_input = hidden_states.mean(dim=1)
        router_logits = self.router(router_input)

        # ۲. انتخاب K درصد سرهای برتر
        num_heads_to_activate = int(self.num_heads * self.config.top_k_percent)
        k = max(1, num_heads_to_activate)

        _, top_k_indices = torch.topk(router_logits, k=k, dim=-1)
        
        # ۳. ایجاد یک ماسک قابل تمایز (differentiable) برای سرها
        head_mask = torch.zeros_like(router_logits).scatter_(-1, top_k_indices, 1)
        head_mask = head_mask + router_logits - router_logits.detach() # STE Trick
        
        # تغییر ابعاد ماسک برای اعمال بر روی Q, K, V
        # (batch_size, num_heads) -> (batch_size, num_heads, 1, 1) برای broadcasting
        head_mask_expanded = head_mask.view(head_mask.size(0), self.num_heads, 1, 1)

        # ۴. انجام محاسبات داخلی توجه
        q = self.original_attention.self.query(hidden_states)
        k = self.original_attention.self.key(hidden_states)
        v = self.original_attention.self.value(hidden_states)

        # تغییر ابعاد تنسورها برای جدا کردن سرها
        q_heads = q.view(q.size(0), q.size(1), self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        k_heads = k.view(k.size(0), k.size(1), self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        v_heads = v.view(v.size(0), v.size(1), self.num_heads, self.head_dim).permute(0, 2, 1, 3)

        # ۵. اعمال ماسک برای صفر کردن سرهای غیرفعال
        q_heads = q_heads * head_mask_expanded
        k_heads = k_heads * head_mask_expanded
        v_heads = v_heads * head_mask_expanded

        # ۶. محاسبه امتیازات توجه
        attention_scores = torch.matmul(q_heads, k_heads.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.head_dim)
        if attention_mask is not None:
            # attention_mask از مدل باید قابل broadcast به امتیازات باشد
            # شکل اصلی: [batch_size, 1, 1, seq_length]
            # شکل امتیازات ما: [batch_size, num_heads, seq_length, seq_length]
            # ما باید ماسک را unsqueeze کنیم تا مطابقت پیدا کند
            attention_scores = attention_scores + attention_mask

        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        context_layer = torch.matmul(attention_probs, v_heads)

        # ۷. ترکیب خروجی سرها و عبور از لایه خطی نهایی
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.hidden_size,)
        context_layer = context_layer.view(new_context_layer_shape)
        
        # ما زیرماژول خروجی اصلی را که همیشه فعال است، فراخوانی می‌کنیم
        attention_output = self.original_attention.output(context_layer, hidden_states)

        self.last_sparsity_loss = (head_mask > 0).float().mean()
        
        # خروجی یک لایه توجه در transformers یک tuple است
        return (attention_output,)