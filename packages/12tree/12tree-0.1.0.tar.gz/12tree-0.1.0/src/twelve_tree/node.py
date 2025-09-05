"""Tree Node for 12Tree data store"""

from typing import Optional, Any


class TreeNode:
    """A node in the 12Tree data structure"""

    def __init__(self, value: float, data: Any = None):
        self.value: float = value
        self.data: Any = data
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None
        self.height: int = 1

    def __repr__(self) -> str:
        return f"TreeNode(value={self.value}, data={self.data})"
