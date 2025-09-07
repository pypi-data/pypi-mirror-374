"""
InstallerPack v0.1.0

InstallerPack is a Python module designed to simplify adding 'Installer' functionality to Python applications.
It provides functions that can be linked to button clicks, enabling cloud-based version updates and seamless
rebuilding with `pyinstaller`.

Uses OctaStore for version storage. Configure OctaStore using `setocta(...)`.
"""

from __future__ import annotations

import os
import re
import sys
import shutil
import json
import tempfile
import subprocess
import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, Union, Callable, Literal
from .__config__ import VersionStyle, version_style as DEFAULT_VERSION_STYLE

try:
    from altcolor import init as _alt_init, colored_text
    _alt_init()
except Exception:
    def colored_text(color: str, text: str) -> str:
        return text

CAN_USE: bool = False

# OctaStore config object set by the user via setocta(...)
@dataclass
class OctaConfig:
    # Cluster-aware lists (match octastore CLI)
    tokens: List[str] = field(default_factory=list)
    owners: List[str] = field(default_factory=list)
    repos: List[str] = field(default_factory=list)
    branch: str = "main"
    app_name: str = ""               # e.g. "APP_NAME" where versions are under APP_NAME/<version>/
    path_prefix: Optional[str] = None # optional path prefix inside repo before the app_name
    encryption_key: Optional[bytes] = None  # if using OctaStore encryption
    use_cli_fallback: bool = True    # use the `octastore` CLI if python api fails

    def validate(self):
        if not self.app_name:
            raise ValueError("OctaConfig.app_name must be set (e.g. 'MyApp').")
        if not (self.tokens and self.owners and self.repos):
            raise ValueError("OctaConfig.tokens, owners and repos must be provided (at least one each).")


# internal module-level OctaStore config (set via setocta)
_OCTACONF: Optional[OctaConfig] = None

# Attempt to import octastore Python API (best-effort)
_OCTAPI = None
try:
    import octastore as _octastore
    _octastore.init()
    _OCTAPI = _octastore
except Exception:
    _OCTAPI = None  # fallback to CLI if available


def init(SHOW_CREDITS: bool = True) -> None:
    """Initialize InstallerPack module (optional credit message)."""
    global CAN_USE
    if SHOW_CREDITS:
        print(colored_text("BLUE", "This module was developed by Uniplex (Uniplex LLC / Uniplex_LLC)."))
    CAN_USE = True


def setocta(conf: OctaConfig) -> None:
    """
    Set OctaStore configuration for InstallerPack.

    Example:
        setocta(OctaConfig(
            tokens=["ghp_xxx"],
            owners=["user"],
            repos=["repo"],
            branch="main",
            app_name="MyApp",
            path_prefix="apps",  # optional
        ))
    """
    if CAN_USE:
        conf.validate()
        global _OCTACONF
        _OCTACONF = conf
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")


# -----------------------
# Version parsing / compare
# -----------------------
def _normalize_int(s: str) -> int:
    if CAN_USE:
        try:
            return int(s)
        except Exception:
            return 0
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")

def parse_semver(v: str) -> Tuple[int, int, int, Optional[str]]:
    """
    Parse semver-ish strings like "1.2.3", "1.2.3-alpha.1".
    Returns (major, minor, patch, pre_release_or_none)
    """
    if CAN_USE:
        # remove leading 'v'
        v = v.strip()
        if v.startswith("v"):
            v = v[1:]
        m = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-([\w\.\-]+))?", v)
        if not m:
            return (0, 0, 0, None)
        major = _normalize_int(m.group(1))
        minor = _normalize_int(m.group(2) or "0")
        patch = _normalize_int(m.group(3) or "0")
        pre = m.group(4)
        return (major, minor, patch, pre)
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")

def parse_calver(v: str) -> Tuple[int, int, int]:
    """
    Parse calver like YYYY.MM.DD or YYYY.MM
    """
    if CAN_USE:
        parts = re.split(r"[._\-\/]", v)
        parts = [p for p in parts if p.isdigit()]
        year = _normalize_int(parts[0]) if len(parts) > 0 else 0
        month = _normalize_int(parts[1]) if len(parts) > 1 else 0
        day = _normalize_int(parts[2]) if len(parts) > 2 else 0
        return (year, month, day)
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")

