"""12Tree - Efficient Floating Point Data Store"""

__version__ = "0.1.0"
__author__ = "12Tree Team"
__description__ = "A high-performance floating point data store with tree-based indexing"

from .tree_store import FloatTreeStore
from .node import TreeNode

__all__ = ["FloatTreeStore", "TreeNode"]
