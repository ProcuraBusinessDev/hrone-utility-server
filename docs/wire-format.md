# ADMS Wire Format

Reference: [ZKTeco PUSH SDK Communication Protocol v2.0.1](https://www.scribd.com/document/695654988/PUSH-SDK-Communication-Protocol-V2-0-1)

## Endpoint Summary

| Method | Path | Initiated by | Purpose |
|--------|------|-------------|---------|
| GET | `/iclock/cdata.aspx` | Device (on boot + periodic) | Registration, get server options |
| POST | `/iclock/cdata.aspx` | Device | Push attendance / enrollment data |
| GET | `/iclock/getrequest.aspx` | Device (every few seconds) | Poll for pending commands |
| GET | `/iclock/devicecmd.aspx` | Device | Reply after executing a command |
| GET | `/iclock/ping.aspx` | Device (heartbeat) | Keep-alive |

---

## GET /iclock/cdata.aspx — Registration

Device sends: `GET /iclock/cdata.aspx?SN=QJT3253600356&options=...`

Server replies with a plain-text options block:
```
GET OPTION FROM: QJT3253600356
ATTLOGStamp=None
OPERLOGStamp=9999
TransTimes=00:00;14:05
TransInterval=1
TransFlag=TransData AttLog OpLog EnrollUser
Realtime=1
Encrypt=None
ServerVer=2.2.14
```

Key fields:
- `TransInterval` — heartbeat interval in minutes (1 = every minute)
- `Realtime=1` — push punches immediately as they happen
- `Encrypt=None` — no encryption (default; most firmware ignores TLS toggle)

---

## POST /iclock/cdata.aspx — Data Push

Device sends a multipart-style body. The `table` query parameter identifies the data type.

### ATTLOG (attendance records)

```
POST /iclock/cdata.aspx?SN=QJT3253600356&table=ATTLOG&Stamp=2026-04-11+10:30:00
```

Body (tab-separated, one record per line):
```
PIN     DateTime              Status  VerifyType  WorkCode  Reserved  Reserved
12345   2026-04-11 10:30:00   0       15          0         0         0
```

| Field | Values |
|-------|--------|
| Status | 0=Check-in, 1=Check-out, 2=Break-out, 3=Break-in, 4=OT-in, 5=OT-out |
| VerifyType | 0=Password, 1=Fingerprint, 4=Card, 15=Face, 20=Face+FP |

### OPERLOG (user/template operations)

```
POST /iclock/cdata.aspx?SN=...&table=OPERLOG
```

Body lines:
```
USER PIN=12345 Name=Alice Pri=0 Passwd= Card=0 Grp=1 TZ=0 Verify=0
FP PIN=12345 FID=0 Size=498 Valid=1 TMP=<base64>
FACE PIN=12345 FID=50 Size=296 Valid=1 TMP=<base64>
```

---

## GET /iclock/getrequest.aspx — Command Polling

Device polls every few seconds. Server returns either `OK` (nothing to do) or a command:

```
C:<cmd_id>:<command_string>
```

Examples:
```
C:1:CHECK
C:2:SET TIME:2026-04-11 10:30:00
C:3:DATA QUERY ATTLOG StartTime=2026-04-01 00:00:00 EndTime=2026-04-11 23:59:59
C:4:DATA DELETE ATTLOG
C:5:REBOOT
```

---

## GET /iclock/devicecmd.aspx — Command Result

After executing a command, device replies:
```
GET /iclock/devicecmd.aspx?SN=QJT...&CmdID=1&Return=0&CMD=CHECK
```

`Return=0` = success.

---

## Critical Gotcha — HTTPS

Some firmware versions send TLS ClientHello bytes even when "HTTPS = Off" is set in the device menu. Symptom: server sees garbled binary on port 8081 instead of HTTP GET.

**Fix**: physically toggle HTTPS off in `Menu → COMM → Cloud Server Setting` and reboot the device.
