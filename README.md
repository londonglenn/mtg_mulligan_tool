# MTG Mulligan Tool

## Overview
Desktop tool for collecting Magic: The Gathering mulligan decisions from users.

## Features
- Random 7-card hand generation from predefined decklists
- Card image display using Scryfall
- Keep / Mulligan classification
- Random play/draw assignment
- Local CSV saving
- Automatic upload to the server

## Project Structure
- `main.py` - app entry point
- `config.py` - paths and upload URL
- `mtg_mulligan/parser.py` - decklist parsing
- `mtg_mulligan/hand_generator.py` - hand generation and play/draw
- `mtg_mulligan/gui.py` - GUI logic
- `mtg_mulligan/results.py` - CSV output
- `mtg_mulligan/uploader.py` - upload logic

## Download & Run (Windows Executable)

You can use the app without installing Python by downloading the prebuilt executable.

### 1) Download

1. Go to the **Releases** page:  
   https://github.com/londonglenn/mtg_mulligan_tool/releases

2. Download the latest file (e.g. `mtg_mulligan_v1.0.1.zip`).

---

### 2) Extract

- Right-click the ZIP → **Extract All…**
- Open the extracted folder (**do not run from inside the ZIP**)

You should see something like:

```
mtg_mulligan/
├── mtg_mulligan.exe
└── _internal/
```

---

### 3) Run

- Double-click `mtg_mulligan.exe`

On first run, Windows may show a SmartScreen warning:
- Click **More info** → **Run anyway**

On first run the app will download all of the card images into a local cache for smooth operation. This may take a minute to load. 

---

### 4) Use the app

- Enter your username when prompted
- Review each hand and click:
  - **Keep** or **Mulligan**
- Click **Stop** when finished

---

### 5) What happens to your data

- A CSV is saved locally in: results/


- When you click **Stop**, the app automatically attempts to upload your results to the server.

- If upload fails, your data is still saved locally in the `results/` folder.

---

## Updating

- Download the newest ZIP from **Releases**
- Replace your old folder with the new one (or keep both)
- Run the new `mtg_mulligan.exe`

---

## Troubleshooting

### “App won’t open”
- Make sure you **extracted** the ZIP
- Try right-click → **Run as administrator**

### “Windows protected your PC”
- Click **More info** → **Run anyway**

### Images don’t load
- Check internet connection (images are cached on first run)

### Upload failed
- Your results are still saved locally in `results/`
- You can send that CSV manually if needed

---