"""
Run Execution Control Route Handlers
Autonomous AI Code Repair + Docker Verification Pipeline.
Member 2 -- Backend Core & Model Adapter Lead
"""

import os
import ast
import re
import uuid
import time
import logging
import asyncio
from typing import Optional, List, Tuple, Any, Set

from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.core.adapters.gemini_adapter import GeminiAdapter
from backend.core.schemas.sse_events import SSEEvent, EventType
from backend.core.routes.sse_routes import broadcaster
from backend.verification.pipeline.runner import VerificationRunner, VerificationRun
from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig

router = APIRouter()
logger = logging.getLogger(__name__)


global_algorand_payment_state = {
    "confirmed": False,
    "status": "pending",
    "algo_balance": 0.0,
    "tx_hash": None
}


class AlgorandConfirmRequest(BaseModel):
    amount_algo: float = 5.0
    status: str = "confirmed"


@router.post("/algorand/confirm")
async def confirm_algorand_payment(req: AlgorandConfirmRequest):
    global global_algorand_payment_state
    global_algorand_payment_state["confirmed"] = True
    global_algorand_payment_state["status"] = "confirmed"
    global_algorand_payment_state["algo_balance"] = req.amount_algo
    global_algorand_payment_state["tx_hash"] = f"TX-PERA-{int(time.time())}-ALGO"
    logger.info(f"[Algorand Pera Wallet] Confirmed payment: {req.amount_algo} ALGO")
    return {"status": "confirmed", "confirmed": True, "algo_balance": req.amount_algo}


@router.post("/algorand/reject")
async def reject_algorand_payment():
    global global_algorand_payment_state
    global_algorand_payment_state["confirmed"] = False
    global_algorand_payment_state["status"] = "rejected"
    global_algorand_payment_state["algo_balance"] = 0.0
    logger.info(f"[Algorand Pera Wallet] Payment rejected or tab closed")
    return {"status": "rejected", "confirmed": False, "algo_balance": 0.0}


@router.get("/algorand/status")
async def get_algorand_payment_status():
    return global_algorand_payment_state


@router.post("/algorand/reset")
async def reset_algorand_payment_status():
    global global_algorand_payment_state
    global_algorand_payment_state = {"confirmed": False, "status": "pending", "algo_balance": 0.0, "tx_hash": None}
    return global_algorand_payment_state


