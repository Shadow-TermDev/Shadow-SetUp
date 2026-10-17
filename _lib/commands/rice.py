"""Rice command — manage RICE themes."""

from _lib.commands import Command

class RiceCommand(Command):
    name = "rice"
    aliases = []
    description = "Manage RICE themes"
    usage = "rice [list|set|install|delete|backup|check|reset|update]"
    examples = [
        "rice                 # List RICEs",
        "rice list            # List available RICEs",
        "rice set kawaii      # Activate kawaii RICE",
        "rice set kawaii -f   # Re-apply local RICE (no re-download)",
        "rice update nordic   # Update rice from git",
        "rice reset           # Reset to default rice",
        "rice check           # Show active RICE",
    ]
    tui_label = "[6] Manage RICEs"
    tui_position = 60
    tui_section = "main"
    has_submenu = True

    subcommands = {
        "list":    "List available RICEs",
        "set":     "Set active RICE",
        "check":   "Show active RICE",
        "install": "Install RICE from git",
        "update":  "Update RICE from git",
        "delete":  "Delete a local RICE",
        "backup":  "Backup current RICE",
        "reset":   "Reset to default rice",
    }

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
            force = "--force" in subargs or "-f" in subargs
            subargs = [a for a in subargs if a not in ("--force", "-f")]
            self._rice_set(subargs[0], force=force)
        elif subcmd == "install" and subargs:
            self._rice_install(subargs[0])
        elif subcmd == "delete" and subargs:
            self._rice_delete(subargs[0])
        elif subcmd == "backup" and subargs:
            self._rice_backup(subargs[0])
        elif subcmd == "check" or subcmd == "ck":
            self._rice_check()
        elif subcmd == "reset":
            self._rice_reset()
        elif subcmd == "update" and subargs:
            self._rice_update(subargs[0])
        elif subcmd == "update":
            self._rice_update_all()
        else:
            error_box("Error", "Usage: rice [list|set|install|delete|backup|check|reset|update] [args]")

    def _rice_list(self) -> None:
        from _lib.utils.ui import console, banner
        from _lib.utils.rice_manager import fetch_official_rices, list_local_rices, get_active_rice
        from pathlib import Path

        banner()
        official = fetch_official_rices()
        local = list_local_rices()
        local_names = {r["name"] for r in local}
        incomplete_names = {r["name"] for r in local if r.get("incomplete")}
        # Mapa nombre manifest -> dir para resolver alias nordic <-> nordic-rice-termux
        manifest_to_dir = {}
        for r in local:
            mname = r["manifest"].get("name")
            if mname:
                manifest_to_dir[mname] = r["name"]
        active = get_active_rice()

        def _is_active(official_key: str) -> bool:
            # No active RICE: nothing can match (None == None used to be True)
            if active is None:
                return False
            if official_key == active:
                return True
            # alias manifest.name
            if manifest_to_dir.get(official_key) == active:
                return True
            # reverse: active es manifest.name
            for r in local:
                if r["name"] == active and r["manifest"].get("name") == official_key:
                    return True
                if r["name"] == official_key and r["manifest"].get("name") == active:
                    return True
            return False

        console.print("[bold]Official RICEs:[bold]")
        for name, info in sorted(official.items()):
            installed = name in local_names or manifest_to_dir.get(name) in local_names
            if not installed:
                installed_str = ""
            elif name in incomplete_names or manifest_to_dir.get(name) in incomplete_names:
                installed_str = " [yellow]+incomplete[/yellow]"
            else:
                installed_str = " [dim]+installed[/dim]"
            marker = " [green]*[/green]" if _is_active(name) else ""
            # tag externo vs bundled
            tag = ""
            if info.get("external"):
                tag = " [dim](external)[/dim]"
            elif info.get("local"):
                tag = ""
            desc = info.get("description", "")
            # Si tiene repo, mostrar hint
            console.print(f"  [cyan]{name}[/cyan]{marker}{installed_str}{tag} — {desc}")

        # Local = community/custom (no están en official ni via alias)
        # Pero mostrar todos los custom con etiqueta
        custom = []
        for rice in local:
            is_official = rice["name"] in official or rice["manifest"].get("name") in official
            # También considerar external repo match
            if not is_official:
                # check if any official repo maps to this dir name
                for k, v in official.items():
                    repo = v.get("repo", "")
                    if repo and (repo.rstrip("/").endswith(f"/{rice['name']}") or repo.rstrip("/").endswith(f"/{rice['name']}.git") or k == rice["manifest"].get("name")):
                        is_official = True
                        break
            if not is_official:
                custom.append(rice)

        if custom:
            console.print()
            console.print("[bold]Community / Local RICEs:[bold]")
            for rice in custom:
                is_act = rice["name"] == active or (
                    active is not None and rice["manifest"].get("name") == active
                )
                marker = " [green]*[/green]" if is_act else ""
                # Detectar source meta
                meta_path = Path(rice["path"]).parent / f".{rice['name']}.meta.json" if False else None
                # mostrar descripción del manifest si existe
                desc = rice["manifest"].get("description", "")
                desc_str = f" — {desc}" if desc else ""
                incomplete = " [yellow](incomplete)[/yellow]" if rice.get("incomplete") else ""
                console.print(f"  [cyan]{rice['name']}[/cyan]{marker} [dim](community)[/dim]{incomplete}{desc_str}")
        elif not custom and local:
            # Todos son oficiales, mostrar sección local informativa pero vacía
            console.print()
            console.print("[dim]Local RICEs: todos los instalados son oficiales (ver arriba).[/dim]")
            console.print("[dim]Community rices instalados vía [cyan]sw rice install <url>[/cyan] aparecerán aquí.[/dim]")

        console.print()
        console.print("[dim]* = active | + = downloaded | (external) = repo aparte[/dim]")

    def _rice_set(self, rice_name: str, force: bool = False) -> None:
        from _lib.utils.ui import banner
        from _lib.utils.rice_manager import download_and_apply_rice
        banner()
        download_and_apply_rice(rice_name, force=force)

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
        backup_current_rice(rice_name, ask=True)

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
                is_act = rice["name"] == active or (
                    active is not None and rice["manifest"].get("name") == active
                )
                marker = " [green]*[/green]" if is_act else ""
                incomplete = " [yellow](incomplete)[/yellow]" if rice.get("incomplete") else ""
                console.print(f"  [cyan]{rice['name']}[/cyan]{marker}{incomplete}")
        else:
            console.print()
            console.print("[dim]No RICEs installed[/dim]")

    def _rice_reset(self) -> None:
        from _lib.utils.ui import banner
        from _lib.utils.rice_manager import reset_rice_files
        banner()
        reset_rice_files()

    def _rice_update(self, rice_name: str) -> None:
        from _lib.utils.ui import banner
        from _lib.utils.rice_manager import update_rice
        banner()
        update_rice(rice_name)

    def _rice_update_all(self) -> None:
        from _lib.utils.ui import banner, console
        from _lib.utils.rice_manager import list_local_rices, update_rice
        banner()
        local = list_local_rices()
        if not local:
            console.print("[dim]No RICEs installed[/dim]")
            return
        for rice in local:
            update_rice(rice["name"])
