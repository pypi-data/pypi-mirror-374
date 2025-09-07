#!/usr/bin/env python3
"""
CloudChain for Google Drive — Single-Chain Backup Manager

Features:
- First run: asks for LOCAL BACKUP ROOT.
- All state managed inside <LOCAL_ROOT>/cloud_backup/:
    accounts.yaml, per-account dirs (token.json, uploads.yaml, mirrored files).
- Account naming enforced:
    <base><NNN>.cloudchain@gmail.com  (e.g., mybackup001.cloudchain@gmail.com)
- On first account creation:
    Shows WARNING requiring suffix "001.cloudchain".
- On next account creation:
    Checks quota >=95% OR >=14.25 GB, computes required next email.
- Remote path always Drive:/backup/
- Optional local mirror on upload; ledger tracks cloud vs local separately.
- Download from Drive (with export for Google Docs/Sheets/Slides).
- Delete from Drive and delete from local mirror.
- Reset option wipes all data/config and exits (with confirmation).
- NEW: Export / Restore Application State (.ccbak, encrypted).
- NEW: Color-coded ledger display (UNC Wolf Gray / Navy / Carolina Blue).
- NEW: Submenu-driven UI (Accounts, Cloud, Local, System).
"""

import os
import re
import io
import shutil
import time
import webbrowser
import json
import tarfile
import secrets
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

import yaml
import keyring
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

console = Console()

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_NAME = "cloudchain"
INDEX_WIDTH = 3
REQUIRED_SUFFIX = "cloudchain"
RE_EMAIL_LOCAL = re.compile(rf"^(?P<base>.+?)(?P<idx>\d{{{INDEX_WIDTH}}})\.{REQUIRED_SUFFIX}$")
GMAIL_DOMAIN = "gmail.com"

MAX_BYTES = 15 * 1024**3
CUTOFF_BYTES = int(MAX_BYTES * 0.95)

# UNC Tar Heel color palette
UNC_GRAY = "#7A8690"       # Wolf Gray
UNC_NAVY = "#13294B"       # Navy Blue
UNC_CAROLINA = "#7BAFD4"   # Carolina Blue

# Backup constants
BACKUP_MAGIC = b"CCBAK\0"
BACKUP_VERSION = 1
# ---------------- Keyring & Path helpers ---------------- #

def kr_get(key: str) -> str | None:
    return keyring.get_password(SERVICE_NAME, key)

def kr_set(key: str, val: str) -> None:
    keyring.set_password(SERVICE_NAME, key, val)

def get_base_root() -> Path:
    base = kr_get("base_backup")
    if not base:
        root_input = Prompt.ask("Enter LOCAL BACKUP ROOT (CloudChain will create 'cloud_backup' here)")
        root = Path(root_input).expanduser().resolve()
        cloud_backup = root / "cloud_backup"
        cloud_backup.mkdir(parents=True, exist_ok=True)
        kr_set("base_backup", str(cloud_backup))
        return cloud_backup
    return Path(base).expanduser().resolve()

def reg_path() -> Path:
    return get_base_root() / "accounts.yaml"

def account_dir_local(account_local: str) -> Path:
    d = get_base_root() / account_local
    d.mkdir(parents=True, exist_ok=True)
    return d

def token_path(account_local: str) -> Path:
    return account_dir_local(account_local) / "token.json"

def ledger_path(account_local: str) -> Path:
    return account_dir_local(account_local) / "uploads.yaml"

# ---------------- Registry ---------------- #

def load_registry() -> Dict:
    rp = reg_path()
    if not rp.exists() or rp.stat().st_size == 0:
        return {}
    with rp.open() as f:
        return yaml.safe_load(f) or {}

def save_registry(reg: Dict) -> None:
    with reg_path().open("w") as f:
        yaml.safe_dump(reg, f, sort_keys=False)

def get_current_account_local() -> str:
    reg = load_registry()
    return reg["current_account"]

def get_chain_base(reg: Dict) -> str | None:
    return reg.get("chain_base")
    
    
# ---------------- Init flow ---------------- #

def _extract_local_and_domain(email: str) -> Tuple[str, str]:
    email = email.strip().lower()
    if "@" not in email:
        raise ValueError("Enter FULL Gmail (e.g., mybackup001.cloudchain@gmail.com)")
    local, domain = email.split("@", 1)
    return local, domain

def _validate_first_account(email: str) -> Tuple[str, str, int]:
    local, domain = _extract_local_and_domain(email)
    if domain != GMAIL_DOMAIN:
        raise ValueError(f"Domain must be {GMAIL_DOMAIN}")
    m = RE_EMAIL_LOCAL.match(local)
    if not m:
        raise ValueError("Username must end with 001.cloudchain")
    base = m.group("base")
    idx = int(m.group("idx"))
    if idx != 1:
        raise ValueError("First account must end with 001.cloudchain")
    return base, local, idx

def _format_local(chain_base: str, idx: int) -> str:
    return f"{chain_base}{idx:0{INDEX_WIDTH}d}.{REQUIRED_SUFFIX}"

