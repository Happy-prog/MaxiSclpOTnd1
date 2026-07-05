# Scalping Bot

Maxized Scalping On Trend — a Python-based scalping trading bot designed to identify and trade short-term opportunities following the prevailing trend.

## Overview

This repository contains a scalping bot implemented in Python. The bot is intended for algorithmic traders who want a lightweight, configurable strategy that opens and closes positions quickly to capture small profits while staying aligned with the trend.

## Features

- Trend-aware scalping strategy
- Modular structure for indicators, signal generation, order execution, and risk management
- Configurable parameters via a YAML/JSON config file or environment variables
- Logging and basic metrics
- Support for paper trading before going live

## Requirements

- Python 3.10+ recommended
- pip
- Optional: Docker (for containerized runs)

## Installation (recommended)

1. Clone the repository:

   git clone https://github.com/Happy-prog/MaxiSclpOTnd1.git
   cd MaxiSclpOTnd1

2. Create and activate a virtual environment (recommended):

   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   .\.venv\Scripts\activate  # Windows (PowerShell)

3. Upgrade pip and install dependencies:

   python -m pip install --upgrade pip
   if [ -f requirements.txt ]; then
     pip install -r requirements.txt
   else
     # If this repo uses setup.py / pyproject, install editable
     pip install -e .
   fi

4. (Optional) Docker: build and run the included Dockerfile (if provided):

   docker build -t scalping-bot .
   docker run --env-file .env scalping-bot

Notes:
- Pin dependencies in requirements.txt to ensure reproducible installs.
- Use a tools like pip-tools or Poetry for dependency management in larger projects.

## Configuration

The bot supports two common configuration methods. Choose one based on your deployment preferences.

1. Configuration file (recommended for reproducibility)

   - Create a `config.yaml` (or `config.json`) in the project root. Example `config.yaml`:

```yaml
exchange: "binance"
api_key: ""
api_secret: ""
symbol: "BTCUSDT"
timeframe: "1m"
position_size: 0.001
risk_per_trade: 0.002  # fraction of account equity
indicators:
  ema_short: 8
  ema_long: 34
  rsi_period: 14
paper_trade: true
logging:
  level: "INFO"
  file: "bot.log"
```

   - Load the config in your app using a helper (e.g., PyYAML) and validate required fields before connecting to exchanges.

2. Environment variables (recommended for secrets in CI/CD or containers)

   - Use `.env` or your environment provider to store secrets. Typical variables:

     - SCALP_EXCHANGE
     - SCALP_API_KEY
     - SCALP_API_SECRET
     - SCALP_SYMBOL
     - SCALP_TIMEFRAME
     - SCALP_PAPER_TRADE

   - Use python-dotenv or your runtime environment to inject these into the process.

Security best practices:
- Never commit API keys or secrets to the repository.
- Prefer environment variables or secret managers (e.g., AWS Secrets Manager, HashiCorp Vault, GitHub Secrets) for production credentials.
- Use a dedicated API key with restricted permissions (withdrawals disabled) for trading.

## Usage

- Dry run / paper trading (recommended for testing):

  python -m bot.main --config config.yaml

- Live trading (only after thorough testing):

  python -m bot.main --config config.yaml --live

- CLI flags (examples — actual options depend on implementation):
  --config PATH     Path to config file
  --env             Read configuration from environment variables
  --live            Enable live trading (otherwise uses paper mode)
  --log-level LEVEL Set logging verbosity

## Running as a service

- Use systemd, Docker, or a process manager (supervisord, pm2) to run the bot continuously.
- Ensure automatic restarts on failure and log rotation for long-running jobs.

Example systemd unit (basic):

```
[Unit]
Description=Scalping Bot
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/MaxiSclpOTnd1
ExecStart=/path/to/.venv/bin/python -m bot.main --config /path/to/config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Testing and Safety

- Start in paper trading mode and run against historical or live market data to validate behavior.
- Add unit tests for indicators and signal logic. Use pytest and mock exchange responses.
- Implement maximum daily loss and position limits to prevent runaway behavior.

## Logging and Monitoring

- Log to both console and file; include timestamps, level, and key trade details.
- Consider exposing simple metrics (Prometheus) or sending notifications (email, Slack) for critical events such as large losses or connectivity errors.

## Contributing

Contributions are welcome. Suggested workflow:

- Fork the repo
- Create a feature branch
- Add tests for new behavior
- Open a pull request explaining the change

## License

Include a LICENSE file (e.g., MIT) and ensure the header is present in source files as needed.

## Contact

Repo: https://github.com/Happy-prog/MaxiSclpOTnd1


---

Best practices I followed in this README update:
- Recommend virtual environments and pinned dependencies for reproducible installs.
- Suggest storing secrets in environment variables or secret managers and never committing them.
- Encourage paper trading and tests before live trading.