def parse_seq(v: str) -> int:
    """Parse sequence number from v (digits only)."""
    if CAN_USE:
        m = re.search(r"(\d+)", v)
        if m:
            return int(m.group(1))
        return 0
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")

def version_key(v: str, style: VersionStyle) -> Any:
    """Return a sortable key for version 'v' according to 'style'."""
    if CAN_USE:
        style = VersionStyle(style)
        if style == VersionStyle.SEMVER or style == VersionStyle.PREVER or style == VersionStyle.BUILDVER or style == VersionStyle.HYBRIDVER:
            major, minor, patch, pre = parse_semver(v)
            # For pre-release types (PREVER), consider pre-release < no pre-release
            pre_key = (0, pre) if pre else (1, "")
            # For buildver: we still use semver fields (build metadata isn't generally comparable).
            return (major, minor, patch, pre_key)
        elif style == VersionStyle.SHORTSEMVER:
            major, minor, _, _ = parse_semver(v)
            return (major, minor)
        elif style == VersionStyle.CALVER:
            year, month, day = parse_calver(v)
            return (year, month, day)
        elif style == VersionStyle.SEQVER:
            return (parse_seq(v),)
        elif style == VersionStyle.ZERVER:
            # treat 0 as baseline; any non-zero numeric after dash considered newer
            try:
                n = int(v)
                return (n,)
            except Exception:
                return (0,)
        else:
            # fallback: lexical
            return (v,)
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")


def compare_versions(a: str, b: str, style: VersionStyle) -> int:
    """
    Compare two version strings a and b according to style:
    returns -1 if a < b, 0 if equal, 1 if a > b
    """
    if CAN_USE:
        ka = version_key(a, style)
        kb = version_key(b, style)
        if ka < kb:
            return -1
        elif ka > kb:
            return 1
        return 0
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")


# -----------------------
# OctaStore helpers
# -----------------------
def _build_repo_path_for_version(version: str, conf: OctaConfig) -> str:
    """
    Compute path inside repo to version contents. Default: "<app_name>/<version>/"
    If conf.path_prefix is set, prefix with it.
    """
    if CAN_USE:
        base = conf.app_name.strip("/")
        if conf.path_prefix:
            return f"{conf.path_prefix.strip('/')}/{base}/{version}"
        return f"{base}/{version}"
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")

def _list_versions_via_cli(conf: OctaConfig) -> List[str]:
    """
    Use the octastore CLI to list files under the app_name folder and extract version directory names.
    This is a robust fallback if Python API isn't available.
    """
    if CAN_USE:
        # We'll try to use `octastore list-all` per docs; but to be robust, use `octastore --help` fallback:
        # Use the CLI 'octastore list-all --tokens ... --owners ... --repos ... --path <path>'
        try:
            path = conf.path_prefix.strip("/") + "/" + conf.app_name if conf.path_prefix else conf.app_name
            path = path.strip("/")
            cmd = ["octastore", "list-all",
                "--tokens"] + conf.tokens + ["--owners"] + conf.owners + ["--repos"] + conf.repos + ["--path", path]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            out = proc.stdout or proc.stderr or ""
            # CLI prints JSON or lines. Try to parse JSON first.
            versions = set()
            try:
                data = json.loads(out)
                # data may be list of file entries; we extract directories immediate under path
                for entry in data:
                    # entry might be {'path': 'APP_NAME/0.1.0/...' }
                    p = entry.get("path") if isinstance(entry, dict) else None
                    if p:
                        # get directory portion relative to path
                        rel = p[len(path):].strip("/")
                        if rel:
                            parts = rel.split("/")
                            versions.add(parts[0])
            except Exception:
                # fallback parse lines: find things like APP_NAME/0.1.0/ or /APP_NAME/0.1.0
                for line in out.splitlines():
                    for match in re.finditer(rf"{re.escape(path)}/([^/\s]+)/", line):
                        versions.add(match.group(1))
                    # lines might contain raw file listings: search for pattern path/<ver>/
                    for match in re.finditer(rf"{re.escape(path)}/([^/\s]+)", line):
                        versions.add(match.group(1))
            return sorted(list(versions))
        except FileNotFoundError:
            raise RuntimeError("octastore CLI not found (and octastore Python API unavailable). Install octastore or provide Python octastore package.")
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")


