#!/usr/bin/env python3
import requests
import time
import urllib3
import re
from prometheus_client import start_http_server, Gauge
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MODEM_IP = "192.168.100.1"
EXPORTER_PORT = 8000

session = requests.Session()
session.verify = False

# Gauges for all metrics
gauges = {
    "downstream_power": Gauge("modem_downstream_power", "Downstream Power Level (dBmV)", ["channel"]),
    "downstream_snr": Gauge("modem_downstream_snr", "Downstream SNR (dB)", ["channel"]),
    "downstream_correctables": Gauge("modem_downstream_correctables", "Downstream Correctable Codewords", ["channel"]),
    "downstream_uncorrectables": Gauge("modem_downstream_uncorrectables", "Downstream Uncorrectable Codewords", ["channel"]),
    "upstream_power": Gauge("modem_upstream_power", "Upstream Power Level (dBmV)", ["channel"]),
    "ofdm_power": Gauge("modem_ofdm_power", "OFDM Downstream Power Level (dBmV)", ["channel"]),
    "ofdm_snr": Gauge("modem_ofdm_snr", "OFDM Downstream SNR/MER (dB)", ["channel"]),
    "ofdm_correctable": Gauge("modem_ofdm_correctable", "OFDM Correctable Codewords", ["channel"]),
    "ofdm_uncorrectable": Gauge("modem_ofdm_uncorrectable", "OFDM Uncorrectable Codewords", ["channel"]),
    "modem_uptime": Gauge("modem_uptime", "Modem uptime in seconds"),
    "modem_system_time": Gauge("modem_system_time", "Modem system time (unix timestamp)")
}

def parse_uptime(uptime_str):
    uptime_str = uptime_str.strip()
    match = re.match(r"(\d+)h:(\d+)m:(\d+)s", uptime_str)
    if match:
        hours, minutes, seconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds
    return 0

def parse_system_time(system_time_str):
    """Convert 'Sun Jun 29, 2025, 18:40:40' to unix timestamp."""
    try:
        dt = datetime.strptime(system_time_str.strip(), "%a %b %d, %Y, %H:%M:%S")
        return int(dt.timestamp())
    except Exception:
        return 0

def scrape():
    # Downstream Bonded
    ds = session.get(f"https://{MODEM_IP}/data/dsinfo.asp").json()
    for ch in ds:
        ch_id = ch["channelId"]
        gauges["downstream_power"].labels(channel=ch_id).set(float(ch["signalStrength"]))
        gauges["downstream_snr"].labels(channel=ch_id).set(float(ch["snr"]))
        gauges["downstream_correctables"].labels(channel=ch_id).set(float(ch["correcteds"]))
        gauges["downstream_uncorrectables"].labels(channel=ch_id).set(float(ch["uncorrect"]))

    # Upstream Bonded
    us = session.get(f"https://{MODEM_IP}/data/usinfo.asp").json()
    for ch in us:
        ch_id = ch["channelId"]
        gauges["upstream_power"].labels(channel=ch_id).set(float(ch["signalStrength"]))

    # Downstream OFDM
    ofdm = session.get(f"https://{MODEM_IP}/data/dsofdminfo.asp").json()
    for ch in ofdm:
        ch_index = ch["receive"]
        if ch.get("plcpower", "NA") != "NA":
            gauges["ofdm_power"].labels(channel=ch_index).set(float(ch["plcpower"]))
        if ch.get("SNR", "NA") != "NA":
            gauges["ofdm_snr"].labels(channel=ch_index).set(float(ch["SNR"]))
        if ch.get("correcteds", "NA") != "NA":
            gauges["ofdm_correctable"].labels(channel=ch_index).set(float(ch["correcteds"]))
        if ch.get("uncorrect", "NA") != "NA":
            gauges["ofdm_uncorrectable"].labels(channel=ch_index).set(float(ch["uncorrect"]))

    # System uptime/system time (correct endpoint!)
    try:
        sysinfo = session.get(f"https://{MODEM_IP}/data/getSysInfo.asp").json()
    except Exception:
        sysinfo = []

    if sysinfo and isinstance(sysinfo, list):
        info = sysinfo[0]
        uptime_str = info.get("systemUptime", "")
        system_time_str = info.get("systemTime", "")
        # Export as Prometheus gauges
        gauges["modem_uptime"].set(parse_uptime(uptime_str))
        gauges["modem_system_time"].set(parse_system_time(system_time_str))

def main():
    start_http_server(EXPORTER_PORT)
    while True:
        scrape()
        time.sleep(30)

if __name__ == "__main__":
    main()