def _required_email_for_next(reg: Dict) -> str:
    chain_base = reg["chain_base"]
    next_idx = len(reg["accounts"]) + 1
    return f"{_format_local(chain_base, next_idx)}@{GMAIL_DOMAIN}"

def sanity_and_init_if_needed() -> None:
    reg = load_registry()
    if reg.get("accounts"):
        return
    console.print("\n[bold red]WARNING: Gmail username MUST end with '001.cloudchain'[/]")
    console.print("Example: mybackup001.cloudchain@gmail.com\n")
    input("Press Enter to continue to Google signup...")
    webbrowser.open("https://accounts.google.com/signup")
    email = Prompt.ask("Enter EXACT Gmail you created").strip()
    try:
        chain_base, local_first, _ = _validate_first_account(email)
    except Exception as e:
        console.print(f"[red]ERROR:[/] {e}")
        input("Press any key to exit...")
        raise SystemExit(1)
    new_reg = {
        "chain_base": chain_base,
        "domain": GMAIL_DOMAIN,
        "suffix": REQUIRED_SUFFIX,
        "accounts": [local_first],
        "current_account": local_first,
    }
    save_registry(new_reg)
    account_dir_local(local_first)
    if not ledger_path(local_first).exists():
        with ledger_path(local_first).open("w") as f:
            yaml.safe_dump([], f)
    console.print(f"[green]Setup complete.[/] First account: {email}")

# ---------------- Ledger helpers ---------------- #

def load_ledger(account_local: str) -> List[Dict]:
    p = ledger_path(account_local)
    if p.exists():
        with p.open() as f:
            return yaml.safe_load(f) or []
    return []

def save_ledger(account_local: str, rows: List[Dict]) -> None:
    with ledger_path(account_local).open("w") as f:
        yaml.safe_dump(rows, f, sort_keys=False)

def _account_local_dir(account_local: str) -> Path:
    return account_dir_local(account_local)

def _has_local_mirror(rec: Dict, account_local: str) -> bool:
    # Check current path in record
    lp = rec.get("local_path")
    if lp and Path(lp).exists():
        rec["local_mirrored"] = True
        return True

    # If path is missing, check for same-name file in account dir
    candidate = account_dir_local(account_local) / rec.get("name", "")
    if candidate.exists():
        rec["local_mirrored"] = True
        rec["local_path"] = str(candidate)
        return True

    # Nothing found locally → clear flags
    rec["local_mirrored"] = False
    rec["local_path"] = ""
    return False

def _set_local_mirror(rec: Dict, account_local: str, local_path: Path) -> None:
    rec["local_mirrored"] = True
    rec["local_path"] = str(local_path)

def _clear_local_mirror(rec: Dict) -> None:
    rec["local_mirrored"] = False
    rec["local_path"] = ""

# ---------------- Download helpers ---------------- #

_GOOGLE_EXPORTS = {
    "application/vnd.google-apps.document": ("application/pdf", ".pdf"),
    "application/vnd.google-apps.spreadsheet": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
    "application/vnd.google-apps.presentation": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
    "application/vnd.google-apps.drawing": ("image/png", ".png"),
    "application/vnd.google-apps.script": ("application/zip", ".zip"),
}

def _get_file_meta(service, file_id: str):
    return service.files().get(fileId=file_id, fields="id,name,mimeType,size").execute()

def _human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    f = float(n); i = 0
    while f >= 1024 and i < len(units) - 1:
        f /= 1024.0; i += 1
    return f"{f:.1f} {units[i]}" if i > 1 else f"{int(f)} {units[i]}"

def _human_rate(bps: float) -> str:
    return f"{_human_bytes(int(bps))}/s" if bps > 0 else "--/s"

def _human_eta(seconds: float | None) -> str:
    if not seconds or seconds == float("inf"):
        return "--:--"
    s = int(seconds); h, r = divmod(s, 3600); m, s = divmod(r, 60)
    return f"{h}h {m:02d}m" if h else f"{m:02d}m {s:02d}s"

def _parse_indices(expr: str, max_len: int) -> List[int]:
    out = set()
    for part in expr.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a, b = int(a), int(b)
            if a > b: a, b = b, a
            for i in range(a, b + 1):
                if 1 <= i <= max_len:
                    out.add(i)
        else:
            i = int(part)
            if 1 <= i <= max_len:
                out.add(i)
    return sorted(out)

