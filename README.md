# MTG Mulligan Tool

## Overview
Desktop tool for collecting Magic: The Gathering mulligan decisions from users.

The tool can now optionally compare the player's decision against the latest deployed ML model. When enabled, the app shows what the model would have done, along with a confidence score and a short explanation, before moving to the next hand.

---

## Features
- Random 7-card hand generation from predefined decklists
- Card image display using Scryfall
- Keep / Mulligan classification
- Random play/draw assignment
- Local CSV saving
- Automatic upload to the server
- Optional model comparison mode
- Automatic model download from the server on startup
- Local model caching for offline use

---

## Project Structure
- `main.py` - app entry point  
- `config.py` - paths and server URLs  
- `mtg_mulligan/parser.py` - decklist parsing  
- `mtg_mulligan/hand_generator.py` - hand generation and play/draw  
- `mtg_mulligan/gui.py` - GUI logic  
- `mtg_mulligan/results.py` - CSV output  
- `mtg_mulligan/uploader.py` - result upload logic  
- `mtg_mulligan/model_sync.py` - model download and cache logic  
- `mtg_mulligan/predictor.py` - local inference logic  

---

## Download & Run (Windows Executable)

You can use the app without installing Python by downloading the prebuilt executable.

### 1) Download
1. Go to the **Releases** page:  
   https://github.com/londonglenn/mtg_mulligan_tool/releases  

2. Download the latest file (for example, `mtg_mulligan_v1.1.0.zip`).

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

On first run, the app may:
- cache card images locally
- check the server for the latest model
- download the latest model bundle if internet is available

---

### 4) Use the app
- Enter your username when prompted
- Review each hand and click:
  - **Keep** or **Mulligan**
- Optionally enable **Show Model Comparison**
- If model comparison is enabled:
  - the app will display what the model would do
  - a **Next** button will appear before the next hand
- Click **Stop** when finished

---

### 5) What happens to your data
- A CSV is saved locally in: `results/`
- The CSV includes the player decision and, when enabled, the model comparison data
- When you click **Stop**, the app automatically attempts to upload your results to the server
- If upload fails, your data is still saved locally in the `results/` folder

---

## Model Updates
- On startup, the tool checks for the latest model if internet is available
- If a newer model is found, it downloads and caches it locally
- If the app cannot connect to the server, it uses the cached model if one exists
- If no cached model exists, model comparison mode is unavailable but normal hand collection still works

---

## Running from Source

### Requirements
- Python 3.10+ recommended
- See `requirements.txt`

### Setup
```
bash
pip install -r requirements.txt
python main.py
```

---

## Updating

- Download the newest ZIP from **Releases**
- Replace your old folder with the new one, or keep both
- Run the new `mtg_mulligan.exe`

---

## Troubleshooting

### App won’t open
- Make sure you **extracted** the ZIP
- Try right-click → **Run as administrator**

### Windows protected your PC
- Click **More info** → **Run anyway**

### Images don’t load
- Check internet connection
- Images are cached locally after first successful download

### Model comparison is unavailable
- Check internet connection on first startup
- Make sure the server has a deployed model
- If offline, the app can only use a previously cached model

### Upload failed
- Your results are still saved locally in `results/`
- You can send that CSV manually if needed