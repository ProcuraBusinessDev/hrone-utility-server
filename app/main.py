#!/usr/bin/env python3
"""
ADMS Push Server — receives attendance and enrollment data from biometric terminals.

Tested devices:
  - eSSL X2008 (ZKTeco SpeedFace-V5L OEM, ZAM180_TFT firmware)
  - Any ZKTeco/OEM terminal in "ADMS" / "Cloud Server" push mode

Wire protocol: ZKTeco PUSH SDK v2.0 (HTTP, not HTTPS by default)
Reference: https://www.scribd.com/document/695654988/PUSH-SDK-Communication-Protocol-V2-0-1
"""

import logging
import json
import os
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from app.models.attendance import AttendanceEvent
from app.db.session import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration (override via environment variables)
# ---------------------------------------------------------------------------
DATA_DIR = Path(os.getenv("ADMS_DATA_DIR", "/var/lib/adms-push-server"))
CMD_QUEUE = Path(os.getenv("ADMS_CMD_QUEUE", "/tmp/adms-cmd-queue.jsonl"))
EVENT_LOG = Path(os.getenv("ADMS_EVENT_LOG", "/var/log/adms-push-server/events.jsonl"))
SERVER_VER = "2.2.14"  # version string returned to device during handshake

DATA_DIR.mkdir(parents=True, exist_ok=True)
EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ADMS Push Server", version="1.0.0")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _log_event(event_type: str, sn: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": event_type,
        "sn": sn,
        **payload,
    }
    with open(EVENT_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")


def _save_attlog(sn: str, lines: list[str]):
    records = []

    for line in lines:
        parts = line.split("\t")
        if len(parts) < 2:
            continue

        try:
            attendance_time = datetime.fromisoformat(parts[1].strip())
        except ValueError:
            logger.warning("Invalid attendance timestamp: %r", line)
            continue

        records.append(
            AttendanceEvent(
                ts=attendance_time,
                sn=sn,
                pin=parts[0],
                attendance_time=attendance_time,
                status=parts[2] if len(parts) > 2 else None,
                verify=parts[3] if len(parts) > 3 else None,
                raw=line,
            )
        )

    if not records:
        return 0

    with SessionLocal() as session:
        session.add_all(records)
        session.commit()

    logger.info("Saved %d attendance records", len(records))
    return len(records)


def _save_operlog(sn: str, lines: list[str]):
    out = DATA_DIR / f"operlog_{sn}.jsonl"
    with open(out, "a") as f:
        for line in lines:
            record = {"ts": datetime.utcnow().isoformat() + "Z", "sn": sn, "raw": line}
            f.write(json.dumps(record) + "\n")


def _pop_command() -> Optional[dict]:
    """Return and remove the first entry from CMD_QUEUE, or None."""
    if not CMD_QUEUE.exists():
        return None
    lines = CMD_QUEUE.read_text().splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            cmd = json.loads(line)
            remaining = "\n".join(lines[i + 1 :]) + "\n"
            CMD_QUEUE.write_text(remaining)
            return cmd
        except json.JSONDecodeError:
            continue
    return None


def _device_options(sn: str) -> str:
    """
    Options string returned on device registration (GET /iclock/cdata.aspx).
    Adjust TransTimes (heartbeat interval in seconds) as needed.
    """
    return (
        f"GET OPTION FROM: {sn}\n"
        f"ATTLOGStamp=None\n"
        f"OPERLOGStamp=9999\n"
        f"ATTPHOTOStamp=None\n"
        f"ErrorDelay=30\n"
        f"Delay=10\n"
        f"TransTimes=00:00;14:05\n"
        f"TransInterval=1\n"
        f"TransFlag=TransData AttLog OpLog EnrollUser\n"
        f"TimeZone=5.5\n"
        f"Realtime=1\n"
        f"Encrypt=None\n"
        f"ServerVer={SERVER_VER}\n"
        f"TableNameStamp=None\n"
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/iclock/cdata.aspx", response_class=PlainTextResponse)
async def device_register(request: Request):
    """Device registration — sent once on boot and periodically."""
    params = dict(request.query_params)
    sn = params.get("SN", "UNKNOWN")
    _log_event("register", sn, {"params": params})
    return _device_options(sn)


@app.post("/iclock/cdata.aspx", response_class=PlainTextResponse)
async def data_push(request: Request):
    """
    Attendance + enrollment data push.

    Body format:
      SN=QJT...&table=ATTLOG&Stamp=...&Count=N\tATTLOG\n
      PIN<TAB>DateTime<TAB>Status<TAB>VerifyType<TAB>WorkCode<TAB>0<TAB>0\n
    """
    params = dict(request.query_params)
    sn = params.get("SN", "UNKNOWN")

    raw_body = await request.body()
    body_text = raw_body.decode("utf-8", errors="replace")

    table = params.get("table", "").upper()
    lines = [ln for ln in body_text.splitlines() if ln.strip()]

    if table == "ATTLOG":
        data_lines = [ln for ln in lines if "\t" in ln and not ln.startswith("SN=")]

        try:
            count = _save_attlog(sn, data_lines)
        except SQLAlchemyError:
            logger.exception(
                "Failed to save attendance logs for device %s",
                sn,
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to persist attendance records",
            )

        _log_event("attlog", sn, {"count": len(data_lines)})
        return PlainTextResponse(f"OK: {count}")

    if table in ("OPERLOG", "OPERLOG_RECORD"):
        _save_operlog(sn, lines)
        _log_event("operlog", sn, {"count": len(lines)})
        return f"OK: {len(lines)}"

    # Fallback — store as-is
    _log_event(
        "push_unknown",
        sn,
        {"table": table, "lines": len(lines), "body": body_text[:500]},
    )
    return "OK"


@app.get("/iclock/getrequest.aspx", response_class=PlainTextResponse)
async def get_command(request: Request):
    """
    Device polls this every few seconds asking "any command for me?".

    Inject a command by appending JSON to CMD_QUEUE:
      echo '{"id":"cmd001","cmd":"CHECK"}' >> /tmp/adms-cmd-queue.jsonl

    Supported commands (device-dependent):
      C:cmd_id:CHECK            — device replies with status
      C:cmd_id:SET TIME:YYYY-MM-DD HH:MM:SS
      C:cmd_id:DATA QUERY ATTLOG StartTime=... EndTime=...
      C:cmd_id:DATA DELETE ATTLOG
    """
    params = dict(request.query_params)
    sn = params.get("SN", "UNKNOWN")

    cmd = _pop_command()
    if cmd:
        cmd_id = cmd.get("id", "C1")
        cmd_str = cmd.get("cmd", "CHECK")
        _log_event("cmd_sent", sn, {"cmd": cmd_str, "id": cmd_id})
        return f"C:{cmd_id}:{cmd_str}"

    return "OK"


@app.get("/iclock/devicecmd.aspx", response_class=PlainTextResponse)
async def device_cmd_result(request: Request):
    """Device posts back the result of a command we sent."""
    params = dict(request.query_params)
    sn = params.get("SN", "UNKNOWN")
    cmdid = params.get("CmdID", "")
    ret = params.get("Return", "")
    _log_event("cmd_result", sn, {"cmd_id": cmdid, "return": ret, "params": params})
    return "OK"


@app.get("/iclock/ping.aspx", response_class=PlainTextResponse)
async def ping(request: Request):
    """Heartbeat — device sends this every TransInterval seconds."""
    params = dict(request.query_params)
    sn = params.get("SN", "UNKNOWN")
    _log_event("ping", sn, {})
    return "OK"


@app.get("/health")
async def health():
    attlogs = list(DATA_DIR.glob("attlog_*.jsonl"))
    operlogs = list(DATA_DIR.glob("operlog_*.jsonl"))
    return {
        "status": "running",
        "devices": len(set(f.stem.split("_", 1)[1] for f in attlogs + operlogs)),
        "attlog_files": len(attlogs),
        "operlog_files": len(operlogs),
        "cmd_queue": CMD_QUEUE.exists(),
    }
