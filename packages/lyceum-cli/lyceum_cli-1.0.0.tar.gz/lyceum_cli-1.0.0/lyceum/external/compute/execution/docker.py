"""
Docker execution commands
"""

from typing import Optional
import typer
import json
from rich.console import Console

from ....shared.config import config
from ....shared.streaming import stream_execution_output

console = Console()

# Import generated client modules
from lyceum_cloud_execution_api_client.api.docker_execution import start_docker_execution_api_v2_external_compute_execution_docker_post
from lyceum_cloud_execution_api_client.models import DockerExecution

docker_app = typer.Typer(name="docker", help="Docker execution commands")


@docker_app.command("run")
def run_docker(
    image: str = typer.Argument(..., help="Docker image to run"),
    machine_type: str = typer.Option("cpu", "--machine", "-m", help="Machine type (cpu, a100, h100, etc.)"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Execution timeout in seconds"),
    file_name: Optional[str] = typer.Option(None, "--file-name", "-f", help="Name for the execution"),
    command: Optional[str] = typer.Option(None, "--command", "-c", help="Command to run in container (e.g., 'python app.py')"),
    env: Optional[list[str]] = typer.Option(None, "--env", "-e", help="Environment variables (e.g., KEY=value)"),
    callback_url: Optional[str] = typer.Option(None, "--callback", help="Webhook URL for completion notification"),
    registry_creds: Optional[str] = typer.Option(None, "--registry-creds", help="Docker registry credentials as JSON string"),
    registry_type: Optional[str] = typer.Option(None, "--registry-type", help="Registry credential type: basic, aws, etc."),
):
    """Execute a Docker container on Lyceum Cloud"""
    client = config.get_client()
    
    try:
        # Parse environment variables
        docker_env = {}
        if env:
            for env_var in env:
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    docker_env[key] = value
                else:
                    console.print(f"[yellow]Warning: Ignoring invalid env var format: {env_var}[/yellow]")
        
        # Parse command into list
        docker_cmd = None
        if command:
            # Simple split on spaces - could be enhanced for quoted strings
            docker_cmd = command.split()
        
        # Parse registry credentials
        registry_credentials = None
        if registry_creds:
            try:
                registry_credentials = json.loads(registry_creds)
            except json.JSONDecodeError:
                console.print(f"[red]Error: Invalid JSON format for registry credentials[/red]")
                raise typer.Exit(1)
        
        # Validate registry credentials and type
        if (registry_creds and not registry_type) or (registry_type and not registry_creds):
            console.print(f"[red]Error: Both --registry-creds and --registry-type must be provided together[/red]")
            raise typer.Exit(1)
        
        # Create Docker execution request
        docker_request = DockerExecution(
            docker_image=image,
            docker_cmd=docker_cmd,
            docker_env=docker_env if docker_env else None,
            execution_type=machine_type,
            timeout=timeout,
            file_name=file_name,
            callback_url=callback_url,
            docker_registry_credentials=registry_credentials,
            docker_registry_credential_type=registry_type
        )
        
        response = start_docker_execution_api_v2_external_compute_execution_docker_post.sync_detailed(
            client=client,
            body=docker_request
        )
        
        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if hasattr(response, 'content'):
                console.print(f"[red]{response.content}[/red]")
            raise typer.Exit(1)
        
        data = response.parsed
        execution_id = data.execution_id
        
        console.print(f"[green]✅ Docker execution started![/green]")
        console.print(f"[dim]Execution ID: {execution_id}[/dim]")
        console.print(f"[dim]Machine Type: {data.execution_type}[/dim]")
        
        # Stream the execution output
        success = stream_execution_output(execution_id, client)
        
        if not success:
            console.print(f"[yellow]💡 You can check the execution later with: lyceum status[/yellow]")
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@docker_app.command("registry-examples")
def show_registry_examples():
    """Show examples of Docker registry credential formats"""
    console.print("[bold cyan]Docker Registry Credential Examples[/bold cyan]\n")
    
    console.print("[bold]1. Docker Hub (basic)[/bold]")
    console.print("Type: [green]basic[/green]")
    console.print('Credentials: [yellow]\'{"username": "myuser", "password": "mypassword"}\'[/yellow]\n')
    
    console.print("[bold]2. AWS ECR (aws)[/bold]")
    console.print("Type: [green]aws[/green]")
    console.print('Credentials: [yellow]\'{"region": "us-west-2", "aws_access_key_id": "AKIAI...", "aws_secret_access_key": "wJalrX...", "session_token": "optional..."}\'[/yellow]\n')
    
    console.print("[bold]3. Private Registry (basic)[/bold]")
    console.print("Type: [green]basic[/green]")
    console.print('Credentials: [yellow]\'{"username": "admin", "password": "secret"}\'[/yellow]\n')
    
    console.print("[bold]Example Commands:[/bold]")
    console.print("# Docker Hub:")
    console.print('[dim]lyceum docker run myuser/myapp:latest --registry-type basic --registry-creds \'{"username": "myuser", "password": "mytoken"}\'[/dim]')
    console.print("\n# AWS ECR:")
    console.print('[dim]lyceum docker run 123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:latest --registry-type aws --registry-creds \'{"region": "us-west-2", "aws_access_key_id": "AKIAI...", "aws_secret_access_key": "wJalrX..."}\'[/dim]')
    console.print("\n# Private Registry:")
    console.print('[dim]lyceum docker run myregistry.com/myapp:latest --registry-type basic --registry-creds \'{"username": "admin", "password": "secret"}\'[/dim]')