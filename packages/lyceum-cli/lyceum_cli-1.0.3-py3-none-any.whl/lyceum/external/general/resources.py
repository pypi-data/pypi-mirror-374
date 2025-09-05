"""
Machine types and resources commands
"""

import typer
from rich.console import Console

from ...shared.config import config
from ...shared.display import create_table

console = Console()

# Import generated client modules
from lyceum_cloud_execution_api_client.api.machine_types import get_machine_types_api_v2_external_compute_machine_types_get

resources_app = typer.Typer(name="resources", help="Machine types and resources")


@resources_app.command("machine-types")
def list_machine_types():
    """List available machine types and their pricing"""
    client = config.get_client()
    
    try:
        response = get_machine_types_api_v2_external_compute_machine_types_get.sync_detailed(client=client)
        
        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            raise typer.Exit(1)
        
        data = response.parsed
        
        columns = [
            {"header": "Hardware Profile", "style": "cyan", "no_wrap": True},
            {"header": "Price per Hour", "style": "magenta"}
        ]
        
        table = create_table("Available Machine Types", columns)
        
        for machine_type in data.machine_types:
            table.add_row(
                machine_type.hardware_profile,
                f"${machine_type.price_per_hour}"
            )
        
        console.print(table)
        console.print(f"\n[dim]Found {data.count} machine types[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)