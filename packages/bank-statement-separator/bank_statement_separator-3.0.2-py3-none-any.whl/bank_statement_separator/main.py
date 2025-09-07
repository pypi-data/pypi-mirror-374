"""Main CLI interface for bank statement separator."""

import click
import logging
import time
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from .config import load_config, ensure_directories, validate_file_access
from .workflow import BankStatementWorkflow
from .utils.logging_setup import setup_logging

console = Console()


@click.group()
def main():
    """Bank Statement Separator with error handling and quarantine management."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    help="Output directory for separated statements",
)
@click.option(
    "--env-file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to .env configuration file",
)
@click.option(
    "--model",
    type=click.Choice(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]),
    help="LLM model to use for analysis",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--dry-run", is_flag=True, help="Analyze document without creating output files"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option(
    "--no-header", is_flag=True, help="Suppress the application header display"
)
def process(
    input_file: Path,
    output_dir: Optional[Path],
    env_file: Optional[Path],
    model: Optional[str],
    verbose: bool,
    dry_run: bool,
    yes: bool,
    no_header: bool,
):
    """
    Bank Statement Separator

    Automatically separate multi-statement PDF files using AI-powered analysis.

    INPUT_FILE: Path to the PDF file containing multiple bank statements
    """
    try:
        # Load configuration
        config = load_config(str(env_file) if env_file else None)

        # Override model if specified
        if model:
            config.openai_model = model

        # Set output directory
        if not output_dir:
            output_dir = Path(config.default_output_dir)

        # Setup logging
        log_level = "DEBUG" if verbose else config.log_level
        setup_logging(config.log_file, log_level)
        logger = logging.getLogger(__name__)

        # Ensure directories exist
        ensure_directories(config)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Display banner unless suppressed
        if not no_header:
            display_banner()

        # Validate file access
        if not validate_file_access(str(input_file), config, "read"):
            console.print(
                "[red]❌ Input file access denied by security configuration[/red]"
            )
            return

        if not validate_file_access(str(output_dir), config, "write"):
            console.print(
                "[red]❌ Output directory access denied by security configuration[/red]"
            )
            return

        # Display configuration summary
        display_config_summary(input_file, output_dir, config, dry_run)

        if not yes and not click.confirm("Proceed with processing?"):
            console.print("[yellow]Processing cancelled by user[/yellow]")
            return

        # Initialize and run workflow
        workflow = BankStatementWorkflow(config)

        start_time = time.time()

        if dry_run:
            console.print(
                "[yellow]🔍 Running analysis in dry-run mode (no files will be created)[/yellow]"
            )
            result = run_analysis_only(workflow, str(input_file), str(output_dir))
        else:
            console.print("[green]🚀 Starting workflow processing[/green]")
            result = run_full_workflow(workflow, str(input_file), str(output_dir))

        end_time = time.time()
        processing_time = end_time - start_time

        # Display results
        display_results(result, processing_time, dry_run)

    except Exception as e:
        logger.error(f"CLI execution failed: {e}")
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise click.ClickException(str(e))


def display_banner():
    """Display application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║               Bank Statement Separator                    ║
    ║         AI-Powered PDF Statement Processing               ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue"))


