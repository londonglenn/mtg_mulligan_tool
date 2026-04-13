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

## Requirements
- Python 3.8+
- `requests`
- `pillow`

## Installation
```bash
pip install -r requirements.txt