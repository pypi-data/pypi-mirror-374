import sys
import json
import argparse
import subprocess


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"


def get_change_symbol_and_color(actions):
    if "create" in actions and "delete" in actions:
        return f"{Colors.RED}-{Colors.RESET}/{Colors.GREEN}+{Colors.RESET}", "replace"
    elif "create" in actions:
        return f"{Colors.GREEN}+{Colors.RESET}", "create"
    elif "delete" in actions:
        return f"{Colors.RED}-{Colors.RESET}", "delete"
    elif "update" in actions:
        return f"{Colors.YELLOW}~{Colors.RESET}", "update"
    return "?", "unknown"


def format_value(value, is_sensitive):
    if is_sensitive:
        return f"{Colors.CYAN}(sensitive){Colors.RESET}"
    if value is None:
        return "null"
    return json.dumps(value, indent=None, separators=(",", ":"))


def get_detailed_changes(change_obj):
    before = change_obj.get("before", {}) or {}
    after = change_obj.get("after", {}) or {}
    before_sensitive = change_obj.get("before_sensitive", {}) or {}
    after_sensitive = change_obj.get("after_sensitive", {}) or {}

    all_keys = sorted(list(set(before.keys()) | set(after.keys())))
    diffs = []

    for key in all_keys:
        val_before = before.get(key)
        val_after = after.get(key)
        sensitive_before = before_sensitive.get(key, False)
        sensitive_after = after_sensitive.get(key, False)

        if val_before == val_after and sensitive_before == sensitive_after:
            continue

        detail = {"key": key}
        if key not in before:
            detail["action"] = "add"
            detail["after"] = format_value(val_after, sensitive_after)
        elif key not in after:
            detail["action"] = "remove"
            detail["before"] = format_value(val_before, sensitive_before)
        else:
            detail["action"] = "update"
            detail["before"] = format_value(val_before, sensitive_before)
            detail["after"] = format_value(val_after, sensitive_after)
        diffs.append(detail)
    return diffs


def get_resource_identifier(change_data):
    """Extract resource identifier from change data, checking name, arn, id in order."""
    after = change_data.get("after", {}) or {}
    before = change_data.get("before", {}) or {}

    for data in [after, before]:
        if not data:
            continue
        for key in [
            "name",
            "arn",
            "resource_id",
            "identifier",
            "dns_name",
            "endpoint",
            "url",
            "address",
            "id",
        ]:
            if key in data and data[key] is not None:
                return data[key]

    return None


def build_change_tree(plan_json, verbosity=0, show_ids=False):
    if "resource_changes" not in plan_json:
        print(
            f"{Colors.RED}Error: 'resource_changes' not found in the input. Is this a valid Terraform plan JSON?{Colors.RESET}",
            file=sys.stderr,
        )
        sys.exit(1)

    tree_root = {"modules": {}, "resources": []}

    for change in plan_json.get("resource_changes", []):
        change_data = change.get("change", {})
        actions = change_data.get("actions", [])
        if actions == ["no-op"]:
            continue

        symbol, action_type = get_change_symbol_and_color(actions)
        resource_id = f"{change['type']}.{change['name']}"
        details = []

        if verbosity > 0 and action_type in ["update", "replace"]:
            details = get_detailed_changes(change_data)

        resource_identifier = None
        if show_ids:
            resource_identifier = get_resource_identifier(change_data)

        resource_info = {
            "symbol": symbol,
            "id": resource_id,
            "details": details,
            "resource_identifier": resource_identifier,
        }

        current_level = tree_root
        module_address = change.get("module_address")
        if module_address:
            path_parts = [
                part for i, part in enumerate(module_address.split(".")) if i % 2 != 0
            ]
            for part in path_parts:
                if part not in current_level["modules"]:
                    current_level["modules"][part] = {"modules": {}, "resources": []}
                current_level = current_level["modules"][part]
        current_level["resources"].append(resource_info)

    return tree_root


def print_tree(node, verbosity, show_ids=False, name="root_module", prefix=""):
    print(f"{prefix}{Colors.BLUE}{Colors.BOLD}{name}{Colors.RESET}")

    sorted_resources = sorted(node.get("resources", []), key=lambda r: r["id"])
    sorted_modules = sorted(node.get("modules", {}).items())

    items = sorted_resources + list(sorted_modules)

    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")

        if isinstance(item, dict):
            display_text = f"{prefix}{connector}{item['symbol']} {item['id']}"
            if show_ids and item.get("resource_identifier"):
                display_text += f" ({item['resource_identifier']})"
            print(display_text)
            if verbosity > 0 and item["details"]:
                for j, detail in enumerate(item["details"]):
                    detail_is_last = j == len(item["details"]) - 1
                    detail_connector = "└── " if detail_is_last else "├── "

                    if verbosity == 1:
                        if detail["action"] == "add":
                            symbol = f"{Colors.GREEN}+"
                        elif detail["action"] == "remove":
                            symbol = f"{Colors.RED}-"
                        else:
                            symbol = f"{Colors.YELLOW}~"
                        print(
                            f"{child_prefix}{detail_connector}{symbol} {detail['key']}{Colors.RESET}"
                        )

                    elif verbosity >= 2:
                        if detail["action"] == "add":
                            print(
                                f"{child_prefix}{detail_connector}{Colors.GREEN}+ {detail['key']}: {detail['after']}{Colors.RESET}"
                            )
                        elif detail["action"] == "remove":
                            print(
                                f"{child_prefix}{detail_connector}{Colors.RED}- {detail['key']}: {detail['before']}{Colors.RESET}"
                            )
                        else:
                            print(
                                f"{child_prefix}{detail_connector}{Colors.YELLOW}~ {detail['key']}:{Colors.RESET} {detail['before']} -> {detail['after']}"
                            )

        else:
            module_name, sub_node = item
            print_tree(sub_node, verbosity, show_ids, module_name, prefix + connector)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a Terraform plan.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        help="Path to the Terraform plan (or JSON plan file).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity. -v shows changed attributes, -vv shows their values.",
    )
    parser.add_argument(
        "--show-ids",
        action="store_true",
        help="Display resource identifiers (name, arn, or id) in the summary.",
    )
    args = parser.parse_args()

    if args.file is None or args.file == sys.stdin:
        print(
            f"{Colors.RED}Error: No input file provided. Please provide a valid JSON file or stream.{Colors.RESET}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        plan_data = json.load(args.file)
    except UnicodeDecodeError:
        cmd = ["terraform", "show", "-json", args.file.name]
        args.file.close()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            plan_data = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(
                f"{Colors.RED}Error running 'terraform show -json': {e}{Colors.RESET}",
                file=sys.stderr,
            )
            sys.exit(1)
        except json.JSONDecodeError:
            print(
                f"{Colors.RED}Error: Output from 'terraform show -json' is not valid JSON.{Colors.RESET}",
                file=sys.stderr,
            )
            sys.exit(1)
    except json.JSONDecodeError:
        print(
            f"{Colors.RED}Error: Invalid JSON. Please provide a valid JSON file or stream.{Colors.RESET}",
            file=sys.stderr,
        )
        sys.exit(1)
    finally:
        if args.file is not sys.stdin:
            try:
                args.file.close()
            except Exception:
                pass

    change_tree = build_change_tree(plan_data, args.verbose, args.show_ids)
    print_tree(change_tree, args.verbose, args.show_ids)


if __name__ == "__main__":
    main()
