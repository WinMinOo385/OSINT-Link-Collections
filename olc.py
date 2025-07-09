import json, os, argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table

DATA_FILE = "links.json"
console = Console()

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
    table.add_column("#", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Link", style="blue")
    table.add_column("Description", style="white")

    for i, e in enumerate(data, 1):
        table.add_row(str(i), e["name"], e["type"], e["link"], e["description"][:50] + "...")
    console.print(table)

def edit(args):
    data = load_data()
    for e in data:
        if e["link"] == args.link:
            if args.name: e["name"] = args.name
            if args.desc: e["description"] = args.desc
            if args.type: e["type"] = args.type
            e["date_collected"] = datetime.now().isoformat()
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
    result = [e for e in data if
              keyword in e["name"].lower() or
              keyword in e["description"].lower() or
              keyword in e["type"].lower()]
    
    if not result:
        console.print(f"[yellow]No results for '{args.query}'[/yellow]")
        return

    table = Table(title=f"🔍 Search Results for '{args.query}'")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Link", style="blue")
    table.add_column("Description", style="white")

    for e in result:
        table.add_row(e["name"], e["type"], e["link"], e["description"][:50] + "...")
    console.print(table)

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
    p_add.set_defaults(func=add)

    # List
    p_ls = sub.add_parser("ls", help="List all links")
    p_ls.set_defaults(func=ls)

    # Edit
    p_edit = sub.add_parser("edit", help="Update an existing link")
    p_edit.add_argument("-l", "--link", required=True)
    p_edit.add_argument("-n", "--name")
    p_edit.add_argument("-d", "--desc")
    p_edit.add_argument("-t", "--type")
    p_edit.set_defaults(func=edit)

    # Remove
    p_rm = sub.add_parser("rm", help="Remove a link")
    p_rm.add_argument("-l", "--link", required=True)
    p_rm.set_defaults(func=rm)

    # Search
    p_find = sub.add_parser("find", help="Search entries by keyword")
    p_find.add_argument("query", help="Search keyword")
    p_find.set_defaults(func=find)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
