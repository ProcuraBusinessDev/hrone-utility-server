# adms-push-server

Standalone Python server that receives attendance and enrollment data from biometric terminals in **ADMS push mode** (ZKTeco PUSH SDK v2.0 protocol).

No Windows. No vendor software. No ZKBioTime license.

## Supported devices

Any terminal with `Menu → COMM → Cloud Server Setting → Server Mode: ADMS`:

| Brand | Model | Notes |
|-------|-------|-------|
| eSSL | X2008 | ✅ primary test device (ZAM180_TFT firmware) |
| ZKTeco | SpeedFace-V5L | ✅ same firmware as eSSL X2008 |
| ZKTeco | SpeedFace-V4L, K40 Pro, … | should work |
| Any OEM | ZKTeco-based, ADMS option in menu | likely works |

> **Can't use pyzk?** If `pyzk` returns empty data or `0x07f0` errors, your device has the Pull protocol disabled (common on ZAM180+ firmware). ADMS push is the only path — this server handles it.

## Quick start

```bash
pip install fastapi "uvicorn[standard]"

# Run (default port 8081)
uvicorn server:app --host 0.0.0.0 --port 8081

# Verify
curl http://localhost:8081/health
```

Point device at `<your-server-ip>:8081` with HTTPS disabled. See [`docs/device-setup.md`](docs/device-setup.md).

## Data output

All events are written to JSONL files. Default path: `/var/lib/adms-push-server/`.

```json
{"ts":"2026-04-11T10:30:00Z","type":"attlog","sn":"QJT3253600356","count":1}
{"ts":"2026-04-11T10:30:00Z","type":"attlog","sn":"QJT3253600356","pin":"12345","time":"2026-04-11 10:30:00","status":"0","verify":"15","raw":"12345\t2026-04-11 10:30:00\t0\t15\t0\t0\t0"}
```

VerifyType 15 = face, 1 = fingerprint, 4 = card, 0 = password.

## Command injection

Inject commands by appending JSON to the queue file. The device picks them up on its next poll (~5 seconds).

```bash
# Sync device clock
./examples/inject-set-time.sh

# Or manually
echo '{"id":"cmd1","cmd":"CHECK"}' >> /tmp/adms-cmd-queue.jsonl
echo '{"id":"cmd2","cmd":"SET TIME:2026-04-11 10:30:00"}' >> /tmp/adms-cmd-queue.jsonl
echo '{"id":"cmd3","cmd":"REBOOT"}' >> /tmp/adms-cmd-queue.jsonl
```

## Configuration

Via environment variables (or copy `.env.example` to `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMS_DATA_DIR` | `/var/lib/adms-push-server` | Attendance/operlog JSONL output |
| `ADMS_CMD_QUEUE` | `/tmp/adms-cmd-queue.jsonl` | Command injection queue |
| `ADMS_EVENT_LOG` | `/var/log/adms-push-server/events.jsonl` | All-events log |

## Production deployment (systemd)

```bash
sudo cp systemd/adms-push-server.service /etc/systemd/system/
# Edit User= and paths in the service file first
sudo systemctl daemon-reload
sudo systemctl enable --now adms-push-server
```

## Protocol reference

See [`docs/wire-format.md`](docs/wire-format.md) for the full ATTLOG/OPERLOG format, all endpoints, command syntax, and the HTTPS gotcha.

## Related

- [`realand-bioface-m61-protocol`](https://github.com/Vibhav-Aggarwal/realand-bioface-m61-protocol) — for devices running Realand/EBKN firmware (Secureye S-FB3K, BIOFACE M61BH) — different protocol, different server
- [`zkteco-linux-toolkit`](https://github.com/Vibhav-Aggarwal/zkteco-linux-toolkit) — scripts for ZKTeco devices with port 4370 Pull mode still enabled
- [`biometric-oemware-guide`](https://github.com/Vibhav-Aggarwal/biometric-oemware-guide) — "which firmware is inside my device and which repo should I use?"

## License

MIT