def _list_versions_via_api(conf: OctaConfig) -> List[str]:
    """
    Try to use Python octastore API to list versions. Best-effort - API shape varies by version.
    We'll attempt a few reasonable calls (DataBase or OctaStore API).
    """
    if CAN_USE:
        if _OCTAPI is None:
            raise RuntimeError("octastore Python API not available")
        try:
            # create core (cluster style)
            cluster_cfg = []
            for t, o, r in zip(conf.tokens, conf.owners, conf.repos):
                cluster_cfg.append({
                    "token": t,
                    "repo_owner": o,
                    "repo_name": r,
                    "branch": conf.branch
                })
            core = _OCTAPI.OctaStore(cluster_cfg)
            # DataBase expects an encryption key; use conf.encryption_key or None
            db = _OCTAPI.DataBase(core=core, encryption_key=conf.encryption_key)
            # Attempt to list all files under folder using a plausible method name
            path = conf.path_prefix.strip("/") + "/" + conf.app_name if conf.path_prefix else conf.app_name
            path = path.strip("/")
            # Some versions might expose core.list_files or db.get_all_files — try a few options
            versions = set()

            # Common variant: core.list_files(path=...)
            if hasattr(core, "list_files"):
                files = core.list_files(path=path)
                for f in files:
                    p = f.get("path") if isinstance(f, dict) else str(f)
                    if p.startswith(path + "/"):
                        rel = p[len(path) + 1 :]
                        parts = rel.split("/")
                        if parts and parts[0]:
                            versions.add(parts[0])
                return sorted(list(versions))

            # Fallback: db.get_all maybe can list keys
            if hasattr(db, "get_all"):
                # get all data under path — this might return entries with .path attrs
                items = db.get_all(isencrypted=False, datatype=_OCTAPI.All, path=path)
                # items might be list of KeyValue or objects
                for it in items:
                    # try to pull a .path or .key or string
                    s = None
                    if isinstance(it, dict) and "path" in it:
                        s = it["path"]
                    elif hasattr(it, "path"):
                        s = getattr(it, "path")
                    elif hasattr(it, "key"):
                        s = getattr(it, "key")
                    if s and s.startswith(path + "/"):
                        rel = s[len(path) + 1 :]
                        parts = rel.split("/")
                        if parts and parts[0]:
                            versions.add(parts[0])
                return sorted(list(versions))

            # Last resort: try CLI fallback inside this function
            return _list_versions_via_cli(conf)
        except Exception as ex:
            # bubble up to allow fallback to CLI at higher level
            raise RuntimeError(f"octastore API listing failed: {ex}")
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")


