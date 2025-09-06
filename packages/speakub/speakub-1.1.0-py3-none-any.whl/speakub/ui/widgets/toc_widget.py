"""
TOC (Table of Contents) widget for the EPUB reader.
"""

from typing import Dict, List, Optional

from textual.widgets import Tree


class TOCWidget(Tree):
    """A custom Tree widget for displaying the Table of Contents."""

    def __init__(self, toc_data: Optional[Dict] = None, **kwargs):
        super().__init__("Loading...", **kwargs)
        self.toc_data = toc_data
        if toc_data:
            self.update_toc(toc_data)

    def update_toc(self, toc_data: Dict) -> None:
        """Update the TOC tree with new data."""
        self.toc_data = toc_data
        self.clear()
        self.label = toc_data.get("book_title", "Book")

        # Build the TOC tree structure
        for node in toc_data.get("nodes", []):
            if node.get("type") == "group":
                # Create a group node
                group_node = self.root.add(node.get("title", "Group"), expand=False)
                for child in node.get("children", []):
                    group_node.add_leaf(child.get("title", "Item"), data=child)
            else:
                # Create a regular node
                self.root.add_leaf(node.get("title", "Item"), data=node)

        self.root.expand()

    def get_selected_chapter(self) -> Optional[Dict]:
        """Get the currently selected chapter data."""
        if self.cursor_node and self.cursor_node.data:
            return self.cursor_node.data
        return None

    def select_chapter_by_src(self, src: str) -> bool:
        """Select a chapter by its source path."""

        def find_node_by_src(node):
            if node.data and node.data.get("src") == src:
                return node
            for child in node.children:
                result = find_node_by_src(child)
                if result:
                    return result
            return None

        target_node = find_node_by_src(self.root)
        if target_node:
            self.select_node(target_node)
            return True
        return False

    def get_chapter_path(self, chapter_data: Dict) -> List[str]:
        """Get the path of titles from root to the given chapter."""
        path = []

        def build_path(node, target_data):
            if node.data == target_data:
                return True
            for child in node.children:
                if build_path(child, target_data):
                    path.insert(
                        0,
                        (
                            node.label.plain
                            if hasattr(node.label, "plain")
                            else str(node.label)
                        ),
                    )
                    return True
            return False

        build_path(self.root, chapter_data)
        return path
