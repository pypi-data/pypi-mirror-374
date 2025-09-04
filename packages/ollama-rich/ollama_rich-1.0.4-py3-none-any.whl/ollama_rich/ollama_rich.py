from ollama import Client
from ollama._types import ResponseError
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from .utils import progress


console = Console()

class OllamaRichClient:
    def __init__(self, host=''):
        self.client = Client(host=host)

    def chat_and_display(self, model, messages):
        response = self.client.chat(
            model=model,
            stream=True,
            messages=messages,
        )

        full_content = ""
        with Live(Markdown(full_content), console=console, refresh_per_second=2) as live:
            for chunk in response:
                full_content += chunk['message']['content']
                live.update(Markdown(full_content))


    def chat(self, model, messages):
        with console.status("[bold green]Generating response...", spinner="dots"):
            response = self.client.chat(
                model=model,
                stream=False,
                messages=messages,
            )
        return Markdown(response['message']['content'])
    
    def models(self):
        try:
            return self.client.list()
        except ConnectionError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return []
        
    def models_name_list(self):
        try:
            models = self.client.list()
            return [model.get('model') for model in models.get('models', [])]
        except ConnectionError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return []

    def model_info(self, model):
        try:
            models = self.client.list()
            for m in models.get('models', []):
                if m.get('model') == model:
                    return m
            return {}
        except ConnectionError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return {}
    
    def ps(self):
        try:
            return self.client.ps()
        except ConnectionError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return []
    
    def load(self, model):
        try:
            # Show spinner with Rich
            with console.status(
                f"[bold cyan]⏳ Please wait... loading model [yellow]{model}[/yellow] into memory[/bold cyan]",
                spinner="dots"
            ):
                res = self.client.generate(model=model, prompt="")  # empty prompt loads model

            if res.get("done", False):
                console.print(f"[bold green]✅ Model '{model}' loaded into memory successfully.[/bold green]")
            else:
                console.print(f"[bold red]❌ Error loading model '{model}': {res.get('status', 'Unknown error')}[/bold red]")
        except ResponseError as e:
            console.print(f"[bold red]❌ Response error while loading model '{model}': {e}[/bold red]")
        except ConnectionError as e:
            console.print(f"[bold red]❌ Connection error while loading model '{model}': {e}[/bold red]")

    def pull(self, model, stream: bool = True):
        try:
            if stream:
                console.print(f"[bold green] Pulling model [bold yellow]{model}[/bold yellow] with streaming...[/ bold green]")
                with progress:
                    task_id = None
                    for chunk in self.client.pull(model, stream=True):
                        # Initialize task when total size is known
                        if 'total' in chunk and task_id is None:
                            total_bytes = chunk['total']
                            task_id = progress.add_task("Downloading", total=total_bytes)

                        # Update progress
                        if task_id is not None and 'completed' in chunk:
                            progress.update(task_id, completed=chunk['completed'])
                    
                console.print(f"[bold green]:heavy_check_mark: Model '{model}' pulled successfully.[/bold green]")

            else:
                with console.status("[bold green]Pulling...") as status:
                    res = self.client.pull(model)
                    if res["status"] == "success":
                        console.print(f" [bold green]:heavy_check_mark: Model '{model}' pulled successfully.[/bold green]")
                    else:
                        console.print(f"[bold red]Error pulling model '{model}': {res['status']}[/bold red]")
        except ConnectionError as e:
            console.print(f"[bold red]Error pulling model '{model}': {e}[/bold red]")

    def delete(self, model):
        try:
            confirm = console.input(f"[bold yellow]Are you sure you want to delete the model '{model}'? This action cannot be undone. (y/n): [/bold yellow]")
            if confirm.lower() != 'y':
                console.print("[bold cyan]Deletion cancelled by user.[/bold cyan]")
                return
            console.print(f"[bold green]Deleting model [bold yellow]{model}[/bold yellow]...[/bold green]")
            res = self.client.delete(model)
            if res["status"] == "success":
                console.print(f"[bold green]✅ Model '{model}' deleted successfully.[/bold green]")
            else:
                console.print(f"[bold red]❌ Error deleting model '{model}': {res['status']}[/bold red]")
        except ResponseError as e:
            console.print(f"[bold red]❌ Response error while deleting model '{model}': {e}[/bold red]")
        except ConnectionError as e:
            console.print(f"[bold red]❌ Connection error while deleting model '{model}': {e}[/bold red]")
