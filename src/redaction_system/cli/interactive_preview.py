"""Interactive TUI Preview for Document Redaction"""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, RichLog
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from rich.text import Text
from rich.panel import Panel

class DocumentPreview(App):
    """Interactive document preview with entity highlighting"""
    
    CSS = """
    RichLog {
        height: 1fr;
        border: solid green;
    }
    
    #status {
        height: 3;
        border: solid blue;
    }
    """
    
    BINDINGS = [
        Binding("left", "previous_page", "Previous Page", show=True),
        Binding("right", "next_page", "Next Page", show=True),
        Binding("up", "scroll_up", "Scroll Up", show=False),
        Binding("down", "scroll_down", "Scroll Down", show=False),
        Binding("a", "approve", "Approve & Redact", show=True),
        Binding("q", "quit", "Cancel", show=True),
    ]
    
    def __init__(self, chunks, entities_by_chunk):
        """
        Initialize preview
        
        Args:
            chunks: List of document chunks/pages
            entities_by_chunk: Dict mapping chunk index to list of entities
        """
        super().__init__()
        self.chunks = chunks
        self.entities_by_chunk = entities_by_chunk
        self.current_page = 0
        self.approved = False
        self.total_entities = sum(len(ents) for ents in entities_by_chunk.values())
    
    def compose(self) -> ComposeResult:
        """Create UI layout"""
        yield Header()
        yield VerticalScroll(RichLog(id="content", wrap=True, markup=True))
        yield Static(id="status")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app starts"""
        self.title = "Redaction Preview"
        self.sub_title = f"Total: {len(self.chunks)} pages, {self.total_entities} entities"
        self.render_page()
    
    def render_page(self) -> None:
        """Render current page with entity highlights"""
        content_log = self.query_one("#content", RichLog)
        content_log.clear()
        
        # Get current page data
        chunk = self.chunks[self.current_page]
        page_text = chunk['text']
        entities = self.entities_by_chunk.get(self.current_page, [])
        
        # Create Rich Text with highlights
        highlighted_text = Text()
        last_pos = 0
        
        # Sort entities by start position
        sorted_entities = sorted(entities, key=lambda e: e['start'])
        
        for entity in sorted_entities:
            # Add text before entity
            highlighted_text.append(page_text[last_pos:entity['start']])
            
            # Add highlighted entity
            entity_text = page_text[entity['start']:entity['end']]
            highlighted_text.append(
                entity_text,
                style="black on red bold"  # Red background highlight
            )
            
            # Add entity label below
            entity_label = f" [{entity['type']} {entity['score']*100:.0f}%]"
            highlighted_text.append(entity_label, style="dim italic")
            
            last_pos = entity['end']
        
        # Add remaining text
        highlighted_text.append(page_text[last_pos:])
        
        # Display in panel
        panel = Panel(
            highlighted_text,
            title=f"Page {self.current_page + 1}/{len(self.chunks)}",
            border_style="green"
        )
        content_log.write(panel)
        
        # Update status bar
        self.update_status()
    
    def update_status(self) -> None:
        """Update status bar with current page info"""
        entities_on_page = len(self.entities_by_chunk.get(self.current_page, []))
        status = self.query_one("#status", Static)
        
        status_text = Text()
        status_text.append(f"Page {self.current_page + 1}/{len(self.chunks)} | ", style="bold cyan")
        status_text.append(f"{entities_on_page} entities on this page | ", style="yellow")
        status_text.append(f"{self.total_entities} total in document\n", style="green")
        status_text.append("Navigate: ←→ Pages  ↑↓ Scroll | ", style="dim")
        status_text.append("[A]pprove  [Q]uit", style="bold")
        
        status.update(status_text)
    
    def action_previous_page(self) -> None:
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()
        else:
            self.notify("Already at first page", severity="information")
    
    def action_next_page(self) -> None:
        """Go to next page"""
        if self.current_page < len(self.chunks) - 1:
            self.current_page += 1
            self.render_page()
        else:
            self.notify("Already at last page", severity="information")
    
    def action_scroll_up(self) -> None:
        """Scroll up within current page"""
        content = self.query_one("#content", RichLog)
        content.scroll_up()
    
    def action_scroll_down(self) -> None:
        """Scroll down within current page"""
        content = self.query_one("#content", RichLog)
        content.scroll_down()
    
    def action_approve(self) -> None:
        """Approve redaction and exit"""
        self.approved = True
        self.exit()
    
    def action_quit(self) -> None:
        """Cancel and exit"""
        self.approved = False
        self.exit()


def show_interactive_preview(filepath, prompt, orchestrator):
    """
    Show interactive TUI preview
    
    Returns:
        bool: True if approved, False if cancelled
    """
    from rich.console import Console
    console = Console()
    
    try:
        # Get parser and extract chunks
        parser = orchestrator._get_parser(filepath)
        chunks = parser.parse(filepath)
        
        # Get entity config
        from redaction_system.agent import interpret_prompt
        config = interpret_prompt(prompt)
        
        # Analyze all chunks and collect entities
        console.print("[cyan]🔍 Analyzing document...[/cyan]")
        entities_by_chunk = {}
        
        for i, chunk in enumerate(chunks):
            text = chunk['text']
            results = orchestrator.redactor.analyzer.analyze(
                text=text,
                entities=config.entities,
                language='en'
            )
            
            # Store entities with their positions
            entities_by_chunk[i] = []
            for result in results:
                entities_by_chunk[i].append({
                    'start': result.start,
                    'end': result.end,
                    'type': result.entity_type,
                    'score': result.score,
                })
        
        total_entities = sum(len(ents) for ents in entities_by_chunk.values())
        
        if total_entities == 0:
            console.print("[yellow]⚠️  No entities detected[/yellow]")
            from rich.prompt import Confirm
            return Confirm.ask("Proceed anyway?")
        
        console.print(f"[green]✓[/green] Found {total_entities} entities across {len(chunks)} pages")
        console.print("[dim]Launching interactive preview...[/dim]\n")
        
        # Launch TUI
        app = DocumentPreview(chunks, entities_by_chunk)
        app.run()
        
        return app.approved
        
    except Exception as e:
        console.print(f"[red]❌ Preview failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False
