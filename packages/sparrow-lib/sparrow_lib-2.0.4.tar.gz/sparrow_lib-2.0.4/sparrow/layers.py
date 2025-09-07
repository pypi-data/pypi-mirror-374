# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from .config import SparrowConfig
from transformers.models.bert.modeling_bert import BertAttention

# کلاس RouterAugmentedLinear بدون تغییر است و باید در این فایل وجود داشته باشد
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

class RouterAugmentedAttention(nn.Module):
    def __init__(self, original_attention_module: BertAttention, config: SparrowConfig):
        super().__init__()
        self.original_attention = original_attention_module
        self.config = config
        for param in self.original_attention.parameters():
            param.requires_grad = False
        self.num_heads = self.original_attention.self.num_attention_heads
        self.head_dim = self.original_attention.self.attention_head_size
        self.hidden_size = self.num_heads * self.head_dim
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

    # --- اصلاح نهایی و قطعی اینجاست ---
    # امضای این متد حالا دقیقاً با امضای متد اصلی در BertAttention یکی است
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: torch.FloatTensor | None = None,
        head_mask: torch.FloatTensor | None = None,
        encoder_hidden_states: torch.FloatTensor | None = None,
        encoder_attention_mask: torch.FloatTensor | None = None,
        past_key_value: tuple[tuple[torch.FloatTensor]] | None = None,
        output_attentions: bool | None = False,
    ):
        router_input = hidden_states.mean(dim=1)
        router_logits = self.router(router_input)
        num_heads_to_activate = int(self.num_heads * self.config.top_k_percent)
        k = max(1, num_heads_to_activate)
        _, top_k_indices = torch.topk(router_logits, k=k, dim=-1)
        head_mask = torch.zeros_like(router_logits).scatter_(-1, top_k_indices, 1)
        head_mask = head_mask + router_logits - router_logits.detach()
        head_mask_expanded = head_mask.view(head_mask.size(0), self.num_heads, 1, 1)

        q_heads = self.original_attention.self.query(hidden_states).view(hidden_states.size(0), hidden_states.size(1), self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        k_heads = self.original_attention.self.key(hidden_states).view(hidden_states.size(0), hidden_states.size(1), self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        v_heads = self.original_attention.self.value(hidden_states).view(hidden_states.size(0), hidden_states.size(1), self.num_heads, self.head_dim).permute(0, 2, 1, 3)

        q_heads, k_heads, v_heads = q_heads * head_mask_expanded, k_heads * head_mask_expanded, v_heads * head_mask_expanded
        
        attention_scores = torch.matmul(q_heads, k_heads.transpose(-1, -2)) / math.sqrt(self.head_dim)
        if attention_mask is not None:
            attention_scores = attention_scores + attention_mask

        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        context_layer = torch.matmul(attention_probs, v_heads)
        
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        context_layer = context_layer.view(context_layer.size(0), context_layer.size(1), self.hidden_size)
        
        attention_output = self.original_attention.output(context_layer, hidden_states)
        self.last_sparsity_loss = (head_mask > 0).float().mean()
        
        return (attention_output,)