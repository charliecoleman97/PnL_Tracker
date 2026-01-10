.PHONY: help setup run fetch-trades install clean

# Variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Default target
help:
	@echo "Available targets:"
	@echo "  make setup            - Set up virtual environment and install dependencies"
	@echo "  make install          - Install/update dependencies"
	@echo "  make run              - Run the driver script (default: last 1 day)"
	@echo "  make fetch-trades     - Run the driver script (default: last 1 day)"
	@echo "  make clean            - Remove virtual environment"
	@echo ""
	@echo "Examples:"
	@echo "  make run FROM_DATE=2024-01-01 TO_DATE=2024-01-31"
	@echo "  make fetch-trades FROM_DATE=2024-01-01"

# Set up virtual environment and install dependencies
setup: $(VENV)/bin/python
	@echo "Virtual environment ready!"
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo ""
	@echo "Setup complete! Don't forget to set environment variables:"
	@echo "  export IG_USERNAME='your_username'"
	@echo "  export IG_PASSWORD='your_password'"
	@echo "  export IG_API_KEY='your_api_key'"
	@echo "  export TRADES_FILE_PATH='transaction_history_files/ig_transactions_formatted.csv'"

# Create virtual environment if it doesn't exist
$(VENV)/bin/python:
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV)
	@echo "Virtual environment created!"

# Install/update dependencies
install: $(VENV)/bin/python
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt

# Run the driver script
run fetch-trades: $(VENV)/bin/python
	@$(PYTHON) driver.py \
		$$([ -n "$(FROM_DATE)" ] && echo --from-date $(FROM_DATE)) \
		$$([ -n "$(TO_DATE)" ] && echo --to-date $(TO_DATE))

# Clean virtual environment
clean:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "Virtual environment removed!"