def _download_by_id(service, file_id: str, dest_path: Path):
    meta = _get_file_meta(service, file_id)
    name = meta.get("name")
    mime = meta.get("mimeType", "")
    size = int(meta.get("size")) if (meta.get("size") or "").isdigit() else None

    if mime.startswith("application/vnd.google-apps."):
        export_mime, ext = _GOOGLE_EXPORTS.get(mime, ("application/pdf", ".pdf"))
        if not dest_path.name.lower().endswith(ext):
            dest_path = dest_path.with_suffix(ext)
        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        request = service.files().get_media(fileId=file_id)

    with io.FileIO(str(dest_path), "wb") as fh, Progress(
        TextColumn("[bold]Downloading[/]"),
        BarColumn(),
        TextColumn("{task.percentage:>4.0f}%"),
        TextColumn("• {task.fields[done]}/{task.fields[total_h]}"),
        TextColumn("• {task.fields[speed]}"),
        TextColumn("• ETA {task.fields[eta]}"),
        console=console, transient=True,
    ) as progress:
        total_h = _human_bytes(size) if size else "--"
        task = progress.add_task(
            name, total=size or 0,
            done="0 B", total_h=total_h, speed="--/s", eta="--:--"
        )

        downloader = MediaIoBaseDownload(fh, request, chunksize=8 * 1024 * 1024)
        start = time.time()
        bytes_written = 0
        done = False
        while not done:
            status, done = downloader.next_chunk()
            try:
                bytes_written = fh.tell()
            except Exception:
                if status and hasattr(status, "total_size") and status.total_size:
                    bytes_written = int(status.total_size * status.progress())
            elapsed = max(time.time() - start, 1e-6)
            avg_bps = bytes_written / elapsed
            eta = (None if not size or avg_bps <= 0 else (max(size - bytes_written, 0) / avg_bps))
            progress.update(
                task,
                completed=bytes_written if size else 0,
                done=_human_bytes(bytes_written),
                speed=_human_rate(avg_bps),
                eta=_human_eta(eta),
            )

    return {"id": file_id, "name": name, "path": str(dest_path)}

# ---------------- Commands ---------------- #
# ---------------- Google Drive helpers ---------------- #

def build_service(account_local: str):
    cid = kr_get("client_id")
    csec = kr_get("client_secret")
    if not cid or not csec:
        console.print("[red]Missing client_id/client_secret in keyring![/]")
        raise SystemExit(1)

    config = {
        "installed": {
            "client_id": cid,
            "project_id": "cloudchain-local",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": csec,
            "redirect_uris": ["http://localhost"],
        }
    }

    creds = None
    tpath = token_path(account_local)

    if tpath.exists():
        creds = Credentials.from_authorized_user_file(str(tpath), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(config, SCOPES)
            auth_url, _ = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="select_account"
            )
            webbrowser.open(auth_url)
            creds = flow.run_local_server(
                port=0,
                authorization_prompt_message="",
                open_browser=False
            )

        with tpath.open("w") as f:
            f.write(creds.to_json())
        os.chmod(tpath, 0o600)

    return build("drive", "v3", credentials=creds, cache_discovery=False)

