import json
import os
import argparse
import sys
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
        json.dump(data, f, indent=2, ensure_ascii=False)

# === CRUD ===
def add(args):
    data = load_data()
    
    # Handle stdin if no link provided
    if not args.link and not sys.stdin.isatty():
        args.link = sys.stdin.read().strip()
    
    if not args.link:
        console.print("[red]✗ No link provided[/red]")
        return
        
    if any(e['link'] == args.link for e in data):
        console.print(f"[red]✗ Entry for {args.link} already exists[/red]")
        return

    entry = {
        "link": args.link,
        "name": args.name,
        "description": args.desc,
        "type": args.type,
        "subtypes": args.sub or [],
        "tags": args.tags.split(",") if args.tags else [],
        "roles": args.roles.split(",") if args.roles else [],
        "language": args.lang or "en",
        "cost": args.cost or "free",
        "requires_account": args.account.lower() == "true" if args.account else False,
        "data_types": args.data_types.split(",") if args.data_types else [],
        "api_available": args.api.lower() == "true" if args.api else False,
        "metrics": {
            "rating": float(args.rating) if args.rating else 0.0,
            "rating_count": int(args.rating_count) if args.rating_count else 0
        },
        "date_collected": datetime.now().isoformat(),
        "date_updated": datetime.now().isoformat()
    }
    
    data.append(entry)
    save_data(data)
    console.print(f"[green]✓ Entry added for {args.name}[/green]")

def ls(args):
    data = load_data()
    if not data:
        console.print("[yellow]No entries found.[/yellow]")
        return

    table = Table(title="🔗 OSINT Useful Links")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Type", style="magenta", width=12)
    table.add_column("Tags", style="yellow", width=20)
    table.add_column("Cost", style="green", width=8)
    table.add_column("Rating", style="blue", width=8)
    table.add_column("Link", style="blue", overflow="fold")

    for i, e in enumerate(data, 1):
        tags = ", ".join(e.get("tags", []))[:18] + "..." if e.get("tags") else ""
        rating = f"{e.get('metrics', {}).get('rating', 0):.1f}★"
        table.add_row(
            str(i), 
            e["name"], 
            e["type"], 
            tags,
            e.get("cost", ""),
            rating,
            e["link"]
        )
    console.print(table)

def edit(args):
    data = load_data()
    for entry in data:
        if entry["link"] == args.link:
            if args.name: entry["name"] = args.name
            if args.desc: entry["description"] = args.desc
            if args.type: entry["type"] = args.type
            if args.sub: entry["subtypes"] = args.sub
            if args.tags: entry["tags"] = args.tags.split(",")
            if args.roles: entry["roles"] = args.roles.split(",")  
            if args.rating: entry["metrics"]["rating"] = float(args.rating)
            if args.rating_count: entry["metrics"]["rating_count"] = int(args.rating_count)
            if args.cost: entry["cost"] = args.cost
            if args.lang: entry["language"] = args.lang
            if args.account: entry["requires_account"] = args.account.lower() == "true"
            if args.api: entry["api_available"] = args.api.lower() == "true"
            entry["date_updated"] = datetime.now().isoformat()
            save_data(data)
            console.print(f"[blue]~ Updated entry for {args.link}[/blue]")
            return
    console.print(f"[red]✗ No entry found for {args.link}[/red]")

def rm(args):
    data = load_data()
    
    if not args.link and not sys.stdin.isatty():
        args.link = sys.stdin.read().strip()
    
    if not args.link:
        console.print("[red]✗ No link provided[/red]")
        return

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
        if (keyword in e["name"].lower() or
            keyword in e["description"].lower() or
            keyword in e["type"].lower() or
            keyword in " ".join(e.get("subtypes", [])).lower() or
            keyword in " ".join(e.get("tags", [])).lower() or
            keyword in " ".join(e.get("roles", [])).lower()):
            results.append(e)

    if not results:
        console.print(f"[yellow]No results for '{args.query}'[/yellow]")
        return

    table = Table(title=f"🔍 Search Results for '{args.query}'")
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Type", style="magenta", width=12)
    table.add_column("Tags", style="yellow", width=20)
    table.add_column("Rating", style="blue", width=8)
    table.add_column("Link", style="blue", overflow="fold")

    for e in results:
        tags = ", ".join(e.get("tags", []))[:18] + "..." if e.get("tags") else ""
        rating = f"{e.get('metrics', {}).get('rating', 0):.1f}★"
        table.add_row(
            e["name"], 
            e["type"], 
            tags,
            rating,
            e["link"]
        )
    console.print(table)

