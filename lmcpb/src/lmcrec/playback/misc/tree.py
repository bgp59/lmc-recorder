import sys
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Optional,
    TextIO,
    Union,
)

fancy_connectors = [
    "    ",
    "├── ",
    "│   ",
    "└── ",
]

ascii_connectors = ["    ", "|__ ", "|   ", "\__ "]

CONN_SPACE = 0
CONN_TEE = 1
CONN_EYE = 2
CONN_ELBOW = 3


@dataclass
class Node:
    value: Any = None
    children: List["Node"] = field(default_factory=list)

    def __eq__(self, other: "Node") -> bool:
        if other is None:
            return False
        if self.value != other.value:
            return False
        if len(self.children) != len(other.children):
            return False
        my_children = sorted(self.children, key=lambda c: c.value)
        other_children = sorted(other.children, key=lambda c: c.value)
        for i, child in enumerate(my_children):
            if child != other_children[i]:
                return False
        return True


def print_tree(
    root: Union[Node, Hashable],
    from_dict: Optional[Dict[Hashable, Iterable[Hashable]]] = None,
    use_ascii: bool = False,
    fh: TextIO = sys.stdout,
    sort_key: Optional[Callable] = None,
):
    """Print a tree

    Args:
        root (Node):
            Starting Node or key in the dictionary

        from_dict (dict):
            parent: children

        use_ascii (bool):
            If True, use ASCII connectors, in case the terminal cannot render Unicode

        fh (TextIO):
            The destination stream

        sort_key (Callable):
            The sort key function to use for sorting the children, if None then
            no sorting

    """

    connectors = ascii_connectors if use_ascii else fancy_connectors

    def print_node(node, prefix=""):
        if from_dict:
            value = node
            children = from_dict.get(node, [])
        else:
            value = node.value
            children = node.children
        print(prefix, value, sep="", file=fh)
        n = len(children)
        if sort_key is not None:
            children = sorted(children, key=sort_key)
        for i, child in enumerate(children):
            last_child = i == n - 1
            connector = connectors[CONN_ELBOW if last_child else CONN_TEE]
            if prefix.endswith(connectors[CONN_TEE]):
                # The current node is not the last child, its parent's connection
                # should be extended:
                new_prefix = (
                    prefix[: -len(connectors[CONN_TEE])]
                    + connectors[CONN_EYE]
                    + connector
                )
            elif prefix.endswith(connectors[CONN_ELBOW]):
                # The current node is the last child, its parent's connection
                # need not be extended:
                new_prefix = (
                    prefix[: -len(connectors[CONN_ELBOW])]
                    + connectors[CONN_SPACE]
                    + connector
                )
            else:
                new_prefix = prefix + connector
            print_node(child, prefix=new_prefix)

    print_node(root)


# _test_tree = Node(
#     "1",
#     [
#         Node("1.1", [Node("1.1.1", [Node("1.1.1.1"), Node("1.1.1.2")]), Node("1.1.2")]),
#         Node("1.2"),
#     ],
# )

# _test_tree_from_dict = {
#     "1": ["1.1", "1.2"],
#     "1.1": ["1.1.1", "1.1.2"],
#     "1.1.1": ["1.1.1.1", "1.1.1.2"],
# }
