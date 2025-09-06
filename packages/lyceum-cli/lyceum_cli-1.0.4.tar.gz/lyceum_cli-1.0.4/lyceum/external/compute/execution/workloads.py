"""
Workload management commands: list jobs, abort, history
"""

import typer
from rich.console import Console

from ....shared.config import config
from ....shared.display import create_table, format_timestamp, truncate_id

console = Console()

# Import generated client modules
from lyceum_cloud_execution_api_client.api.workload_management import list_non_complete_executions_api_v1_workloads_list_get, abort_execution_api_v1_workloads_abort_execution_id_post
from lyceum_cloud_execution_api_client.api.billing_credits import get_execution_history_api_v2_external_billing_history_get

workloads_app = typer.Typer(name="workloads", help="Workload management commands")


@workloads_app.command("list")
def list_jobs():
    """List currently running executions"""
    client = config.get_client()
    
    try:
        response = list_non_complete_executions_api_v1_workloads_list_get.sync_detailed(client=client)
        
        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            raise typer.Exit(1)
        
        jobs = response.parsed if response.parsed else []
        
        if not jobs:
            console.print("[dim]No running jobs found[/dim]")
            return
        
        columns = [
            {"header": "ID", "style": "cyan", "no_wrap": True, "max_width": 12},
            {"header": "Status", "style": "yellow"},
            {"header": "Type", "style": "magenta"},
            {"header": "Started", "style": "dim"}
        ]
        
        table = create_table("Running Jobs", columns)
        
        for job in jobs:
            table.add_row(
                truncate_id(job.execution_id, 8),
                job.status,
                job.execution_type,
                format_timestamp(getattr(job, 'created_at', None))
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@workloads_app.command("abort")
def abort(
    execution_id: str = typer.Argument(..., help="Execution ID to abort"),
):
    """Abort a running execution"""
    client = config.get_client()
    
    try:
        response = abort_execution_api_v1_workloads_abort_execution_id_post.sync_detailed(
            client=client, 
            execution_id=execution_id
        )
        
        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            raise typer.Exit(1)
        
        console.print(f"[green]✅ Execution {truncate_id(execution_id, 8)} aborted[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@workloads_app.command("history")
def history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of executions to show"),
):
    """Show your execution history"""
    client = config.get_client()
    
    try:
        response = get_execution_history_api_v2_external_billing_history_get.sync_detailed(client=client)
        
        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            raise typer.Exit(1)
        
        executions = response.parsed[:limit] if response.parsed else []
        
        if not executions:
            console.print("[dim]No execution history found[/dim]")
            return
        
        columns = [
            {"header": "ID", "style": "cyan", "no_wrap": True, "max_width": 12},
            {"header": "Status", "style": "green"},
            {"header": "Type", "style": "yellow"},
            {"header": "Machine", "style": "magenta"},
            {"header": "Created", "style": "dim"}
        ]
        
        table = create_table("Execution History", columns)
        
        for execution in executions:
            table.add_row(
                truncate_id(execution.execution_id, 8),
                execution.status,
                execution.execution_type,
                getattr(execution, 'hardware_profile', 'N/A'),
                format_timestamp(getattr(execution, 'created_at', None))
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)