def upload_file(service, local_path: Path, parent_id: str):
    media = MediaFileUpload(str(local_path), chunksize=8 * 1024 * 1024, resumable=True)
    body = {"name": local_path.name, "parents": [parent_id]}
    request = service.files().create(body=body, media_body=media, fields="id,name,size")

    def human_bytes(n: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB"]
        f = float(n); i = 0
        while f >= 1024 and i < len(units) - 1:
            f /= 1024.0; i += 1
        return f"{f:.1f} {units[i]}" if i > 1 else f"{int(f)} {units[i]}"

    total = os.path.getsize(local_path)
    start = time.time()

    with Progress(
        TextColumn("[bold]Uploading[/]"), BarColumn(),
        TextColumn("{task.percentage:>4.0f}%"),
        TextColumn("• {task.fields[done]}/{task.fields[total_h]}"),
        TextColumn("• {task.fields[speed]}"),
        TextColumn("• ETA {task.fields[eta]}"),
        console=console, transient=True,
    ) as progress:
        task = progress.add_task(local_path.name, total=total,
            done="0 B", total_h=human_bytes(total),
            speed="--/s", eta="--:--")

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                completed = int(status.resumable_progress or 0)
                elapsed = max(time.time() - start, 1e-6)
                avg_bps = completed / elapsed
                remaining = max(total - completed, 0)
                eta = (remaining / avg_bps) if avg_bps > 0 else None

                def human_rate(bps): return f"{human_bytes(int(bps))}/s" if bps > 0 else "--/s"
                def human_eta(sec):
                    if not sec or sec == float("inf"): return "--:--"
                    m, s = divmod(int(sec), 60); h, m = divmod(m, 60)
                    return f"{h}h{m:02d}m" if h else f"{m:02d}m{s:02d}s"

                progress.update(task, completed=completed,
                    done=human_bytes(completed),
                    speed=human_rate(avg_bps),
                    eta=human_eta(eta))
    return response

def get_backup_folder(service) -> str:
    resp = service.files().list(
        q="name='backup' and mimeType='application/vnd.google-apps.folder' "
          "and 'root' in parents and trashed=false",
        fields="files(id,name)"
    ).execute()
    files = resp.get("files", [])
    if files:
        return files[0]["id"]
    meta = {
        "name": "backup",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": ["root"]
    }
    folder = service.files().create(body=meta, fields="id").execute()
    return folder["id"]

def show_current_account():
    reg = load_registry()
    if not reg.get("accounts"):
        console.print("[yellow]No account recorded yet.[/]")
        return
    account = reg["current_account"]
    console.print(f"[cyan]Current account:[/] {account}@{reg.get('domain','gmail.com')}")
    console.print(f"Local backup folder: {account_dir_local(account)}")

def switch_account():
    reg = load_registry()
    accts = reg.get("accounts", [])
    if not accts:
        console.print("[yellow]No accounts available.[/]")
        return
    console.print("Accounts:")
    for idx, acc in enumerate(accts, start=1):
        console.print(f"  {idx}) {acc}@{reg.get('domain','gmail.com')}")
    choice = Prompt.ask("Enter account number to switch")
    try:
        idx = int(choice) - 1
        reg["current_account"] = accts[idx]
        save_registry(reg)
        console.print(f"[green]Switched to {reg['current_account']}[/]")
    except Exception:
        console.print("[red]Invalid choice[/]")

def upload_file_for_account():
    reg = load_registry()
    account = reg["current_account"]
    service = build_service(account)
    backup_id = get_backup_folder(service)

    local_file = Path(Prompt.ask("Enter path to file to upload")).expanduser().resolve()
    if not local_file.exists():
        console.print("[red]File not found[/]")
        return

    mirror_local = Confirm.ask("Mirror to local backup?", default=True)

    response = upload_file(service, local_file, backup_id)
    record = {
        "name": response.get("name"),
        "id": response.get("id"),
        "size": response.get("size"),
        "uploaded_from": str(local_file),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "local_mirrored": False,
        "local_path": "",
    }

    if mirror_local:
        dest = _account_local_dir(account) / local_file.name
        if local_file.resolve() != dest.resolve():
            dest.write_bytes(local_file.read_bytes())
        _set_local_mirror(record, account, dest)

    ledger = load_ledger(account)
    ledger.append(record)
    save_ledger(account, ledger)

    if mirror_local:
        console.print(f"[green]Uploaded[/] {local_file} → Drive:/backup/ and mirrored locally at {record['local_path']}")
    else:
        console.print(f"[green]Uploaded[/] {local_file} → Drive:/backup/ (no local mirror)")
        
def list_cloud_contents():
    reg = load_registry()
    account = reg.get("current_account")
    if not account:
        console.print(f"[{UNC_GRAY}]No account recorded yet.[/]")
        return
    ledger = load_ledger(account)
    if not ledger:
        console.print(f"[{UNC_GRAY}]No uploads recorded for this account[/]")
        return

    table = Table(
        title=f"[{UNC_CAROLINA}]Cloud Ledger for {account}[/]",
        show_lines=True,
        style=UNC_GRAY,
        border_style=UNC_NAVY
    )
    table.add_column("Name")
    table.add_column("Size")
    table.add_column("Uploaded From")
    table.add_column("When")
    table.add_column("Local Mirror")

    for rec in ledger:
        mirrored = _has_local_mirror(rec, account)
        if mirrored and rec.get("id"):      # both
            row_style = UNC_CAROLINA
        elif mirrored and not rec.get("id"): # local only
            row_style = UNC_GRAY
        elif (not mirrored) and rec.get("id"): # cloud only
            row_style = UNC_NAVY
        else:
            row_style = UNC_GRAY

        local_badge = "Yes" if mirrored else "No"

        table.add_row(
            rec.get("name",""),
            str(rec.get("size","")),
            rec.get("uploaded_from",""),
            rec.get("timestamp",""),
            local_badge,
            style=row_style
        )

    console.print(table)
    console.print(f"[{UNC_GRAY}]Row colors → Gray: cloud only • Navy: local only • Carolina Blue: both[/]")

def show_local_backup():
    reg = load_registry()
    account = reg.get("current_account")
    if not account:
        console.print(f"[{UNC_GRAY}]No account recorded yet.[/]")
        return

    folder = account_dir_local(account)
    items = list(folder.rglob("*"))
    if not items:
        console.print(f"[{UNC_GRAY}]Local backup folder for {account} is empty[/]")
        return

    table = Table(
        title=f"[{UNC_CAROLINA}]Local Backup for {account}[/]",
        show_lines=True,
        style=UNC_GRAY,
        border_style=UNC_NAVY
    )
    table.add_column("Type", style=UNC_NAVY)
    table.add_column("Path", style=UNC_GRAY)

    for p in items:
        kind = "DIR" if p.is_dir() else "FILE"
        row_style = UNC_GRAY if p.is_dir() else UNC_NAVY
        table.add_row(kind, str(p.relative_to(folder)), style=row_style)

    console.print(table)
    console.print(f"[{UNC_GRAY}]Row colors → Navy: directories • Gray: files[/]")

def delete_local_backup():
    reg = load_registry()
    account = reg.get("current_account")
    if not account:
        console.print(f"[{UNC_GRAY}]No account recorded yet.[/]")
        return

    ledger = load_ledger(account)
    candidates = [(i+1, rec) for i, rec in enumerate(ledger) if _has_local_mirror(rec, account)]
    if not candidates:
        console.print(f"[{UNC_GRAY}]No local-mirrored files to delete.[/]")
        return

    table = Table(
        title=f"[{UNC_CAROLINA}]Local Mirrors for {account}[/]",
        style=UNC_GRAY,
        border_style=UNC_NAVY
    )
    table.add_column("Index", justify="right", style=UNC_NAVY)
    table.add_column("Name", style=UNC_GRAY)
    table.add_column("Local Path", style=UNC_GRAY)
    for idx, rec in candidates:
        table.add_row(str(idx), rec.get("name",""), rec.get("local_path",""), style=UNC_GRAY)
    console.print(table)

    choice = Prompt.ask("Enter index to delete from local backup (blank to cancel)", default="")
    if not choice.strip():
        console.print(f"[{UNC_GRAY}]Cancelled.[/]")
        return

    try:
        idx = int(choice)
        if idx < 1 or idx > len(ledger):
            raise ValueError
        rec = ledger[idx - 1]
        if not _has_local_mirror(rec, account):
            console.print(f"[{UNC_NAVY}]Selected item has no local mirror.[/]")
            return
    except Exception:
        console.print(f"[{UNC_NAVY}]Invalid choice[/]")
        return

    lp = rec.get("local_path")
    try:
        if lp and Path(lp).exists():
            Path(lp).unlink(missing_ok=True)
        _clear_local_mirror(rec)
        save_ledger(account, ledger)
        console.print(f"[{UNC_CAROLINA}]Removed local mirror[/] for {rec.get('name','')} at {lp}")
    except Exception as e:
        console.print(f"[{UNC_NAVY}]Error removing local mirror:[/] {e}")


def delete_file_for_account():
    reg = load_registry()
    account = reg.get("current_account")
    if not account:
        console.print("[yellow]No account recorded yet.[/]")
        return

    ledger = load_ledger(account)
    if not ledger:
        console.print("[yellow]No uploads recorded for this account[/]")
        return

    table = Table(title=f"Cloud Ledger for {account}")
    table.add_column("Index", justify="right")
    table.add_column("Name")
    table.add_column("Size")
    table.add_column("When")
    for idx, rec in enumerate(ledger, start=1):
        table.add_row(str(idx), rec["name"], str(rec.get("size", "")), rec.get("timestamp", ""))
    console.print(table)

    choice = Prompt.ask("Enter index of file to delete from Drive (or blank to cancel)", default="")
    if not choice.strip():
        console.print("[yellow]Cancelled.[/]")
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(ledger):
            raise ValueError
    except ValueError:
        console.print("[red]Invalid choice[/]")
        return

    rec = ledger[idx]
    file_id = rec["id"]

    try:
        build_service(account).files().delete(fileId=file_id).execute()
        console.print(f"[green]Deleted[/] {rec['name']} (id={file_id}) from Drive")
        ledger.pop(idx)
        save_ledger(account, ledger)
    except Exception as e:
        console.print(f"[red]Error deleting file:[/] {e}")

def download_file_for_account():
    reg = load_registry()
    account = reg.get("current_account")
    if not account:
        console.print("[yellow]No account recorded yet.[/]")
        return

    ledger = load_ledger(account)
    if not ledger:
        console.print("[yellow]No uploads recorded for this account[/]")
        return

    table = Table(title=f"Cloud Ledger for {account}")
    table.add_column("Index", justify="right")
    table.add_column("Name")
    table.add_column("Size")
    table.add_column("When")
    for idx, rec in enumerate(ledger, start=1):
        table.add_row(str(idx), rec.get("name",""), str(rec.get("size","")), rec.get("timestamp",""))
    console.print(table)

    expr = Prompt.ask("Enter index(es) to download (e.g., 2 or 1,3,5 or 2-4). Blank to cancel", default="")
    if not expr.strip():
        console.print("[yellow]Cancelled.[/]")
        return

    try:
        choices = _parse_indices(expr, len(ledger))
        if not choices:
            console.print("[red]No valid indices selected.[/]")
            return
    except Exception:
        console.print("[red]Invalid selection format.[/]")
        return

    dest_dir = _account_local_dir(account)
    service = build_service(account)
    successes, failures = [], []

    for i in choices:
        rec = ledger[i - 1]
        file_id = rec.get("id")
        name = rec.get("name", f"drive-file-{file_id}")
        if not file_id:
            failures.append((name, "missing file id in ledger"))
            continue
        dest_path = dest_dir / name
        try:
            result = _download_by_id(service, file_id, dest_path)
            _set_local_mirror(rec, account, Path(result["path"]))
            successes.append(result)
        except Exception as e:
            failures.append((name, str(e)))

    save_ledger(account, ledger)

    if successes:
        table_ok = Table(title="Downloaded")
        table_ok.add_column("Name"); table_ok.add_column("Saved To")
        for r in successes:
            table_ok.add_row(r["name"], r["path"])
        console.print(table_ok)

    if failures:
        for n, err in failures:
            console.print(f"[red]Failed[/] {n}: {err}")

def check_quota(account_local: str) -> Tuple[int, int, float]:
    service = build_service(account_local)
    about = service.about().get(fields="storageQuota").execute()
    quota = about.get("storageQuota", {})
    used = int(quota.get("usage", 0))
    limit = int(quota.get("limit", 1))
    pct = used / limit if limit else 0.0
    return used, limit, pct

def sync_local_backup_to_cloud():
    reg = load_registry()
    account = reg["current_account"]
    files = [p for p in _account_local_dir(account).rglob("*") if p.is_file()]
    if not files:
        console.print("[yellow]Local backup folder is empty[/]")
        return
    mode = Prompt.ask("Sync mode: (m)erge or (o)verwrite?", choices=["m","o"], default="m")
    service = build_service(account)
    backup_id = get_backup_folder(service)
    ledger = load_ledger(account)
    ledger_names = {r["name"] for r in ledger}
    uploaded = 0
    for f in files:
        if mode == "m" and f.name in ledger_names:
            continue
        response = upload_file(service, f, backup_id)
        record = {
            "name": response.get("name"),
            "id": response.get("id"),
            "size": response.get("size"),
            "uploaded_from": str(f),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "local_mirrored": True,
            "local_path": str(f),
        }
        ledger.append(record)
        uploaded += 1
    save_ledger(account, ledger)
    console.print(f"[green]Sync complete.[/] Files uploaded: {uploaded}")

def sync_cloud_to_local():
    reg = load_registry()
    account = reg["current_account"]
    service = build_service(account)
    backup_id = get_backup_folder(service)

    # Get list of files from Drive:/backup
    resp = service.files().list(
        q=f"'{backup_id}' in parents and trashed=false",
        fields="files(id,name,size,mimeType,modifiedTime)"
    ).execute()
    files = resp.get("files", [])

    if not files:
        console.print("[yellow]No files found in Drive backup folder[/]")
        return

    dest_dir = _account_local_dir(account)
    ledger = load_ledger(account)
    ledger_names = {r["name"] for r in ledger}
    downloaded = 0

    for f in files:
        name = f.get("name")
        fid = f.get("id")
        dest_path = dest_dir / name
        try:
            result = _download_by_id(service, fid, dest_path)
            if name not in ledger_names:
                record = {
                    "name": result["name"],
                    "id": result["id"],
                    "size": f.get("size"),
                    "uploaded_from": "Drive",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "local_mirrored": True,
                    "local_path": str(dest_path),
                }
                ledger.append(record)
            else:
                for rec in ledger:
                    if rec["name"] == name:
                        _set_local_mirror(rec, account, dest_path)
            downloaded += 1
        except Exception as e:
            console.print(f"[red]Failed to download {name}: {e}")

    save_ledger(account, ledger)
    console.print(f"[green]Sync complete.[/] Files downloaded: {downloaded}")

def create_next_account():
    reg = load_registry()
    if not reg.get("accounts"):
        console.print("[red]No chain exists yet.[/]")
        return
    current_local = reg["current_account"]
    used, limit, pct = check_quota(current_local)
    gb_used = used / (1024**3)
    gb_limit = limit / (1024**3)
    console.print(f"[cyan]Quota:[/] {gb_used:.2f} GB / {gb_limit:.2f} GB ({pct*100:.1f}%)")
    if pct < 0.95 and used < CUTOFF_BYTES:
        console.print("[yellow]Current account not full enough.[/]")
        return
    required_email = _required_email_for_next(reg)
    console.print("\n[bold red]WARNING: You MUST create this Gmail EXACTLY:[/]")
    console.print(f"    [cyan]{required_email}[/]")
    input("Press Enter to continue to Google signup...")
    webbrowser.open("https://accounts.google.com/signup")
    actual = Prompt.ask("Enter EXACT Gmail you created").strip().lower()
    if actual != required_email.lower():
        console.print(f"[red]ERROR: Expected {required_email}, got {actual}[/]")
        input("Press any key to exit...")
        raise SystemExit(1)
    new_local, _ = actual.split("@", 1)
    reg["accounts"].append(new_local)
    reg["current_account"] = new_local
    save_registry(reg)
    account_dir_local(new_local)
    if not ledger_path(new_local).exists():
        save_ledger(new_local, [])
    console.print(f"[green]Account added:[/] {actual}")

def reset_cloudchain():
    root = get_base_root()
    console.print("\n[bold red]WARNING: This will WIPE ALL CloudChain data under[/] "
                  f"[cyan]{root}[/]\n"
                  "[bold]This includes accounts.yaml, tokens, ledgers, and local mirrors.[/]")
    confirm_phrase = Prompt.ask("Type 'WIPE' to confirm, or anything else to cancel", default="")
    if confirm_phrase.strip() != "WIPE":
        console.print("[yellow]Reset cancelled.[/]")
        return

    rp = reg_path()
    if rp.exists():
        rp.unlink(missing_ok=True)
    for sub in root.glob("*"):
        if sub.is_dir() and ((sub / "token.json").exists() or (sub / "uploads.yaml").exists()):
            shutil.rmtree(sub, ignore_errors=True)

    for key in ["base_backup", "chain_base", "client_id", "client_secret"]:
        try:
            keyring.delete_password(SERVICE_NAME, key)
        except Exception:
            pass

    console.print("[green]CloudChain reset complete. Restart the app to reinitialize.[/]")
    raise SystemExit(0)

# ---------------- App State Backup / Restore ---------------- #

def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**15,
        r=8,
        p=1,
    )
    return kdf.derive(password.encode())

