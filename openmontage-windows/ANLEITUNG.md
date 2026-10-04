# OpenMontage dauerhaft auf Windows 11 installieren

Das Skript `install-openmontage.ps1` erledigt die komplette Installation:

1. fehlende Programme über `winget` installieren: Git, Python 3.11, Node.js LTS, FFmpeg
2. OpenMontage nach `C:\Projekte\OpenMontage` klonen (bei erneutem Aufruf: `git pull`)
3. Python-Umgebung `.venv` anlegen, `requirements.txt` und `piper-tts` installieren
4. Remotion-Composer installieren (`npm install`), HyperFrames vorladen
5. `.env` aus `.env.example` anlegen (eine vorhandene `.env` bleibt unverändert)

## So geht's

1. `install-openmontage.ps1` herunterladen, z. B. in den Ordner *Downloads*.
2. PowerShell öffnen (Start → „PowerShell“) und ausführen:

   ```powershell
   cd $HOME\Downloads
   powershell -ExecutionPolicy Bypass -File .\install-openmontage.ps1 -Demo
   ```

   `-ExecutionPolicy Bypass` gilt nur für diesen einen Aufruf. Die Systemeinstellung bleibt unverändert.
   `-Demo` rendert zum Schluss die drei Demovideos als Funktionstest (einige Minuten).
   Bei der Installation der Programme kann Windows nach Administratorrechten fragen: bestätigen.

3. Meldet das Skript „Noch nicht gefunden: …“, PowerShell schließen, neu öffnen und den Befehl
   wiederholen. Neu installierte Programme sind manchmal erst in einem neuen Fenster sichtbar.

## Optionen

| Option | Bedeutung |
|---|---|
| `-InstallDir D:\Video\OpenMontage` | anderer Zielordner (nicht in OneDrive!) |
| `-Demo` | nach der Installation die Demovideos rendern |

Das Skript kann jederzeit erneut ausgeführt werden: Es aktualisiert OpenMontage und überspringt
alles, was schon installiert ist.

## Nach der Installation

- **Demovideos:** `C:\Projekte\OpenMontage\projects\demos\renders\`
- **API-Keys (optional):** `notepad C:\Projekte\OpenMontage\.env`
- **Mit Claude arbeiten:** Ordner `C:\Projekte\OpenMontage` in der Claude-Desktop-App im Bereich
  *Code* mit **lokaler** Umgebung öffnen, oder im Terminal `cd C:\Projekte\OpenMontage` und `claude`.

## Hinweise

- Das Skript ändert eine globale Git-Einstellung: `core.longpaths=true`. Sie erlaubt lange Dateipfade,
  wie sie in `node_modules` vorkommen.
- Getestet wurden die PowerShell-Syntax und die Hilfsfunktionen, nicht ein vollständiger Lauf auf
  Windows. Wenn etwas fehlschlägt, die rote Fehlermeldung kopieren und an Claude geben.
