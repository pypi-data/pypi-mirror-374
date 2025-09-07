
import site
import threading
import subprocess
import re
import os
import sys
import importlib
import logging
import platform
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

_PIP_LOCK = threading.Lock()


def envType():
    if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        return "virtual environment"
    if os.getenv("CONDA_PREFIX"):
        return "conda environment"
    return "global environment"

def _bootstrapPip():
    try:
        import pip  # noqa: F401
    except ImportError:
        import ensurepip
        ensurepip.bootstrap()

def _ensureUserSiteOnPath(quiet: bool):
    """
    Ensure the user site-packages dir is importable.
    If PYTHONNOUSERSITE is set, raise (explicitly disabled).
    """
    if os.environ.get("PYTHONNOUSERSITE"):
        raise RuntimeError(
            "User site-packages is disabled (PYTHONNOUSERSITE=1); "
            "cannot import packages installed with --user."
        )
    try:
        user_site = site.getusersitepackages()
    except Exception as e:
        raise RuntimeError(f"Could not resolve user site-packages: {e}")
    if not user_site:
        raise RuntimeError("Could not determine user site-packages directory.")
    if user_site not in sys.path:
        sys.path.insert(0, user_site)
        if not quiet:
            print(f"Added user site to sys.path: {user_site}")

def _ensurePackagesCore(requires, quiet=True, envVarOptOut="NO_AUTO_PIP", failHard=False):
    """
    Core logic for ensuring (import_name, pip_spec) pairs are importable.
    Shared by EnsurePackages.
    """
    if not isinstance(requires, (list, tuple)):
        raise TypeError("requires must be a list/tuple of (import_name, pip_spec) pairs")

    for pair in requires:
        if not (isinstance(pair, (list, tuple)) and len(pair) == 2):
            raise TypeError(f"invalid requirement entry: {pair!r} (expected (import_name, pip_spec))")

    if os.getenv(envVarOptOut):
        return {"installed": [], "present": []}

    present, missing = [], []
    for import_name, pip_spec in requires:
        try:
            importlib.import_module(import_name)
            present.append(import_name)
        except ModuleNotFoundError:
            missing.append((import_name, pip_spec))

    if not missing:
        if not quiet:
            print(f"No installs needed; running in {envType()}.")
        return {"installed": [], "present": present}

    env = envType()
    base_cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
    used_user = False
    if env == "global environment":
        base_cmd.append("--user")
        used_user = True

    if not quiet:
        print(f"Installing {len(missing)} missing packages into {env}...")

    installed, failed = [], []
    with _PIP_LOCK:
        _bootstrapPip()
        for import_name, pip_spec in missing:
            try:
                kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL} if quiet else {}
                subprocess.check_call(base_cmd + [pip_spec], **kwargs)
                if used_user:
                    _ensureUserSiteOnPath(quiet)
                importlib.invalidate_caches()
                importlib.import_module(import_name)  # verify
                installed.append(pip_spec)
            except Exception as exc:
                msg = f"Failed to install '{pip_spec}' for '{import_name}': {exc}"
                if failHard:
                    raise RuntimeError(msg) from exc
                logger.error(msg)
                failed.append({"import": import_name, "spec": pip_spec, "error": str(exc)})

    return {"installed": installed, "present": present, "failed": failed}



def EnsurePackages(requires, quiet=True, envVarOptOut="NO_AUTO_PIP", failHard=False):
    return _ensurePackagesCore(requires, quiet, envVarOptOut, failHard)

HoloPackages = EnsurePackages
HoloInstaller = EnsurePackages


