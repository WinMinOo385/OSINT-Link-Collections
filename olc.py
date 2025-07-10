#!/usr/bin/env python3
import json
import os
import argparse
import sys
import re
from datetime import datetime
from rich.console import Console
from rich.table import Table
from collections import defaultdict
from urllib.parse import urlparse
from cohere import ClientV2

# Configuration
DATA_FILE = "/home/redhoddie/Script/olc/links.json"
console = Console()

# Load API key from environment variable
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
if not COHERE_API_KEY:
    console.print("[red]✗ COHERE_API_KEY environment variable not set[/red]")
    console.print("[yellow]ℹ Run: export COHERE_API_KEY='your_key_here'[/yellow]")
    sys.exit(1)

# === Utility Functions ===
def normalize_url(domain_or_url):
    """Convert domain name or URL to proper URL format"""
    if not re.match(r'^https?://', domain_or_url):
        domain_or_url = f'https://{domain_or_url}'
    # Ensure URL is properly formatted
    parsed = urlparse(domain_or_url)
    if not parsed.netloc:
        domain_or_url = f'https://{parsed.path}'
    return domain_or_url

def extract_domain(url):
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc or parsed.path.split('/')[0]

def load_data():
    """Load data with proper error handling"""
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        with open(DATA_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            content = re.sub(r',\s*([}\]])', r'\1', content)
            return json.loads(content)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Error loading data: {str(e)}[/red]")
        return []
    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {str(e)}[/red]")
        return []

def save_data(data):
    """Save data with proper formatting"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add newline at end of file
    except Exception as e:
        console.print(f"[red]✗ Error saving data: {str(e)}[/red]")

def analyze_website(link):
    """Use Cohere AI to analyze and classify the website"""
    client = ClientV2(api_key=COHERE_API_KEY)
    
    prompt = f"""Act as a website classifier and OSINT metadata formatter. Analyze this website: {link}

Return a structured JSON object with these rules:
1. Replace spaces in values with dashes.
2. rating_count must be 0.
3. cost must be "free", "paid", or "paid,free".
4. api_available must be true or false.
5. Use lowercase for all values.
6. Include relevant user roles.

Format:
```json
{{
  "link": "<link>",
  "name": "<name>",
  "description": "<description>",
  "type": "<main-type>",
  "subtypes": ["subtype1"],
  "tags": ["tag1"],
  "roles": ["role1"],
  "language": "en",
  "cost": "free",
  "requires_account": true,
  "data_types": ["data-type"],
  "api_available": false,
  "metrics": {{"rating": 0.0, "rating_count": 0}}
}}
```"""

    try:
        response = client.chat_stream(
            model="command-a-03-2025",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            temperature=0.3
        )
        
        # Collect the full response
        full_response = ""
        for event in response:
            if event.type == "content-delta":
                full_response += event.delta.message.content.text
        
        # Extract JSON from response
        json_start = full_response.find('{')
        json_end = full_response.rfind('}') + 1
        json_str = full_response[json_start:json_end]
        
        return json.loads(json_str)
    except Exception as e:
        console.print(f"[red]✗ Error analyzing website: {str(e)}[/red]")
        return None

# === Core Functions ===
def add(args):
    data = load_data()
    
    if not args.link and not sys.stdin.isatty():
        args.link = sys.stdin.read().strip()
    
    if not args.link:
        console.print("[red]✗ No domain or URL provided[/red]")
        return
    
    normalized_url = normalize_url(args.link)
    domain = extract_domain(normalized_url)
        
    # Check if domain already exists (compare domains, not full URLs)
    if any(extract_domain(e['link']) == domain for e in data):
        console.print(f"[red]✗ Entry for {domain} already exists[/red]")
        return

    # AI analysis when only domain/URL is provided
    if args.link and not args.name and not args.desc and not args.type:
        console.print(f"[yellow]⚡ Analyzing {normalized_url} with AI...[/yellow]")
        ai_data = analyze_website(normalized_url)
        if ai_data:
            args.name = ai_data.get('name', '')
            args.desc = ai_data.get('description', '')
            args.type = ai_data.get('type', '')
            args.sub = ai_data.get('subtypes', [])
            args.tags = ",".join(ai_data.get('tags', []))
            args.roles = ",".join(ai_data.get('roles', []))
            args.lang = ai_data.get('language', 'en')
            args.cost = ai_data.get('cost', 'free')
            args.account = str(ai_data.get('requires_account', False))
            args.data_types = ",".join(ai_data.get('data_types', []))
            args.api = str(ai_data.get('api_available', False))
            args.rating = str(ai_data.get('metrics', {}).get('rating', 0.0))

    entry = {
        "link": normalized_url,
        "name": args.name or domain,
        "description": args.desc or f"Website for {domain}",
        "type": args.type or "website",
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
    console.print(f"[green]✓ Entry added for {normalized_url}[/green]")

def ls(args):
    data = load_data()
    if not data:
        console.print("[yellow]No entries found.[/yellow]")
        return

    table = Table(title="🔗 OSINT Useful Links")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan", width=20)
    table.add_column("URL", style="blue", width=30, overflow="fold")
    table.add_column("Type", style="magenta", width=12)
    table.add_column("Tags", style="yellow", width=20)
    table.add_column("Rating", style="green", width=8)

    for i, e in enumerate(data, 1):
        tags = ", ".join(e.get("tags", []))[:18] + "..." if e.get("tags") else ""
        rating = f"{e.get('metrics', {}).get('rating', 0):.1f}★"
        table.add_row(
            str(i), 
            e["name"], 
            e["link"],
            e["type"], 
            tags,
            rating
        )
    console.print(table)

def edit(args):
    data = load_data()
    search_url = normalize_url(args.link)
    search_domain = extract_domain(search_url)
    
    for entry in data:
        if extract_domain(entry["link"]) == search_domain:
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
            console.print(f"[blue]~ Updated entry for {entry['link']}[/blue]")
            return
    console.print(f"[red]✗ No entry found for {search_url}[/red]")

def rm(args):
    data = load_data()
    
    if not args.link and not sys.stdin.isatty():
        args.link = sys.stdin.read().strip()
    
    if not args.link:
        console.print("[red]✗ No domain or URL provided[/red]")
        return

    search_url = normalize_url(args.link)
    search_domain = extract_domain(search_url)
    
    new_data = [e for e in data if extract_domain(e["link"]) != search_domain]
    if len(new_data) == len(data):
        console.print(f"[red]✗ No entry found for {search_url}[/red]")
    else:
        save_data(new_data)
        console.print(f"[red]- Deleted entry for {search_url}[/red]")

def find(args):
    data = load_data()
    keyword = args.query.lower()
    results = []

    for e in data:
        domain = extract_domain(e["link"])
        if (keyword in e["name"].lower() or
            keyword in e["link"].lower() or
            keyword in domain.lower() or
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
    table.add_column("URL", style="blue", width=30, overflow="fold")
    table.add_column("Type", style="magenta", width=12)
    table.add_column("Rating", style="green", width=8)

    for e in results:
        rating = f"{e.get('metrics', {}).get('rating', 0):.1f}★"
        table.add_row(
            e["name"], 
            e["link"],
            e["type"], 
            rating
        )
    console.print(table)

def view_details(args):
    data = load_data()
    search_url = normalize_url(args.link)
    search_domain = extract_domain(search_url)
    
    for entry in data:
        if extract_domain(entry["link"]) == search_domain:
            console.print(f"\n[bold cyan]{entry['name']}[/bold cyan]")
            console.print(f"[blue]{entry['link']}[/blue]")
            console.print(f"\n[bold]Description:[/bold] {entry['description']}")
            
            details = Table(show_header=False)
            details.add_column("Field", style="cyan")
            details.add_column("Value", style="white")
            
            details.add_row("URL", entry["link"])
            details.add_row("Type", entry["type"])
            details.add_row("Subtypes", ", ".join(entry.get("subtypes", [])))
            details.add_row("Tags", ", ".join(entry.get("tags", [])))
            details.add_row("Roles", ", ".join(entry.get("roles", []))) 
            details.add_row("Language", entry.get("language", "en"))
            details.add_row("Cost", entry.get("cost", "unknown"))
            details.add_row("Requires Account", "Yes" if entry.get("requires_account") else "No")
            details.add_row("API Available", "Yes" if entry.get("api_available") else "No")
            details.add_row("Rating", f"{entry.get('metrics', {}).get('rating', 0):.1f} (based on {entry.get('metrics', {}).get('rating_count', 0)} reviews)")
            details.add_row("Data Types", ", ".join(entry.get("data_types", [])))
            details.add_row("Date Collected", entry["date_collected"])
            details.add_row("Last Updated", entry.get("date_updated", "never"))
            
            console.print(details)
            return
    console.print(f"[red]✗ No entry found for {search_url}[/red]")

# === Main Function ===
def main():
    parser = argparse.ArgumentParser(description="🔗 OSINT Link Manager with AI Classification")
    sub = parser.add_subparsers(title="Commands")

    # Add command
    p_add = sub.add_parser("add", help="Add new link (AI auto-fill when only domain/URL provided)")
    p_add.add_argument("-l", "--link", help="Domain name (example.com) or URL (https://example.com)")
    p_add.add_argument("-n", "--name", help="Name of the resource")
    p_add.add_argument("-d", "--desc", help="Description")
    p_add.add_argument("-t", "--type", help="Main type/category")
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

    # List command
    p_ls = sub.add_parser("ls", help="List all links")
    p_ls.set_defaults(func=ls)

    # Edit command
    p_edit = sub.add_parser("edit", help="Edit a link")
    p_edit.add_argument("-l", "--link", required=True, help="Domain name (example.com) or URL (https://example.com) to edit")
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

    # Remove command
    p_rm = sub.add_parser("rm", help="Remove a link")
    p_rm.add_argument("-l", "--link", help="Domain name (example.com) or URL (https://example.com) to remove")
    p_rm.set_defaults(func=rm)

    # Find command
    p_find = sub.add_parser("find", help="Search links")
    p_find.add_argument("query", help="Search term")
    p_find.set_defaults(func=find)

    # View command
    p_view = sub.add_parser("view", help="View detailed information")
    p_view.add_argument("-l", "--link", required=True, help="Domain name (example.com) or URL (https://example.com) to view")
    p_view.set_defaults(func=view_details)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()