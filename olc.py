import json, os, argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table
from collections import defaultdict

DATA_FILE = "links.json"
console = Console()

# === Utilities ===
def load_data():
    return json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === CRUD ===
def add(args):
    data = load_data()
    if any(e['link'] == args.link for e in data):
        console.print(f"[red]✗ Entry for {args.link} already exists[/red]")
        return

    data.append({
        "link": args.link,
        "name": args.name,
        "description": args.desc,
        "type": args.type,
        "subtypes": args.sub or [],
        "date_collected": datetime.now().isoformat()
    })
    save_data(data)
    console.print(f"[green]✓ Entry added for {args.name}[/green]")

def ls(args):
    data = load_data()
    if not data:
        console.print("[yellow]No entries found.[/yellow]")
        return

    table = Table(title="🔗 OSINT Useful Links")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan", width=25)
    table.add_column("Type", style="magenta", width=10)
    table.add_column("Subtypes", style="yellow", width=20)
    table.add_column("Link", style="blue", overflow="fold")
    table.add_column("Description", style="white")

    for i, e in enumerate(data, 1):
        subtypes = ", ".join(e.get("subtypes", []))
        table.add_row(str(i), e["name"], e["type"], subtypes, e["link"], e["description"][:50] + "...")
    console.print(table)

def edit(args):
    data = load_data()
    for entry in data:
        if entry["link"] == args.link:
            if args.name: entry["name"] = args.name
            if args.desc: entry["description"] = args.desc
            if args.type: entry["type"] = args.type
            if args.sub: entry["subtypes"] = args.sub
            entry["date_collected"] = datetime.now().isoformat()
            save_data(data)
            console.print(f"[blue]~ Updated entry for {args.link}[/blue]")
            return
    console.print(f"[red]✗ No entry found for {args.link}[/red]")

def rm(args):
    data = load_data()
    new_data = [e for e in data if e["link"] != args.link]
    if len(new_data) == len(data):
        console.print(f"[red]✗ No entry found for {args.link}[/red]")
    else:
        save_data(new_data)
        console.print(f"[red]- Deleted entry for {args.link}[/red]")

def find(args):
    data = load_data()
    keyword = args.query.lower()
    results = []

    for e in data:
        if (
            keyword in e["name"].lower()
            or keyword in e["description"].lower()
            or keyword in e["type"].lower()
            or keyword in " ".join(e.get("subtypes", [])).lower()
        ):
            results.append(e)

    if not results:
        console.print(f"[yellow]No results for '{args.query}'[/yellow]")
        return

    table = Table(title=f"🔍 Search Results for '{args.query}'")
    table.add_column("Name", style="cyan", width=25)
    table.add_column("Type", style="magenta", width=10)
    table.add_column("Subtypes", style="yellow", width=20)
    table.add_column("Link", style="blue", overflow="fold")
    table.add_column("Description", style="white")

    for e in results:
        subtypes = ", ".join(e.get("subtypes", []))
        table.add_row(e["name"], e["type"], subtypes, e["link"], e["description"][:50] + "...")
    console.print(table)

def grouped_ls(args):
    data = load_data()
    if not data:
        console.print("[yellow]No entries found.[/yellow]")
        return

    grouped = defaultdict(lambda: defaultdict(list))
    for e in data:
        t = e.get("type", "unknown")
        for sub in e.get("subtypes", ["general"]):
            grouped[t][sub].append(e)

    for t in grouped:
        console.print(f"[bold cyan]{t.upper()}[/bold cyan]")
        for sub in grouped[t]:
            console.print(f"  [magenta]{sub}[/magenta]")
            for e in grouped[t][sub]:
                console.print(f"    [green]- {e['name']}[/green] ([blue]{e['link']}[/blue])")

# === CLI Setup ===
def main():
    parser = argparse.ArgumentParser(description="🔗 OSINT Link Manager")
    sub = parser.add_subparsers(title="Commands")

    # Add
    p_add = sub.add_parser("add", help="Add new link")
    p_add.add_argument("-l", "--link", required=True)
    p_add.add_argument("-n", "--name", required=True)
    p_add.add_argument("-d", "--desc", required=True)
    p_add.add_argument("-t", "--type", required=True)
    p_add.add_argument("--sub", nargs="+", help="One or more subtypes")
    p_add.set_defaults(func=add)

    # List
    p_ls = sub.add_parser("ls", help="List all links")
    p_ls.set_defaults(func=ls)

    # Edit
    p_edit = sub.add_parser("edit", help="Edit a link")
    p_edit.add_argument("-l", "--link", required=True)
    p_edit.add_argument("-n", "--name")
    p_edit.add_argument("-d", "--desc")
    p_edit.add_argument("-t", "--type")
    p_edit.add_argument("--sub", nargs="+")
    p_edit.set_defaults(func=edit)

    # Remove
    p_rm = sub.add_parser("rm", help="Remove a link")
    p_rm.add_argument("-l", "--link", required=True)
    p_rm.set_defaults(func=rm)

    # Find
    p_find = sub.add_parser("find", help="Search links")
    p_find.add_argument("query")
    p_find.set_defaults(func=find)

    # Grouped
    p_grouped = sub.add_parser("grouped", help="Grouped view by type/subtypes")
    p_grouped.set_defaults(func=grouped_ls)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
