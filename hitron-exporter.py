#!/usr/bin/env python3
import requests
import time
import urllib3
import prometheus_client
from prometheus_client import start_http_server, Gauge
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MODEM_IP = "192.168.100.1"
EXPORTER_PORT = 8000

session = requests.Session()
session.verify = False

# Create Gauges
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
    "uptime": Gauge("modem_uptime", "Exporter scrape timestamp"),
    "system_time": Gauge("modem_system_time", "Exporter scrape timestamp")
}

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

    # Uptime & System Time (we just record scrape timestamp since modem doesn't give uptime)
    ts = time.time()
    gauges["uptime"].set(ts)
    gauges["system_time"].set(ts)

def main():
    print(f"Starting exporter on port {EXPORTER_PORT}")
    start_http_server(EXPORTER_PORT)
    while True:
        scrape()
        time.sleep(30)

if __name__ == "__main__":
    main()