def _download_version_files(conf: OctaConfig, version: str, dest: str) -> None:
    """
    Download all files under repo path for that version into local dest folder.
    This function tries Python API first, then falls back to the CLI.
    """
    if CAN_USE:
        if _OCTAPI is not None:
            try:
                cluster_cfg = []
                for t, o, r in zip(conf.tokens, conf.owners, conf.repos):
                    cluster_cfg.append({
                        "token": t,
                        "repo_owner": o,
                        "repo_name": r,
                        "branch": conf.branch
                    })
                core = _OCTAPI.OctaStore(cluster_cfg)
                db = _OCTAPI.DataBase(core=core, encryption_key=conf.encryption_key)
                path = _build_repo_path_for_version(version, conf)
                # Try API download_file if exists
                if hasattr(core, "download_file"):
                    # Some method signatures expect path and output file; we'll attempt to list files first
                    # Attempt to list files under path via core.list_files if present
                    files = []
                    if hasattr(core, "list_files"):
                        files = core.list_files(path=path)
                    else:
                        # fallback to the CLI fallback if we cannot list; raise to trigger CLI
                        raise RuntimeError("cannot list files via octastore API; will fallback to CLI")
                    # iterate and download each file
                    for fileentry in files:
                        # fileentry might be dict or string
                        fp = fileentry.get("path") if isinstance(fileentry, dict) else str(fileentry)
                        if not fp.startswith(path):
                            continue
                        rel = fp[len(path):].lstrip("/")
                        if not rel:
                            continue
                        local_path = os.path.join(dest, rel)
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        # call core.download_file(path=fp, output=local_path) or similar
                        try:
                            if hasattr(core, "download_file"):
                                core.download_file(path=fp, output=local_path)
                            elif hasattr(core, "download_file_to"):
                                core.download_file_to(fp, local_path)
                            else:
                                raise RuntimeError("no supported download API on octastore core")
                        except Exception:
                            # try db.download_file
                            if hasattr(db, "download_file"):
                                db.download_file(path=fp, output=local_path)
                            else:
                                raise
                    return
            except Exception:
                # fall through to CLI fallback
                pass

        # CLI fallback
        # octastore download-file --tokens ... --owners ... --repos ... --path <repo_path> --output <file_or_folder> --recursive
        path = _build_repo_path_for_version(version, conf)
        # The CLI supports uploading/downloading a file; for directories we may have to list and loop.
        # We'll list remote files first
        try:
            # list remote files under path via 'list-all' then download individually
            cmd_list = ["octastore", "list-all", "--tokens"] + conf.tokens + ["--owners"] + conf.owners + ["--repos"] + conf.repos + ["--path", path]
            proc = subprocess.run(cmd_list, capture_output=True, text=True, check=False)
            out = proc.stdout or proc.stderr or ""
            files = []
            try:
                data = json.loads(out)
                for e in data:
                    p = e.get("path") if isinstance(e, dict) else None
                    if p and p.startswith(path):
                        files.append(p)
            except Exception:
                # parse lines
                for line in out.splitlines():
                    for match in re.finditer(rf"{re.escape(path)}/([^:\s]+)", line):
                        files.append(match.group(0))
            if not files:
                raise RuntimeError(f"No files found at remote path '{path}'.")
            # download each file
            for remote in files:
                rel = remote[len(path):].lstrip("/")
                if not rel:
                    continue
                local_path = os.path.join(dest, rel)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                cmd_dl = ["octastore", "download-file", "--tokens"] + conf.tokens + ["--owners"] + conf.owners + ["--repos"] + conf.repos + ["--path", remote, "--output", local_path]
                proc2 = subprocess.run(cmd_dl, capture_output=True, text=True)
                if proc2.returncode != 0:
                    # try to at least record output
                    raise RuntimeError(f"Failed to download '{remote}': {proc2.stdout or proc2.stderr}")
            return
        except FileNotFoundError:
            raise RuntimeError("octastore CLI not found and octastore Python API unavailable. Install octastore or provide Python octastore package.")
        except Exception as ex:
            raise RuntimeError(f"Download via CLI failed: {ex}")
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")

# -----------------------
# Spec / pyinstaller helpers
# -----------------------
def _generate_spec(main_script: str, dest_spec: str, name: Optional[str] = None, icon: Optional[str] = None):
    """
    Generate a minimal pyinstaller .spec file for the given main_script.
    """
    if CAN_USE:
        name = name or "app"
        # Spec content: a simple one-file build
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
# auto-generated by installerpack
block_cipher = None

