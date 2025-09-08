<p align="center">
  <a href="https://github.com/Jo0X01/TempMail-Generator">
    <img src="TempMailGenerator.ico" alt="Temp Mail Generator" width="300" height="250">
  </a>
</p>


# Temp Mail Generator

A lightweight **temporary email generator** built with Flask and a modern frontend. It allows you to generate disposable emails, read messages, and refresh automatically.

## Features
- Generate temporary emails via API
- Read inbox messages in real-time
- Multiple API key fallback
- CLI support (`--port`, `--host`, `--no-browser`, `--config`)

## Installation
```bash
git clone https://github.com/Jo0X01/temp-mail-generator.git
cd temp-mail-generator
pip install -r requirements.txt
```

## Configuration
Run the script with:
```bash
python main.py --config
```
This lets you edit your API keys and base URLs.

## Usage
Run server with default options:
```bash
python main.py
```
Or with CLI:
```bash
python main.py --host 0.0.0.0 --port 8080 --no-browser
```

## License
MIT License