def backup_app_state():
    reg = load_registry()
    if not reg.get("accounts"):
        console.print("[yellow]No chain exists yet, nothing to back up.[/]")
        return

    password = Prompt.ask("Enter passphrase to encrypt backup (will not be saved)")
    confirm = Prompt.ask("Confirm passphrase")
    if password != confirm:
        console.print("[red]Passphrases do not match.[/]")
        return

    root = get_base_root()
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_file = root / f"cloudchain_state_{ts}.ccbak"

    # gather files
    files_to_backup = [reg_path()]
    for acct in reg.get("accounts", []):
        if token_path(acct).exists():
            files_to_backup.append(token_path(acct))
        if ledger_path(acct).exists():
            files_to_backup.append(ledger_path(acct))

    # include keyring entries
    kr_dump = {}
    for key in ["base_backup", "chain_base", "client_id", "client_secret"]:
        val = kr_get(key)
        if val:
            kr_dump[key] = val
    kr_path = root / "keyring_dump.yaml"
    with kr_path.open("w") as f:
        yaml.safe_dump(kr_dump, f)
    files_to_backup.append(kr_path)

    # create tarball
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode="w") as tar:
        for f in files_to_backup:
            tar.add(f, arcname=f.name)
    kr_path.unlink(missing_ok=True)

    data = tar_bytes.getvalue()

    # encrypt
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, data, None)

    with backup_file.open("wb") as f:
        f.write(BACKUP_MAGIC)
        header = {
            "version": BACKUP_VERSION,
            "created_at": ts,
            "kdf": {"algo": "scrypt", "salt": salt.hex(), "n": 2**15, "r": 8, "p": 1},
            "cipher": {"algo": "AES-256-GCM", "nonce": nonce.hex()},
        }
        header_bytes = json.dumps(header).encode()
        f.write(len(header_bytes).to_bytes(4, "big"))
        f.write(header_bytes)
        f.write(ct)

    console.print(f"[green]Application state exported:[/] {backup_file}")
    input("Press Enter to continue...")

