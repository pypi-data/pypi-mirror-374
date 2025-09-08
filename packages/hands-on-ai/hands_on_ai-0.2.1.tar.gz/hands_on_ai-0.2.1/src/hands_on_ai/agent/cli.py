"""
CLI for the agent module.
"""

import typer
from .commands import ask, tools, interactive, web

app = typer.Typer(help="Agent - ReAct-style reasoning with tool use")

# Add command modules
app.add_typer(ask.app, name="ask", help="Ask a question using agent tools")
app.add_typer(tools.app, name="tools", help="List available agent tools")
app.add_typer(interactive.app, name="interactive", help="Run interactive agent chat")
app.add_typer(web.app, name="web", help="Start web interface for the agent")

# Default command - show help
@app.callback(invoke_without_command=True)
def main():
    """
    Agent module - ReAct-style reasoning with tool use.
    
    Use 'agent ask' to ask a question, 'agent interactive' for a chat session,
    or 'agent web' to launch the web interface.
    """
    import typer
    typer.echo("Use 'agent --help' for available commands.")


if __name__ == "__main__":
    app()