def view_details(args):
    data = load_data()
    for entry in data:
        if entry["link"] == args.link:
            console.print(f"\n[bold cyan]{entry['name']}[/bold cyan]")
            console.print(f"[blue]{entry['link']}[/blue]")
            console.print(f"\n[bold]Description:[/bold] {entry['description']}")
            
            details = Table(show_header=False)
            details.add_column("Field", style="cyan")
            details.add_column("Value", style="white")
            
            details.add_row("Type", entry["type"])
            details.add_row("Subtypes", ", ".join(entry.get("subtypes", [])))
            details.add_row("Tags", ", ".join(entry.get("tags", [])))
            details.add_row("Roles", ", ".join(entry.get("roles", []))) 
            details.add_row("Language", entry.get("language", "en"))
            details.add_row("Cost", entry.get("cost", "unknown"))
            details.add_row("Requires Account", "Yes" if entry.get("requires_account") else "Null")
            details.add_row("API Available", "Yes" if entry.get("api_available") else "Null")
            details.add_row("Rating", f"{entry.get('metrics', {}).get('rating', 0):.1f} (based on {entry.get('metrics', {}).get('rating_count', 0)} reviews)")
            details.add_row("Data Types", ", ".join(entry.get("data_types", [])))
            details.add_row("Date Collected", entry["date_collected"])
            details.add_row("Last Updated", entry.get("date_updated", "never"))
            
            console.print(details)
            return
    console.print(f"[red]✗ No entry found for {args.link}[/red]")

# === CLI Setup ===
def main():
    parser = argparse.ArgumentParser(description="🔗 OSINT Link Manager")
    sub = parser.add_subparsers(title="Commands")

    # Add
    p_add = sub.add_parser("add", help="Add new link")
    p_add.add_argument("-l", "--link", help="Link URL (or read from stdin)")
    p_add.add_argument("-n", "--name", required=True, help="Name of the resource")
    p_add.add_argument("-d", "--desc", required=True, help="Description")
    p_add.add_argument("-t", "--type", required=True, help="Main type/category")
    p_add.add_argument("--sub", nargs="+", help="One or more subtypes")
    p_add.add_argument("--tags", help="Comma-separated tags")
    p_add.add_argument("--roles", help="Comma-separated user roles")  
    p_add.add_argument("--lang", help="Language (default: en)")
    p_add.add_argument("--cost", help="Cost model (free/freemium/paid)")
    p_add.add_argument("--account", help="Requires account (true/false)")
    p_add.add_argument("--data_types", help="Comma-separated data types")
    p_add.add_argument("--api", help="API available (true/false)")
    p_add.add_argument("--rating", help="Rating (0-5)")
    p_add.add_argument("--rating_count", help="Number of ratings")
    p_add.set_defaults(func=add)

    # List
    p_ls = sub.add_parser("ls", help="List all links")
    p_ls.set_defaults(func=ls)

    # Edit
    p_edit = sub.add_parser("edit", help="Edit a link")
    p_edit.add_argument("-l", "--link", required=True, help="Link to edit")
    p_edit.add_argument("-n", "--name", help="New name")
    p_edit.add_argument("-d", "--desc", help="New description")
    p_edit.add_argument("-t", "--type", help="New type")
    p_edit.add_argument("--sub", nargs="+", help="New subtypes")
    p_edit.add_argument("--tags", help="Comma-separated tags")
    p_edit.add_argument("--roles", help="Comma-separated user roles") 
    p_edit.add_argument("--rating", help="New rating (0-5)")
    p_edit.add_argument("--rating_count", help="New rating count")
    p_edit.add_argument("--cost", help="New cost model")
    p_edit.add_argument("--lang", help="New language")
    p_edit.add_argument("--account", help="New requires account (true/false)")
    p_edit.add_argument("--api", help="New API available (true/false)")
    p_edit.set_defaults(func=edit)

    # Remove
    p_rm = sub.add_parser("rm", help="Remove a link")
    p_rm.add_argument("-l", "--link", help="Link URL to remove (or read from stdin)")
    p_rm.set_defaults(func=rm)

    # Find
    p_find = sub.add_parser("find", help="Search links")
    p_find.add_argument("query", help="Search term")
    p_find.set_defaults(func=find)

    # View Details
    p_view = sub.add_parser("view", help="View detailed information")
    p_view.add_argument("-l", "--link", required=True, help="Link to view")
    p_view.set_defaults(func=view_details)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()