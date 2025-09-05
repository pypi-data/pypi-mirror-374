"""12Tree - AVL Tree-based Floating Point Data Store"""

import json
from typing import List, Optional, Any, Dict, Union
from pathlib import Path
import pickle
from .node import TreeNode


class FloatTreeStore:
    """An AVL tree-based data store optimized for floating point values"""

    def __init__(self):
        self.root: Optional[TreeNode] = None
        self._size: int = 0

    def _get_height(self, node: Optional[TreeNode]) -> int:
        """Get height of a node"""
        return node.height if node else 0

    def _get_balance(self, node: Optional[TreeNode]) -> int:
        """Get balance factor of a node"""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _right_rotate(self, y: TreeNode) -> TreeNode:
        """Right rotate subtree rooted with y"""
        x = y.left
        if not x:
            return y
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.height = max(self._get_height(y.left), self._get_height(y.right)) + 1
        x.height = max(self._get_height(x.left), self._get_height(x.right)) + 1

        return x

    def _left_rotate(self, x: TreeNode) -> TreeNode:
        """Left rotate subtree rooted with x"""
        y = x.right
        if not y:
            return x
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = max(self._get_height(x.left), self._get_height(x.right)) + 1
        y.height = max(self._get_height(y.left), self._get_height(y.right)) + 1

        return y

    def insert(self, value: float, data: Any = None) -> None:
        """Insert a floating point value with optional associated data"""
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a number")

        self.root = self._insert_recursive(self.root, float(value), data)
        self._size += 1

    def _insert_recursive(self, node: Optional[TreeNode], value: float, data: Any) -> TreeNode:
        """Recursive insert with AVL balancing"""
        # Perform normal BST insertion
        if not node:
            return TreeNode(value, data)

        if value < node.value:
            node.left = self._insert_recursive(node.left, value, data)
        elif value > node.value:
            node.right = self._insert_recursive(node.right, value, data)
        else:
            # Duplicate values allowed, store as right child
            node.right = self._insert_recursive(node.right, value, data)

        # Update height
        node.height = max(self._get_height(node.left), self._get_height(node.right)) + 1

        # Get balance factor
        balance = self._get_balance(node)

        # Balance the tree
        # Left Left Case
        if balance > 1 and node.left and value < node.left.value:
            return self._right_rotate(node)

        # Right Right Case
        if balance < -1 and node.right and value > node.right.value:
            return self._left_rotate(node)

        # Left Right Case
        if balance > 1 and node.left and value > node.left.value:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Right Left Case
        if balance < -1 and node.right and value < node.right.value:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def search(self, value: float, tolerance: float = 0.0) -> Optional[Any]:
        """Search for a value with optional tolerance"""
        node = self._search_recursive(self.root, value, tolerance)
        return node.data if node else None

    def _search_recursive(self, node: Optional[TreeNode], value: float, tolerance: float) -> Optional[TreeNode]:
        """Recursive search with tolerance"""
        if not node:
            return None

        if abs(node.value - value) <= tolerance:
            return node

        if value < node.value:
            return self._search_recursive(node.left, value, tolerance)
        else:
            return self._search_recursive(node.right, value, tolerance)

    def find_range(self, min_val: float, max_val: float) -> List[Dict[str, Any]]:
        """Find all values within a range"""
        results: List[Dict[str, Any]] = []
        self._find_range_recursive(self.root, min_val, max_val, results)
        return results

    def _find_range_recursive(self, node: Optional[TreeNode], min_val: float, max_val: float, results: List[Dict[str, Any]]) -> None:
        """Recursive range search"""
        if not node:
            return

        if min_val < node.value:
            self._find_range_recursive(node.left, min_val, max_val, results)

        if min_val <= node.value <= max_val:
            results.append({"value": node.value, "data": node.data})

        if max_val > node.value:
            self._find_range_recursive(node.right, min_val, max_val, results)

    def get_all_values(self) -> List[float]:
        """Get all stored values in sorted order"""
        values: List[float] = []
        self._inorder_traversal(self.root, values)
        return values

    def _inorder_traversal(self, node: Optional[TreeNode], values: List[float]) -> None:
        """Inorder traversal to get sorted values"""
        if node:
            self._inorder_traversal(node.left, values)
            values.append(node.value)
            self._inorder_traversal(node.right, values)

    def size(self) -> int:
        """Get number of stored values"""
        return self._size

    def is_empty(self) -> bool:
        """Check if store is empty"""
        return self._size == 0

    def clear(self) -> None:
        """Clear all data"""
        self.root = None
        self._size = 0

    def save_to_file(self, filepath: Union[str, Path]) -> None:
        """Save the tree to a file"""
        filepath = Path(filepath)
        data = {
            "values": self.get_all_values(),
            "size": self._size
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath: Union[str, Path]) -> None:
        """Load the tree from a file"""
        filepath = Path(filepath)
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.clear()
        # Note: This is a simplified load that doesn't preserve the tree structure
        # For production, you'd want to rebuild the AVL tree properly
        for value in data.get("values", []):
            self.insert(value)

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"FloatTreeStore(size={self._size})"
