# Device Configuration Guide

## What devices work with this server?

Any terminal that supports ZKTeco **ADMS push mode** (also called "Cloud Server" mode):

| Brand | Model | Firmware | Tested |
|-------|-------|----------|--------|
| eSSL | X2008 | ZAM180_TFT | ✅ verified |
| ZKTeco | SpeedFace-V5L | ZAM180_TFT | ✅ same firmware |
| ZKTeco | SpeedFace-V4L | ZMM220_TFT | should work |
| ZKTeco | K40 Pro | — | should work |
| Any OEM | "ADMS" / "Cloud Server" option in menu | — | likely works |

> If your device has `Menu → COMM → Cloud Server Setting` with a "Server Address" field, it speaks ADMS push.

---

## eSSL X2008 / ZKTeco SpeedFace-V5L

```
Menu → COMM → Cloud Server Setting:
  Server Mode:          ADMS
  Enable Domain Name:   Off
  Server Address:       <your-server-ip>
  Server Port:          8081
  Enable Proxy Server:  Off
  HTTPS:                Off     ← MUST be Off (see troubleshooting)
```

After saving, reboot the device. Within ~30 seconds you should see:
```
GET /iclock/getrequest.aspx?SN=<serial> HTTP/1.1
```
in your server log.

---

## ZKTeco (generic)

Menu path may be `Menu → ADMS` or `Menu → Cloud` depending on firmware version.

Set:
- Protocol: ADMS (not BioTime, not ADMS2.0)
- Server IP: your server
- Port: 8081 (or whichever port you bind)
- HTTPS: Disabled

---

## Why ADMS and not port 4370 (Pull)?

**Pull mode (port 4370, pyzk)** works on older ZKTeco firmware but is disabled or returns `0x07f0` errors on newer devices (e.g. ZAM180 series). If `pyzk` silently fails or returns empty data, your device has the pull protocol disabled. ADMS push is the only reliable path on these devices.

See `troubleshooting.md` for the full diagnostic.
