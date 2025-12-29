#! /usr/bin/env python3

description = """
Given a (list of) record file(s) display the instance and class hierarchy and
the per class variable inventory.

IMPORTANT! Only record files from the same LSEG instance should be combined
           together, otherwise the results are unreliable or the tool may even
           crash.
"""

import argparse
import os
import sys
from typing import Optional

import yaml
from cache import (
    InstTree,
    InstTreeKey,
    LmcrecClassVarInfo,
    get_inventory_from_files,
)
from config import get_lmcrec_runtime
from misc.timeutils import format_ts
from misc.tree import Node, print_tree
from query import (
    build_lmcrec_file_chains,
    chain_to_file_list,
    get_file_selection_arg_parser,
    process_file_selection_args,
)
from tabulate import SEPARATING_LINE, tabulate

from .help_formatter import CustomWidthFormatter
from .lmcrec_schema import generate_lmcrec_schema

VAR_INFO_CLASS_NAME_EVERY_NTH_ROW = -1

INVENTORY_FILE_NAME = "lmcrec-inventory.txt"
SCHEMA_FILE_NAME = "lmcrec-schema.yaml"


def build_tree(inst_tree: InstTree, class_only: bool = False) -> Node:

    def process(node: Node, inst_tree_key: Optional[InstTreeKey] = None):

        for child_key in inst_tree.get(inst_tree_key, []):
            exists = False
            child_value = child_key[1] if class_only else child_key
            for child_node in node.children:
                if child_node.value == child_value:
                    exists = True
                    break
            if not exists:
                child_node = Node(child_value)
                node.children.append(child_node)
            process(child_node, child_key)

    root_node = Node("Root")
    process(root_node)
    return root_node


def heading(txt: str, fh=sys.stdout):
    line = "+" + "-" * (len(txt) + 2) + "+"
    print(file=fh)
    print(line, file=fh)
    print("| " + txt + " |", file=fh)
    print(line, file=fh)
    print(file=fh)


def generate_inventory(
    inst_tree: InstTree,
    class_var_info: LmcrecClassVarInfo,
    inst_max_size: int,
    instance_inventory=False,
    class_inventory=False,
    variable_inventory=False,
    use_ascii=False,
    fh=sys.stdout,
):

    if instance_inventory:
        heading("Instance & Class Tree", fh=fh)
        print_tree(
            build_tree(inst_tree),
            use_ascii=use_ascii,
            fh=fh,
            sort_key=lambda node: node.value[0].lower(),
        )
        print(file=fh)
        print(f"Instance Max Size: {inst_max_size}", file=fh)
        print(file=fh)

    if class_inventory or variable_inventory:
        class_tree = build_tree(inst_tree, class_only=True)
        heading("Class Tree", fh=fh)
        print_tree(
            class_tree,
            use_ascii=use_ascii,
            fh=fh,
            sort_key=lambda node: node.value.lower(),
        )
        print(file=fh)

    if variable_inventory:
        heading("Class Variables", fh=fh)
        headers = ("Class", "Variable", "Type", "Obs")
        empty_row = ("", "", "", "")
        rows = []
        for class_name in sorted(class_var_info, key=lambda s: s.lower()):
            if rows:
                # Inter-table separation:
                rows.append(SEPARATING_LINE)
                rows.append(empty_row)
                rows.append(empty_row)
                rows.append(SEPARATING_LINE)
            rows.append(headers)
            rows.append(SEPARATING_LINE)
            var_info_by_name = class_var_info[class_name]
            n_vars = len(var_info_by_name)
            for i, var_name in enumerate(
                sorted(var_info_by_name, key=lambda s: s.lower())
            ):
                include_class_name = i == (n_vars - 1) // 2
                var_info = var_info_by_name[var_name]
                var_type = var_info.var_type.name
                obs = []
                if var_info.neg_vals:
                    obs.append("Neg Vals")
                if var_info.max_size > 0:
                    obs.append(f"MaxSz={var_info.max_size}")
                rows.append(
                    (
                        class_name if include_class_name else "",
                        var_name,
                        var_type,
                        ", ".join(obs),
                    )
                )
            # Handle empty classes:
            if n_vars == 0:
                rows.append([class_name, "", "", ""])
        print(tabulate(rows, tablefmt="simple"), file=fh)
        print(file=fh)
    if hasattr(fh, "flush"):
        fh.flush()


