import requests

urls = [
    "https://timesofindia.indiatimes.com/india/india-peak-power-demand-hits-record-270-gw-as-heatwave-intensifies/articleshow/131234567.cms",
    "https://economictimes.indiatimes.com/industry/energy/power/indias-peak-power-demand-touches-record-high-of-270-82-gw/articleshow/131248900.cms",
    "https://www.news18.com/india/heatwave-effect-indias-peak-power-demand-crosses-270-gw-mark-for-first-time-10178900.html",
    "https://www.livemint.com/industry/energy/indias-power-demand-hits-record-high-of-270-82-gw-amid-heatwave-11716380000000.html",
    "https://indianexpress.com/article/india/heatwave-delhi-up-rajasthan-imd-forecast-may-22-2026-10700890/"
]

headers = {"User-Agent": "Mozilla/5.0 (compatible; AIShortScript/1.0; +https://github.com/local)"}

for u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=5)
        print(f"[{r.status_code}] {u}")
    except Exception as e:
        print(f"[ERR] {u} {e}")
