import time
import math
import json
import requests
from presto import Presto


def load_config(filename="config.json"):
    """
    Loads JSON configuration from a file.
    """
    with open(filename, "r") as f:
        return json.load(f)


# ---- Shared HTTP utility ----


def fetch_json(url, timeout=9):
    """
    Utility to fetch JSON from a URL with basic error handling.

    :param url: The URL to fetch.
    :param timeout: How many seconds to wait for a response.
    :return: Parsed JSON data or None on error.
    """
    try:
        resp = requests.get(url, timeout=timeout)
        data = resp.json()
        resp.close()
        return data
    except Exception as exc:
        print(f"Request error: {exc}")
        return None


# ---- Initialize from config ----

config = load_config()

presto = Presto(ambient_light=False)

wifi_cfg = config.get("wifi", {})
if wifi_cfg.get("enable"):
    if presto.connect(wifi_cfg["ssid"], wifi_cfg["password"]):
        print("WiFi connected!")
    else:
        print("WiFi connection failed.")
else:
    print("WiFi disabled in config.")

display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# ---- Weather ----


def get_weather(conf):
    """
    Fetches weather data from wttr.in or another user-configured endpoint.
    Returns a nicely formatted weather string, or a fallback if disabled/error.
    """
    w = conf.get("weather", {})
    if not w.get("enable", False):
        return "Weather: Disabled"

    city = w.get("city", "").replace(" ", "+")
    base = w.get("api_url", "").split("?format=j1")[0]
    if not base or not city:
        return "Weather: N/A"

    url = f"{base}/{city}?format=j1"
    data = fetch_json(url)

    if not data:
        return "Weather: N/A (fetch error)"

    try:
        current = data["current_condition"][0]
        temp_f = current["temp_F"]
        feels_f = current["FeelsLikeF"]
        desc = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind_mph = current["windspeedMiles"]
        precip = current["precipInches"]

        return (
            f"Weather: {temp_f}°F ({desc}), Feels {feels_f}°F, "
            f"{humidity}% RH, {wind_mph} mph, {precip} in"
        )
    except (KeyError, IndexError, TypeError) as exc:
        print(f"Weather parse error: {exc}")
        return "Weather: N/A"


# ---- Crypto ----


def get_crypto(conf):
    """
    Fetches crypto prices (USD) from CoinGecko or similar.
    Returns a formatted string or fallback.
    """
    c = conf.get("crypto", {})
    if not c.get("enable", False):
        return "Crypto: Disabled"

    tickers = c.get("tickers", [])
    base_url = c.get("api_url", "")
    if not tickers or not base_url:
        return "Crypto: N/A (invalid config)"

    ticker_str = ",".join(tickers)
    url = f"{base_url}&ids={ticker_str}"
    data = fetch_json(url)

    if not data:
        return "Crypto: N/A (fetch error)"

    lines = []
    for ticker, price_info in data.items():
        usd_price = price_info.get("usd", 0)
        lines.append(f"{ticker} ${usd_price}")
    return "Crypto: " + ", ".join(lines)


# ---- Stocks ----


def get_stocks(conf):
    """
    Fetches stock prices from Alpha Vantage (or user-specified).
    Returns a formatted string or fallback.
    """
    s = conf.get("stocks", {})
    if not s.get("enable", False):
        return "Stocks: Disabled"

    tickers = s.get("tickers", [])
    api_key = s.get("api_key", "")
    if not tickers or not api_key:
        return "Stocks: N/A (invalid config)"

    lines = []
    for ticker in tickers:
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE"
            f"&symbol={ticker}"
            f"&apikey={api_key}"
        )
        data = fetch_json(url)
        if not data:
            lines.append(f"{ticker} $N/A")
            continue

        quote = data.get("Global Quote", {})
        price_str = quote.get("05. price", "N/A")
        lines.append(f"{ticker} ${price_str}")

    return "Stocks: " + ", ".join(lines)


# ---- Electricity (TOU-D-PRIME) ----


def get_electricity_cost(conf):
    """
    Looks up the current cost bracket from the TOU-D-PRIME config
    using localtime.
    """
    now = time.localtime()
    month = now[1]
    hour = now[3]
    weekday_idx = now[6]

    tou = conf.get("tou_d_prime", {})
    summer_months = tou.get("summer_months", [])
    weekend_days = tou.get("weekend_days", [])

    # Safely handle missing data
    if not summer_months or "summer" not in tou or "winter" not in tou:
        return "Cost: Config Error"

    def find_rule(rules):
        for r in rules:
            if r["start"] <= hour < r["end"]:
                return r
        return None

    is_summer = month in summer_months
    if is_summer:
        is_weekend = weekday_idx in weekend_days
        schedule = "weekend" if is_weekend else "weekday"
        ruleset = tou["summer"].get(schedule, [])
    else:
        ruleset = tou.get("winter", [])

    rule = find_rule(ruleset)
    if rule:
        rate_str = f"{rule['rate']}¢"
        label_str = rule["label"]
        recommendation_str = rule["recommendation"]
        return f"Cost: {rate_str} {label_str} - {recommendation_str}"

    return "Cost: Unknown"


# ---- Drawing the screen ----


def draw_screen():
    """
    The main function to draw data to the screen, including
    date/time, weather, cost, crypto, and stocks. Also draws a
    dynamic circle for 'art'.
    """
    t = time.localtime()
    date_str = "{:04d}-{:02d}-{:02d}".format(t[0], t[1], t[2])
    time_str = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])

    weather_str = get_weather(config)
    crypto_str = get_crypto(config)
    stocks_str = get_stocks(config)
    cost_str = get_electricity_cost(config)

    display.set_pen(0)
    display.clear()
    display.set_pen(15)

    y = 5
    display.text(f"Date: {date_str}", 5, y, WIDTH, 2)
    y += 20
    display.text(f"Time: {time_str}", 5, y, WIDTH, 2)
    y += 20
    display.text(weather_str, 5, y, WIDTH, 2)
    y += 40
    display.text(cost_str, 5, y, WIDTH, 2)
    y += 40
    display.text(crypto_str, 5, y, WIDTH, 2)
    y += 40
    display.text(stocks_str, 5, y, WIDTH, 2)

    # Simple "art" - a bouncing circle
    now_s = time.time()
    cx = int(WIDTH / 2 + (WIDTH / 4) * math.sin(now_s))
    cy = int(HEIGHT - 30 - (HEIGHT / 8) * math.cos(now_s))
    display.set_pen(9)
    display.circle(cx, cy, 10)

    presto.update()


# ---- Main Loop ----

update_interval = config.get("main_loop", {}).get("update_interval", 10)

while True:
    draw_screen()
    time.sleep(update_interval)
