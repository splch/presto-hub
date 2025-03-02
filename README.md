# Presto Hub

This repository showcases a simple MicroPython project that displays dynamic information on a [Pimoroni Presto](https://shop.pimoroni.com/products/presto?variant=54894104052091) board (or a similarly configured Pico system).

It renders:

1. Date and Time
2. Weather (from configurable API)
3. Time-of-Use (TOU) Electrical Cost
4. Stock Quotes
5. Crypto Prices
6. A Small Dynamic “Artwork”

All settings (Wi-Fi credentials, APIs, and time-of-use pricing details) are managed through **config.json**.

---

## Files

- **LICENSE**  
  MIT license for this repository.

- **README.md**  
  You are here!

- **cherry-hq.af**  
  An Alright Fonts (.af) font used for fancy text.  
  _(Optionally used in your Presto project if you need a decorative font.)_

- **config.json**  
  Contains all the user-configurable settings:

  - **wifi**: Enable/disable Wi-Fi, plus SSID and password.
  - **weather**: Enable, plus city and API endpoints (defaults to `wttr.in`).
  - **stocks**: Enable, plus list of stock tickers and API key (defaults to Alpha Vantage).
  - **crypto**: Enable, plus list of crypto tickers and API URL (defaults to CoinGecko).
  - **tou_d_prime**: Time-of-use scheduling details for electricity cost.
  - **main_loop**: `update_interval` in seconds (the pause between each refresh).

- **main.py**  
  The main MicroPython script that:
  1. Loads **config.json**
  2. Connects to Wi-Fi if enabled
  3. Fetches weather, stock, and crypto data periodically
  4. Determines time-of-use cost rates
  5. Draws everything to the Presto display
  6. Updates every `update_interval` seconds

---

## Getting Started

1. **Copy Files**  
   Place `main.py`, `config.json`, and the optional `cherry-hq.af` font onto the Presto’s filesystem.  
   For example, if you’re using Thonny, drag-and-drop or open them in the “Raspberry Pi Pico” device and save them there.

2. **Set Up config.json**

   - **Wi-Fi**:
     ```json
     "wifi": {
       "enable": true,
       "ssid": "YourNetworkSSID",
       "password": "YourNetworkPass"
     }
     ```
     Set `enable` to `true` or `false` depending on whether you want to connect.
   - **Weather**:
     ```json
     "weather": {
       "enable": true,
       "city": "London",
       "api_url": "http://wttr.in?format=j1"
     }
     ```
     You can specify your city or region.
   - **Stocks**:
     ```json
     "stocks": {
       "enable": true,
       "tickers": ["AAPL", "GOOG"],
       "api_key": "YourAlphaVantageKey"
     }
     ```
   - **Crypto**:
     ```json
     "crypto": {
       "enable": true,
       "tickers": ["bitcoin", "ethereum"],
       "api_url": "https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd"
     }
     ```
   - **Time-of-Use**:
     ```json
     "tou_d_prime": {
       "summer_months": [6, 7, 8, 9],
       "weekend_days": [5, 6],
       ...
     }
     ```
     Adjust “summer” and “winter” schedules to reflect your local electricity rates.
   - **Main Loop**:
     ```json
     "main_loop": {
       "update_interval": 10
     }
     ```
     The number of seconds to wait between each screen refresh.

3. **Install Dependencies**  
   This script expects the “Presto” ecosystem, including modules like `requests` (from the MicroPython networking bundle) and `pico_graphics`.  
   Make sure you’re using the custom MicroPython build for Presto or have these modules available.

4. **Run main.py**
   - After resetting or pressing “Play” in Thonny, the script should load your config and begin displaying data.
   - If Wi-Fi is enabled and credentials are valid, the script will attempt to connect and then fetch real data.

---

## Troubleshooting

- **Wi-Fi Failing**: Double-check your SSID and password in `config.json`.
- **No Weather/Stocks**: Possibly missing or invalid API keys. Also make sure the device is indeed connected to Wi-Fi.
- **Unresponsive Display**: Ensure you’ve flashed a Presto-compatible MicroPython firmware. Check that your cable/pins are correct.
- **Performance**: The `update_interval` in `config.json` can be raised if you need fewer API calls or to lighten the CPU load.

---

## License

This project is licensed under the [MIT License](LICENSE) – see the file for details.

---

**Enjoy your Presto Hub!**