def restore_app_state():
    path_str = Prompt.ask("Enter path to backup file or directory")
    path = Path(path_str).expanduser().resolve()

    backup_file = None
    if path.is_dir():
        files = sorted(path.glob("*.ccbak"))
        if not files:
            console.print(f"[red]No .ccbak files found in {path}[/]")
            return
        if len(files) == 1:
            backup_file = files[0]
        else:
            console.print("Found the following backups:")
            for i, f in enumerate(files, start=1):
                console.print(f"  {i}) {f.name}")
            choice = Prompt.ask("Select a backup number", default="1")
            try:
                idx = int(choice) - 1
                backup_file = files[idx]
            except Exception:
                console.print("[red]Invalid choice[/]")
                return
    else:
        if not path.exists() or not path.is_file() or path.suffix.lower() != ".ccbak":
            console.print("[red]Invalid backup path[/]")
            return
        backup_file = path

    password = Prompt.ask("Enter passphrase to decrypt backup")

    with backup_file.open("rb") as f:
        magic = f.read(len(BACKUP_MAGIC))
        if magic != BACKUP_MAGIC:
            console.print("[red]Invalid backup file[/]")
            return
        header_len = int.from_bytes(f.read(4), "big")
        header = json.loads(f.read(header_len).decode())
        salt = bytes.fromhex(header["kdf"]["salt"])
        nonce = bytes.fromhex(header["cipher"]["nonce"])
        ct = f.read()

    try:
        key = _derive_key(password, salt)
        aesgcm = AESGCM(key)
        data = aesgcm.decrypt(nonce, ct, None)
    except Exception:
        console.print("[red]Decryption failed (wrong passphrase or corrupt file)[/]")
        return

    # extract tar
    tar_bytes = io.BytesIO(data)
    with tarfile.open(fileobj=tar_bytes, mode="r") as tar:
        tar.extractall(get_base_root())

    # restore keyring
    kr_path = get_base_root() / "keyring_dump.yaml"
    if kr_path.exists():
        with kr_path.open() as f:
            kr_dump = yaml.safe_load(f) or {}
        for k, v in kr_dump.items():
            kr_set(k, v)
        kr_path.unlink(missing_ok=True)

    console.print(f"[green]Application state restored from[/] {backup_file}")
    input("Press Enter to continue...")


