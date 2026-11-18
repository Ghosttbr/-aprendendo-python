"""Detecta atividades prontas, atualiza a documentação e publica no GitHub.

O monitor só considera arquivos atividades/NN-titulo.py. Um arquivo precisa
ficar sem alterações por cinco minutos, ser Python válido e não conter sinais
comuns de dados pessoais ou segredos antes de ser commitado e enviado.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ACTIVITIES = ROOT / "atividades"
TASK_NAME = "AprendendoPythonAutoPublish"
STABLE_SECONDS = 300
POLL_SECONDS = 10
EXPECTED_REMOTE = "https://github.com/Ghosttbr/-aprendendo-python.git"
ACTIVITY_NAME = re.compile(
    r"^(?:atividade (?P<activity_number>\d+)|(?P<number>\d{2})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*))\.py$",
    re.I,
)

DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "AprendendoPythonWatcher"
LOG_FILE = DATA_DIR / "watcher.log"
STATE_FILE = DATA_DIR / "state.json"

PRIVACY_CHECKS = (
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    ("endereco IPv4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("endereco MAC", re.compile(r"\b(?:[0-9A-F]{2}[:-]){5}[0-9A-F]{2}\b", re.I)),
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")),
    ("telefone", re.compile(r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[- ]\d{4}\b")),
    ("chave/token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b")),
    ("chave privada", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("senha/chave literal", re.compile(r"\b(?:password|senha|api[_-]?key|token|secret)\s*=\s*['\"][^'\"]{4,}['\"]", re.I)),
)
INCOMPLETE = re.compile(r"\b(?:TODO|FIXME|PREENCHER|CODIGO PRECISA SER PREENCHIDO)\b", re.I)


def log(message: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n"
    with LOG_FILE.open("a", encoding="utf-8") as stream:
        stream.write(line)


def git(*args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        env=env,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "falha no Git")
    return result


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_state() -> dict[str, str]:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            log("Estado local ilegivel; reconstruindo a partir do commit atual.")
    state: dict[str, str] = {}
    tracked = git("ls-files", "--", "atividades", check=False)
    for relative in tracked.stdout.splitlines():
        result = git("show", f"HEAD:{relative}", check=False)
        if result.returncode == 0:
            state[Path(relative).name] = digest(result.stdout.encode("utf-8"))
    return state


def save_state(state: dict[str, str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(STATE_FILE)


def infer_concepts(tree: ast.AST) -> str:
    calls: set[str] = set()
    concepts: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else ""
            calls.add(name)
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            concepts.add("variáveis")
        if isinstance(node, ast.BinOp):
            concepts.add("operações matemáticas")
        if isinstance(node, ast.If):
            concepts.add("condicionais")
        if isinstance(node, ast.Compare):
            concepts.add("comparações")
        if isinstance(node, ast.BoolOp):
            concepts.add("operadores lógicos")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            concepts.add("operadores lógicos")
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            concepts.add("laços de repetição")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            concepts.add("funções")
        if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp, ast.DictComp)):
            concepts.add("coleções")
    if "input" in calls:
        concepts.add("entrada de dados (`input()`)")
    if "print" in calls:
        concepts.add("saída de dados (`print()`)")
    if calls.intersection({"int", "float", "str", "bool"}):
        concepts.add("conversão de tipos")
    order = (
        "entrada de dados (`input()`)",
        "saída de dados (`print()`)",
        "variáveis",
        "conversão de tipos",
        "operações matemáticas",
        "condicionais",
        "comparações",
        "operadores lógicos",
        "laços de repetição",
        "funções",
        "coleções",
    )
    return ", ".join(item for item in order if item in concepts) or "conceitos básicos"


def table_row(number: int, values: list[str]) -> str:
    cells = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return f"| {number:02d} | " + " | ".join(cells) + " |"


def update_table(path: Path, number: int, values: list[str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    row_pattern = re.compile(r"^\|\s*(\d{2})\s*\|")
    matching = next((i for i, line in enumerate(lines) if (m := row_pattern.match(line)) and int(m.group(1)) == number), None)
    if matching is not None:
        lines[matching] = table_row(number, values)
    else:
        row_indexes = [i for i, line in enumerate(lines) if row_pattern.match(line)]
        if not row_indexes:
            raise RuntimeError(f"Tabela numerada nao encontrada em {path.name}")
        lines.insert(row_indexes[-1] + 1, table_row(number, values))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def privacy_problem(source: str) -> str | None:
    for label, pattern in PRIVACY_CHECKS:
        if pattern.search(source):
            return label
    if INCOMPLETE.search(source):
        return "marcador de atividade incompleta"
    return None


def published_blob(name: str) -> str | None:
    result = git("show", f"HEAD:atividades/{name}", check=False)
    return digest(result.stdout.encode("utf-8")) if result.returncode == 0 else None


def push_local_commits() -> bool:
    remote = git("remote", "get-url", "origin", check=False)
    if remote.returncode or remote.stdout.strip().rstrip("/") not in {EXPECTED_REMOTE, EXPECTED_REMOTE.removesuffix(".git")}:
        log("Publicacao pausada: origin nao corresponde ao repositorio configurado.")
        return False
    local = git("rev-parse", "HEAD").stdout.strip()
    remote_head = git("ls-remote", "origin", "refs/heads/main", check=False)
    remote_sha = remote_head.stdout.split()[0] if remote_head.stdout.split() else ""
    if local == remote_sha:
        return True
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    result = git("push", "origin", "main", check=False, env=env)
    if result.returncode:
        log("Push pendente; verifique a autenticacao do Git Credential Manager. " + result.stderr.strip())
        return False
    log("Commit enviado ao GitHub: " + local[:12])
    return True


def process_activity(path: Path, state: dict[str, str], current_hash: str) -> bool:
    match = ACTIVITY_NAME.match(path.name)
    if not match:
        return False
    number = int(match.group("activity_number") or match.group("number"))
    slug = match.group("slug")
    try:
        source = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=path.name)
    except (OSError, UnicodeError, SyntaxError) as error:
        log(f"{path.name}: aguardando correcao de sintaxe ou codificacao ({error.__class__.__name__}).")
        return False
    problem = privacy_problem(source)
    if problem:
        log(f"{path.name}: publicacao bloqueada pela verificacao local ({problem}).")
        return False
    if git("diff", "--cached", "--quiet", check=False).returncode != 0:
        log("Publicacao pausada: ha alteracoes staged que nao pertencem ao monitor.")
        return False
    if git("status", "--porcelain", "--", "README.md", "docs/progresso.md").stdout.strip():
        log("Publicacao pausada: README.md ou docs/progresso.md tem alteracoes manuais.")
        return False

    title = f"Atividade {number:02d}" if slug is None else " ".join(word.capitalize() for word in slug.split("-"))
    concepts = infer_concepts(tree)
    update_table(ROOT / "README.md", number, [title, concepts])
    update_table(ROOT / "docs" / "progresso.md", number, [title, concepts, "Concluída"])
    staged = git("add", "--", "README.md", "docs/progresso.md", f"atividades/{path.name}", check=False)
    if staged.returncode:
        log(f"{path.name}: nao foi possivel preparar os arquivos.")
        return False
    commit_message = f"Atualiza atividade {number:02d}: {title}"
    committed = git("commit", "-m", commit_message, check=False)
    if committed.returncode:
        log(f"{path.name}: commit nao criado. " + committed.stderr.strip())
        return False
    if not push_local_commits():
        return False
    state[path.name] = current_hash
    save_state(state)
    log(f"Atividade {number:02d} atualizada e publicada.")
    return True


def watcher() -> None:
    if not ACTIVITIES.is_dir():
        raise RuntimeError("Pasta atividades nao encontrada.")
    state = load_state()
    save_state(state)
    observed: dict[str, tuple[str, float]] = {}
    log("Monitor iniciado. Novos arquivos estaveis serao atualizados e publicados.")
    while True:
        now = time.monotonic()
        if now - watcher.last_push_check >= 60:
            if push_local_commits():
                for existing in ACTIVITIES.iterdir():
                    if not existing.is_file() or not ACTIVITY_NAME.match(existing.name):
                        continue
                    try:
                        current = digest(existing.read_bytes())
                    except OSError:
                        continue
                    if published_blob(existing.name) == current and state.get(existing.name) != current:
                        state[existing.name] = current
                        observed.pop(existing.name, None)
                save_state(state)
            watcher.last_push_check = now
        if git("rev-parse", "--abbrev-ref", "HEAD", check=False).stdout.strip() != "main":
            log("Monitor aguardando a branch main.")
            time.sleep(POLL_SECONDS)
            continue
        for path in ACTIVITIES.iterdir():
            if not path.is_file() or not ACTIVITY_NAME.match(path.name):
                continue
            try:
                content = path.read_bytes()
                current_hash = digest(content)
            except OSError:
                continue
            if state.get(path.name) == current_hash:
                observed.pop(path.name, None)
                continue
            previous = observed.get(path.name)
            if previous is None or previous[0] != current_hash:
                observed[path.name] = (current_hash, time.monotonic())
                continue
            if time.monotonic() - previous[1] < STABLE_SECONDS:
                continue
            if process_activity(path, state, current_hash):
                observed.pop(path.name, None)
            elif published_blob(path.name) == current_hash:
                state[path.name] = current_hash
                save_state(state)
                observed.pop(path.name, None)
            else:
                observed[path.name] = (current_hash, time.monotonic())
        time.sleep(POLL_SECONDS)


def install_task() -> None:
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    if not pythonw.exists():
        raise RuntimeError(f"pythonw.exe nao encontrado ao lado de {sys.executable}")
    action = f'"{pythonw}" "{Path(__file__).resolve()}"'
    result = subprocess.run(
        ["schtasks", "/Create", "/SC", "ONLOGON", "/TN", TASK_NAME, "/TR", action, "/F"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if result.returncode == 0:
        subprocess.run(["schtasks", "/Run", "/TN", TASK_NAME], check=True, capture_output=True)
        print(f"Monitor instalado e iniciado: {TASK_NAME}")
        return

    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    startup = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup.mkdir(parents=True, exist_ok=True)
    launcher = startup / "AprendendoPythonWatcher.vbs"
    vbs_command = f'"""{pythonw}"" ""{Path(__file__).resolve()}"""'
    launcher.write_text(
        'Set shell = CreateObject("WScript.Shell")\n'
        f"shell.Run {vbs_command}, 0, False\n",
        encoding="utf-8",
    )
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(
        [str(pythonw), str(Path(__file__).resolve())],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    log("Inicializacao automatica configurada pela pasta Startup do usuario.")
    print(f"Monitor iniciado e adicionado a inicializacao: {launcher}")


def uninstall() -> None:
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    launcher = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "AprendendoPythonWatcher.vbs"
    if launcher.exists():
        launcher.unlink()
        print("Inicializacao automatica removida.")
    else:
        print("Atalho de inicializacao nao encontrado.")


if __name__ == "__main__":
    if "--install" in sys.argv:
        install_task()
    elif "--uninstall" in sys.argv:
        uninstall()
    else:
        watcher.last_push_check = 0.0
        try:
            watcher()
        except Exception as error:
            log(f"Monitor encerrado por erro: {error}")
            raise
