# sparrow/__init__.py

from .config import SparrowConfig
from .augment import add_routers_to_model, collect_sparsity_losses
from .integrations import SparrowTrainer
from .utils import get_sparsity_report

print("Sparrow Library Loaded 🐦 - Ready to make your models smarter and sparser!")