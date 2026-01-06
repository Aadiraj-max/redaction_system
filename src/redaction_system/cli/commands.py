#!/usr/bin/env python3
"""CLI Commands for Redaction System"""
import click
from pathlib import Path
from rich.console import Console
from rich.progress import track
from redaction_system.orchestrator import Orchestrator
from redaction_system.cli.preview import show_preview
from redaction_system.cli.utils import scan_directory, format_error

console = Console()

@click.group()
@click.version_option(version="0.1.0")
def main():
    """🔒 Redaction System - Privacy-first document anonymization"""
    pass

@main.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--prompt', '-p', required=True, help='Redaction instructions (e.g., "redact names")')
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: <name>_redacted.<ext>)')
@click.option('--no-preview', is_flag=True, help='Skip preview and redact immediately')
def file(filepath, prompt, output, no_preview):
    """Redact a single file"""
    
    console.print(f"\n📁 Processing: [bold cyan]{filepath}[/bold cyan]")
    console.print(f"💬 Prompt: [yellow]{prompt}[/yellow]\n")
    
    try:
        orchestrator = Orchestrator()
        
        if not no_preview:
            # Show preview and get user approval
            approved = show_preview(filepath, prompt, orchestrator)
            if not approved:
                console.print("[yellow]❌ Redaction cancelled by user[/yellow]")
                return
        
        # Execute redaction
        console.print("\n[bold green]🔄 Redacting...[/bold green]")
        output_path = orchestrator.redact_file(filepath, prompt, output)
        
        console.print(f"\n[bold green]✅ Complete![/bold green]")
        console.print(f"📁 Output: [cyan]{output_path}[/cyan]\n")
        
    except Exception as e:
        format_error(e)
        raise click.Abort()

@main.command()
@click.argument('dirpath', type=click.Path(exists=True, file_okay=False))
@click.option('--prompt', '-p', required=True, help='Redaction instructions')
@click.option('--output', '-o', type=click.Path(), help='Output directory (default: same directory)')
@click.option('--mode', type=click.Choice(['interactive', 'batch', 'hybrid']), default='batch', help='Processing mode')
def directory(dirpath, prompt, output, mode):
    """Redact all files in a directory"""
    
    console.print(f"\n📁 Scanning: [bold cyan]{dirpath}[/bold cyan]")
    
    # Scan for supported files
    files = scan_directory(dirpath)
    
    if not files['files']:
        console.print("[yellow]⚠️  No supported files found[/yellow]")
        return
    
    console.print(f"Found: [green]{len(files['files'])} files[/green]")
    for fmt, count in files['summary'].items():
        console.print(f"  • {count} {fmt.upper()} files")
    
    # Confirm before processing
    if not click.confirm(f"\nProcess {len(files['files'])} files?"):
        console.print("[yellow]❌ Cancelled[/yellow]")
        return
    
    # Process files
    orchestrator = Orchestrator()
    output_dir = Path(output) if output else Path(dirpath)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success = 0
    errors = []
    
    for filepath in track(files['files'], description="Processing..."):
        try:
            # For batch mode, skip preview
            if mode == 'batch' or (mode == 'hybrid' and success > 0):
                output_path = output_dir / f"{Path(filepath).stem}_redacted{Path(filepath).suffix}"
                orchestrator.redact_file(str(filepath), prompt, str(output_path))
                success += 1
            else:
                # Interactive mode - show preview for each
                approved = show_preview(str(filepath), prompt, orchestrator)
                if approved:
                    output_path = output_dir / f"{Path(filepath).stem}_redacted{Path(filepath).suffix}"
                    orchestrator.redact_file(str(filepath), prompt, str(output_path))
                    success += 1
        except Exception as e:
            errors.append((filepath, str(e)))
    
    # Summary
    console.print(f"\n[bold green]✅ Complete![/bold green]")
    console.print(f"[green]✓[/green] {success} files redacted successfully")
    if errors:
        console.print(f"[red]✗[/red] {len(errors)} files failed")
        for filepath, error in errors:
            console.print(f"  • {Path(filepath).name}: {error}")

if __name__ == '__main__':
    main()
