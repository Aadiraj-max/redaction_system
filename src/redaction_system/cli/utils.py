"""CLI Utility Functions"""
from pathlib import Path
from rich.console import Console

console = Console()

SUPPORTED_FORMATS = {'.pdf', '.docx', '.xlsx', '.xls', '.csv', '.md', '.txt'}

def scan_directory(dirpath):
    """
    Scan directory for supported files
    
    Returns:
        dict: {
            'files': list of file paths,
            'summary': {format: count}
        }
    """
    dirpath = Path(dirpath)
    files = []
    summary = {}
    
    for file in dirpath.rglob('*'):
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
            files.append(file)
            ext = file.suffix.lower().lstrip('.')
            summary[ext] = summary.get(ext, 0) + 1
    
    return {
        'files': files,
        'summary': summary
    }

def format_error(error):
    """Display formatted error message"""
    console.print(f"\n[bold red]❌ Error:[/bold red] {error}")
