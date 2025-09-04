import os
import platform
import requests
import zipfile
import shutil
import subprocess
import urllib3
from pathlib import Path
from InquirerPy import inquirer
from packaging import version as pkg_version

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TERRAFORM_DIR = Path.home() / ".terraform_versions"
TERRAFORM_BIN = Path.home() / ".terraform_bin" / "terraform"
USER_BIN = Path.home() / "bin" / "terraform"

def get_os_arch():
    system = platform.system().lower()
    arch = platform.machine().lower()

    if system == "darwin":
        system = "darwin"
    elif system == "linux":
        system = "linux"
    else:
        raise Exception(f"Unsupported system: {system}")

    if arch in ("x86_64", "amd64"):
        arch = "amd64"
    elif arch in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        raise Exception(f"Unsupported arch: {arch}")

    return system, arch


def fetch_available_versions():
    url = "https://releases.hashicorp.com/terraform/index.json"
    r = requests.get(url, verify=False, timeout=10)
    data = r.json()["versions"]

    versions = []
    for v in data.keys():
        try:
            pkg_version.parse(v)
            if "beta" not in v and "rc" not in v:
                versions.append(v)
        except Exception:
            continue

    return sorted(versions, key=pkg_version.parse, reverse=True)


def download_terraform(version: str):
    system, arch = get_os_arch()
    url = f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_{system}_{arch}.zip"
    print(f"⬇️  Downloading {url} ...")

    r = requests.get(url, stream=True, verify=False, timeout=60)
    if r.status_code != 200:
        raise Exception(f"Terraform {version} not found!")

    zip_path = TERRAFORM_DIR / f"terraform_{version}.zip"
    TERRAFORM_DIR.mkdir(parents=True, exist_ok=True)

    with open(zip_path, "wb") as f:
        shutil.copyfileobj(r.raw, f)

    extract_path = TERRAFORM_DIR / version
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    os.remove(zip_path)

    terraform_bin = extract_path / "terraform"
    terraform_bin.chmod(0o755)

    print(f"✅ Terraform {version} installed at {extract_path}")


def update_symlinks(version: str):
    bin_path = TERRAFORM_DIR / version / "terraform"

    # ~/.terraform_bin/terraform
    target_dir = TERRAFORM_BIN.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    if TERRAFORM_BIN.exists() or TERRAFORM_BIN.is_symlink():
        TERRAFORM_BIN.unlink()
    TERRAFORM_BIN.symlink_to(bin_path)

    # ~/bin/terraform
    user_bin_dir = USER_BIN.parent
    user_bin_dir.mkdir(parents=True, exist_ok=True)
    if USER_BIN.exists() or USER_BIN.is_symlink():
        USER_BIN.unlink()
    USER_BIN.symlink_to(bin_path)
    USER_BIN.chmod(0o755)

    # ensure ~/bin is in PATH
    shell_rc = Path.home() / (".zshrc" if os.environ.get("SHELL", "").endswith("zsh") else ".bashrc")
    export_line = 'export PATH="$HOME/bin:$PATH"'
    if not shell_rc.exists() or export_line not in shell_rc.read_text():
        with open(shell_rc, "a") as f:
            f.write(f"\n# Added by tfswitch\n{export_line}\n")
        print(f"⚙️  Added ~/bin to PATH in {shell_rc}, restart your shell to apply.")

    print(f"🔀 Switched to Terraform {version}")


def switch_terraform(version: str):
    bin_path = TERRAFORM_DIR / version / "terraform"
    if not bin_path.exists():
        download_terraform(version)

    update_symlinks(version)

    # check version
    try:
        subprocess.run([str(USER_BIN), "-v"], check=False)
    except Exception as e:
        print(f"⚠️ Could not run terraform: {e}")


def main():
    available = fetch_available_versions()

    choice = inquirer.select(
        message="Select Terraform version:",
        choices=[{"name": v, "value": v} for v in available],
    ).execute()

    switch_terraform(choice)