# ---------------- Menus ---------------- #

def accounts_menu():
    while True:
        console.clear()
        console.print("[bold cyan]Accounts Menu[/]")
        menu = Table(show_header=False, box=None, expand=False)
        menu.add_column("Option", style="bold green", justify="right", no_wrap=True)
        menu.add_column("Action", style="white")

        menu.add_row("1", "Show current account")
        menu.add_row("2", "Switch account")
        menu.add_row("3", "Create next account (when full)")
        menu.add_row("4", "Reset CloudChain (WIPE ALL DATA)")
        menu.add_row("5", "Back")

        console.print(menu)
        choice = Prompt.ask("Select option", default="5")
        if choice == "1": show_current_account(); input("Press Enter to continue...")
        elif choice == "2": switch_account(); input("Press Enter to continue...")
        elif choice == "3": create_next_account(); input("Press Enter to continue...")
        elif choice == "4": reset_cloudchain()
        elif choice == "5": break
        else: console.print("[red]Invalid choice[/]")

def cloud_menu():
    while True:
        console.clear()
        console.print("[bold cyan]Cloud Menu[/]")
        menu = Table(show_header=False, box=None, expand=False)
        menu.add_column("Option", style="bold green", justify="right", no_wrap=True)
        menu.add_column("Action", style="white")

        menu.add_row("1", "Upload to Drive")
        menu.add_row("2", "Download from Drive")
        menu.add_row("3", "Show files on Drive (ledger)")
        menu.add_row("4", "Delete a file from Drive")
        menu.add_row("5", "Sync local backup → Drive")
        menu.add_row("6", "Sync Drive → local backup")
        menu.add_row("7", "Back")

        console.print(menu)
        choice = Prompt.ask("Select option", default="7")
        if choice == "1": upload_file_for_account(); input("Press Enter to continue...")
        elif choice == "2": download_file_for_account(); input("Press Enter to continue...")
        elif choice == "3": list_cloud_contents(); input("Press Enter to continue...")
        elif choice == "4": delete_file_for_account(); input("Press Enter to continue...")
        elif choice == "5": sync_local_backup_to_cloud(); input("Press Enter to continue...")
        elif choice == "6": sync_cloud_to_local(); input("Press Enter to continue...")
        elif choice == "7": break
        else: console.print("[red]Invalid choice[/]")

