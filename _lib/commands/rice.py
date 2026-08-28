"""Rice command — manage RICE themes."""

from _lib.commands import Command

class RiceCommand(Command):
    name = "rice"
    aliases = []
    description = "Manage RICE themes"
    usage = "rice [list|set|install|delete|backup|check]"
    examples = [
        "rice                 # List RICEs",
        "rice list            # List available RICEs",
        "rice set kawaii      # Activate kawaii RICE",
        "rice check           # Show active RICE",
    ]
    tui_label = "[6] Manage RICEs"
    tui_position = 60
    tui_section = "main"
    has_submenu = True

    def execute(self, args: list[str] = None) -> None:
        from _lib.utils.ui import console, banner, error_box

        if not args:
            self._rice_list()
            return

        subcmd = args[0]
        subargs = args[1:]

        if subcmd == "list" or subcmd == "ls":
            self._rice_list()
        elif subcmd == "set" and subargs:
            self._rice_set(subargs[0])
        elif subcmd == "install" and subargs:
            self._rice_install(subargs[0])
        elif subcmd == "delete" and subargs:
            self._rice_delete(subargs[0])
        elif subcmd == "backup" and subargs:
            self._rice_backup(subargs[0])
        elif subcmd == "check" or subcmd == "ck":
            self._rice_check()
        else:
            error_box("Error", "Usage: rice [list|set|install|delete|backup|check] [args]")

    def _rice_list(self) -> None:
        from _lib.utils.ui import console, banner
        from _lib.utils.rice_manager import fetch_official_rices, list_local_rices, get_active_rice

        banner()
        official = fetch_official_rices()
        local = list_local_rices()
        local_names = {r["name"] for r in local}
        active = get_active_rice()

        console.print("[bold]Official RICEs:[bold]")
        for name, info in sorted(official.items()):
            installed = " [dim]+installed[/dim]" if name in local_names else ""
            marker = " [green]*[/green]" if name == active else ""
            console.print(f"  [cyan]{name}[/cyan]{marker}{installed} — {info.get('description', '')}")

        if local:
            console.print()
            console.print("[bold]Local RICEs:[bold]")
            for rice in local:
                if rice["name"] not in official:
                    marker = " [green]*[/green]" if rice["name"] == active else ""
                    console.print(f"  [cyan]{rice['name']}[/cyan]{marker}")

        console.print()
        console.print("[dim]* = active | + = downloaded[/dim]")

    def _rice_set(self, rice_name: str) -> None:
        from _lib.utils.ui import banner
        from _lib.utils.rice_manager import download_and_apply_rice
        banner()
        download_and_apply_rice(rice_name)

    def _rice_install(self, url: str) -> None:
        from _lib.utils.ui import banner
        from _lib.utils.rice_manager import install_custom_rice
        banner()
        install_custom_rice(url)

    def _rice_delete(self, rice_name: str) -> None:
        from _lib.utils.ui import banner
        from _lib.utils.rice_manager import delete_rice
        banner()
        delete_rice(rice_name)

    def _rice_backup(self, rice_name: str) -> None:
        from _lib.utils.ui import banner
        from _lib.utils.rice_manager import backup_current_rice
        banner()
        backup_current_rice(rice_name)

    def _rice_check(self) -> None:
        from _lib.utils.ui import console, banner, success_box, error_box
        from _lib.utils.rice_manager import get_active_rice, list_local_rices

        banner()
        active = get_active_rice()
        local = list_local_rices()

        if active:
            success_box("Active RICE", active)
        else:
            error_box("Active RICE", "None set")

        if local:
            console.print()
            console.print("[bold]Installed RICEs:[bold]")
            for rice in local:
                marker = " [green]*[/green]" if rice["name"] == active else ""
                console.print(f"  [cyan]{rice['name']}[/cyan]{marker}")
        else:
            console.print()
            console.print("[dim]No RICEs installed[/dim]")
