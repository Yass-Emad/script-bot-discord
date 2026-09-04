# PRD: CyberControl Discord Bot CLI (Ghost Commander Edition)

## 1. Business Context & Objectives
- **User Goal:** Manage Discord bots, servers, moderation actions (kicks, bans, nukes), backups, and announcements efficiently from a modern, elegant CLI interface.
- **Key Experience:** Interactive arrow-key navigation (via `questionary`), real-time status monitoring, zero-friction token authentication, and robust error handling.

## 2. Functional Scope
- **Authentication:** Token validation via Discord REST API, secure input, optional `token.txt` persistence.
- **Dashboard:** Live latency, guild count, member reach, presence status, and activity tracking.
- **Operations:**
  - Status & Presence Management (Online, Idle, DND, Invisible, Activities, Timers).
  - Server & Guild Inspector (Channels, roles, admin permissions).
  - Broadcast Announcements (All or specific servers).
  - Moderation & Server Control (Single/Mass Kick, Single/Mass Ban, Server Nuke).
  - Remote Backup Management (Create and store server JSON backups).
  - Interactive Help / Guide.
- **Non-Functional Requirements:** Single-file `.bat` delivery, automatic dependency resolution (`rich`, `discord.py`, `questionary`, `requests`), reliable async thread management, and clean shutdown.