def display_config_summary(input_file: Path, output_dir: Path, config, dry_run: bool):
    """Display configuration summary."""
    table = Table(title="📋 Processing Configuration", show_header=False)
    table.add_column("Setting", style="cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("Input File", str(input_file))
    table.add_row("Output Directory", str(output_dir))
    # Display current model based on provider
    if config.llm_provider == "openai":
        table.add_row("LLM Model", f"{config.openai_model} (OpenAI)")
    elif config.llm_provider == "ollama":
        table.add_row("LLM Model", f"{config.ollama_model} (Ollama)")
    else:
        table.add_row("LLM Model", f"{config.llm_provider} provider")
    table.add_row("Max File Size", f"{config.max_file_size_mb} MB")
    table.add_row("Max Pages", str(config.max_total_pages))
    table.add_row("Dry Run Mode", "Yes" if dry_run else "No")
    table.add_row(
        "Paperless Upload", "Enabled" if config.paperless_enabled else "Disabled"
    )

    console.print(table)


def run_analysis_only(
    workflow: BankStatementWorkflow, input_file: str, output_dir: str
) -> dict:
    """Run analysis without creating output files."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # PDF Ingestion
        task = progress.add_task("📄 Loading and analyzing PDF...", total=None)

        # Create initial state for analysis
        from .workflow import WorkflowState

        initial_state = WorkflowState(
            input_file_path=input_file,
            output_directory=output_dir,
            pdf_document=None,
            text_chunks=None,
            detected_boundaries=None,
            extracted_metadata=None,
            generated_files=None,
            processed_input_file=None,
            paperless_upload_results=None,
            current_step="initializing",
            error_message=None,
            processing_complete=False,
            total_pages=0,
            total_statements_found=0,
            processing_time_seconds=None,
            confidence_scores=None,
            validation_results=None,
        )

        # Run only analysis steps
        state = workflow._pdf_ingestion_node(initial_state)
        if state.get("error_message"):
            return state

        progress.update(task, description="🔍 Analyzing document structure...")
        state = workflow._document_analysis_node(state)
        if state.get("error_message"):
            return state

        progress.update(task, description="🎯 Detecting statement boundaries...")
        state = workflow._statement_detection_node(state)
        if state.get("error_message"):
            return state

        progress.update(task, description="📊 Extracting metadata...")
        state = workflow._metadata_extraction_node(state)
        if state.get("error_message"):
            return state

        progress.update(task, description="✅ Analysis complete")
        progress.remove_task(task)

    return state


def run_full_workflow(
    workflow: BankStatementWorkflow, input_file: str, output_dir: str
) -> dict:
    """Run complete workflow with file generation."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Processing bank statements...", total=None)

        # Run complete workflow
        result = workflow.run(input_file, output_dir)

        progress.remove_task(task)

    return result


