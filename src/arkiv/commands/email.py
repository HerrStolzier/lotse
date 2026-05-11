"""Email-related CLI commands."""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from arkiv.commands.common import console, get_context


def import_email(
    path: Path = typer.Argument(..., help="Path to .eml or .mbox file"),
    config: Path | None = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Import and classify emails from .eml or .mbox files."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    from arkiv.inlets.email import parse_eml, parse_mbox, save_attachments

    ctx = get_context(config)
    cfg = ctx.config
    engine = ctx.engine

    if not path.exists():
        console.print(f"[red]Not found:[/red] {path}")
        raise typer.Exit(1)

    suffix = path.suffix.lower()
    if suffix == ".eml":
        emails = [parse_eml(path)]
    elif suffix == ".mbox":
        emails = parse_mbox(path)
    else:
        console.print(f"[red]Unsupported format:[/red] {suffix} (use .eml or .mbox)")
        raise typer.Exit(1)

    console.print(f"[blue]Processing {len(emails)} email(s)...[/blue]\n")

    for i, parsed in enumerate(emails, 1):
        console.print(f"[dim]#{i}[/dim] {parsed.subject}")
        result = engine.ingest_text(
            parsed.text_for_classification,
            name=f"email:{parsed.subject[:50]}",
        )

        if result.success:
            console.print(f"  [green]✓[/green] {result.message}")
        else:
            console.print(f"  [red]✗[/red] {result.message}")

        if parsed.attachments:
            att_dir = cfg.inbox_dir / "email_attachments"
            saved = save_attachments(parsed, att_dir)
            for att_path in saved:
                att_result = engine.ingest_file(att_path)
                if att_result.success:
                    console.print(f"  [green]  ↳[/green] {att_path.name}: {att_result.message}")
                else:
                    console.print(f"  [red]  ↳[/red] {att_path.name}: {att_result.message}")
                att_path.unlink(missing_ok=True)

    console.print(f"\n[green]Done.[/green] Processed {len(emails)} email(s).")


def fetch_email(
    host: str = typer.Option(..., "--host", help="IMAP server (e.g. imap.gmail.com)"),
    username: str = typer.Option(..., "--user", "-u", help="Email address"),
    password: str = typer.Option(
        ..., "--password", "-p", prompt=True, hide_input=True, help="Password/app password"
    ),
    folder: str = typer.Option("INBOX", "--folder", "-f"),
    limit: int = typer.Option(20, "--limit", "-n"),
    config: Path | None = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Fetch and classify unread emails from an IMAP server."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    from arkiv.inlets.email import fetch_imap, save_attachments

    ctx = get_context(config)
    cfg = ctx.config
    engine = ctx.engine

    console.print(f"[blue]Connecting to {host}...[/blue]")

    try:
        emails = fetch_imap(host, username, password, folder=folder, limit=limit)
    except Exception as e:
        console.print(f"[red]Connection failed:[/red] {e}")
        raise typer.Exit(1) from None

    if not emails:
        console.print("[dim]No unread emails.[/dim]")
        return

    console.print(f"[blue]Processing {len(emails)} email(s)...[/blue]\n")

    for i, parsed in enumerate(emails, 1):
        console.print(f"[dim]#{i}[/dim] {parsed.subject}")

        result = engine.ingest_text(
            parsed.text_for_classification,
            name=f"email:{parsed.subject[:50]}",
        )

        if result.success:
            console.print(f"  [green]✓[/green] {result.message}")
        else:
            console.print(f"  [red]✗[/red] {result.message}")

        if parsed.attachments:
            att_dir = cfg.inbox_dir / "email_attachments"
            saved = save_attachments(parsed, att_dir)
            for att_path in saved:
                att_result = engine.ingest_file(att_path)
                if att_result.success:
                    console.print(f"  [green]  ↳[/green] {att_path.name}: {att_result.message}")
                att_path.unlink(missing_ok=True)

    console.print(f"\n[green]Done.[/green] Processed {len(emails)} email(s).")


def register(app: typer.Typer) -> None:
    """Register email commands."""
    app.command("import-email")(import_email)
    app.command("fetch-email")(fetch_email)
