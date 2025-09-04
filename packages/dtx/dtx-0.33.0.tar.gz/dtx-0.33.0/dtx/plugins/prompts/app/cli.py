import yaml
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from dtx_models.prompts import BaseMultiTurnConversation
from dtx_models.template.prompts.app import (
    AppPrompt,
    AppPromptParam,
    AppPromptTemplate,
    AppPromptTemplateConfig,
    AppPromptTemplates,
)

# RoleType and Turn are already defined in your codebase
from dtx_models.prompts import RoleType, Turn  


class AppPromptParamBuilder:
    """Helps build parameters interactively for App prompts."""

    def __init__(self, console: Console):
        self.console = console

    def build_params(self, input_variables: List[str]) -> List[AppPromptParam]:
        params = []
        for var_name in input_variables:
            replacement_value = Prompt.ask(
                f"[bold cyan]Enter a default value for parameter '{var_name}'[/]",
                default="default_value",
            )
            params.append(AppPromptParam(name=var_name, value=replacement_value))
        return params

    def manual_params(self) -> List[AppPromptParam]:
        params = []
        total_params = IntPrompt.ask(
            "[bold cyan]How many parameters do you want to define?[/]", default=1
        )
        for idx in range(total_params):
            var_name = Prompt.ask(
                f"[bold cyan]Enter the name of parameter #{idx + 1}[/]"
            ).strip()
            replacement_value = Prompt.ask(
                f"[bold cyan]Enter a default value for parameter '{var_name}'[/]",
                default="default_value",
            )
            params.append(AppPromptParam(name=var_name, value=replacement_value))
        return params


class AppPromptGenerator:
    """Interactive CLI tool for building App prompts manually."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.prompts: List[AppPromptTemplate] = []

    def _build_conversation(self) -> BaseMultiTurnConversation:
        """Build a multi-turn conversation interactively."""

        turns = []
        self.console.print(
            "[bold cyan]Let's build a multi-turn conversation. Leave role/message blank to stop.[/]"
        )

        while True:
            role_input = Prompt.ask(
                "[bold cyan]Enter role (USER/ASSISTANT/SYSTEM or blank to stop)[/]",
                default="",
            ).strip()
            if not role_input:
                break

            try:
                role = RoleType(role_input.upper())
            except ValueError:
                self.console.print("[red]Invalid role, defaulting to USER[/red]")
                role = RoleType.USER

            message = Prompt.ask(
                "[bold cyan]Enter message (or blank to stop)[/]", default=""
            ).strip()
            if not message:
                break

            turns.append(Turn(role=role, message=message))

            cont = Prompt.ask(
                "[bold cyan]Add another turn? (yes/no)[/]", default="yes"
            ).lower()
            if cont != "yes":
                break

        return BaseMultiTurnConversation(turns=turns)

    def _get_user_input(self) -> Optional[AppPromptTemplate]:
        """Ask user for details to create an AppPromptTemplate."""
        full_name = Prompt.ask(
            "[bold cyan]Enter the full name of the app repo (e.g., myteam/myapp)[/]"
        ).strip()

        # Build conversation
        conversation = self._build_conversation()
        input_vars = []
        if conversation.turns:
            num_vars = IntPrompt.ask(
                "[bold cyan]How many input variables do you want to define?[/]",
                default=0,
            )
            for i in range(num_vars):
                var_name = Prompt.ask(
                    f"[bold cyan]Enter name of input variable #{i+1}[/]"
                ).strip()
                input_vars.append(var_name)

        app_prompt = AppPrompt(conversation=conversation, input_variables=input_vars)

        # Build params
        builder = AppPromptParamBuilder(self.console)
        params = builder.build_params(input_vars) if input_vars else builder.manual_params()

        config = AppPromptTemplateConfig(
            full_name=full_name, prompt=app_prompt, params=params
        )
        return AppPromptTemplate(config=config)

    def _display_provider(self, provider: AppPromptTemplate):
        """Display provider details in a table."""
        table = Table(
            title="✅ App Prompt Configuration",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="bold green")

        data = provider.model_dump()
        table.add_row("Provider", data["provider"])
        table.add_row("Full Name", data["config"]["full_name"])

        prompt = provider.config.prompt
        if prompt:
            table.add_row("Input Variables", ", ".join(prompt.input_variables))

        self.console.print(table)

    def run(self) -> Optional[AppPromptTemplates]:
        """Run the interactive CLI tool."""
        self.console.print(Panel("[bold green]App Prompt Generator[/]", expand=False))

        while True:
            provider = self._get_user_input()
            if provider:
                self._display_provider(provider)
                self.prompts.append(provider)

            if (
                Prompt.ask(
                    "[bold cyan]Do you want to add another app prompt? (yes/no)[/]",
                    default="no",
                ).lower()
                != "yes"
            ):
                break

        if not self.prompts:
            self.console.print("[bold yellow]No prompts were created. Exiting.[/]")
            return None

        self.console.print("[bold green]🎉 App prompts generated successfully![/]")
        return AppPromptTemplates(prompts=self.prompts)

    def save_yaml(self, prompts: AppPromptTemplates, filename: Optional[str] = None):
        """Save prompts to a YAML file."""
        filename = filename or Prompt.ask(
            "[bold magenta]Enter filename to save as (default: app_prompts.yaml)[/]",
            default="app_prompts.yaml",
        )
        yaml_output = yaml.dump(prompts.model_dump(), sort_keys=False)
        with open(filename, "w") as f:
            f.write(yaml_output)
        self.console.print(f"[bold green]✅ Configuration saved to {filename}[/]")


if __name__ == "__main__":
    generator = AppPromptGenerator()
    prompts = generator.run()
    if prompts:
        generator.save_yaml(prompts)
