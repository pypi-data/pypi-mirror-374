import argparse
import importlib
import importlib.util
import inspect
import logging
import os
import json

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from smooth_criminal.analizer import analyze_ast
from smooth_criminal.benchmark import benchmark_jam
from smooth_criminal.dashboard import render_dashboard
from smooth_criminal.memory import (
    suggest_boost,
    clear_execution_history,
    export_execution_history,
    score_function,
)
from smooth_criminal.core import play_mj_effect, set_mj_mode


log_level = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level, logging.INFO)

logging.basicConfig(
    level=numeric_level,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    force=True,
)

logger = logging.getLogger("SmoothCriminal")

def main():
    parser = argparse.ArgumentParser(description="Smooth Criminal CLI")
    parser.add_argument(
        "--mj-mode",
        action="store_true",
        help="Activa efectos MJ cuando hay mejoras de rendimiento",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Comando 'analyze'
    analyze_parser = subparsers.add_parser("analyze", help="Analiza un archivo Python en busca de optimizaciones.")
    analyze_parser.add_argument("filepath", help="Ruta del script a analizar")

    # Comando 'suggest'
    suggest_parser = subparsers.add_parser("suggest", help="Sugiere el mejor decorador para una función registrada.")
    suggest_parser.add_argument("func_name", help="Nombre de la función a consultar")

    # Comando 'dashboard'
    subparsers.add_parser("dashboard", help="Muestra un resumen del historial de optimizaciones.")

    # Comando 'clean'
    subparsers.add_parser("clean", help="Elimina el historial de ejecuciones registrado.")

    # Comando 'export'
    export_parser = subparsers.add_parser(
        "export", help="Exporta el historial como archivo CSV, JSON, XLSX o Markdown."
    )
    export_parser.add_argument("filepath", help="Ruta del archivo de salida")
    export_parser.add_argument(
        "--format",
        choices=["csv", "json", "xlsx", "md"],
        default="csv",
        help="Formato de exportación",
    )

    # Comando 'score'
    score_parser = subparsers.add_parser("score", help="Muestra una puntuación de optimización para una función.")
    score_parser.add_argument("func_name", help="Nombre de la función a evaluar")

    # Comando 'jam-test'
    jam_parser = subparsers.add_parser(
        "jam-test", help="Benchmark de backends de jam para una función"
    )
    jam_parser.add_argument(
        "func_path", help="Ruta a la función en formato modulo:funcion"
    )
    jam_parser.add_argument(
        "--workers", type=int, default=1, help="Número de workers a utilizar"
    )
    jam_parser.add_argument(
        "--reps", type=int, default=1, help="Número de repeticiones del benchmark"
    )
    jam_parser.add_argument(
        "--silent",
        action="store_true",
        help="Muestra solo el resultado en formato JSON",
    )

    args = parser.parse_args()
    set_mj_mode(args.mj_mode)
    if not getattr(args, "silent", False):
        show_intro()

    if args.command == "analyze":
        analyze_file(args.filepath)
    elif args.command == "suggest":
        handle_suggestion(args.func_name)
    elif args.command == "dashboard":
        render_dashboard()
    elif args.command == "clean":
        handle_clean()
    elif args.command == "export":
        handle_export(args.filepath, args.format)
    elif args.command == "score":
        handle_score(args.func_name)
    elif args.command == "jam-test":
        handle_jam_test(
            args.func_path, args.workers, args.reps, args.silent, args.mj_mode
        )

    else:
        logger.warning(
            "[bold red]Annie, are you OK?[/bold red] "
            "Use '[green]smooth-criminal analyze <file.py>[/green]', "
            "'[green]smooth-criminal suggest <func>[/green]', "
            "'[green]smooth-criminal dashboard[/green]' or "
            "'[green]smooth-criminal export <file> --format csv/json/xlsx/md[/green]'."
        )

def show_intro():
    logger.info(
        "[bold magenta]Smooth Criminal[/bold magenta]\n"
        "[dim]By Adolfo – Powered by Python + MJ energy 🕺[/dim]"
    )

def analyze_file(filepath):
    logger.info(
        f"\n🎤 [cyan]Analyzing [bold]{filepath}[/bold] for optimization opportunities...[/cyan]\n"
    )

    spec = importlib.util.spec_from_file_location("target_module", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    functions = [getattr(module, name) for name in dir(module)
                 if inspect.isfunction(getattr(module, name)) and getattr(module, name).__module__ == module.__name__]

    if not functions:
        logger.warning("[yellow]No se encontraron funciones para analizar.[/yellow]")
        return

    for func in functions:
        logger.info(
            f"\n🔎 [bold blue]Analyzing function:[/bold blue] [white]{func.__name__}[/white]"
        )
        analyze_ast(func)

def handle_suggestion(func_name):
    logger.info(
        f"\n🧠 [bold cyan]Consulting memory for:[/bold cyan] [white]{func_name}[/white]\n"
    )
    suggestion = suggest_boost(func_name)
    logger.info(suggestion)

def handle_clean():
    if clear_execution_history():
        logger.info("[green]Historial de ejecuciones borrado exitosamente.[/green]")
    else:
        logger.warning("[yellow]No se encontró historial para borrar.[/yellow]")

def handle_export(filepath, format):
    success = export_execution_history(filepath, format)
    if success:
        logger.info(
            f"[green]Historial exportado a [bold]{filepath}[/bold] como {format.upper()}.[/green]"
        )
    else:
        logger.warning("[yellow]No hay historial para exportar.[/yellow]")

def handle_score(func_name):
    score, summary = score_function(func_name)
    if score is None:
        logger.warning(f"[yellow]{summary}[/yellow]")
    else:
        logger.info(summary)
        color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
        logger.info(f"[bold {color}]Optimization Score: {score}/100[/bold {color}]")


def handle_jam_test(
    func_path: str, workers: int, reps: int, silent: bool, mj_mode: bool
) -> None:
    module_name, func_name = func_path.split(":", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)

    backends = ["thread", "process", "async"]
    args = list(range(workers))
    if silent:
        logging.disable(logging.CRITICAL)

    totals = {b: 0.0 for b in backends}
    for _ in range(reps):
        result = benchmark_jam(func, args, backends)
        if not all(m.get("success") for m in result["metrics"]):
            logger.error("[red]One or more backends failed during benchmarking.[/red]")
            if silent:
                logging.disable(logging.NOTSET)
            return
        for metric in result["metrics"]:
            totals[metric["backend"]] += metric["duration"]

    averages = {b: totals[b] / reps for b in backends}
    fastest = min(averages, key=averages.get)
    if silent:
        print(json.dumps({"averages": averages, "fastest": fastest}))
        logging.disable(logging.NOTSET)
        return

    max_duration = max(averages.values()) or 1.0
    min_duration = min(averages.values()) or 0.0
    improvement = ((max_duration - min_duration) / max_duration) * 100
    play_mj_effect(improvement, mj_mode)

    console = Console()
    table = Table(title="Resultados jam-test")
    table.add_column("Backend")
    table.add_column("Promedio (s)", justify="right")
    table.add_column("Comparativa")

    for backend in backends:
        duration = averages[backend]
        bar_length = int((duration / max_duration) * 40)
        bar = "█" * bar_length
        table.add_row(backend, f"{duration:.4f}", bar)

    console.print(table)
    logger.info("🎶 Just jammin' through those CPU cores! 🧠🕺")


if __name__ == "__main__":
    main()
