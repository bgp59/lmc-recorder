#! /usr/bin/env python3

description = """ 
Check REST response(s), like for instance those collected by snap-samples.sh,
for internal inconsistencies:
    * Critical, lmcrec will exit upon detecting any the of following:
        * duplicated instances
        * same variables from the same class but with different types
    * Silently ignored:
        * duplicated (within the instance) variables; the last value is the one
          that will populated the state cache during playback.
    * FYI:
        * missing variables from instances with the same class
"""

import argparse
import sys
from typing import Dict, List

from tabulate import SEPARATING_LINE, tabulate

from .help_formatter import CustomWidthFormatter
from .lmcrec_check_consistency import load_sample_file


def box(title, file=sys.stdout):
    h_line = "+" + "-" * (len(title) + 2) + "+"
    print(h_line, file=file)
    print("| " + title + " |", file=file)
    print(h_line, file=file)
    print(file=file)


def star(title, file=sys.stdout):
    h_line = "*" * (len(title) + 4)
    print(h_line, file=file)
    print("* " + title + " *", file=file)
    print(h_line, file=file)
    print(file=file)


def underline(title, file=sys.stdout):
    print(title, file=file)
    print("=" * len(title), file=file)
    print(file=file)


def check_instances(inst_list: List[Dict], missing_variables: bool = False):
    found_inst = set()
    dup_inst = set()
    dup_vars = dict()  # [class][var] = set(instances)
    class_var_inventory = dict()  # [class][var][type] = set(instances)
    missing_vars = dict()  # [class][var] = set(instances)

    tally = dict(
        inst_count=0,
        var_count=0,
        duplicated_inst_count=0,
        inconsistent_var_count=0,
        duplicated_var_count=0,
        missing_var_count=0,
    )

    def load_inventory(inst_list: List[Dict]):
        if not inst_list:
            return

        for inst in inst_list:
            tally["inst_count"] += 1
            inst_name = inst["Instance"]
            if inst_name in found_inst:
                dup_inst.add(inst_name)
            else:
                found_inst.add(inst_name)
            class_name = inst["Class"]
            if class_name not in class_var_inventory:
                class_var_inventory[class_name] = dict()

            class_vars = set()
            for var in inst["Variables"]:
                tally["var_count"] += 1
                var_name, var_type = var["Name"], var["Type"]
                if var_name in class_vars:
                    tally["duplicated_var_count"] += 1
                    if class_name not in dup_vars:
                        dup_vars[class_name] = {var_name: set([inst_name])}
                    elif var_name not in dup_vars[class_name]:
                        dup_vars[class_name][var_name] = set([inst_name])
                    else:
                        dup_vars[class_name][var_name].add(inst_name)
                else:
                    class_vars.add(var_name)
                if var_name not in class_var_inventory[class_name]:
                    class_var_inventory[class_name][var_name] = {
                        var_type: set([inst_name])
                    }
                else:
                    if var_type not in class_var_inventory[class_name][var_name]:
                        class_var_inventory[class_name][var_name][var_type] = set(
                            [inst_name]
                        )
                    else:
                        class_var_inventory[class_name][var_name][var_type].add(
                            inst_name
                        )

            load_inventory(inst["Children"])

    def load_missing_vars(inst_list: List[Dict]):
        if not inst_list:
            return

        for inst in inst_list:
            inst_name = inst["Instance"]
            class_name = inst["Class"]
            inst_vars = set(v["Name"] for v in inst["Variables"])
            for var_name in class_var_inventory[class_name]:
                if var_name not in inst_vars:
                    tally["missing_var_count"] += 1
                    if class_name not in missing_vars:
                        missing_vars[class_name] = {var_name: set([inst_name])}
                    elif var_name not in missing_vars[class_name]:
                        missing_vars[class_name][var_name] = set([inst_name])
                    else:
                        missing_vars[class_name][var_name].add(inst_name)

            load_missing_vars(inst["Children"])

    load_inventory(inst_list)
    if missing_variables:
        load_missing_vars(inst_list)

    if dup_inst:
        underline("Duplicate Instances (Critical)")
        for inst in sorted(dup_inst):
            print(f"  f{inst!r}")
        print()

    rows = []
    for class_name in sorted(class_var_inventory):
        for var_name in sorted(class_var_inventory[class_name]):
            inst_list_by_type = class_var_inventory[class_name][var_name]
            if len(inst_list_by_type) == 1:
                continue
            tally["inconsistent_var_count"] += 1
            type_col, inst_list_col = "", ""
            for var_type in sorted(inst_list_by_type):
                inst_list = sorted(inst_list_by_type[var_type])
                if type_col != "":
                    type_col += "\n"
                type_col += var_type + "\n" * (len(inst_list) - 1)
                if inst_list_col != "":
                    inst_list_col += "\n"
                inst_list_col += "\n".join(inst_list)
            rows.append([class_name, var_name, type_col, inst_list_col])
            rows.append(SEPARATING_LINE)
    if rows:
        underline("Inconsistent Variables (Critical)")
        print(tabulate(rows, headers=["Class", "Variable", "Type(s)", "Instance(s)"]))
        print()

    # Merge the variables by instance list and classes:
    dup_var_by_inst_list_class = dict()
    for class_name in dup_vars:
        for var_name, inst_set in dup_vars[class_name].items():
            inst_list_class_key = ("\n".join(sorted(inst_set)), class_name)
            if inst_list_class_key not in dup_var_by_inst_list_class:
                dup_var_by_inst_list_class[inst_list_class_key] = [var_name]
            else:
                dup_var_by_inst_list_class[inst_list_class_key].append(var_name)
    rows = []
    for inst_list_class, var_list in dup_var_by_inst_list_class.items():
        inst_list, class_name = inst_list_class
        rows.append([class_name, "\n".join(var_list), inst_list])
        rows.append(SEPARATING_LINE)
    if rows:
        underline("Duplicate Variables (they should be avoided at playback)")
        print(tabulate(rows, headers=["Class", "Variable(s)", "Instance(s)"]))
        print()

    if missing_variables:
        # Merge the variables by instance list and classes:
        missing_var_by_inst_list_class = dict()
        for class_name in missing_vars:
            for var_name, inst_set in missing_vars[class_name].items():
                inst_list_class_key = ("\n".join(sorted(inst_set)), class_name)
                if inst_list_class_key not in missing_var_by_inst_list_class:
                    missing_var_by_inst_list_class[inst_list_class_key] = [var_name]
                else:
                    missing_var_by_inst_list_class[inst_list_class_key].append(var_name)
        rows = []
        for inst_list_class, var_list in missing_var_by_inst_list_class.items():
            inst_list, class_name = inst_list_class
            rows.append([class_name, "\n".join(var_list), inst_list])
            rows.append(SEPARATING_LINE)
        if rows:
            underline("Missing Variables (FYI)")
            print(tabulate(rows, headers=["Class", "Variable(s)", "Instance(s)"]))
            print()

    rows = []
    for disp_name, tally_key in [
        ("Inst", "inst_count"),
        ("Var", "var_count"),
        ("Duplicate Inst", "duplicated_inst_count"),
        ("Inconsistent Var", "inconsistent_var_count"),
        ("Duplicate Var", "duplicated_var_count"),
    ]:
        rows.append([disp_name, tally[tally_key]])
    if missing_variables:
        rows.append(
            [
                "Missing Var",
                tally["missing_var_count"],
                f'{tally["missing_var_count"]/tally["var_count"] * 100:.1f}%',
            ]
        )
    underline("Totals")
    print(tabulate(rows, headers=["Tally", "Total", "Obs"]))
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument(
        "-z",
        "--inflate",
        action="store_true",
        help="""Assume deflate(d) content even if the file does not end in .gz
             and no headers file can be found""",
    )
    parser.add_argument(
        "-m",
        "--missing-variables",
        action="store_true",
        help="""Add missing variables from instances that share the same
             class to the report""",
    )
    parser.add_argument("rest_json_file", nargs="+")
    args = parser.parse_args()

    for rest_json_file in args.rest_json_file:
        star(rest_json_file)
        inst_list, _ = load_sample_file(rest_json_file, force_compressed=args.inflate)
        check_instances(inst_list, args.missing_variables)


if __name__ == "__main__":
    sys.exit(main())