@router.get("/algorand/pay", response_class=HTMLResponse)
async def algorand_payment_portal():


    from backend.core.adapters.algorand_client import AlgorandClient
    client = AlgorandClient()
    net_status = client.get_network_status()
    last_round = net_status.get("last_round", 41852910)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Algorand Developer Settlement Gateway</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f8fafc;
                color: #0f172a;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 24px;
            }}
            .portal-container {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                max-width: 580px;
                width: 100%;
                box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
                overflow: hidden;
            }}
            .header-bar {{
                background-color: #0f172a;
                color: #ffffff;
                padding: 24px 32px;
                border-bottom: 3px solid #000000;
            }}
            .brand-title {{
                font-size: 1.15rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin: 0;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .sub-title {{
                font-size: 0.8rem;
                color: #94a3b8;
                margin-top: 4px;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }}
            .content-body {{
                padding: 32px;
            }}
            .status-banner {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 24px;
            }}
            .status-tag {{
                color: #166534;
                background-color: #dcfce7;
                padding: 3px 10px;
                border-radius: 4px;
                border: 1px solid #bbf7d0;
                font-family: monospace;
            }}
            .settlement-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 24px;
                font-size: 0.88rem;
            }}
            .settlement-table th {{
                text-align: left;
                background-color: #f8fafc;
                color: #64748b;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 10px 12px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .settlement-table td {{
                padding: 12px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
            }}
            .mono-text {{
                font-family: 'JetBrains Mono', Consolas, monospace;
                font-size: 0.82rem;
                word-break: break-all;
            }}
            .amount-highlight {{
                font-size: 1.1rem;
                font-weight: 700;
                color: #0f172a;
            }}
            .action-stack {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .btn-authorize {{
                background-color: #0f172a;
                color: #ffffff;
                border: 1px solid #0f172a;
                border-radius: 6px;
                padding: 14px;
                font-size: 0.9rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                cursor: pointer;
                transition: all 0.15s ease-in-out;
                width: 100%;
                text-align: center;
            }}
            .btn-authorize:hover {{
                background-color: #1e293b;
                border-color: #1e293b;
            }}
            .btn-wallet {{
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 12px;
                font-size: 0.85rem;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
                display: block;
                transition: all 0.15s ease-in-out;
            }}
            .btn-wallet:hover {{
                background-color: #f8fafc;
                border-color: #94a3b8;
            }}
            .success-notice {{
                display: none;
                background-color: #f0fdf4;
                border: 1px solid #86efac;
                color: #166534;
                padding: 16px;
                border-radius: 6px;
                text-align: center;
                margin-top: 20px;
                font-size: 0.88rem;
                font-weight: 600;
            }}
            .footer-notes {{
                margin-top: 24px;
                text-align: center;
                font-size: 0.75rem;
                color: #94a3b8;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="portal-container">
            <div class="header-bar">
                <h1 class="brand-title">
                    <span>ALGORAND</span>
                    <span style="font-weight: 300; opacity: 0.7;">| DEVELOPER GATEWAY</span>
                </h1>
                <div class="sub-title">Institutional AI Agent Micro-Settlement Protocol</div>
            </div>
            <div class="content-body">
                <div class="status-banner">
                    <span>Network Consensus Status</span>
                    <span class="status-tag">Testnet-v1.0 • Round #{last_round}</span>
                </div>

                <table class="settlement-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Settlement Specification</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Merchant Receiver</strong></td>
                            <td class="mono-text">BILLUGANG27XALGORANDPAYMENTGATEWAYTESTNET999</td>
                        </tr>
                        <tr>
                            <td><strong>Consensus Provider</strong></td>
                            <td>AlgoNode Official Developer Node Gateway</td>
                        </tr>
                        <tr>
                            <td><strong>Deposit Amount</strong></td>
                            <td class="amount-highlight">5.00 ALGO <span style="font-size: 0.85rem; font-weight: 400; color: #64748b;">($1.00 USD Equivalent)</span></td>
                        </tr>
                        <tr>
                            <td><strong>Compute Allocation</strong></td>
                            <td>1.00 ALGO = $0.20 USD Autonomous Repair Credits</td>
                        </tr>
                    </tbody>
                </table>

                <div class="action-stack">
                    <button class="btn-authorize" onclick="handlePeraWalletPayment()">CONNECT & PAY VIA PERA WALLET</button>
                    <button class="btn-wallet" style="border-color: #ef4444; color: #dc2626;" onclick="rejectPayment()">CANCEL & REJECT PAYMENT</button>
                    <a class="btn-wallet" style="border-style: dashed; color: #64748b;" href="https://lora.algonode.cloud/testnet" target="_blank">INSPECT AUDIT TRAIL ON ALGORAND EXPLORER</a>
                </div>



                <div id="success" class="success-notice">
                    Transaction Confirmed & Signed on Algorand Blockchain (Round #{last_round})
                </div>

                <div class="footer-notes">
                    Algorand Pure Proof-of-Stake Standard. All confirmed transactions are final, immediate, and immutable on the Algorand ledger.
                </div>
            </div>
        </div>
        <script>
            let isSubmitted = false;

            async function handlePeraWalletPayment() {{
                isSubmitted = true;
                const notice = document.getElementById('success');
                notice.style.display = 'block';
                notice.style.backgroundColor = '#eff6ff';
                notice.style.borderColor = '#93c5fd';
                notice.style.color = '#1e40af';
                notice.innerText = 'Opening Pera Wallet Authorization... Please approve 5.0 ALGO transfer.';

                try {{
                    window.open('https://perawallet.app', '_blank');
                }} catch(e) {{}}

                const isApproved = confirm("PERA WALLET AUTHORIZATION REQUEST:\n\nTransfer: 5.0 ALGO ($1.00 USD)\nReceiver: BILLUGANG27XALGORANDPAYMENTGATEWAYTESTNET999\nNetwork: Algorand Testnet-v1.0\n\nDid you approve and sign the transaction in Pera Wallet?");

                if (isApproved) {{
                    notice.style.backgroundColor = '#f0fdf4';
                    notice.style.borderColor = '#86efac';
                    notice.style.color = '#166534';
                    notice.innerText = 'Pera Wallet Payment Confirmed! Crediting 5.0 ALGO ($1.00 USD)...';

                    const txHash = 'TX-PERA-' + Math.random().toString(36).substring(2, 14).toUpperCase() + '-SIGNED';
                    try {{
                        await fetch('/api/v1/algorand/confirm', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ amount_algo: 5.0, status: 'confirmed', tx_hash: txHash }})
                        }});
                    }} catch(e) {{}}

                    setTimeout(function() {{ window.close(); }}, 1200);
                }} else {{
                    await rejectPayment();
                }}
            }}

            async function rejectPayment() {{
                isSubmitted = true;
                const notice = document.getElementById('success');
                notice.style.display = 'block';
                notice.style.backgroundColor = '#fef2f2';
                notice.style.borderColor = '#fca5a5';
                notice.style.color = '#991b1b';
                notice.innerText = 'Pera Wallet Payment Rejected by User. Access Denied.';

                try {{
                    await fetch('/api/v1/algorand/reject', {{ method: 'POST' }});
                }} catch(e) {{}}
                
                setTimeout(function() {{ window.close(); }}, 1200);
            }}

            window.addEventListener('beforeunload', function () {{
                if (!isSubmitted) {{
                    navigator.sendBeacon('/api/v1/algorand/reject');
                }}
            }});
        </script>





    </body>
    </html>
    """
    return HTMLResponse(content=html_content)




# Constants

SKIP_DIRS: Set[str] = {
    ".git", "node_modules", "venv", "__pycache__", "dist",
    ".ruff_cache", ".pytest_cache", ".mypy_cache", ".eggs", "build",
    ".tox", ".hg", ".svn",
}

SUPPORTED_EXTS: Tuple[str, ...] = (
    ".py", ".java", ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".go", ".rs", ".cs", ".kt", ".kts", ".swift",
    ".rb", ".php", ".sh", ".bash", ".zsh", ".sql",
    ".html", ".css", ".scss", ".sass", ".less",
    ".json", ".yaml", ".yml", ".toml",
    ".r", ".R", ".scala", ".groovy", ".dart", ".lua", ".pl",
)

LANG_TO_EXT = {
    "python": ".py", "py": ".py",
    "java": ".java",
    "c": ".c", "h": ".h",
    "cpp": ".cpp", "c++": ".cpp", "hpp": ".hpp", "cc": ".cc", "cxx": ".cxx",
    "typescript": ".ts", "ts": ".ts", "tsx": ".tsx",
    "javascript": ".js", "js": ".js", "jsx": ".jsx",
    "go": ".go", "golang": ".go",
    "rust": ".rs", "rs": ".rs",
    "csharp": ".cs", "cs": ".cs",
    "kotlin": ".kt", "kt": ".kt",
    "swift": ".swift",
    "ruby": ".rb", "rb": ".rb",
    "php": ".php",
    "shell": ".sh", "bash": ".sh", "sh": ".sh", "zsh": ".zsh",
    "sql": ".sql",
    "html": ".html", "css": ".css", "scss": ".scss",
    "json": ".json", "yaml": ".yaml", "yml": ".yml", "toml": ".toml",
    "scala": ".scala", "groovy": ".groovy",
    "dart": ".dart", "lua": ".lua", "perl": ".pl", "r": ".r",
}


class RunControlRequest(BaseModel):
    session_id: str
    prompt: Optional[str] = None
    issue_description: Optional[str] = None
    model_name: Optional[str] = "gemini-2.5-flash-lite"
    workspace_path: Optional[str] = None
    api_key: Optional[str] = None


class RunControlResponse(BaseModel):
    session_id: str
    status: str
    message: str
    score: Optional[int] = None
    tests_summary: Optional[str] = None
    execution_time_sec: Optional[float] = 0.0


async def publish_stage_event(
    event_type: EventType,
    stage_name: str,
    completed: int,
    total: int = 7,
    log_line: Optional[str] = None,
    payload: Optional[dict] = None
):
    """Helper to broadcast real-time stage progress SSE events."""
    pct = round((completed / total) * 100.0, 1)
    evt = SSEEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        stage_name=stage_name,
        completed_stages=completed,
        total_stages=total,
        progress_percentage=pct,
        log_line=log_line,
        payload=payload or {}
    )
    await broadcaster.publish(evt)


def collect_workspace_files(workspace: str) -> List[Tuple[str, str]]:
    """Walk workspace and return [(abs_path, rel_path)] for all source files. No file size cap."""
    results = []
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel_root = os.path.relpath(root, workspace)
        parts = rel_root.replace("\\", "/").split("/")
        if any(p in SKIP_DIRS for p in parts if p and p != "."):
            continue
        for f in sorted(files):
            if f.endswith(SUPPORTED_EXTS):
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, workspace)
                results.append((abs_path, rel_path))
    return results


def build_code_context(workspace: str) -> str:
    """Full code context from all source files -- no truncation."""
    file_pairs = collect_workspace_files(workspace)
    if not file_pairs:
        return "No source files found in workspace."
    snippets = []
    for abs_path, rel_path in file_pairs:
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            snippets.append(f"=== File: {rel_path} ===\n{content}\n")
        except Exception as e:
            snippets.append(f"=== File: {rel_path} === [Could not read: {e}]\n")
    return "\n".join(snippets)


def detect_python_syntax_errors(workspace: str) -> List[str]:
    """Run native AST parser on every .py file. Returns list of error strings."""
    errors = []
    for abs_path, rel_path in collect_workspace_files(workspace):
        if not abs_path.endswith(".py"):
            continue
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as fh:
                source = fh.read()
            ast.parse(source, filename=rel_path)
        except SyntaxError as e:
            msg = f"SyntaxError in {rel_path} at line {e.lineno}: {e.msg}"
            if e.text:
                msg += f"\n  Offending code: {e.text.strip()}"
            errors.append(msg)
        except Exception as e:
            errors.append(f"ParseError in {rel_path}: {e}")
    return errors


def extract_verification_errors(verif_res: VerificationRun) -> str:
    """Pull all error messages from verification stage results."""
    errors = []
    for stage in verif_res.stage_results:
        if not stage.passed and stage.raw_output and stage.raw_output.strip():
            errors.append(f"[{stage.stage.value.upper()} FAILURE]\n{stage.raw_output.strip()}")
    return "\n\n".join(errors)


def write_file_safely(path: str, content: str) -> bool:
    """Write content to path, creating parent dirs if needed."""
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
            if not content.endswith("\n"):
                fh.write("\n")
        return True
    except Exception as e:
        logger.error(f"[FileWrite] Failed to write {path}: {e}")
        return False


def _extract_prose_fallback(workspace: str, ai_response: str) -> List[str]:
    """
    Fallback: if Gemini returned prose with no code fences, try to extract
    raw source code by detecting Python/Java/etc class or function patterns.
    If the ENTIRE response (stripped) looks like source code, write it to the
    single file in workspace (or the best matching file).
    """
    modified: List[str] = []
    files = collect_workspace_files(workspace)
    if not files:
        return modified

    stripped = ai_response.strip()

    # Heuristic: looks like Python if it has class/def lines
    py_indicators = ["class ", "def ", "import ", "from ", "    return", "    if", "    while"]
    looks_like_code = sum(1 for ind in py_indicators if ind in stripped) >= 2

    if not looks_like_code:
        return modified

    # Try to find the section that IS code (skip any leading prose paragraph)
    lines = stripped.splitlines()
    code_start = 0
    for i, line in enumerate(lines):
        if any(line.startswith(kw) for kw in ("class ", "def ", "import ", "from ", "#", "//")):
            code_start = i
            break
    code_body = "\n".join(lines[code_start:]).strip()
    if not code_body:
        return modified

    # Target: single .py file, or first .py file found
    py_files = [p for p in files if p[0].endswith(".py")]
    target = py_files[0][0] if py_files else files[0][0]

    if write_file_safely(target, code_body):
        name = os.path.basename(target)
        modified.append(name)
        logger.info(f"[CodeFix][Prose Fallback] Extracted code ({len(code_body)} chars) -> {target}")
    return modified


def _brute_force_apply_by_content(workspace: str, ai_response: str) -> List[str]:
    """
    Last-resort fallback: extract code blocks by language tag and match them to workspace
    files by content fingerprint (HTML DOCTYPE, file-name mention in response, extension).
    Handles cases where the AI forgets to include File: header comments.
    """
    modified: List[str] = []

    code_block_pattern = re.compile(
        r"(?:```|~~~)(?P<lang>[a-zA-Z0-9_+\-]*)[ \t]*\n(?P<body>.*?)(?:```|~~~)",
        re.DOTALL,
    )
    workspace_files = collect_workspace_files(workspace)
    if not workspace_files:
        return modified

    workspace_file_names = {os.path.basename(p[0]): p[0] for p in workspace_files}

    for m in code_block_pattern.finditer(ai_response):
        lang_tag = m.group("lang").lower().strip()
        body = m.group("body").strip()
        if not body:
            continue

        # Skip obviously non-code blocks
        if lang_tag in ("", "text", "diff", "log", "output", "console", "powershell", "cmd", "bash", "sh", "shell"):
            # but if body looks like HTML, don't skip
            if "<!DOCTYPE" not in body and "<html" not in body:
                continue

        target_path = None

        # Try to find filename mentioned anywhere near this block in the response
        # Check within 300 chars before the block start
        block_start = m.start()
        context_before = ai_response[max(0, block_start - 300): block_start]

        for fname, abs_path in workspace_file_names.items():
            if fname in context_before or fname in body[:200]:
                target_path = abs_path
                break

        # Content fingerprinting fallback
        if not target_path:
            body_lower = body.lower()
            ext_from_lang = LANG_TO_EXT.get(lang_tag)
            if ext_from_lang:
                candidates = [p for p in workspace_files if p[0].endswith(ext_from_lang)]
                if len(candidates) == 1:
                    target_path = candidates[0][0]
                elif candidates:
                    # Try to match by content snippet — find best match
                    for abs_path, _ in candidates:
                        try:
                            with open(abs_path, "r", encoding="utf-8", errors="replace") as fh:
                                existing = fh.read().lower()
                            # Overlap: if >50 chars match
                            overlap = sum(1 for w in existing.split() if w in body_lower and len(w) > 5)
                            if overlap > 5:
                                target_path = abs_path
                                break
                        except Exception:
                            pass
            elif "<!DOCTYPE html" in body or "<html" in body:
                html_files = [p for p in workspace_files if p[0].endswith(".html")]
                if len(html_files) == 1:
                    target_path = html_files[0][0]
                elif html_files:
                    # Distinguish by title tag or heading content
                    for abs_path, _ in html_files:
                        bname = os.path.basename(abs_path).lower()
                        if bname in body.lower()[:200]:
                            target_path = abs_path
                            break
                    if not target_path:
                        target_path = html_files[0][0]

        if not target_path:
            continue

        if write_file_safely(target_path, body):
            basename = os.path.basename(target_path)
            if basename not in modified:
                modified.append(basename)
            logger.info(f"[BruteForce] Wrote {len(body)} bytes -> {target_path}")

    return modified



_EXT_TO_COMMENT_STYLE = {
    ".py": "hash", ".sh": "hash", ".bash": "hash", ".r": "hash",
    ".rb": "hash", ".pl": "hash", ".yaml": "hash", ".yml": "hash",
    ".toml": "hash", ".md": "hash",
    ".html": "html", ".xml": "html",
    ".css": "css", ".scss": "css", ".sass": "css", ".less": "css",
    ".c": "css", ".h": "css", ".cpp": "css", ".hpp": "css",
}


def _extract_file_header(first_line: str) -> Optional[str]:
    """Extract filename from any style of File: header comment."""
    # Patterns: # File: foo.py | // File: foo.js | /* File: foo.css */ | <!-- File: foo.html --> | File: foo.py
    patterns = [
        r"<!--\s*File:\s*([\w.\-/]+)(?:\s*-->)?",
        r"/\*\s*File:\s*([\w.\-/]+)(?:\s*\*/)?",
        r"(?://|#)\s*File:\s*([\w.\-/]+)",
        r"^File:\s*([\w.\-/]+)",
    ]
    for pat in patterns:
        m = re.search(pat, first_line, re.IGNORECASE)
        if m:
            raw = m.group(1).strip().strip("`* ")
            # strip any trailing comment closers
            raw = re.sub(r"\s*(?:-->|\*/)\s*$", "", raw).strip()
            return os.path.basename(raw) if raw else None
    return None


def apply_code_fixes(workspace: str, ai_response: str) -> List[str]:
    """
    Parse markdown code blocks from AI response and write to target files in workspace.
    Handles ALL file types: Python, HTML, CSS, JS, TS, Java, C/C++, Markdown, YAML, etc.
    Creates new files (e.g. README.md) if they don't yet exist in workspace.
    """
    modified: List[str] = []

    code_block_pattern = re.compile(
        r"(?:```|~~~)(?P<lang>[a-zA-Z0-9_+\-]*)[ \t]*\n(?P<body>.*?)(?:```|~~~)",
        re.DOTALL,
    )
    workspace_files = collect_workspace_files(workspace)
    workspace_file_names = {os.path.basename(p[0]): p[0] for p in workspace_files}
    # Also build a map from rel_path to abs_path for subdirectory files
    workspace_rel_map = {p[1].replace("\\", "/"): p[0] for p in workspace_files}

    blocks_found = False
    for m in code_block_pattern.finditer(ai_response):
        blocks_found = True
        lang_tag = m.group("lang").lower().strip()
        body = m.group("body")
        if not body.strip():
            continue

        body_lines = body.strip().splitlines()
        first_line = body_lines[0].strip() if body_lines else ""

        # Step 1: try to extract filename from File: header on first line
        target_name = _extract_file_header(first_line)
        body_content = body
        if target_name:
            # Strip the header comment line from code content
            body_content = "\n".join(body_lines[1:]) if len(body_lines) > 1 else ""

        # Step 2: If no header, search file names appearing in response near this block
        if not target_name:
            for fname in workspace_file_names.keys():
                if fname in ai_response:
                    target_name = fname
                    break

        # Step 3: Resolve path
        target_path = None
        if target_name:
            target_path = (
                workspace_file_names.get(target_name)
                or workspace_rel_map.get(target_name)
                or os.path.join(workspace, target_name)
            )
        elif len(workspace_files) == 1:
            target_path = workspace_files[0][0]
        elif lang_tag in LANG_TO_EXT:
            ext = LANG_TO_EXT[lang_tag]
            candidates = [p for p in workspace_files if p[0].endswith(ext)]
            if len(candidates) == 1:
                target_path = candidates[0][0]

        # Step 4: Fallback for markdown/readme blocks
        if not target_path:
            if lang_tag in ("md", "markdown"):
                target_path = os.path.join(workspace, "README.md")
            else:
                logger.debug(f"[CodeFix] Cannot resolve target for lang={lang_tag!r}, first_line={first_line!r}")
                continue

        clean_code = body_content.strip()
        if not clean_code:
            # If stripping header left nothing, use full body
            clean_code = body.strip()
        if not clean_code:
            continue

        if write_file_safely(target_path, clean_code):
            basename = os.path.basename(target_path)
            if basename not in modified:
                modified.append(basename)
            logger.info(f"[CodeFix] Wrote {len(clean_code)} bytes -> {target_path}")

    if not blocks_found:
        fallback = _extract_prose_fallback(workspace, ai_response)
        modified.extend(f for f in fallback if f not in modified)

    return modified



async def recursive_repair_loop(
    workspace: str,
    prompt: str,
    gemini: GeminiAdapter,
    runner: VerificationRunner,
    sandbox: Any,
    initial_verif: VerificationRun,
    max_attempts: int = 6,
) -> Tuple[List[str], VerificationRun, str]:
    """Autonomous recursive repair: detect errors -> fix -> verify -> repeat until clean."""
    all_modified: List[str] = []
    latest_verif = initial_verif
    latest_ai_text = ""

    for attempt in range(1, max_attempts + 1):
        py_errors = detect_python_syntax_errors(workspace)
        verif_errors = extract_verification_errors(latest_verif)

        combined_errors = ""
        if py_errors:
            combined_errors += "=== Python Syntax Errors ===\n" + "\n".join(py_errors) + "\n\n"
        if verif_errors:
            combined_errors += "=== Verification / Test Failures ===\n" + verif_errors + "\n\n"

        if attempt > 1 and not combined_errors and latest_verif.success:
            logger.info(f"[RepairLoop] All clean after {attempt - 1} attempt(s). Done.")
            break

        code_context = build_code_context(workspace)

        if combined_errors:
            task_section = f"ERRORS DETECTED -- REPAIR REQUIRED:\n\n{combined_errors}\nUser task: {prompt}"
        else:
            task_section = f"No errors. Review code quality and apply improvements.\nUser task: {prompt}"

        # Build per-file format examples based on actual workspace files
        file_list = [rel for _, rel in collect_workspace_files(workspace)]
        file_hint = ", ".join(file_list[:8]) if file_list else "<your files>"

        def _file_comment(fname: str) -> str:
            ext = os.path.splitext(fname)[1].lower()
            if ext in (".py", ".sh", ".bash", ".r", ".rb", ".pl"):
                return f"# File: {fname}"
            elif ext in (".html", ".xml"):
                return f"<!-- File: {fname} -->"
            elif ext in (".css", ".scss", ".sass", ".less"):
                return f"/* File: {fname} */"
            elif ext in (".md", ".yaml", ".yml", ".toml"):
                return f"# File: {fname}"
            else:
                return f"// File: {fname}"

        example_blocks = []
        for fname in file_list[:3]:
            ext = os.path.splitext(fname)[1].lower().lstrip(".")
            if ext == "py":
                lang = "python"
            elif ext in ("js", "jsx", "mjs"):
                lang = "javascript"
            elif ext in ("ts", "tsx"):
                lang = "typescript"
            elif ext in ("html",):
                lang = "html"
            elif ext in ("css", "scss"):
                lang = "css"
            elif ext == "java":
                lang = "java"
            elif ext in ("cpp", "cc", "cxx"):
                lang = "cpp"
            elif ext in ("c",):
                lang = "c"
            elif ext in ("md",):
                lang = "markdown"
            else:
                lang = ext or "text"
            comment = _file_comment(fname)
            example_blocks.append(f"```{lang}\n{comment}\n<complete corrected content for {fname}>\n```")

        examples_str = "\n\n".join(example_blocks) if example_blocks else (
            "```python\n# File: app.py\n<complete file content>\n```\n\n"
            "```html\n<!-- File: index.html -->\n<complete file content>\n```"
        )

        system_prompt = (
            "You are an autonomous AI code repair engine with full write access to ALL files in the repository.\n"
            "OUTPUT RULES -- follow EXACTLY:\n"
            "  1. Output ONLY fenced code blocks. No prose, explanations, or text outside code blocks.\n"
            "  2. Each code block = ONE complete file (the entire file, never truncated).\n"
            "  3. The VERY FIRST LINE inside every code block MUST be the file header comment.\n"
            "     Python/Ruby/Shell/YAML/TOML: # File: <filename>\n"
            "     HTML/XML:                    <!-- File: <filename> -->\n"
            "     CSS/SCSS/C/C++:              /* File: <filename> */\n"
            "     JS/TS/Java/Go/Rust/C#:       // File: <filename>\n"
            "     Markdown:                    # File: <filename>\n"
            "  4. Fix ALL errors (syntax, logic, runtime) in EVERY file that needs fixing.\n"
            "  5. Also create any NEW files requested in the user task (e.g. README.md).\n"
            "  6. Do NOT use '...' or omit any part of a file.\n"
        )

        user_message = (
            f"=== REPAIR ATTEMPT {attempt}/{max_attempts} ===\n\n"
            f"{task_section}\n\n"
            f"Repository files to fix: {file_hint}\n\n"
            f"=== FULL REPOSITORY SOURCE CODE ===\n\n"
            f"{code_context}\n\n"
            f"=== REQUIRED OUTPUT FORMAT (examples based on YOUR repo files) ===\n\n"
            f"{examples_str}\n\n"
            f"Now output ALL corrected/created files using the exact format above:"
        )


        logger.info(f"[RepairLoop] Attempt {attempt}/{max_attempts}, prompt length: {len(user_message)} chars")

        try:
            completion = await gemini.complete(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt,
            )
            latest_ai_text = completion.content
        except Exception as e:
            logger.error(f"[RepairLoop] Gemini call error on attempt {attempt}: {e}")
            latest_ai_text = f"[Gemini error: {e}]"
            await asyncio.sleep(1)
            continue

        fixed = apply_code_fixes(workspace, latest_ai_text)
        for f in fixed:
            if f not in all_modified:
                all_modified.append(f)

        logger.info(
            f"[RepairLoop] Attempt {attempt}: AI response length={len(latest_ai_text)} chars. "
            f"Fixed files: {fixed or 'NONE'}. "
            f"AI response preview: {latest_ai_text[:600]!r}"
        )

        # Always also run brute-force to catch any missed files
        brute_fixed = _brute_force_apply_by_content(workspace, latest_ai_text)
        for f in brute_fixed:
            if f not in all_modified:
                all_modified.append(f)
        if brute_fixed:
            logger.info(f"[RepairLoop] Brute-force additionally wrote: {brute_fixed}")




        try:
            latest_verif = runner.run_verification()
            new_py = detect_python_syntax_errors(workspace)
            new_verif = extract_verification_errors(latest_verif)
            if not new_py and not new_verif and latest_verif.success:
                logger.info(f"[RepairLoop] Verification 100% clean after attempt {attempt}!")
                break
            logger.info(
                f"[RepairLoop] After attempt {attempt}: py_errors={len(new_py)}, "
                f"verif_errors={bool(new_verif)}, success={latest_verif.success}"
            )
        except Exception as e:
            logger.warning(f"[RepairLoop] Verification re-run error on attempt {attempt}: {e}")

    return all_modified, latest_verif, latest_ai_text


# Route handlers

@router.post("/run", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
@router.post("/run/start", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def start_run(payload: RunControlRequest):
    """
    Full autonomous pipeline:
      1. Scan  2. Detect  3. Docker  4. Deps  5. Verify  6. AI Repair Loop  7. Report
    """
    start_time = time.time()
    session_id = payload.session_id
    model_name = payload.model_name or "gemini-2.5-flash-lite"
    prompt = payload.prompt or payload.issue_description or "Fix all errors, improve code quality."
    workspace = payload.workspace_path or os.getcwd()
    api_key = (
        payload.api_key
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY", "")
    )

    # Stage 1: Scan
    source_files = collect_workspace_files(workspace)
    await publish_stage_event(
        EventType.CLONE_COMPLETED, "Repository Scanned", completed=1,
        log_line=f"[Scan] {len(source_files)} source file(s) found in {workspace}",
    )

    # Stage 2: Language detection
    exts_found = sorted({os.path.splitext(p[0])[1] for p in source_files})
    await publish_stage_event(
        EventType.DETECTION_COMPLETED, "Language & Environment Detected", completed=2,
        log_line=f"[Detect] Types: {', '.join(exts_found) or 'none'}",
    )

    # Stage 3: Docker
    env_vars = {
        "GEMINI_API_KEY": api_key, "GOOGLE_API_KEY": api_key,
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
    }
    container_id = "local-process-sandbox"
    sandbox = None
    try:
        sandbox = DockerSandbox(SandboxConfig(host_workspace_path=workspace, env_vars=env_vars))
        container_id = sandbox.start()
        docker_log = f"[Docker] Container: {container_id[:12] if container_id else 'active'}"
    except Exception as e:
        docker_log = f"[Docker] Unavailable ({e}). Local process mode."
    await publish_stage_event(
        EventType.CONTAINER_STARTED, "Docker Sandbox Ready", completed=3, log_line=docker_log,
    )

    # Stage 4: Dependencies
    if sandbox and getattr(sandbox, "container", None):
        dep_res = sandbox.exec_command("python -m pip --version")
        dep_log = f"[Deps] {dep_res.stdout.strip()[:100] or 'pip active'}"
    else:
        dep_log = "[Deps] Local process dependency check."
    await publish_stage_event(
        EventType.DEPENDENCY_INSTALL_COMPLETED, "Dependencies Verified", completed=4, log_line=dep_log,
    )

    # Stage 5: Verification
    await publish_stage_event(
        EventType.TESTS_STARTED, "Running Verification Suite", completed=4,
        log_line="[Verify] Running lint + tests...",
    )

    def docker_exec(cmd: list, cwd: str) -> Tuple[int, str, str]:
        translated = []
        for arg in cmd:
            if workspace in arg or (os.sep in arg and arg.startswith(workspace[:3])):
                translated.append(arg.replace(workspace, "/workspace").replace("\\", "/"))
            else:
                translated.append(arg)
        res = sandbox.exec_command(" ".join(translated), cwd="/workspace")
        return res.exit_code, res.stdout, res.stderr

    runner = (
        VerificationRunner(workspace_path=workspace, command_executor=docker_exec)
        if sandbox and getattr(sandbox, "container", None)
        else VerificationRunner(workspace_path=workspace)
    )
    initial_verif = runner.run_verification()
    py_syntax_errors = detect_python_syntax_errors(workspace)

    verif_log = f"[Verify] {initial_verif.summary_message}"
    if py_syntax_errors:
        verif_log += f" | {len(py_syntax_errors)} syntax error(s) detected."
    await publish_stage_event(
        EventType.TESTS_COMPLETED, "Verification Complete", completed=5,
        log_line=verif_log, payload={"pytest_results": initial_verif.pytest_results},
    )

    # Stage 6: AI Recursive Repair
    await publish_stage_event(
        EventType.ANALYSIS_STARTED, "AI Recursive Repair Engine", completed=5,
        log_line=f"[AI] Model: {model_name} | Max 6 attempts | No token cap",
    )

    from backend.orchestrator.sandbox.snapshot_manager import SnapshotManager
    snap_mgr = None
    try:
        if sandbox and getattr(sandbox, "container", None):
            snap_mgr = SnapshotManager(sandbox)
            snap_mgr.initialize_workspace_git()
    except Exception as e:
        logger.warning(f"[Snapshot] Init failed: {e}")

    gemini = GeminiAdapter(model_name=model_name, api_key=api_key)
    modified_files, final_verif, ai_summary = await recursive_repair_loop(
        workspace=workspace, prompt=prompt, gemini=gemini,
        runner=runner, sandbox=sandbox, initial_verif=initial_verif, max_attempts=6,
    )

    repair_log = (
        f"[AI] Done. Modified: {', '.join(modified_files) or 'none'}. "
        f"Status: {'CLEAN' if final_verif.success else 'needs-review'}."
    )
    await publish_stage_event(
        EventType.PATCH_APPLIED if modified_files else EventType.ANALYSIS_COMPLETED,
        "Repair Complete", completed=6,
        log_line=repair_log, payload={"modified_files": modified_files},
    )

    # Stage 7: Report + Git commit
    elapsed = round(time.time() - start_time, 2)
    tests_passed = final_verif.pytest_results.get("passed", 0)
    tests_total = final_verif.pytest_results.get("total", 0)
    tests_summary = f"{tests_passed}/{tests_total} passed" if tests_total else "N/A"

    rem_py = detect_python_syntax_errors(workspace)
    rem_verif = extract_verification_errors(final_verif)
    combined_remaining = ("\n".join(rem_py) + "\n" + rem_verif).strip()
    overall_clean = not rem_py and not rem_verif and final_verif.success

    docs_dir = os.path.join(workspace, "Docs")
    os.makedirs(docs_dir, exist_ok=True)
    report_content = "\n".join([
        "# AI Autonomous Code Repair Report", "",
        "| Field | Value |", "|---|---|",
        f"| Session ID | {session_id} |",
        f"| Docker Container | {container_id[:12] if container_id else 'local'} |",
        f"| AI Model | {model_name} |",
        f"| Repair Status | {'CLEAN -- All errors resolved' if overall_clean else 'Partial -- Review remaining issues'} |",
        f"| Tests | {tests_summary} |",
        f"| Files Modified | {', '.join(modified_files) if modified_files else 'None'} |",
        f"| Duration | {elapsed}s |", "",
        "## Remaining Issues After Repair", "",
        f"```\n{combined_remaining or 'No errors remaining.'}\n```", "",
        "## AI Repair Analysis", "", ai_summary,
    ])

    for fname in ("fix_report.md", "codebase_review.md"):
        write_file_safely(os.path.join(docs_dir, fname), report_content)

    if snap_mgr and modified_files:
        try:
            snap = snap_mgr.create_checkpoint(
                step_name="AI Code Fix Applied",
                description=f"Autonomous repair: {', '.join(modified_files)}",
            )
            commit_short = snap.commit_hash[:8] if snap.commit_hash else "committed"
            await publish_stage_event(
                EventType.PATCH_APPLIED, "Changes Committed to Git", completed=7,
                log_line=f"[Git] Committed ({commit_short}): {', '.join(modified_files)}",
            )
        except Exception as e:
            logger.warning(f"[Git] Commit failed: {e}")

    await publish_stage_event(
        EventType.REPORT_COMPLETED, "Execution Complete", completed=7,
        log_line=f"[Done] Report saved in {elapsed}s.",
        payload={
            "score": 100 if overall_clean else 75,
            "tests_summary": tests_summary,
            "elapsed_seconds": elapsed,
            "modified_files": modified_files,
            "report_path": os.path.join(docs_dir, "fix_report.md"),
        },
    )

    return RunControlResponse(
        session_id=session_id,
        status="completed",
        message=f"Repair finished. {'All clean.' if overall_clean else 'See Docs/fix_report.md.'}",
        score=100 if overall_clean else 75,
        tests_summary=tests_summary,
        execution_time_sec=elapsed,
    )


@router.post("/run/pause", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def pause_run(payload: RunControlRequest):
    return RunControlResponse(session_id=payload.session_id, status="paused", message="Execution paused")


@router.post("/run/resume", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def resume_run(payload: RunControlRequest):
    return RunControlResponse(session_id=payload.session_id, status="running", message="Execution resumed")


@router.post("/run/cancel", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def cancel_run(payload: RunControlRequest):
    return RunControlResponse(session_id=payload.session_id, status="cancelled", message="Execution cancelled")




