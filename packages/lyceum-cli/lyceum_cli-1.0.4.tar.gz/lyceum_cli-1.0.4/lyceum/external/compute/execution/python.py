"""
Python execution commands
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from ....shared.config import config
from ....shared.streaming import stream_execution_output

console = Console()

# Import generated client modules
from lyceum_cloud_execution_api_client.api.code_execution import start_execution_api_v2_external_compute_execution_run_post
from lyceum_cloud_execution_api_client.models import CodeExecution

python_app = typer.Typer(name="python", help="Python execution commands")


@python_app.command("run")
def run_python(
    code_or_file: str = typer.Argument(..., help="Python code to execute or path to Python file"),
    machine_type: str = typer.Option("cpu", "--machine", "-m", help="Machine type (cpu, a100, h100, etc.)"),
    timeout: int = typer.Option(60, "--timeout", "-t", help="Execution timeout in seconds"),
    file_name: Optional[str] = typer.Option(None, "--file-name", "-f", help="Name for the execution"),
    requirements: Optional[str] = typer.Option(None, "--requirements", "-r", help="Requirements file path or pip requirements string"),
    imports: Optional[list[str]] = typer.Option(None, "--import", help="Pre-import modules (can be used multiple times)"),
):
    """Execute Python code or file on Lyceum Cloud"""
    client = config.get_client()
    
    try:
        # Check if it's a file path
        code_to_execute = code_or_file
        if Path(code_or_file).exists():
            console.print(f"[dim]Reading code from file: {code_or_file}[/dim]")
            with open(code_or_file, 'r') as f:
                code_to_execute = f.read()
            # Use filename as execution name if not provided
            if not file_name:
                file_name = Path(code_or_file).name
        
        # Handle requirements
        requirements_content = None
        if requirements:
            # Check if it's a file path
            if Path(requirements).exists():
                console.print(f"[dim]Reading requirements from file: {requirements}[/dim]")
                with open(requirements, 'r') as f:
                    requirements_content = f.read()
            else:
                # Treat as direct pip requirements string
                requirements_content = requirements
        
        # Create execution request
        execution_request = CodeExecution(
            code=code_to_execute,
            execution_type=machine_type,
            timeout=timeout,
            file_name=file_name,
            requirements_content=requirements_content,
            prior_imports=imports
        )
        
        response = start_execution_api_v2_external_compute_execution_run_post.sync_detailed(
            client=client,
            body=execution_request
        )
        
        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if hasattr(response, 'content'):
                console.print(f"[red]{response.content}[/red]")
            raise typer.Exit(1)
        
        data = response.parsed
        execution_id = data['execution_id']
        
        console.print(f"[green]✅ Execution started![/green]")
        console.print(f"[dim]Execution ID: {execution_id}[/dim]")
        
        if 'pythia_decision' in data:
            console.print(f"[dim]Pythia recommendation: {data['pythia_decision']}[/dim]")
        
        # Stream the execution output
        success = stream_execution_output(execution_id, client)
        
        if not success:
            console.print(f"[yellow]💡 You can check the execution later with: lyceum status[/yellow]")
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)