def display_results(result: dict, processing_time: float, dry_run: bool):
    """Display processing results."""
    if result.get("error_message"):
        console.print(f"[red]❌ Processing failed: {result['error_message']}[/red]")
        return

    # Check for API-related warnings in the processing
    if processing_time > 5:  # Longer processing might indicate API retries/fallbacks
        console.print(
            "[yellow]ℹ️  Note: Extended processing time may indicate API issues. Check logs for details.[/yellow]"
        )

    # Create results table
    table = Table(title="📊 Processing Results", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Total Pages Processed", str(result.get("total_pages", 0)))
    table.add_row("Statements Detected", str(result.get("total_statements_found", 0)))
    table.add_row("Processing Time", f"{processing_time:.2f} seconds")
    table.add_row("Status", result.get("current_step", "unknown"))

    console.print(table)

    # Display detected statements
    if result.get("extracted_metadata"):
        console.print("\n📄 Detected Statements:")

        stmt_table = Table(show_header=True)
        stmt_table.add_column("#", style="cyan", width=3)
        stmt_table.add_column("Pages", style="white", width=8)
        stmt_table.add_column("Account", style="yellow", width=15)
        stmt_table.add_column("Period", style="green", width=12)
        stmt_table.add_column("Bank", style="blue", width=15)
        if not dry_run:
            stmt_table.add_column("Output File", style="magenta")

        for i, metadata in enumerate(result["extracted_metadata"], 1):
            account = metadata.get("account_number") or "Unknown"
            period = metadata.get("statement_period") or "Unknown"
            bank = metadata.get("bank_name") or "Unknown"

            row = [
                str(i),
                f"{metadata.get('start_page', '?')}-{metadata.get('end_page', '?')}",
                str(account)[:15],
                str(period)[:12],
                str(bank)[:15],
            ]

            if not dry_run:
                row.append(metadata.get("filename", "N/A"))

            stmt_table.add_row(*row)

        console.print(stmt_table)

    # Display output files (if not dry run)
    if not dry_run and result.get("generated_files"):
        console.print(
            f"\n✅ Successfully created {len(result['generated_files'])} statement files:"
        )
        for file_path in result["generated_files"]:
            console.print(f"   📄 {Path(file_path).name}")

        console.print(
            f"\n📁 Files saved to: {Path(result['generated_files'][0]).parent}"
        )

        # Display validation results if available
        if result.get("validation_results"):
            validation = result["validation_results"]
            if validation["is_valid"]:
                console.print(
                    f"\n[green]✅ Output validation passed: {validation['summary']}[/green]"
                )
            else:
                console.print(
                    f"\n[red]❌ Output validation failed: {validation['summary']}[/red]"
                )
                for error in validation["error_details"]:
                    console.print(f"   [red]• {error}[/red]")

                # Show detailed check results
                console.print("\n📊 Validation Check Details:")
                val_table = Table(show_header=True)
                val_table.add_column("Check", style="cyan", width=20)
                val_table.add_column("Status", style="white", width=8)
                val_table.add_column("Details", style="white")

                for check_name, check_data in validation["checks"].items():
                    status_style = (
                        "green" if check_data["status"] == "passed" else "red"
                    )
                    status_symbol = "✅" if check_data["status"] == "passed" else "❌"

                    val_table.add_row(
                        check_name.replace("_", " ").title(),
                        f"[{status_style}]{status_symbol}[/{status_style}]",
                        check_data.get("details", ""),
                    )

                console.print(val_table)

        # Display processed file information if available
        if result.get("processed_input_file"):
            console.print("\n[blue]📦 Input file moved to processed directory:[/blue]")
            console.print(f"   [blue]🗂️  {result['processed_input_file']}[/blue]")

        # Display paperless upload results if available
        if result.get("paperless_upload_results"):
            display_paperless_results(result["paperless_upload_results"])

    # Summary message
    if dry_run:
        console.print(
            "\n[green]✅ Analysis completed successfully (dry-run mode)[/green]"
        )
        console.print(
            "[yellow]💡 Run without --dry-run to create the separated statement files[/yellow]"
        )
    else:
        console.print(
            "\n[green]🎉 Statement separation completed successfully![/green]"
        )

    # Add helpful note about API usage
    if processing_time < 2:  # Fast processing likely means fallback was used
        console.print(
            "\n[blue]ℹ️  Note: Processing used pattern-matching fallback. For improved accuracy with AI analysis:[/blue]"
        )
        console.print(
            "[blue]   • Ensure OPENAI_API_KEY is set in your .env file[/blue]"
        )
        console.print(
            "[blue]   • Check your OpenAI account has available credits[/blue]"
        )
        console.print(
            "[blue]   • Visit: https://platform.openai.com/account/usage[/blue]"
        )


def display_paperless_results(upload_results: dict):
    """Display paperless-ngx upload results."""
    if not upload_results.get("enabled"):
        console.print("\n[dim]📤 Paperless-ngx: Integration disabled[/dim]")
        return

    # Display upload summary
    if upload_results.get("success"):
        console.print(
            f"\n[green]📤 Paperless Upload: {upload_results['summary']}[/green]"
        )
    else:
        console.print(
            f"\n[yellow]📤 Paperless Upload: {upload_results['summary']}[/yellow]"
        )

    # Display successful uploads
    uploads = upload_results.get("uploads", [])
    if uploads:
        console.print(f"\n✅ Successfully uploaded {len(uploads)} document(s):")

        upload_table = Table(show_header=True)
        upload_table.add_column("Document", style="cyan", width=30)
        upload_table.add_column("ID", style="green", width=12)
        upload_table.add_column("Tags", style="blue")
        upload_table.add_column("Correspondent", style="yellow")

        for upload in uploads:
            # Show document ID if available, otherwise show task ID
            document_id = upload.get("document_id")
            task_id = upload.get("task_id")
            id_display = (
                str(document_id)
                if document_id
                else f"Task: {task_id[:8]}..."
                if task_id
                else "N/A"
            )

            title = upload.get("title", "Unknown")[:30]
            tags = (
                ", ".join(upload.get("tags", []))[:20] if upload.get("tags") else "None"
            )
            correspondent = upload.get("correspondent", "None")[:15]

            upload_table.add_row(title, id_display, tags, correspondent)

        console.print(upload_table)

    # Display errors if any
    errors = upload_results.get("errors", [])
    if errors:
        console.print(f"\n[red]❌ Upload errors ({len(errors)}):[/red]")
        for i, error in enumerate(errors, 1):
            if isinstance(error, dict):
                file_name = Path(error.get("file_path", "Unknown")).name
                error_msg = error.get("error", "Unknown error")
                console.print(f"   [red]{i}. {file_name}: {error_msg}[/red]")
            else:
                console.print(f"   [red]{i}. {error}[/red]")

    # Display helpful information
    if upload_results.get("enabled") and uploads:
        console.print(
            "\n[blue]💡 Documents are now available in your paperless-ngx instance[/blue]"
        )


@main.command()
@click.option(
    "--env-file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to .env configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def quarantine_status(env_file: Optional[Path], verbose: bool):
    """Display quarantine directory status and recent failures."""
    try:
        # Load configuration
        config = load_config(str(env_file) if env_file else None)

        # Setup logging
        setup_logging(config.log_file, config.log_level if verbose else "WARNING")

        # Initialize error handler
        from .utils.error_handler import ErrorHandler

        error_handler = ErrorHandler(config)

        # Get quarantine summary
        summary = error_handler.get_quarantine_summary()

        console.print("\n[bold blue]📁 Quarantine Status[/bold blue]")
        console.print("=" * 50)

        if summary["total_quarantined"] == 0:
            console.print("[green]✅ No documents in quarantine[/green]")
            console.print(
                f"[dim]Quarantine directory: {summary['quarantine_directory']}[/dim]"
            )
            return

        # Display summary
        console.print(
            f"[yellow]📊 Total quarantined documents: {summary['total_quarantined']}[/yellow]"
        )
        console.print(
            f"[dim]📁 Quarantine directory: {summary['quarantine_directory']}[/dim]"
        )

        # Display recent failures
        recent_failures = summary.get("recent_failures", [])
        if recent_failures:
            console.print(
                f"\n[yellow]🚨 Recent failures (last 7 days): {len(recent_failures)}[/yellow]"
            )

            failures_table = Table(show_header=True)
            failures_table.add_column("File", style="cyan", width=40)
            failures_table.add_column("Date", style="yellow", width=20)
            failures_table.add_column("Size", style="green", width=10)

            for failure in recent_failures[:10]:  # Show max 10 recent failures
                timestamp = failure["timestamp"][:19].replace(
                    "T", " "
                )  # Format datetime
                size_mb = f"{failure['size_mb']:.1f} MB"
                failures_table.add_row(failure["file"], timestamp, size_mb)

            console.print(failures_table)

            if len(recent_failures) > 10:
                console.print(
                    f"[dim]... and {len(recent_failures) - 10} more recent failures[/dim]"
                )

        # Display helpful commands
        console.print("\n[blue]💡 Management commands:[/blue]")
        console.print("[blue]   • Review quarantine directory manually:[/blue]")
        console.print(f"[blue]     ls -la '{summary['quarantine_directory']}'[/blue]")
        console.print("[blue]   • Check error reports:[/blue]")
        console.print(
            f"[blue]     ls -la '{summary['quarantine_directory']}/reports'[/blue]"
        )

    except Exception as e:
        console.print(f"[red]❌ Error checking quarantine status: {e}[/red]")


@main.command()
@click.option(
    "--env-file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to .env configuration file",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be cleaned without actually deleting",
)
@click.option(
    "--days", type=int, default=30, help="Delete files older than N days (default: 30)"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def quarantine_clean(env_file: Optional[Path], dry_run: bool, days: int, yes: bool):
    """Clean old files from quarantine directory."""
    try:
        # Load configuration
        config = load_config(str(env_file) if env_file else None)

        # Initialize error handler
        from .utils.error_handler import ErrorHandler

        error_handler = ErrorHandler(config)

        from datetime import datetime, timedelta

        quarantine_dir = error_handler.quarantine_dir

        if not quarantine_dir.exists():
            console.print(
                "[green]✅ Quarantine directory doesn't exist - nothing to clean[/green]"
            )
            return

        # Find old files
        cutoff_date = datetime.now() - timedelta(days=days)
        old_files = []

        for file_path in quarantine_dir.glob("failed_*.pdf"):
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    old_files.append((file_path, file_time))
            except Exception as e:
                console.print(
                    f"[yellow]⚠️  Warning: Could not check {file_path.name}: {e}[/yellow]"
                )

        if not old_files:
            console.print(
                f"[green]✅ No files older than {days} days found in quarantine[/green]"
            )
            return

        # Display files to be cleaned
        console.print(
            f"\n[yellow]🧹 Found {len(old_files)} files older than {days} days:[/yellow]"
        )

        for file_path, file_time in old_files[:10]:  # Show first 10
            age_days = (datetime.now() - file_time).days
            console.print(f"   [dim]• {file_path.name} ({age_days} days old)[/dim]")

        if len(old_files) > 10:
            console.print(f"   [dim]... and {len(old_files) - 10} more files[/dim]")

        if dry_run:
            console.print(
                f"\n[blue]🔍 Dry run: {len(old_files)} files would be deleted[/blue]"
            )
            return

        # Confirmation
        if not yes:
            total_size = sum(f[0].stat().st_size for f, _ in old_files) / (1024 * 1024)
            if not click.confirm(
                f"\nDelete {len(old_files)} files ({total_size:.1f} MB)?"
            ):
                console.print("[yellow]Operation cancelled[/yellow]")
                return

        # Delete files
        deleted_count = 0
        errors = []

        for file_path, _ in old_files:
            try:
                # Also delete corresponding error report if it exists
                report_file = (
                    error_handler.error_report_dir
                    / f"error_report_{file_path.stem.replace('failed_', '')}.json"
                )
                if report_file.exists():
                    report_file.unlink()

                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                errors.append(f"{file_path.name}: {e}")

        # Report results
        console.print(f"\n[green]✅ Successfully deleted {deleted_count} files[/green]")

        if errors:
            console.print(f"\n[yellow]⚠️  {len(errors)} errors occurred:[/yellow]")
            for error in errors[:5]:  # Show first 5 errors
                console.print(f"   [red]• {error}[/red]")
            if len(errors) > 5:
                console.print(f"   [dim]... and {len(errors) - 5} more errors[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error cleaning quarantine: {e}[/red]")


# Keep backward compatibility by also accepting direct CLI calls
cli = process  # Alias the main process command


@main.command()
def version():
    """Display version and author information."""
    version_info = """
╔═══════════════════════════════════════════════════════════╗
║                   Bank Statement Separator                ║
║                        Version Information                 ║
╚═══════════════════════════════════════════════════════════╝

Version: 0.1.0
Author: Stephen Eaton
License: MIT
Repository: https://github.com/madeinoz67/bank-statement-separator

An AI-powered tool for automatically separating
multi-statement PDF files using LangChain and LangGraph.
"""
    console.print(Panel(version_info, style="bold blue"))


@main.command()
@click.argument(
    "input_directory", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    help="Output directory for separated statements",
)
@click.option(
    "--pattern", default="*.pdf", help="File pattern to match (default: *.pdf)"
)
@click.option("--exclude", help="Pattern to exclude from processing")
@click.option("--max-files", type=int, help="Maximum number of files to process")
@click.option(
    "--recursive", "-r", is_flag=True, help="Recursively process subdirectories"
)
@click.option(
    "--env-file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to .env configuration file",
)
@click.option(
    "--model",
    type=click.Choice(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]),
    help="LLM model to use for analysis",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--dry-run", is_flag=True, help="Analyze documents without creating output files"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
@click.option(
    "--no-header", is_flag=True, help="Suppress the application header display"
)
def batch_process(
    input_directory: Path,
    output_dir: Optional[Path],
    pattern: str,
    exclude: Optional[str],
    max_files: Optional[int],
    recursive: bool,
    env_file: Optional[Path],
    model: Optional[str],
    verbose: bool,
    dry_run: bool,
    yes: bool,
    no_header: bool,
):
    """
    Batch process all PDF files in a directory.

    Processes multiple PDF files in a directory, with individual file error isolation.
    Failed files are quarantined but don't stop the batch processing.

    INPUT_DIRECTORY: Directory containing PDF files to process
    """
    import fnmatch
    from datetime import datetime

    try:
        # Load configuration
        config = load_config(str(env_file) if env_file else None)

        # Override model if specified
        if model:
            config.openai_model = model

        # Override output directory if specified
        if output_dir:
            config.default_output_dir = str(output_dir)

        # Setup logging
        setup_logging(config.log_file, config.log_level if verbose else "INFO")
        logger = logging.getLogger(__name__)

        # Ensure directories exist
        ensure_directories(config)

        # Discover files
        console.print(
            f"\n[bold blue]🔍 Discovering files in: {input_directory}[/bold blue]"
        )

        # Use glob pattern to find files
        if recursive:
            files = list(input_directory.glob("**/" + pattern))
        else:
            files = list(input_directory.glob(pattern))

        # Filter out excluded patterns
        if exclude:
            files = [f for f in files if not fnmatch.fnmatch(f.name, exclude)]

        # Apply max files limit
        if max_files and len(files) > max_files:
            files = files[:max_files]
            console.print(f"[yellow]⚠️  Limited to {max_files} files[/yellow]")

        if not files:
            console.print("[red]❌ No files found matching criteria[/red]")
            return

        console.print(f"[green]📄 Found {len(files)} file(s) to process[/green]")

        # Show files to be processed
        if len(files) <= 10:
            for file in files:
                console.print(f"  • {file.name}")
        else:
            for file in files[:5]:
                console.print(f"  • {file.name}")
            console.print(f"  ... and {len(files) - 5} more files")

        # Confirm processing unless --yes flag
        if not yes and not dry_run:
            if not click.confirm(f"\nProcess {len(files)} files?"):
                console.print("[yellow]❌ Operation cancelled[/yellow]")
                return

        # Initialize batch tracking
        batch_start_time = datetime.now()
        batch_results = {
            "total_files": len(files),
            "processed": 0,
            "successful": 0,
            "quarantined": 0,
            "validation_failed": 0,
            "paperless_uploaded": 0,
            "errors": [],
        }

        # Display banner unless suppressed
        if not no_header:
            display_banner()

        console.print("\n[bold green]🚀 Starting batch processing...[/bold green]")
        if dry_run:
            console.print("[yellow]🔍 DRY RUN MODE - No files will be created[/yellow]")

        # Process files with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing files...", total=len(files))

            for i, file_path in enumerate(files, 1):
                try:
                    progress.update(
                        task,
                        description=f"Processing {file_path.name} ({i}/{len(files)})",
                    )

                    logger.info(f"Processing file {i}/{len(files)}: {file_path}")

                    # Validate file access
                    validate_file_access(str(file_path), config)

                    # Create workflow instance
                    workflow = BankStatementWorkflow(config)

                    # Process single file
                    if dry_run:
                        result = run_analysis_only(
                            workflow, str(file_path), config.default_output_dir
                        )
                    else:
                        result = run_full_workflow(
                            workflow, str(file_path), config.default_output_dir
                        )

                    batch_results["processed"] += 1

                    # Track results based on workflow outcome
                    if (
                        result.get("processing_complete")
                        and not result.get("error_message")
                    ) or (dry_run and result.get("detected_boundaries")):
                        batch_results["successful"] += 1
                        if result.get("paperless_upload_results"):
                            batch_results["paperless_uploaded"] += len(
                                result["paperless_upload_results"]
                            )
                    elif (
                        result.get("error_message")
                        and "quarantine" in result.get("error_message", "").lower()
                    ):
                        batch_results["quarantined"] += 1
                    elif result.get("validation_results") and not result.get(
                        "validation_results", {}
                    ).get("is_valid", True):
                        batch_results["validation_failed"] += 1

                except Exception as e:
                    # Individual file failure shouldn't stop batch
                    error_msg = f"Failed to process {file_path.name}: {str(e)}"
                    batch_results["errors"].append(error_msg)
                    logger.error(error_msg, exc_info=True)

                    # Try to quarantine the file if possible
                    try:
                        from .utils.error_handler import ErrorHandler

                        error_handler = ErrorHandler(config)
                        error_handler.move_to_quarantine(
                            str(file_path), f"Batch processing error: {str(e)}"
                        )
                        batch_results["quarantined"] += 1
                    except Exception as quarantine_error:
                        logger.error(
                            f"Failed to quarantine {file_path.name}: {quarantine_error}"
                        )

                progress.advance(task)

        # Display batch summary
        batch_end_time = datetime.now()
        processing_time = batch_end_time - batch_start_time

        _display_batch_results(batch_results, processing_time, dry_run)

    except Exception as e:
        console.print(f"[red]❌ Batch processing failed: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.ClickException(str(e))


def _display_batch_results(results: dict, processing_time, dry_run: bool):
    """Display batch processing results summary."""
    console.print(
        f"\n[bold blue]📊 Batch Processing {'Summary' if not dry_run else 'Analysis'} Results[/bold blue]"
    )

    # Create results table
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Metric", style="dim")
    table.add_column("Count", justify="right")
    table.add_column("Percentage", justify="right", style="dim")

    total = results["total_files"]
    table.add_row("Total Files", str(total), "100%")
    table.add_row(
        "Processed",
        str(results["processed"]),
        f"{results['processed'] / total * 100:.1f}%",
    )
    table.add_row(
        "Successful",
        str(results["successful"]),
        f"{results['successful'] / total * 100:.1f}%",
    )

    if results["quarantined"] > 0:
        table.add_row(
            "Quarantined",
            str(results["quarantined"]),
            f"{results['quarantined'] / total * 100:.1f}%",
        )

    if results["validation_failed"] > 0:
        table.add_row(
            "Validation Failed",
            str(results["validation_failed"]),
            f"{results['validation_failed'] / total * 100:.1f}%",
        )

    if results["paperless_uploaded"] > 0:
        table.add_row("Uploaded to Paperless", str(results["paperless_uploaded"]), "")

    table.add_row("Processing Time", f"{processing_time.total_seconds():.1f}s", "")

    console.print(table)

    # Show errors if any
    if results["errors"]:
        console.print(
            f"\n[bold red]❌ Errors encountered ({len(results['errors'])})[/bold red]"
        )
        for error in results["errors"][:5]:  # Show first 5 errors
            console.print(f"  • {error}")
        if len(results["errors"]) > 5:
            console.print(f"  ... and {len(results['errors']) - 5} more errors")
        console.print("\n💡 Check quarantine directory for failed files")

    # Success message
    if results["successful"] == total and not results["errors"]:
        console.print(f"\n[green]🎉 All {total} files processed successfully![/green]")
    elif results["successful"] > 0:
        console.print(
            f"\n[green]✅ {results['successful']}/{total} files processed successfully[/green]"
        )

    if not dry_run and results["successful"] > 0:
        console.print("📁 Output files saved to configured directories")


if __name__ == "__main__":
    main()
