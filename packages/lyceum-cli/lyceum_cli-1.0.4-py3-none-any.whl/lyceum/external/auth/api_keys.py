"""
API key management commands
"""

import typer
from rich.console import Console

from ...shared.config import config
from ...shared.display import create_table, format_timestamp, truncate_id

console = Console()

# Import generated client modules
from lyceum_cloud_execution_api_client.api.api_keys import list_api_keys_api_v1_api_keys_get

api_keys_app = typer.Typer(name="api-keys", help="API key management")


@api_keys_app.command("list")
def list_api_keys():
    """List your API keys"""
    client = config.get_client()
    
    try:
        response = list_api_keys_api_v1_api_keys_get.sync_detailed(client=client)
        
        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            raise typer.Exit(1)
        
        api_keys = response.parsed if response.parsed else []
        
        if not api_keys:
            console.print("[dim]No API keys found[/dim]")
            return
        
        columns = [
            {"header": "ID", "style": "cyan", "no_wrap": True, "max_width": 12},
            {"header": "Name", "style": "yellow"},
            {"header": "Active", "style": "green"},
            {"header": "Created", "style": "dim"}
        ]
        
        table = create_table("API Keys", columns)
        
        for key in api_keys:
            table.add_row(
                truncate_id(key.id, 8),
                key.key_name, 
                "✅" if key.is_active else "❌",
                format_timestamp(getattr(key, 'created_at', None))
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)