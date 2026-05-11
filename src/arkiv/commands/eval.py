"""Evaluation and benchmark CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from arkiv.commands.common import console
from arkiv.evals.llm_benchmark import (
    TaskName,
    default_models,
    parse_model_spec,
    run_benchmark,
    write_report,
)

eval_app = typer.Typer(help="Run Kurier evaluation benchmarks.")


def _tasks_from_options(task: str, run_all: bool) -> list[TaskName]:
    if run_all:
        return ["classifier", "search", "retrieval"]
    if task not in ("classifier", "search", "retrieval"):
        raise typer.BadParameter("task must be classifier, search, or retrieval")
    return [task]  # type: ignore[list-item]


@eval_app.command("llm")
def llm(
    task: Annotated[
        str,
        typer.Option(
            "--task",
            help="Benchmark task: classifier, search, or retrieval. Ignored when --all is set.",
        ),
    ] = "classifier",
    models: Annotated[
        list[str] | None,
        typer.Option("--models", help="Model spec provider:model. Can be passed multiple times."),
    ] = None,
    run_all: Annotated[bool, typer.Option("--all", help="Run all benchmark tasks.")] = False,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Validate selected tasks/models without calling LLMs."),
    ] = False,
) -> None:
    """Run LLM quality benchmarks for Kurier."""
    selected_tasks = _tasks_from_options(task, run_all)
    selected_models = models or default_models()

    # Parse early so CLI users get immediate feedback on invalid specs.
    parsed_models = [parse_model_spec(model) for model in selected_models]

    if dry_run:
        console.print("[bold]Kurier LLM Benchmark dry run[/bold]")
        console.print(f"Tasks: {', '.join(selected_tasks)}")
        console.print(f"Models: {', '.join(model.label for model in parsed_models)}")
        return

    report = run_benchmark(tasks=selected_tasks, model_specs=selected_models)

    table = Table(title="Kurier LLM Benchmark")
    table.add_column("Task")
    table.add_column("Model")
    table.add_column("Status")
    table.add_column("Cases", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Latency", justify="right")

    for result in report.results:
        latency = f"{result.avg_latency_ms:.0f} ms" if result.avg_latency_ms is not None else "-"
        table.add_row(
            result.task,
            result.model,
            result.status,
            str(result.cases),
            f"{result.overall_score:.2f}",
            latency,
        )

    console.print(table)
    report_path = write_report(report, output)
    console.print(f"[green]✓[/green] Benchmark report written to {report_path}")


def register(app: typer.Typer) -> None:
    """Register eval commands."""
    app.add_typer(eval_app, name="eval")
