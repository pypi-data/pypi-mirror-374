# Valuator

A lightweight Python library to fetch AI model pricing data and perform searches to retrieve input and output costs per token for matching models. Supports currency conversion for prices (e.g., INR, EUR, GBP, JPY), defaulting to USD.

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/valuator?period=total&units=NONE&left_color=YELLOW&right_color=BLUE&left_text=Downloads)](https://pepy.tech/projects/valuator)

## Installation

```bash
pip install valuator
```

## Usage

```python
import asyncio
from valuator import Valuator

async def main():
    valuator = Valuator()
    try:

        await valuator.initialize()

        print(valuator.get_model_costs("claude"))
        # Get prices in INR
        print(valuator.get_model_costs("claude", currency="INR"))
        # Get prices in EUR
        print(valuator.get_model_costs("claude", currency="EUR"))

        await valuator.initialize(force_refresh=False)
        print(valuator.get_model_costs("gpt.*"))
    finally:
        await valuator.close()

asyncio.run(main())
```

## Example

```python
import asyncio
import json
from valuator import Valuator

async def main():
    valuator = Valuator()
    try:
        await valuator.initialize()
        # Get prices in USD (default)
        print("Prices in USD:")
        data_usd = valuator.get_model_costs("claude")
        if data_usd:
            model_names = list(data_usd.keys())
            
            # First model
            if len(model_names) >= 1:
                first_model = model_names[0]
                first_model_data = data_usd[first_model]
                print("First model:")
                print(f"  Model name: {first_model}")
                print(f"  Input cost: {first_model_data['input_cost_per_token']}")
                print(f"  Output cost: {first_model_data['output_cost_per_token']}")
            
            # Second model (if available)
            if len(model_names) >= 2:
                second_model = model_names[1]
                second_model_data = data_usd[second_model]
                print("\nSecond model:")
                print(f"  Model name: {second_model}")
                print(f"  Input cost: {second_model_data['input_cost_per_token']}")
                print(f"  Output cost: {second_model_data['output_cost_per_token']}")
            else:
                print("\nNo second model found.")
            
            print("\nFull result (USD):")
            print(json.dumps(data_usd, indent=2))

        # Get prices in INR
        print("\nPrices in INR:")
        data_inr = valuator.get_model_costs("claude", currency="INR")
        if data_inr:
            model_names = list(data_inr.keys())
            
            # First model
            if len(model_names) >= 1:
                first_model = model_names[0]
                first_model_data = data_inr[first_model]
                print("First model:")
                print(f"  Model name: {first_model}")
                print(f"  Input cost: {first_model_data['input_cost_per_token']}")
                print(f"  Output cost: {first_model_data['output_cost_per_token']}")
            
            # Second model (if available)
            if len(model_names) >= 2:
                second_model = model_names[1]
                second_model_data = data_inr[second_model]
                print("\nSecond model:")
                print(f"  Model name: {second_model}")
                print(f"  Input cost: {second_model_data['input_cost_per_token']}")
                print(f"  Output cost: {second_model_data['output_cost_per_token']}")
            else:
                print("\nNo second model found.")
            
            print("\nFull result (INR):")
            print(json.dumps(data_inr, indent=2))

        # Get prices in EUR
        print("\nPrices in EUR:")
        data_eur = valuator.get_model_costs("claude"n, currency="EUR")
        if data_eur:
            model_names = list(data_eur.keys())
            
            if len(model_names) >= 1:
                first_model = model_names[0]
                first_model_data = data_eur[first_model]
                print("First model:")
                print(f"  Model name: {first_model}")
                print(f"  Input cost: {first_model_data['input_cost_per_token']}")
                print(f"  Output cost: {first_model_data['output_cost_per_token']}")
            
            if len(model_names) >= 2:
                second_model = model_names[1]
                second_model_data = data_eur[second_model]
                print("\nSecond model:")
                print(f"  Model name: {second_model}")
                print(f"  Input cost: {second_model_data['input_cost_per_token']}")
                print(f"  Output cost: {second_model_data['output_cost_per_token']}")
            else:
                print("\nNo second model found.")
            
            print("\nFull result (EUR):")
            print(json.dumps(data_eur, indent=2))
        else:
            print("No models found.")
    finally:
        await valuator.close()

asyncio.run(main())
```

## Example Output

```bash
Prices in USD:
First model:
  Model name: us.anthropic.claude-3-5-sonnet-20240620-v1:0
  Input cost: 3e-06
  Output cost: 1.5e-05

Second model:
  Model name: us.anthropic.claude-3-sonnet-20240101-v1:0
  Input cost: 4e-06
  Output cost: 2e-05

Full result (USD):
{
  "us.anthropic.claude-3-5-sonnet-20240620-v1:0": {
    "input_cost_per_token": 3e-06,
    "output_cost_per_token": 1.5e-05
  },
  "us.anthropic.claude-3-sonnet-20240101-v1:0": {
    "input_cost_per_token": 4e-06,
    "output_cost_per_token": 2e-05
  }
}

Prices in INR:
First model:
  Model name: us.anthropic.claude-3-5-sonnet-20240620-v1:0
  Input cost: 0.0002629968906
  Output cost: 0.001314984453

Second model:
  Model name: us.anthropic.claude-3-sonnet-20240101-v1:0
  Input cost: 0.0003506625208
  Output cost: 0.00175332604

Full result (INR):
{
  "us.anthropic.claude-3-5-sonnet-20240620-v1:0": {
    "input_cost_per_token": 0.0002629968906,
    "output_cost_per_token": 0.001314984453
  },
  "us.anthropic.claude-3-sonnet-20240101-v1:0": {
    "input_cost_per_token": 0.0003506625208,
    "output_cost_per_token": 0.00175332604
  }
}

Prices in EUR:
First model:
  Model name: us.anthropic.claude-3-5-sonnet-20240620-v1:0
  Input cost: 2.57636796e-06
  Output cost: 1.28818398e-05

Second model:
  Model name: us.anthropic.claude-3-sonnet-20240101-v1:0
  Input cost: 3.43515728e-06
  Output cost: 1.71757864e-05

Full result (EUR):
{
  "us.anthropic.claude-3-5-sonnet-20240620-v1:0": {
    "input_cost_per_token": 2.57636796e-06,
    "output_cost_per_token": 1.28818398e-05
  },
  "us.anthropic.claude-3-sonnet-20240101-v1:0": {
    "input_cost_per_token": 3.43515728e-06,
    "output_cost_per_token": 1.71757864e-05
  }
}
```

## Features

- Fetches AI model pricing data from a specified URL or local cache.
- Supports currency conversion for prices to any currency listed in the currency API (e.g., INR, EUR, GBP, JPY), defaulting to USD.
- Automatically checks if remote JSON files (model prices and currency rates) have changed using ETag headers.
- Defaults to fetching the latest data (`force_refresh=True`) to ensure up-to-date model prices and exchange rates.
- Performs searches on model names for flexible matching, returning up to 5 matches.
- Returns `input_cost_per_token` and `output_cost_per_token` for matched models in a dictionary format.
- Optimized for low memory usage with efficient data structures (sets, cached regex).
- Asynchronous HTTP requests for fast data retrieval.

## Requirements

- Python 3.8+
- `aiohttp>=3.8.0`

## License

MIT License