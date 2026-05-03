# Troubleshooting

## Server sees garbled binary / TLS bytes instead of HTTP

**Symptom**: server log shows `b'\x16\x03\x01...'` or "Invalid HTTP request".

**Cause**: Device firmware sends TLS ClientHello even when "HTTPS = Off" is set in the menu. The toggle in some firmware versions controls only the certificate check, not whether TLS is used.

**Fix**:
1. Go to `Menu → COMM → Cloud Server Setting`
2. Set `HTTPS = Off`
3. **Reboot the device** (power cycle, not just save settings)
4. If still TLS: check if your firmware has a separate "Encrypt" toggle

---

## Device never connects (no log entries)

1. Ping the server from the device's network: `Menu → System Info → Network Diagnosis → Ping`
2. Verify firewall: `sudo ufw allow 8081/tcp` (or whatever port you use)
3. Verify server is actually listening: `ss -tlnp | grep 8081`
4. Check the device's serial number: `Menu → System Info → Device Info` — SN should match log

---

## pyzk / pyzatt returns empty data or `0x07f0` error

Newer ZKTeco OEM firmware (ZAM180 series and later) disables the Pull protocol on port 4370. All commands succeed the TCP handshake but return error code `0x07f0` with an empty payload.

**Diagnostic**:
```python
from zk import ZK
zk = ZK('<device-ip>', port=4370, timeout=5, password=0)
conn = zk.connect()
print(conn.get_users())   # returns [] on disabled pull
```

**Fix**: Switch to ADMS push mode — this server. There is no way to re-enable the pull protocol without firmware downgrade.

---

## No attendance records received

- Device only pushes attendance when `Realtime=1` is in the options response, OR at the scheduled `TransTimes` intervals.
- This server returns `Realtime=1` by default, so punches should arrive within seconds.
- If delayed: check `TransInterval` in `server.py` `_device_options()`.

---

## Commands not being picked up

- Device polls `getrequest.aspx` every few seconds. After appending to the queue file, wait up to ~10 seconds.
- Verify the queue file is readable by the server process: `ls -la /tmp/adms-cmd-queue.jsonl`
- Check `events.jsonl` for `"type": "cmd_sent"` entries.
