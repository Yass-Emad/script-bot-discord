"""
CYBERBOT CLI v3.4 - Ghost Commander Fixed
Fixed: Crash/reopen issue with better error handling
"""

import sys
import os
import asyncio
import time
import datetime
import threading
from pathlib import Path
from typing import Optional

import discord
import requests
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

console = Console(theme=Theme({
    "banner": "bold bright_cyan",
    "primary": "bold cyan",
    "secondary": "bold bright_magenta",
    "accent": "bold bright_blue",
    "success": "bold bright_green",
    "warning": "bold bright_yellow",
    "danger": "bold bright_red",
    "muted": "dim cyan",
    "border": "bright_blue",
}), width=76)

class CyberBotApp:
    def __init__(self):
        self.token: Optional[str] = None
        self.bot_user_data: Optional[dict] = None
        self.client: Optional[discord.Client] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.bot_thread: Optional[threading.Thread] = None
        self.is_connected: bool = False
        self.timer_task: Optional[asyncio.Task] = None
        self.timer_end_time: Optional[float] = None
        self.timer_label: Optional[str] = None

    def print_banner(self):
        console.clear()
        banner = Text()
        banner.append("Claude Code ", style="bold cyan")
        banner.append("• ", style="dim")
        banner.append("Discord CLI", style="bold white")
        banner.append(" v3.4", style="dim")
        
        console.print(Panel(
            banner,
            title="[bold cyan]✦ GHOST COMMANDER ✦[/bold cyan]",
            subtitle="[dim]Discord Bot Management[/dim]",
            border_style="cyan",
            width=70
        ))
        console.print()

    def validate_token(self, token: str) -> Optional[dict]:
        clean_token = token.strip().strip('"')
        headers = {"Authorization": f"Bot {clean_token}"}
        try:
            resp = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None

    def start_bot_client(self, token: str) -> bool:
        clean_token = token.strip().strip('"')
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True

        self.client = discord.Client(intents=intents)
        self.loop = asyncio.new_event_loop()

        ready_event = threading.Event()
        login_error = [None]

        @self.client.event
        async def on_ready():
            self.is_connected = True
            ready_event.set()

        def run_loop():
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(self.client.start(clean_token))
            except Exception as e:
                login_error[0] = str(e)
                ready_event.set()

        self.bot_thread = threading.Thread(target=run_loop, daemon=True)
        self.bot_thread.start()

        success = ready_event.wait(timeout=15)
        if success and self.is_connected:
            return True
        else:
            if login_error[0]:
                console.print(f"[danger]Connection error: {login_error[0]}[/danger]")
            return False

    def prompt_token_login(self) -> bool:
        self.print_banner()
        console.print(Panel("AUTHENTICATION", style="secondary", width=70, padding=(0, 2)))
        console.print("[dim]  Paste token or use saved token.txt[/dim]\n")

        token_file = Path("token.txt")
        saved_token = ""
        if token_file.exists():
            try:
                saved_token = token_file.read_text(encoding="utf-8").strip()
                if saved_token:
                    use_saved = questionary.confirm("  Use saved token?", default=True).ask()
                    if not use_saved:
                        saved_token = ""
            except Exception:
                pass

        while True:
            if not saved_token:
                token = questionary.password("  Bot Token:").ask()
                if not token:
                    continue
                token = token.strip().strip('"')
            else:
                token = saved_token
                saved_token = ""

            with console.status("[accent]Verifying...[/accent]", spinner="dots"):
                user_data = self.validate_token(token)

            if not user_data:
                console.print("[danger]Invalid token![/danger]\n")
                continue

            bot_tag = f"{user_data.get('username')}#{user_data.get('discriminator', '0000')}"
            console.print(f"[success]✓ Verified as {bot_tag}[/success]")

            if not token_file.exists():
                save_choice = questionary.confirm("  Save token?", default=True).ask()
                if save_choice:
                    token_file.write_text(token, encoding="utf-8")

            with console.status("[accent]Connecting...[/accent]", spinner="dots"):
                connected = self.start_bot_client(token)

            if connected:
                self.token = token
                self.bot_user_data = user_data
                console.print("[success]✓ Connected![/success]\n")
                time.sleep(1)
                return True
            else:
                console.print("[danger]Connection failed.[/danger]\n")

    def show_dashboard(self):
        self.print_banner()
        if not self.client or not self.client.user:
            console.print("[warning]Not connected.[/warning]")
            return

        bot = self.client.user
        guilds = self.client.guilds
        total_members = sum(g.member_count or 0 for g in guilds)
        ping = round(self.client.latency * 1000, 1)

        table = Table(show_header=False, width=70)
        table.add_column("Property", style="bold cyan", width=24)
        table.add_column("Value", style="bright_white")

        table.add_row("Bot", f"[bold white]{bot.name}[/bold white]")
        table.add_row("Ping", f"[bold green]{ping}ms[/bold green]")
        table.add_row("Guilds", f"[bold magenta]{len(guilds)}[/bold magenta]")
        table.add_row("Members", f"[bold green]{total_members:,}[/bold green]")

        console.print(Panel(table, title="[bold cyan]Status[/bold cyan]", border_style="cyan", width=74))

    def run_coroutine(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=120)

    def send_dm_menu(self):
        self.print_banner()
        console.print(Panel("SEND DM", style="secondary", width=70, padding=(0, 2)))
        console.print()

        msg = questionary.text("Message:").ask()
        if not msg:
            return

        ids_input = questionary.text("User IDs (comma-separated):", placeholder="123, 456").ask()
        if not ids_input:
            return

        valid_ids = [int(uid.strip()) for uid in ids_input.split(',') if uid.strip().isdigit()]
        if not valid_ids:
            console.print("[danger]No valid IDs![/danger]")
            questionary.press_any_key_to_continue().ask()
            return

        confirm = questionary.confirm(f"Send to {len(valid_ids)} users?", default=False).ask()
        if not confirm:
            return

        async def send_all():
            ok, fail = 0, []
            for uid in valid_ids:
                try:
                    u = await self.client.fetch_user(uid)
                    await u.send(msg)
                    ok += 1
                    await asyncio.sleep(0.5)
                except Exception as e:
                    fail.append(f"{uid}: {str(e)[:30]}")
            return ok, fail

        with console.status("Sending...", spinner="dots"):
            try:
                ok, fail = self.run_coroutine(send_all())
            except Exception as e:
                console.print(f"[danger]Error: {e}[/danger]")
                questionary.press_any_key_to_continue().ask()
                return

        console.print(f"[success]✓ Sent: {ok}, Failed: {len(fail)}[/success]")
        console.print()
        questionary.press_any_key_to_continue().ask()

    def moderation_action_menu(self, action_type: str):
        self.print_banner()
        titles = {
            "kick_single": "SINGLE KICK",
            "ban_single": "SINGLE BAN",
            "kick_mass": "MASS KICK",
            "ban_mass": "MASS BAN",
            "nuke": "SERVER NUKE",
            "backup": "BACKUP"
        }
        console.print(Panel(titles.get(action_type, action_type), style="danger", width=70, padding=(0, 2)))
        console.print()

        guilds = self.client.guilds
        if not guilds:
            console.print("[warning]No servers.[/warning]")
            questionary.press_any_key_to_continue().ask()
            return

        server_choices = [questionary.Choice(title=g.name, value=g) for g in guilds]
        guild = questionary.select("Target Server:", choices=server_choices).ask()
        if not guild:
            return

        try:
            if action_type == "kick_single":
                target_id = questionary.text("User ID:").ask()
                if target_id and target_id.isdigit():
                    async def do_kick():
                        m = guild.get_member(int(target_id)) or await guild.fetch_member(int(target_id))
                        if m:
                            await m.kick(reason="Kick")
                            console.print(f"[success]✓ Kicked {m}[/success]")
                    self.run_coroutine(do_kick())

            elif action_type == "nuke":
                confirm = questionary.confirm(f"Nuke {guild.name}?", default=False).ask()
                if confirm:
                    async def do_nuke():
                        for c in guild.channels:
                            try:
                                await c.delete()
                                await asyncio.sleep(0.3)
                            except:
                                pass
                        for r in guild.roles:
                            if not r.is_default() and guild.me.top_role > r:
                                try:
                                    await r.delete()
                                    await asyncio.sleep(0.3)
                                except:
                                    pass
                        console.print(f"[success]✓ Nuked {guild.name}[/success]")
                    self.run_coroutine(do_nuke())

            elif action_type == "backup":
                async def do_backup():
                    roles = [{"id": r.id, "name": r.name} for r in guild.roles]
                    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    data = {"guild": guild.name, "id": guild.id, "roles": roles, "time": ts}
                    vault = Path("vault_backups")
                    vault.mkdir(exist_ok=True)
                    fname = f"backup_{guild.name[:10]}_{int(time.time())}.json"
                    (vault / fname).write_text(str(data), encoding="utf-8")
                    console.print(f"[success]✓ Backup: {fname}[/success]")
                self.run_coroutine(do_backup())

        except Exception as e:
            console.print(f"[danger]Error: {e}[/danger]")

        console.print()
        questionary.press_any_key_to_continue().ask()

    def run_main_loop(self):
        if not self.prompt_token_login():
            return

        while True:
            try:
                self.show_dashboard()
                
                action = questionary.select(
                    "Select Operation:",
                    choices=[
                        "Send DM to Users",
                        "Single Kick",
                        "Single Ban",
                        "Mass Kick",
                        "Mass Ban",
                        "Server Nuke",
                        "Backup",
                        "Switch Token",
                        "Exit"
                    ]
                ).ask()

                if not action:
                    break

                if action == "Send DM to Users":
                    self.send_dm_menu()
                elif action == "Single Kick":
                    self.moderation_action_menu("kick_single")
                elif action == "Single Ban":
                    self.moderation_action_menu("ban_single")
                elif action == "Mass Kick":
                    self.moderation_action_menu("kick_mass")
                elif action == "Mass Ban":
                    self.moderation_action_menu("ban_mass")
                elif action == "Server Nuke":
                    self.moderation_action_menu("nuke")
                elif action == "Backup":
                    self.moderation_action_menu("backup")
                elif action == "Switch Token":
                    if self.client:
                        asyncio.run_coroutine_threadsafe(self.client.close(), self.loop)
                    self.is_connected = False
                    if not self.prompt_token_login():
                        break
                elif action == "Exit":
                    console.print("[dim]Goodbye.[/dim]")
                    if self.client:
                        asyncio.run_coroutine_threadsafe(self.client.close(), self.loop)
                    time.sleep(1)
                    break

            except KeyboardInterrupt:
                console.print("\n[dim]Interrupted.[/dim]")
                break
            except Exception as e:
                console.print(f"[danger]Error: {e}[/danger]")
                questionary.press_any_key_to_continue().ask()

def main():
    try:
        app = CyberBotApp()
        app.run_main_loop()
    except Exception as e:
        console.print(f"[danger]Fatal error: {e}[/danger]")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()