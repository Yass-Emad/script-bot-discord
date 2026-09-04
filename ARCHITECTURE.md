# ARCHITECTURE.md: CyberControl CLI

## 1. System Topology & Data Flow
```mermaid
graph TD
    A[CyberControl.bat] -->|Checks Python & Deps| B[Runtime Bootstrap]
    B -->|Decodes Base64 Payload| C[cyber_bot_app.py]
    C -->|REST API Validation| D[Discord REST API]
    C -->|WebSocket Gateway| E[Discord Gateway WS]
    C -->|Interactive UI| F[User Terminal via questionary & rich]
```

## 2. Core Modules
- **`CyberBotApp` Controller:** Manages state, client threads, and event loops.
- **Async Thread Bridge (`run_coroutine`):** Safely executes Discord API coroutines from interactive menus without event loop conflicts.
- **Interactive CLI Menus:** Arrow-key navigation for streamlined operations.