def local_menu():
    while True:
        console.clear()
        console.print("[bold cyan]Local Menu[/]")
        menu = Table(show_header=False, box=None, expand=False)
        menu.add_column("Option", style="bold green", justify="right", no_wrap=True)
        menu.add_column("Action", style="white")

        menu.add_row("1", "Show local backup")
        menu.add_row("2", "Delete from local backup")
        menu.add_row("3", "Back")

        console.print(menu)
        choice = Prompt.ask("Select option", default="3")
        if choice == "1": show_local_backup(); input("Press Enter to continue...")
        elif choice == "2": delete_local_backup(); input("Press Enter to continue...")
        elif choice == "3": break
        else: console.print("[red]Invalid choice[/]")

def system_menu():
    while True:
        console.clear()
        console.print("[bold cyan]System Menu[/]")
        menu = Table(show_header=False, box=None, expand=False)
        menu.add_column("Option", style="bold green", justify="right", no_wrap=True)
        menu.add_column("Action", style="white")

        menu.add_row("1", "Export application state (.ccbak)")
        menu.add_row("2", "Restore application state (.ccbak)")
        menu.add_row("3", "Quit to main menu")

        console.print(menu)
        choice = Prompt.ask("Select option", default="3")
        if choice == "1": backup_app_state()
        elif choice == "2": restore_app_state()
        elif choice == "3": break
        else: console.print("[red]Invalid choice[/]")

def interactive():
    banner = r"""▄▖▜      ▌▄▖▌   ▘    ▐▘              ▜      ▌  ▘      
▌ ▐ ▛▌▌▌▛▌▌ ▛▌▀▌▌▛▌  ▜▘▛▌▛▘  ▛▌▛▌▛▌▛▌▐ █▌  ▛▌▛▘▌▌▌█▌  
▙▖▐▖▙▌▙▌▙▌▙▖▌▌█▌▌▌▌  ▐ ▙▌▌   ▙▌▙▌▙▌▙▌▐▖▙▖  ▙▌▌ ▌▚▘▙▖▗ 
                             ▄▌    ▄▌                 """

    console.print(Panel("[bold red]DISCLAIMER:[/] DO NOT VIOLATE Google’s Terms.", expand=False))
    time.sleep(1)

    while True:
        console.clear()
        console.print(f"[bold cyan]{banner}[/]")
        console.print("[bold white]CloudChain for Google Drive[/]")

        reg = load_registry()
        if reg.get("current_account"):
            acc = reg["current_account"]
            console.print(Panel(
                f"Active Google Account: [cyan]{acc}@{reg.get('domain','gmail.com')}[/]\n"
                f"Local backup folder: [green]{account_dir_local(acc)}[/]",
                title="Active Account",
                expand=False
            ))

        menu = Table(title="Main Menu", show_header=False, box=None, expand=False, show_lines=True)
        menu.add_column("Option", style="bold green", justify="right", no_wrap=True)
        menu.add_column("Action", style="white")

        menu.add_row("1", "Accounts")
        menu.add_row("2", "Cloud")
        menu.add_row("3", "Local")
        menu.add_row("4", "System")
        menu.add_row("5", "Quit")

        console.print(menu)

        choice = Prompt.ask("Select option", default="5")
        if choice == "1": accounts_menu()
        elif choice == "2": cloud_menu()
        elif choice == "3": local_menu()
        elif choice == "4": system_menu()
        elif choice == "5": break
        else:
            console.print("[red]Invalid choice[/]")

# ---------------- Main ---------------- #

if __name__ == "__main__":
    reg = load_registry()
    if not reg.get("accounts"):
        console.print("[bold cyan]First run detected.[/]")
        if Confirm.ask("Restore from application state backup?", default=False):
            restore_app_state()
            reg = load_registry()
            if not reg.get("accounts"):
                # still empty after restore
                sanity_and_init_if_needed()
        else:
            sanity_and_init_if_needed()
    interactive()

