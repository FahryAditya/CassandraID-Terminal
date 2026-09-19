import typer
from rich.prompt import Confirm

from cassandra_terminal.modules.ports import get_active_listening_ports, kill_port_process
from cassandra_terminal.ui.theme import console, create_table, error_console

ports_app = typer.Typer(help="Inspect active localhost ports & kill zombie processes")
app = ports_app


@ports_app.callback(invoke_without_command=True)
def list_ports_cmd(
    ctx: typer.Context,
    port_filter: int | None = typer.Option(
        None, "--port", "-p", help="Filter by specific port number"
    ),
):
    """List all active listening localhost ports and processes."""
    if ctx.invoked_subcommand is None:
        try:
            with console.status("[bold cyan]Scanning listening ports...[/bold cyan]"):
                ports = get_active_listening_ports()

            if port_filter:
                ports = [p for p in ports if p.port == port_filter]

            if not ports:
                console.print(
                    "[bold green]✓ No active listening ports found matching criteria.[/bold green]"
                )
                return

            table = create_table(
                title="🔌 Active Localhost Ports & Processes",
                columns=["Port", "Protocol", "IP Address", "PID", "Process Name", "Status"],
            )
            for p in ports:
                is_web_port = p.port in (80, 443, 3000, 5000, 5173, 8000, 8080, 8888, 9000)
                port_style = "bold green" if is_web_port else "bold cyan"
                table.add_row(
                    f"[{port_style}]{p.port}[/{port_style}]",
                    p.protocol,
                    p.ip,
                    str(p.pid or "-"),
                    f"[bold magenta]{p.process_name}[/bold magenta]",
                    f"[dim]{p.status}[/dim]",
                )

            console.print(table)
            console.print(
                "\n[dim]To terminate a process blocking a port, run:[/dim] [yellow]cassandra ports kill <PORT>[/yellow]"
            )
        except Exception as e:
            error_console.print(f"[error]Failed to scan ports:[/error] {e}")
            raise typer.Exit(1)


@ports_app.command("kill")
def kill_cmd(
    target: int = typer.Argument(..., help="Port number or PID to terminate"),
    force: bool = typer.Option(False, "--force", "-f", help="Bypass confirmation prompt"),
):
    """Terminate the process listening on a port or by PID."""
    try:
        if not force:
            if not Confirm.ask(
                f"[bold red]Are you sure you want to kill the process on port/PID {target}?[/bold red]"
            ):
                console.print("[dim]Operation cancelled.[/dim]")
                return

        success, msg = kill_port_process(target)
        if success:
            console.print(f"[bold green]✓ {msg}[/bold green]")
        else:
            console.print(f"[bold red]✗ {msg}[/bold red]")
            raise typer.Exit(1)
    except Exception as e:
        error_console.print(f"[error]Kill failed:[/error] {e}")
        raise typer.Exit(1)
