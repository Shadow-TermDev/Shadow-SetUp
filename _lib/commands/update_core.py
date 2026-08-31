"""Update-core command — update framework from GitHub."""

from _lib.commands import Command

class UpdateCoreCommand(Command):
    name = "update-core"
    aliases = ["update core"]
    description = "Update framework from GitHub"
    usage = "update-core"
    examples = ["update-core        # Update framework"]
    tui_label = "[7] Update framework"
    tui_position = 70
    tui_section = "main"

    def execute(self, args=None):
        import subprocess
        import shutil
        from pathlib import Path
        from _lib.utils.ui import console, success_box, error_box
        from _lib.utils import SHADOW_DATA

        temp_dir = SHADOW_DATA / "cache" / "shadow-update"

        with console.status("[bold cyan]Downloading update...[/bold cyan]", spinner="dots") as status:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)

                result = subprocess.run([
                    "git", "clone", "--depth=1",
                    "https://github.com/Shadow-TermDev/Shadow-SetUp.git",
                    str(temp_dir)
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    error_box("Update failed", "Could not download update")
                    return

                status.update("[bold cyan]Installing files...[/bold cyan]")

                # Copy _lib
                lib_src = temp_dir / "_lib"
                lib_dst = SHADOW_DATA / "_lib"
                if lib_src.exists():
                    if lib_dst.exists():
                        shutil.rmtree(lib_dst)
                    shutil.copytree(lib_src, lib_dst)

                # Copy dotfiles (all except rices, but preserve existing rices)
                dotfiles_src = temp_dir / "dotfiles"
                dotfiles_dst = SHADOW_DATA / "dotfiles"
                if dotfiles_src.exists():
                    dotfiles_dst.mkdir(parents=True, exist_ok=True)
                    # Copy every top-level file/dir except 'rices'
                    for item in dotfiles_src.iterdir():
                        if item.name == "rices":
                            continue
                        dst = dotfiles_dst / item.name
                        if item.is_dir():
                            if dst.exists():
                                shutil.rmtree(dst)
                            shutil.copytree(item, dst)
                        else:
                            shutil.copy2(item, dst)

                    # Sync active home file ~/.zshrc from the new dotfiles
                    # This was missing and caused .zshrc to stay on old version
                    src_zshrc = dotfiles_dst / ".zshrc"
                    dst_zshrc = Path.home() / ".zshrc"
                    if src_zshrc.exists():
                        try:
                            # Backup if differs
                            if dst_zshrc.exists():
                                try:
                                    if dst_zshrc.read_text() != src_zshrc.read_text():
                                        from _lib.utils import backup_file
                                        backup_file(dst_zshrc)
                                except Exception:
                                    pass
                            shutil.copy2(src_zshrc, dst_zshrc)
                            console.print("  [dim].zshrc synced to home[/dim]")
                        except Exception as e:
                            console.print(f"  [warning]Could not sync .zshrc: {e}[/warning]")

                    # Also sync base aliases if needed (kept in dotfiles, sourced by .zshrc)
                    # No need to copy to home, just ensure dotfiles version is fresh

                # Copy .version
                version_src = temp_dir / ".version"
                version_dst = SHADOW_DATA / ".version"
                if version_src.exists():
                    shutil.copy2(version_src, version_dst)

                # Update wrappers
                bin_dir = Path.home() / ".local" / "bin"
                bin_dir.mkdir(parents=True, exist_ok=True)

                for cmd_name in ["sw", "shadow"]:
                    wrapper = bin_dir / cmd_name
                    wrapper.write_text(f"""#!/data/data/com.termux/files/usr/bin/bash
exec python3 "{SHADOW_DATA}/_lib/cli.py" "$@"
""")
                    wrapper.chmod(0o755)

                shutil.rmtree(temp_dir)

            except Exception as e:
                error_box("Update failed", str(e))
                return

        success_box("Update complete!", "Shadow-SetUp is now up to date")
