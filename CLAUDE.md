# Wallbox – Projektkontext

## Was ist das?
EV-Ladestation-App für **Langen CNC**. FastAPI-Server (`wallbox.py`) als Proxy für die Reev-API, mit Web-UI zum Starten von Ladevorgängen an 6 Stationen.

## Infrastruktur (Proxmox auf 192.168.178.50)

| ID  | Typ | Name           | Status  |
|-----|-----|----------------|---------|
| 100 | CT  | adguard        | running |
| 101 | CT  | iobroker       | stopped |
| 102 | VM  | homeassistant  | running (aber nicht erreichbar) |
| 103 | CT  | Webserver      | stopped |
| 104 | CT  | immich         | stopped |
| 105 | CT  | Paperless      | stopped |
| 106 | VM  | Windows11      | running |

## Wallbox-Server (läuft direkt auf Proxmox-Host)
- `/root/wallbox.py` (61 KB – die echte Version, größer als im GitHub-Repo)
- Port: `8001`
- Proxy für: `https://auth.reev.com` und `https://api.reev.com`

## Automations auf dem Proxmox-Host (/root/)

### watch_automation.py + watch_automation.service
- Systemd-Service: `watch_automation.service` ("Wallbox Watch Automation")
- Läuft direkt auf dem Proxmox-Host als Python-Script
- Liest `/root/watch_config.json` → `{"w": true, "t": "08:30"}`
- Schickt HA-Push-Notification wenn Uhrzeit == Zielzeit
- Schreibt alle 30 Sekunden ins Log → **KRITISCH: Log war 1,6 TB groß!**
- `haversine()`-Funktion definiert aber nicht verwendet (GPS-Geofencing geplant aber nicht implementiert)
- Schickt Notifications an HA (`192.168.178.50:8123`) – aktuell nicht erreichbar

### Weitere relevante Dateien in /root/
- `app.py` – weiteres Python-Script
- `reev_proxy.py`, `reev_token.py` – Reev API Hilfsskripte
- `arrived.shortcut` – iOS Shortcut
- `laden_fertig.mp3`, `laden_gestartet.mp3`, `ladestation_vergessen.mp3` – Audio-Notifications
- `push_subs.json` + `vapid_private.pem` – Web-Push Subscriptions
- `watch_station.json`, `watch_result.json`, `watch_config.json` – Watch-Automation Config/State
- `stiga_ha_integration/` – Stiga Mähroboter HA-Integration
- `_ra.py` bis `_ra5.py`, `_rb.py` bis `_rb5.py`, `_wk2.py`, `_wk3.py` – Test/Utility Scripts

## Fiat 500 (Neuer 500 MJ22) – Ladestatus-Updates
- ioBroker-Adapter: **weg** (CT gestoppt)
- HA-Adapter: **weg** (HA nicht erreichbar)
- Fiat-App zeigt trotzdem unregelmäßige Updates → kommen vom **Stellantis-Cloud-Backend** (eingebaute LTE-Konnektivität des Autos)
- Früher: exakt alle 15 Minuten (ioBroker/HA-Adapter)
- Jetzt: event-getrieben vom Auto selbst

## GitHub
- Branch: `claude/wallbox-7ori4`
- PR #1: https://github.com/alexbln01/Wallbox/pull/1
- Commits auf diesem Branch aktualisieren den PR automatisch

## Offene Punkte
- [ ] `watch_automation.log` auf 1,6 TB angewachsen → leeren: `> /root/watch_automation.log`
- [ ] Log-Rotation für watch_automation.log einrichten
- [ ] watch_automation.py: haversine-Geofencing implementieren oder entfernen
- [ ] HA (VM 102) nicht erreichbar – prüfen ob nötig
- [ ] wallbox.py auf Host vs. GitHub-Repo synchronisieren
