# Hitron CODA56 Prometheus Exporter

This exporter collects DOCSIS metrics from a Hitron CODA56 modem and exposes them to Prometheus.

---

## 📈 Features

- **Downstream Bonded Channels**
  - Frequency
  - Power level
  - SNR
  - Correctables / Uncorrectables
- **Upstream Bonded Channels**
  - Frequency
  - Power level
  - Modulation type
- **Downstream OFDM Channels**
  - Power
  - SNR
  - Codewords
- **Upstream OFDMA Channels**
  - Reported state
- **WAN Configuration**

---

## 🌐 Endpoints Queried

| Endpoint                   | Purpose                      |
|----------------------------|------------------------------|
| `/data/dsinfo.asp`         | Downstream bonded channels  |
| `/data/usinfo.asp`         | Upstream bonded channels    |
| `/data/dsofdminfo.asp`     | Downstream OFDM channels    |
| `/data/usofdminfo.asp`     | Upstream OFDMA channels     |
| `/data/getCmDocsisWan.asp` | WAN configuration           |

> **Note:** No login credentials are required.

---

## 🖥️ Example Metrics

```
# HELP modem_downstream_power Downstream Power Level (dBmV)
# TYPE modem_downstream_power gauge
modem_downstream_power{channel="1"} 9.1

# HELP modem_downstream_snr Downstream SNR (dB)
# TYPE modem_downstream_snr gauge
modem_downstream_snr{channel="1"} 38.6

# HELP modem_downstream_correctables Correctable Codewords
# TYPE modem_downstream_correctables gauge
modem_downstream_correctables{channel="1"} 6421

# HELP modem_downstream_uncorrectables Uncorrectable Codewords
# TYPE modem_downstream_uncorrectables gauge
modem_downstream_uncorrectables{channel="1"} 0

# HELP modem_upstream_power Upstream Power Level (dBmV)
# TYPE modem_upstream_power gauge
modem_upstream_power{channel="1"} 41.2

# HELP modem_ofdm_power OFDM Downstream Power Level (dBmV)
# TYPE modem_ofdm_power gauge
modem_ofdm_power{channel="1"} 9.5

# HELP modem_ofdm_snr OFDM Downstream SNR (dB)
# TYPE modem_ofdm_snr gauge
modem_ofdm_snr{channel="1"} 39
```

---

## ⚙️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jhgrazier/Hitron-Coda56-Prometheus-Exporter.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the exporter:

   ```bash
   python hitron-exporter.py
   ```

Exporter runs by default on port `8000` at `/metrics`.

---

## 🛠️ Running as a Service

To have the exporter start automatically on boot with `systemd`:

Create a unit file at `/etc/systemd/system/hitron-exporter.service`:

```ini
[Unit]
Description=Hitron CODA56 Prometheus Exporter
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/bin/hitron-exporter.py
WorkingDirectory=/usr/bin
User=root
Group=root
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=hitron-exporter

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hitron-exporter.service
sudo systemctl start hitron-exporter.service
```

Check status:

```bash
sudo systemctl status hitron-exporter.service
```

View logs:

```bash
journalctl -u hitron-exporter.service -f
```

---

## 📊 Prometheus Configuration

Add this job to your `prometheus.yml`:

```yaml
  - job_name: hitron_modem
    honor_timestamps: true
    track_timestamps_staleness: false
    scrape_interval: 15s
    scrape_timeout: 10s
    scrape_protocols:
      - OpenMetricsText1.0.0
      - OpenMetricsText0.0.1
      - PrometheusText0.0.4
    metrics_path: /metrics
    scheme: http
    enable_compression: true
    follow_redirects: true
    enable_http2: true
    static_configs:
      - targets:
          - localhost:8000
```

---

## 🧭 Grafana Dashboard

A sample dashboard can be imported into Grafana to visualize:

- Downstream channels
- Upstream channels
- OFDM metrics
- Modem uptime and status

---

## 🔑 License

MIT License

---