class HoloViro:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HoloViro, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.envDir   = None
        self.sitePath = None
        self.fileName = None
        self._venvPython = None
        self._venvPip = None

    def setEnvDir(self, envDir: str = None) -> None:
        if envDir is None:
            envDir = self._getDir("SkillsEnv")
        self.envDir = envDir
        self.createVirtualEnv()
        self._resolveVenvExecutables()
        self.sitePath = self._getSitePackages()

    def _resolveVenvExecutables(self) -> None:
        env_path = Path(self.envDir)
        if platform.system() == "Windows":
            py = env_path / "Scripts" / "python.exe"
            pip = env_path / "Scripts" / "pip.exe"
        else:
            py = env_path / "bin" / "python"
            pip = env_path / "bin" / "pip"
        if not py.exists():
            raise FileNotFoundError(f"Could not find venv python at: {py}")
        self._venvPython = str(py)
        self._venvPip = str(pip) if pip.exists() else None

    def _getSitePackages(self) -> str:
        try:
            out = subprocess.check_output(
                [self._venvPython, "-c", "import sysconfig;print(sysconfig.get_paths()['purelib'])"],
                text=True
            ).strip()
            p = Path(out)
            if not p.exists():
                raise FileNotFoundError(out)
            return str(p)
        except Exception as e:
            raise FileNotFoundError(f"Unable to locate site-packages for venv at '{self.envDir}': {e}")

    def importFromVenv(self, package: str) -> str:
        if str(self.sitePath) not in sys.path:
            sys.path.insert(0, str(self.sitePath))
        try:
            return importlib.import_module(package)
        except Exception as e:
            raise ImportError(f"Could not import '{package}' from virtual environment: {e}")

    def _getDir(self, *paths: str) -> str:
        return str(Path(*paths).resolve())

    def saveCode(self, code: str, codeDir: str) -> None:
        code_path = Path(codeDir)
        code_path.mkdir(parents=True, exist_ok=True)

        match = re.search(r"class (.+):", code)
        if not match:
            raise ValueError("No class declaration found in the provided code.")

        name = match.group(1).lower()
        self.fileName = f"{name}.py"
        lines = code.splitlines()

        importLines = []
        bodyLines = []
        insideDocstring = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("'''") or stripped.startswith('"""'):
                insideDocstring = not insideDocstring
                bodyLines.append(line)
                continue
            if not insideDocstring and (stripped.startswith("import ") or stripped.startswith("from ")):
                importLines.append(stripped)
            else:
                bodyLines.append(line)

        importLines = [line for line in importLines if line]
        formattedCode = "\n" + "\n".join(importLines) + "\n\n\n" + "\n".join(bodyLines).lstrip()
        formattedCode = self.fixDocstringIndentation(formattedCode)

        (code_path / self.fileName).write_text(formattedCode, encoding="utf-8")
        return self.fileName

    def extractSegments(self, codeBlock: str, pipInstalls: bool = False) -> str:
        try:
            pattern_backticks = r"```(?:python|bash)?\n(.*?)```"
            pattern_python_code = r"(^(?:from|import|class|def)\b[\s\S]+?(?=^(?:from|import|class|def)\b|\Z))"
            pip_install_pattern = r"pip install ([\w\s,-]+)"

            matches_backticks = re.findall(pattern_backticks, codeBlock, re.DOTALL)
            matches_python_code = re.findall(pattern_python_code, codeBlock, re.MULTILINE)

            extracted_segments = matches_backticks + matches_python_code

            if pipInstalls:
                pip_installs = re.findall(pip_install_pattern, codeBlock)
                for install_line in pip_installs:
                    if install_line.strip().lower() == "none":
                        continue
                    packages = [pkg.strip() for pkg in install_line.split(',') if pkg.strip().lower() != "none"]
                    for package in packages:
                        if package:
                            self.pipInstall(package)

            return '\n\n'.join(extracted_segments)

        except Exception as e:
            logger.error(f"Error extracting segments:", exc_info=True)
            return ""

    def fixDocstringIndentation(self, codeBlock: str) -> str:
        pattern = re.compile(r"(Args:\n(?:\s+.+?: .+?\n)+)", re.MULTILINE)

        def reindent(match):
            section = match.group(1)
            lines = section.strip().splitlines()
            fixed = []
            for line in lines:
                if ":" in line:
                    fixed.append(line)
                else:
                    fixed.append(" " * 22 + line.strip())
            return "\n".join(fixed) + "\n"

        return pattern.sub(reindent, codeBlock)

    def pipInstall(self, package: str) -> None:
        packageName = package.strip().split()[-1]
        try:
            self.importFromVenv(packageName)
            print(f"Package '{packageName}' is already installed in venv.")
        except ImportError:
            print(f"Installing '{packageName}' to virtual environment...")
            self.installPackage(packageName)

    def createVirtualEnv(self):
        env_path = Path(self.envDir)
        if env_path.exists():
            return

        print(f"Creating virtual environment at:\n'{env_path}'.")
        uv = shutil.which("uv")
        if uv:
            subprocess.check_call(
                [uv, "venv", str(env_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT
            )
        else:
            subprocess.check_call([sys.executable, "-m", "venv", str(env_path)])
            self._resolveVenvExecutables()
            try:
                subprocess.check_call([self._venvPython, "-m", "ensurepip", "--upgrade"])
            except subprocess.CalledProcessError:
                pass

        self._resolveVenvExecutables()

    def installPackage(self, package: str) -> bool:
        my_env = os.environ.copy()
        my_env["VIRTUAL_ENV"] = str(self.envDir)

        uv = shutil.which("uv")
        try:
            if uv:
                subprocess.check_call([uv, "pip", "install", package], env=my_env)
            else:
                if not self._venvPip or not Path(self._venvPip).exists():
                    subprocess.check_call([self._venvPython, "-m", "ensurepip", "--upgrade"], env=my_env)
                    self._resolveVenvExecutables()
                cmd = [self._venvPython, "-m", "pip", "install", package]
                subprocess.check_call(cmd, env=my_env)
            print(f"Package '{package}' installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install package '{package}': {e}")
            return False

    @classmethod
    def ensurePackages(cls, requires, quiet=True, envVarOptOut="NO_AUTO_PIP", failHard=False):
        return _ensurePackagesCore(requires, quiet, envVarOptOut, failHard)

    @classmethod
    def installPackages(cls, requires, quiet=True, envVarOptOut="NO_AUTO_PIP", failHard=False):
        return _ensurePackagesCore(requires, quiet, envVarOptOut, failHard)



# import sys, subprocess, importlib, threading, os

# _PIP_LOCK = threading.Lock()

# def envType():
#     return "virtual environment" if sys.prefix != getattr(sys, "base_prefix", sys.prefix) else "global environment"

# def _bootstrapPip():
#     try:
#         import pip  # noqa: F401
#     except ImportError:
#         import ensurepip
#         ensurepip.bootstrap()

# def ensurePackages(requires, quiet=True, envVarOptOut="NO_AUTO_PIP"):
#     if not isinstance(requires, (list, tuple)):
#         raise TypeError("requires must be a list/tuple of (import_name, pip_spec) pairs")

#     if os.getenv(envVarOptOut):
#         return {"installed": [], "present": []}

#     present, missing = [], []
#     for import_name, pip_spec in requires:
#         try:
#             importlib.import_module(import_name)
#             present.append(import_name)
#         except ModuleNotFoundError:
#             missing.append((import_name, pip_spec))

#     if not missing:
#         if not quiet:
#             print(f"No installs needed; running in {envType()}.")
#         return {"installed": [], "present": present}

#     base_cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
#     if sys.prefix == getattr(sys, "base_prefix", sys.prefix):  # global env
#         base_cmd.append("--user")

#     if not quiet:
#         print(f"Installing {len(missing)} missing packages into {envType()}...")

#     installed = []
#     with _PIP_LOCK:
#         _bootstrapPip()
#         for import_name, pip_spec in missing:
#             try:
#                 kwargs = {}
#                 if quiet:
#                     kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}

#                 subprocess.check_call(base_cmd + [pip_spec], **kwargs)
#                 importlib.invalidate_caches()
#                 importlib.import_module(import_name)  # verify
#                 installed.append(pip_spec)
#             except Exception as exc:
#                 raise RuntimeError(f"Failed to install '{pip_spec}' for '{import_name}': {exc}") from exc

#     return {"installed": installed, "present": present}














# import subprocess
# import re
# import os
# import sys
# import importlib
# import time
# import pyperclip
# import pyautogui
# from pathlib import Path
# import venv
# from dotenv import load_dotenv
# import logging


# logger = logging.getLogger(__name__)


# class HoloViro:
#     _instance = None

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super(HoloViro, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         if hasattr(self, "initialized"):
#             return
#         self._initComponents()
#         self.initialized = True

#     def _initComponents(self):
#         self.envDir   = None
#         self.sitePath = None
#         self.fileName = None

#     def setEnvDir(self, envDir: str = None) -> None:
#         if envDir is None:
#             envDir = self._getDir("SkillsEnv")
#         self.envDir = envDir
#         self.createVirtualEnv()
#         self.sitePath = self._getSitePackages()

#     def _getSitePackages(self) -> str:
#         try:
#             return next(Path(self.envDir).rglob("site-packages"))
#         except StopIteration:
#             raise FileNotFoundError(f"No 'site-packages' found in virtual environment '{self.envDir}'")

#     def importFromVenv(self, package: str) -> str:
#         if str(self.sitePath) not in sys.path:
#             sys.path.insert(0, str(self.sitePath))
#         try:
#             return importlib.import_module(package)
#         except Exception as e:
#             raise ImportError(f"Could not import '{package}' from virtual environment: {e}")

#     def _getDir(self, *paths: str) -> str:
#         return str(Path(*paths).resolve())

#     def saveCode(self, code: str, codeDir: str) -> None:
#         if not os.path.exists(codeDir):
#             os.makedirs(codeDir)

#         match = re.search(r"class (.+):", code)
#         if not match:
#             # print("No match found in the code.")
#             # return
#             raise ValueError("No class declaration found in the provided code.")

#         name = match.group(1).lower()
#         self.fileName = f"{name}.py"
#         lines = code.splitlines()

#         importLines = []
#         bodyLines = []
#         insideDocstring = False

#         for line in lines:
#             stripped = line.strip()

#             # Handle multi-line docstring content
#             if stripped.startswith("'''") or stripped.startswith('"""'):
#                 insideDocstring = not insideDocstring
#                 bodyLines.append(line)
#                 continue

#             if not insideDocstring and (stripped.startswith("import ") or stripped.startswith("from ")):
#                 importLines.append(stripped)
#             else:
#                 bodyLines.append(line)

#         # Remove blank lines and sort imports (optional sorting)
#         importLines = [line for line in importLines if line]

#         # Build final output: blank line at top, grouped imports, two blank lines, then rest
#         formattedCode = "\n" + "\n".join(importLines) + "\n\n\n" + "\n".join(bodyLines).lstrip()
#         formattedCode = self.fixDocstringIndentation(formattedCode)

#         with open(rf"{codeDir}\{name}.py", "w", encoding="utf-8") as file:
#             file.write(formattedCode)
#         return self.fileName

#     def extractSegments(self, codeBlock: str, pipInstalls: bool = False) -> str:
#         try:
#             pattern_backticks = r"```(?:python|bash)?\n(.*?)```"
#             pattern_python_code = r"(^(?:from|import|class|def)\b[\s\S]+?(?=^(?:from|import|class|def)\b|\Z))"
#             pip_install_pattern = r"pip install ([\w\s,-]+)"

#             matches_backticks = re.findall(pattern_backticks, codeBlock, re.DOTALL)
#             matches_python_code = re.findall(pattern_python_code, codeBlock, re.MULTILINE)

#             extracted_segments = matches_backticks + matches_python_code

#             if pipInstalls:
#                 pip_installs = re.findall(pip_install_pattern, codeBlock)
#                 for install_line in pip_installs:
#                     if install_line.strip().lower() == "none":
#                         continue
#                     packages = [pkg.strip() for pkg in install_line.split(',') if pkg.strip().lower() != "none"]
#                     for package in packages:
#                         if package:
#                             self.pipInstall(package)

#             return '\n\n'.join(extracted_segments)

#         except Exception as e:
#             logger.error(f"Error extracting segments:", exc_info=True)
#             return ""

#     def fixDocstringIndentation(self, codeBlock: str) -> str:
#         pattern = re.compile(r"(Args:\n(?:\s+.+?: .+?\n)+)", re.MULTILINE)

#         def reindent(match):
#             section = match.group(1)
#             lines = section.strip().splitlines()
#             fixed = []

#             for line in lines:
#                 if ":" in line:
#                     fixed.append(line)
#                 else:
#                     # Continuation line
#                     fixed.append(" " * 22 + line.strip())
#             return "\n".join(fixed) + "\n"

#         return pattern.sub(reindent, codeBlock)

#     def pipInstall(self, package: str) -> None:
#         packageName = package.strip().split()[-1]
#         try:
#             self.importFromVenv(packageName)
#             print(f"Package '{packageName}' is already installed in venv.")
#         except ImportError:
#             print(f"Installing '{packageName}' to virtual environment...")
#             self.installPackage(packageName)

#     def createVirtualEnv(self):
#         if not os.path.exists(self.envDir):
#             print(f"Creating virtual environment at:\n'{self.envDir}'.")
#             my_env = os.environ.copy()
#             subprocess.check_call(
#                 ["uv", "venv", self.envDir],
#                 env=my_env,
#                 stdout=subprocess.DEVNULL,   # Suppress normal output
#                 stderr=subprocess.STDOUT     # Suppress errors as well, optional
#             )

#     def installPackage(self, package: str) -> bool:
#         my_env = os.environ.copy()
#         my_env["VIRTUAL_ENV"] = self.envDir  # Ensures uv installs to your venv

#         try:
#             subprocess.check_call(["uv", "pip", "install", package], env=my_env)
#             print(f"Package '{package}' installed successfully.")
#             return True
#         except subprocess.CalledProcessError as e:
#             logger.error(f"Failed to install package '{package}': {e}")
#             return False

#     def enterCode(self, code: str) -> None:
#         # Method to enter code into Notepad
#         subprocess.Popen(['notepad.exe'])
#         time.sleep(1)
#         pyperclip.copy(code)
#         pyautogui.hotkey('ctrl', 'v')


