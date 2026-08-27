import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo


BASE_DIR = pathlib.Path(__file__).resolve().parent


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def get_weather_name(config, code):
    for item in config.get("weather_codes", []):
        if item.get("code") == code:
            return item.get("name", "天气未知")
    return f"天气未知 ({code})"


def build_message(config, daily_type, now):
    city = config.get("city", "成都")
    encoded_city = urllib.parse.quote(city)
    geo = fetch_json(
        f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=zh&format=json"
    )
    results = geo.get("results") or []
    if not results:
        raise RuntimeError(f"City not found: {city}")

    place = results[0]
    lat = place["latitude"]
    lon = place["longitude"]
    display_city = place.get("name") or city

    weather = fetch_json(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min"
        "&timezone=auto&forecast_days=1"
    )

    current = weather["current"]
    daily = weather["daily"]
    weather_now_name = get_weather_name(config, int(current["weather_code"]))
    weather_today_name = get_weather_name(config, int(daily["weather_code"][0]))
    temp_now = round(float(current["temperature_2m"]))
    feels_like = round(float(current["apparent_temperature"]))
    humidity = round(float(current["relative_humidity_2m"]))
    high = round(float(daily["temperature_2m_max"][0]))
    low = round(float(daily["temperature_2m_min"][0]))

    day_number = int(now.strftime("%Y%m%d"))
    weekday_name = config["weekdays"][now.weekday()]
    date_text = now.strftime("%Y/%m/%d")

    quotes = config.get("quotes", [])
    tips = config.get("tips", [])
    fortunes = config.get("overall_fortunes", [])

    if daily_type == "quotes":
        daily_title = config.get("daily_quotes_title", "今日金句")
        daily_content = quotes[day_number % len(quotes)] if quotes else ""
    elif daily_type == "tips":
        daily_title = config.get("daily_tips_title", "今日养生")
        daily_content = tips[day_number % len(tips)] if tips else ""
    elif day_number % 2 == 0:
        daily_title = config.get("daily_quotes_title", "今日金句")
        daily_content = quotes[day_number % len(quotes)] if quotes else ""
    else:
        daily_title = config.get("daily_tips_title", "今日养生")
        daily_content = tips[day_number % len(tips)] if tips else ""

    overall_fortune = fortunes[day_number % len(fortunes)] if fortunes else ""

    template = config.get("message_template", "")
    template = template.replace("**今日星座运势**", "**今日整体运势**")
    template = template.replace("{horoscope}", "{overall_fortune}")

    message = template
    message = message.replace("{city}", display_city)
    message = message.replace("{date}", date_text)
    message = message.replace("{weekday}", weekday_name)
    message = message.replace("{weather_today}", weather_today_name)
    message = message.replace("{low}", str(low))
    message = message.replace("{high}", str(high))
    message = message.replace("{weather_now}", weather_now_name)
    message = message.replace("{now}", str(temp_now))
    message = message.replace("{feels}", str(feels_like))
    message = message.replace("{humidity}", str(humidity))
    message = message.replace("{overall_fortune}", overall_fortune)
    message = message.replace("{daily_title}", daily_title)
    message = message.replace("{daily_content}", daily_content)

    return message


def main():
    preview = "--preview" in sys.argv
    daily_type = "auto"
    for arg in sys.argv[1:]:
        if arg.startswith("--daily-type="):
            daily_type = arg.split("=", 1)[1].lower()
            if daily_type not in ("auto", "quotes", "tips"):
                raise SystemExit("Invalid daily type")

    config_path = BASE_DIR / "content.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    message = build_message(config, daily_type, now)

    if preview:
        print(message)
        return

    webhook = os.environ.get("WECHAT_WEBHOOK_URL", "").strip()
    if not webhook:
        raise SystemExit("Missing WECHAT_WEBHOOK_URL")

    payload = {
        "msgtype": "markdown",
        "markdown": {"content": message},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    response = json.loads(urllib.request.urlopen(request, timeout=20).read().decode("utf-8"))
    if response.get("errcode") != 0:
        raise RuntimeError(f"WeChat push failed: {response.get('errmsg')}")
    print("Push sent.")


if __name__ == "__main__":
    main()