a = Analysis(
    ['{main_script}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='{name}')
"""
        if icon:
            spec_content = spec_content.replace("exe = EXE(", f"exe = EXE(\n    icon='{icon}',")
        with open(dest_spec, "w", encoding="utf-8") as f:
            f.write(spec_content)
        return dest_spec
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")


def _run_pyinstaller(spec_path: Optional[str] = None, main_script: Optional[str] = None, onefile: bool = True, name: Optional[str] = None):
    """
    Run pyinstaller to create executable. If spec_path is provided, use that; otherwise build a CLI invocation.
    Returns path to built exe or folder.
    """
    if CAN_USE:
        if spec_path:
            cmd = ["pyinstaller", spec_path]
        else:
            cmd = ["pyinstaller"]
            if onefile:
                cmd.append("--onefile")
            if name:
                cmd += ["--name", name]
            if main_script:
                cmd.append(main_script)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"pyinstaller failed: {proc.stdout}\n{proc.stderr}")
        # find dist folder/exe
        dist_dir = os.path.join(os.getcwd(), "dist")
        if not os.path.isdir(dist_dir):
            # try relative to spec
            dir_spec = os.path.dirname(spec_path) if spec_path else os.getcwd()
            dist_dir = os.path.join(dir_spec, "dist")
        # Search for executable under dist
        exe_path = None
        if name:
            candidate = os.path.join(dist_dir, name + (".exe" if os.name == "nt" else ""))
            if os.path.exists(candidate):
                exe_path = candidate
        if not exe_path:
            # find first file in dist
            for root, _, files in os.walk(dist_dir):
                for file in files:
                    if file.endswith(".exe") or (os.name != "nt" and os.access(os.path.join(root, file), os.X_OK)):
                        exe_path = os.path.join(root, file)
                        break
                if exe_path:
                    break
        if not exe_path:
            raise RuntimeError(f"pyinstaller succeeded but could not locate built executable in {dist_dir}.")
        return exe_path
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")

# -----------------------
# Public update(...) function
# -----------------------
def update(versionstyle: Optional[VersionStyle] = None,
           currentver: Optional[str] = None,
           newver: Optional[Union[str, Literal["latest"]]] = "latest",
           buildspec: Optional[bool] = False,
           killspec: Optional[bool] = False,
           pathtospec: Optional[Optional[str]] = None,
           replaceexe: Optional[bool] = True,
           landingfolder: Optional[Optional[str]] = None):
    """
    The update function is meant to be a button-linked event call, which builds and updates your application/software. Built for installer-style apps.
    Uses OctaStore for version storage--must be a directory in a Github repo that holds all the version's files (i.e. 'APP_NAME/0.1.0/' in which files like 'APP_NAME/0.1.0/main.py', 'APP_NAME/0.1.0/assets/image.png')

    Args:
        versionstyle (Optional[VersionStyle], optional): Sets the version style your software uses to detect which stored version is newer. Defaults to configured version_style or VersionStyle.SEMVER.
        currentver (Optional[Union[str, None]], optional): The version of the current application/software instance--must be in 'versinstyle' format. Defaults to None.
        newver (Optional[Union[str, Literal["latest"]]], optional): The version of the application/software that you wish to install for the user--setting to "latest" will default to the latest version of the application/software found on cloud. Defaults to "latest".
        buildspec (Optional[bool], optional): Decides whether InstallerPack should build the spec file itself. Defaults to False.
        killspec (Optional[bool], optional): Decides whether or not InstallerPack should kill the created (or found) `pyinstaller` spec file. Defaults to False.
        pathtospec (Optional[Union[str, None]], optional): Path to your .spec file--only use if 'buildspec' is set to False. Defaults to None.
        replaceexe (Optional[bool], optional): Decides whether InstallerPack should replace the executable file (.exe) of your old app when adding the new one. Defaults to True.
        landingfolder (Optional[Union[str, None]], optional): The path where the .exe file should land (be placed). Defaults to None.
    """
    if CAN_USE:
        if versionstyle is None:
            versionstyle = DEFAULT_VERSION_STYLE

        if _OCTACONF is None:
            raise RuntimeError("OctaStore configuration not set. Call setocta(OctaConfig(...)) before update().")

        conf = _OCTACONF

        # 1) list available versions
        versions = []
        # Try python API first
        try:
            versions = _list_versions_via_api(conf)
        except Exception as api_ex:
            # fallback to CLI
            try:
                versions = _list_versions_via_cli(conf)
            except Exception as cli_ex:
                raise RuntimeError(f"Failed to list versions via octastore API ({api_ex}) and CLI ({cli_ex}).")

        if not versions:
            raise RuntimeError("No versions found in OctaStore under configured path.")

        # 2) pick version to install
        chosen_version = None
        if newver == "latest":
            # find the latest according to versionstyle
            versions_sorted = sorted(versions, key=lambda v: version_key(v, versionstyle))
            chosen_version = versions_sorted[-1]
        else:
            if newver in versions:
                chosen_version = newver
            else:
                # try to find close match (strip leading v)
                match = None
                for v in versions:
                    if v.lstrip("v") == str(newver).lstrip("v"):
                        match = v
                        break
                if match:
                    chosen_version = match
                else:
                    raise RuntimeError(f"Requested version '{newver}' not found among available versions: {versions}")

        # if currentver provided, compare to avoid downgrades
        if currentver:
            cmp = compare_versions(currentver, chosen_version, versionstyle)
            if cmp == 0:
                print(colored_text("GREEN", f"Already on requested version {currentver}. Nothing to do."))
                return {"updated": False, "reason": "already_current", "version": currentver}
            elif cmp > 0:
                print(colored_text("YELLOW", f"Current version ({currentver}) is newer than requested ({chosen_version}). Downgrade prevented."))
                return {"updated": False, "reason": "downgrade_prevented", "current": currentver, "requested": chosen_version}

        print(colored_text("BLUE", f"Selected version '{chosen_version}' for installation."))

        # 3) download version files into temp folder
        tmpdir = tempfile.mkdtemp(prefix="installerpack_")
        try:
            _download_version_files(conf, chosen_version, tmpdir)
        except Exception as e:
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise RuntimeError(f"Failed to download version '{chosen_version}': {e}")

        print(colored_text("GREEN", f"Downloaded version '{chosen_version}' into temporary folder: {tmpdir}"))

        # 4) Determine main script to run/build
        # Heuristic: prefer <app_name>.py, main.py, or first .py at root
        main_script_local = None
        root_files = os.listdir(tmpdir)
        candidates = [f"{conf.app_name}.py", "main.py", "app.py"]
        for c in candidates:
            if c in root_files and c.endswith(".py"):
                main_script_local = os.path.join(tmpdir, c)
                break
        if main_script_local is None:
            # find any .py in root
            for f in root_files:
                if f.endswith(".py"):
                    main_script_local = os.path.join(tmpdir, f)
                    break

        # If still None, search recursively
        if main_script_local is None:
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith(".py"):
                        main_script_local = os.path.join(root, file)
                        break
                if main_script_local:
                    break

        if main_script_local is None:
            # Nothing to build; maybe the version is just data/assets. Return success but no exe.
            print(colored_text("YELLOW", "No Python entry script found in downloaded version. Assuming non-executable release (assets/data)."))
            return {"updated": True, "version": chosen_version, "installed_at": tmpdir, "exe": None}

        print(colored_text("BLUE", f"Main script detected: {main_script_local}"))

        # 5) If buildspec True: generate spec file (unless pathtospec given)
        spec_path = pathtospec
        created_spec_path = None
        if buildspec:
            if pathtospec:
                spec_path = pathtospec
            else:
                # create spec file next to main_script_local
                created_spec_path = os.path.join(tmpdir, f"{conf.app_name}.spec")
                _generate_spec(main_script_local, created_spec_path, name=conf.app_name)
                spec_path = created_spec_path

        # 6) Run pyinstaller to produce executable (if pyinstaller available)
        exe_path = None
        try:
            # Ensure pyinstaller installed
            proc_check = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True)
            if proc_check.returncode != 0:
                raise RuntimeError("pyinstaller not available on PATH")
        except FileNotFoundError:
            raise RuntimeError("pyinstaller not found on PATH. Install pyinstaller to enable building distributables.")

        try:
            exe_path = _run_pyinstaller(spec_path=spec_path, main_script=main_script_local, name=conf.app_name)
        except Exception as ex:
            # Clean up spec if created and killspec True
            if created_spec_path and killspec:
                try:
                    os.remove(created_spec_path)
                except Exception:
                    pass
            # Propagate
            raise RuntimeError(f"pyinstaller build failed: {ex}")

        print(colored_text("GREEN", f"Built executable: {exe_path}"))

        # 7) Optionally place/replace exe in landing folder / replace existing
        final_dest = None
        try:
            if landingfolder:
                os.makedirs(landingfolder, exist_ok=True)
                final_dest = os.path.join(landingfolder, os.path.basename(exe_path))
                if os.path.exists(final_dest) and replaceexe:
                    os.remove(final_dest)
                shutil.copy2(exe_path, final_dest)
            else:
                # default: copy to current working dir or overwrite existing file with same name
                final_dest = os.path.join(os.getcwd(), os.path.basename(exe_path))
                if os.path.exists(final_dest) and replaceexe:
                    os.remove(final_dest)
                shutil.copy2(exe_path, final_dest)
        except Exception as ex:
            raise RuntimeError(f"Failed to place executable to landing folder: {ex}")

        print(colored_text("BLUE", f"Executable placed at: {final_dest}"))

        # 8) cleanup spec if requested
        if created_spec_path and killspec:
            try:
                os.remove(created_spec_path)
            except Exception:
                pass

        # 9) return result summary
        result = {
            "updated": True,
            "version": chosen_version,
            "downloaded_to": tmpdir,
            "main_script": main_script_local,
            "exe": final_dest
        }

        return result
    else:
        raise ModuleNotFoundError("Module 'InstallerPack' not found")