def generate_schema(
    class_var_info: LmcrecClassVarInfo,
    inst_max_size: int = 0,
    fh=sys.stdout,
):

    lmcrec_schema = generate_lmcrec_schema(class_var_info, inst_max_size=inst_max_size)
    yaml.safe_dump(lmcrec_schema, fh, indent=2, sort_keys=True)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
        parents=[get_file_selection_arg_parser()],
    )
    parser.add_argument(
        "-I",
        "--instance-inventory",
        action="store_true",
        help="""
        Include instance inventory, implied if output dir is specified
        """,
    )
    parser.add_argument(
        "-C",
        "--class-inventory",
        action="store_true",
        help="""
        Include class inventory, implied if either of variable inventory or
        output dir are specified
        """,
    )
    parser.add_argument(
        "-V",
        "--variable-inventory",
        action="store_true",
        help="""
        Include class variable inventory, implied if output dir is specified
        """,
    )
    parser.add_argument(
        "-a",
        "--use-ascii",
        action="store_true",
        help="""
        Use ASCII separators when printing a tree, rather than fancier Unicode,
        in case the terminal doesn't support the latter.
        """,
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="OUTPUT_DIR",
        help=f"""
        Save the information under OUTPUT_DIR in {INVENTORY_FILE_NAME!r} and
        {SCHEMA_FILE_NAME!r} files. The directory will be created as needed.
        If OUTPUT_DIR is specified as "auto" then it will default to
        $LMCREC_RUNTIME/inventory/INST/FIRST_TIMESTAMP--LAST_TIMESTAMP. 
        """,
    )

    parser.add_argument(
        "lmcrec_file",
        nargs="*",
        help="""
        Specific lmcrec file(s) for which to run the inventory, they override
        the query style selection. Note that only record files from the same
        LSEG instance should be combined together, otherwise the results are
        unreliable or the tool may even crash.
        """,
    )
    args = parser.parse_args()

    instance_inventory = args.instance_inventory
    class_inventory = args.class_inventory
    variable_inventory = args.variable_inventory
    use_ascii = args.use_ascii
    output_dir = args.output_dir

    if output_dir is not None:
        instance_inventory = True
        class_inventory = True
        variable_inventory = True
    elif not (instance_inventory or class_inventory or variable_inventory):
        class_inventory = True

    lmcrec_files = args.lmcrec_file

    if not lmcrec_files:
        record_files_dir, from_ts, to_ts = process_file_selection_args(args)
        lmcrec_file_chains = build_lmcrec_file_chains(record_files_dir, from_ts, to_ts)
        lmcrec_files = chain_to_file_list(lmcrec_file_chains)

    if not lmcrec_files:
        print("No data found for that window", file=sys.stderr)
        return 0

    inst_tree, class_var_info, inst_max_size, first_ts, last_ts = (
        get_inventory_from_files(lmcrec_files, verbose=True)
    )

    # Check inst_tree class_var_info consistency:
    inst_tree_classes = set()
    for parent, children in inst_tree.items():
        if parent:
            inst_tree_classes.add(parent[1])
        if children:
            for child in children:
                inst_tree_classes.add(child[1])
    class_var_info_classes = set(class_var_info)
    missing = sorted(
        class_var_info_classes - inst_tree_classes, key=lambda c: c.lower()
    )
    assert not missing, f"Classes missing from inst_tree: {missing}"
    missing = sorted(
        inst_tree_classes - class_var_info_classes, key=lambda c: c.lower()
    )
    assert not missing, f"Classes missing from class_var_info: {missing}"

    if output_dir == "auto":
        output_dir = os.path.join(
            get_lmcrec_runtime(),
            "inventory",
            args.inst or "unknown",
            "--".join(
                [
                    format_ts(int(first_ts)) if first_ts is not None else "oldest",
                    format_ts(int(last_ts)) if last_ts is not None else "newest",
                ]
            ),
        )

    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        inventory_file = os.path.join(output_dir, INVENTORY_FILE_NAME)
        schema_file = os.path.join(output_dir, SCHEMA_FILE_NAME)
    else:
        inventory_file, schema_file = None, None

    fh = open(inventory_file, "wt") if inventory_file is not None else sys.stdout
    generate_inventory(
        inst_tree,
        class_var_info,
        inst_max_size,
        instance_inventory=instance_inventory,
        class_inventory=class_inventory,
        variable_inventory=variable_inventory,
        use_ascii=use_ascii,
        fh=fh,
    )
    if inventory_file is not None:
        fh.close()
        print(f"Inventory saved into {inventory_file!r}", file=sys.stderr)

    if schema_file is not None:
        with open(schema_file, "wt") as fh:
            generate_schema(class_var_info, inst_max_size=inst_max_size, fh=fh)
        print(f"Schema saved into {schema_file!r}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
