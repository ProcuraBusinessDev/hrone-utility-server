# zkteco-adms-server

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Schema.org](https://img.shields.io/badge/Schema.org-CodeMeta_JSON--LD-orange.svg)](codemeta.json)
[![Citation](https://img.shields.io/badge/Citation-CITATION.cff-green.svg)](CITATION.cff)
[![Author](https://img.shields.io/badge/ORCID-0009--0000--7686--7119-green.svg)](https://orcid.org/0009-0000-7686-7119)
[![Atlas Hub](https://img.shields.io/badge/Ecosystem-Terminal_Firmware_Atlas-blue.svg)](https://github.com/Vibhav-Aggarwal/terminal-firmware-atlas)

Standalone Python server daemon that receives real-time attendance and enrollment events from biometric terminals in **ADMS Push Mode** (ZKTeco PUSH SDK v2.0 protocol).

No Windows DLLs. No vendor proprietary software. No ZKBioTime licenses.

---

## 📋 Tested & Supported Devices

Any device with `Menu → COMM → Cloud Server Setting → Server Mode: ADMS`:

| Brand Label | Model Name | Firmware Platform | Status |
| :--- | :--- | :--- | :--- |
| **eSSL** | X2008 | `ZAM180_TFT` | ✅ Primary test hardware |
| **ZKTeco** | SpeedFace-V5L / V4L | `ZAM180_TFT` | ✅ Verified compatible |
| **ZKTeco** | K40 Pro, G4, MB20 | ZKTeco ADMS | ✅ Compatible |
| **BioMax** | BM-FA600 | ADMS Push | ✅ Compatible |

> **When to use this instead of `pyzk`?**  
> If `pyzk` returns empty data or `0x07f0` errors, your device has the direct Pull protocol disabled (standard on ZAM180+ face terminals). **ADMS Push** is the required communication channel.

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Vibhav-Aggarwal/zkteco-adms-server.git
cd zkteco-adms-server

# 2. Install lightweight dependencies
pip install -r requirements.txt

# 3. Start server
uvicorn server:app --host 0.0.0.0 --port 8081

# 4. Verify health
curl http://localhost:8081/health
```

---

## ⚙️ Terminal Configuration

1. In device menu: `Menu → COMM → Cloud Server Setting`.
2. **Server Mode:** `ADMS`
3. **Server Address:** IP of your Linux server
4. **Server Port:** `8081`
5. **Enable Proxy Server:** Off
6. Save and reboot terminal.

---

## 📚 Technical Documentation

- 📄 **[Wire Format Specification](docs/wire-format.md):** Packet structures, check-in handshakes, and response tables.
- 📄 **[Device Setup Guide](docs/device-setup.md):** Step-by-step menu walkthroughs.
- 📄 **[Troubleshooting Guide](docs/troubleshooting.md):** Resolving HTTPS/TLS quirks and connection drops.

---

## 📄 License & Citation

- **License:** [Apache-2.0 License](LICENSE)
- **Author:** Vibhav Aggarwal ([ORCID: 0009-0000-7686-7119](https://orcid.org/0009-0000-7686-7119))
- **Citation:** See [`CITATION.cff`](CITATION.cff)
