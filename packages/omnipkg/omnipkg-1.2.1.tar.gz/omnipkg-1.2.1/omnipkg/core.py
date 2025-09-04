"""
omnipkg
An intelligent installer that lets pip run, then surgically cleans up downgrades
and isolates conflicting versions in deduplicated bubbles to guarantee a stable environment.
"""
import concurrent.futures
import hashlib
import importlib.metadata
import io
import json
import locale as sys_locale
import os
import pickle
import platform
import re
import shutil
import site
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Set, Tuple
import filelock
import redis
import requests as http_requests
import zlib
from filelock import FileLock
from importlib.metadata import Distribution, version, metadata, PackageNotFoundError
from packaging.utils import canonicalize_name
from packaging.version import parse as parse_version, InvalidVersion
from .i18n import _, LANG_INFO, SUPPORTED_LANGUAGES
from .package_meta_builder import omnipkgMetadataGatherer
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    magic = None
    HAS_MAGIC = False

def _get_core_dependencies() -> set: # Change return type hint to set
    """
    Correctly reads omnipkg's own production dependencies and returns them as a set.
    """
    try:
        pkg_meta = metadata("omnipkg")
        # Convert the list of dependency strings to a set of package names
        reqs = pkg_meta.get_all("Requires-Dist") or []
        return {canonicalize_name(re.match(r'^[a-zA-Z0-9\-_.]+', req).group(0)) for req in reqs if re.match(r'^[a-zA-Z0-9\-_.]+', req)}
    except PackageNotFoundError:
        # Development path: Read from pyproject.toml
        try:
            pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with pyproject_path.open("rb") as f:
                    pyproject_data = tomllib.load(f)
                return pyproject_data["project"].get("dependencies", [])
        except Exception as e:
            print(f"⚠️ Could not parse pyproject.toml, falling back to empty list: {e}")
            return []
    except Exception as e:
        print(f"⚠️ Could not determine core dependencies, falling back to empty list: {e}")
        return []

class ConfigManager:
    """
    Manages loading and first-time creation of the omnipkg config file.
    Now includes Python interpreter hotswapping capabilities and is environment-aware.
    """

    def __init__(self):
        """
        Initializes the ConfigManager with a robust, fail-safe sequence
        that now AUTOMATICALLY ADOPTS the native interpreter on first run.
        """
        self._python_cache = {}
        self._preferred_version = (3, 11)
        self.venv_path = self._get_venv_root()
        self.env_id = hashlib.md5(str(self.venv_path.resolve()).encode()).hexdigest()[:8]
        self.config_dir = Path.home() / '.config' / 'omnipkg'
        self.config_path = self.config_dir / 'config.json'

        # This flag tracks if the one-time, per-environment setup is complete.
        setup_complete_flag = self.venv_path / '.omnipkg' / '.setup_complete'

        # --- NEW, ROBUST BOOTSTRAP LOGIC ---
        # If the one-time setup for this venv has NOT been done, execute it.
        if not setup_complete_flag.exists():
            print('\n' + '=' * 60)
            print(('  🚀 OMNIPKG ONE-TIME ENVIRONMENT SETUP'))
            print('=' * 60)

            # This is a temporary config just for the setup process.
            self.config = self._get_sensible_defaults()

            try:
                # --- START: THE CRITICAL FIX ---
                # STEP 1: Immediately adopt the native interpreter we are currently running on.
                # This makes it a known, managed entity from the start.
                print(_('   - Step 1: Registering the native Python interpreter...'))
                native_version_str = f'{sys.version_info.major}.{sys.version_info.minor}'
                self._register_and_link_existing_interpreter(Path(sys.executable), native_version_str)
                # --- END: THE CRITICAL FIX ---

                # STEP 2: Check if the preferred control plane (Python 3.11) is also needed.
                if sys.version_info[:2] != self._preferred_version:
                    print(('\n   - Step 2: Setting up the required Python 3.11 control plane...'))
                    # We need a temporary OmnipkgCore instance just for this operation
                    temp_omnipkg = omnipkg(config_manager=self)
                    result_code = temp_omnipkg._fallback_to_download('3.11')
                    if result_code != 0:
                        raise RuntimeError("Failed to set up the Python 3.11 control plane.")

                # STEP 3: Mark setup as complete to prevent this block from running again.
                setup_complete_flag.parent.mkdir(parents=True, exist_ok=True)
                setup_complete_flag.touch()

                print('\n' + '=' * 60)
                print(('  ✅ SETUP COMPLETE'))
                print('=' * 60)
                print(('Your environment is now fully managed by omnipkg.'))
                print(_('👉 Please re-run your previous command: omnipkg {}').format(' '.join(sys.argv[1:])))
                print('=' * 60)
                sys.exit(0) # Exit cleanly to allow the user to re-run in a stable state.

            except Exception as e:
                print(f"❌ A critical error occurred during one-time setup: {e}")
                import traceback
                traceback.print_exc()
                # Clean up the flag on failure so setup can be re-attempted.
                if setup_complete_flag.exists():
                    setup_complete_flag.unlink(missing_ok=True)
                sys.exit(1)

        # --- STANDARD CONFIG LOADING (for all subsequent runs) ---
        self.config = self._load_or_create_env_config()
        if self.config:
            self.multiversion_base = Path(self.config.get('multiversionbase', ''))
        else:
            print(('⚠️ CRITICAL Warning: Config failed to load, omnipkg may not function.'))
            self.multiversion_base = Path('')
    
    def _peek_config_for_flag(self, flag_name: str) -> bool:
        """
        Safely checks the config file for a boolean flag for the current environment
        without fully loading the ConfigManager. Returns False if file doesn't exist.
        """
        if not self.config_path.exists():
            return False
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            return data.get('environments', {}).get(self.env_id, {}).get(flag_name, False)
        except (json.JSONDecodeError, IOError):
            return False

    def _get_venv_root(self) -> Path:
        """
        Reliably finds the root of the virtual environment.
        PRIORITY 1: Check for an override environment variable set during relaunch.
        PRIORITY 2: Search upwards for the pyvenv.cfg file.
        """
        # Priority 1: Check for the override variable set by the gatekeeper.
        venv_root_override = os.environ.get('OMNIPKG_VENV_ROOT')
        if venv_root_override:
            return Path(venv_root_override)

        # Priority 2: Fallback to searching for pyvenv.cfg for the initial run.
        current_dir = Path(sys.executable).resolve().parent
        while current_dir != current_dir.parent:
            if (current_dir / 'pyvenv.cfg').exists():
                return current_dir
            current_dir = current_dir.parent
        
        # Final fallback, should not be hit in a standard venv.
        return Path(sys.prefix)

    def _reset_setup_flag_on_disk(self):
        """Directly modifies the config file on disk to reset the setup flag."""
        try:
            full_config = {'environments': {}}
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    full_config = json.load(f)
            if self.env_id in full_config.get('environments', {}):
                full_config['environments'][self.env_id].pop('managed_python_setup_complete', None)
            with open(self.config_path, 'w') as f:
                json.dump(full_config, f, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            print(_('   ⚠️  Could not reset setup flag in config file: {}').format(e))

    def _trigger_hotswap_relaunch(self):
        """
        Handles the user interaction and download process for an environment that needs to be upgraded.
        This function is self-contained and does not depend on self.config. It ends with an execv call.
        """
        print('\n' + '=' * 60)
        print(_('  🚀 Environment Hotswap to a Managed Python 3.11'))
        print('=' * 60)
        print(f'omnipkg works best with Python 3.11. Your version is {sys.version_info.major}.{sys.version_info.minor}.')
        print(_("\nTo ensure everything 'just works', omnipkg will now perform a one-time setup:"))
        print(_('  1. Download a self-contained Python 3.11 into your virtual environment.'))
        print('  2. Relaunch seamlessly to continue your command.')
        try:
            choice = input('\nDo you want to proceed with the automatic setup? (y/n): ')
            if choice.lower() == 'y':
                self._install_python311_in_venv()
            else:
                print('🛑 Setup cancelled. Aborting, as a managed Python 3.11 is required.')
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            print(_('\n🛑 Operation cancelled. Aborting.'))
            sys.exit(1)

    def _has_suitable_python311(self) -> bool:
        """
        Comprehensive check for existing suitable Python 3.11 installations.
        Returns True if we already have a usable Python 3.11 setup.
        """
        if sys.version_info[:2] == (3, 11) and sys.executable.startswith(str(self.venv_path)):
            return True
        registry_path = self.venv_path / '.omnipkg' / 'interpreters' / 'registry.json'
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
                python_311_path = registry.get('interpreters', {}).get('3.11')
                if python_311_path and Path(python_311_path).exists():
                    try:
                        result = subprocess.run([python_311_path, '-c', "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0 and result.stdout.strip() == '3.11':
                            return True
                    except:
                        pass
            except:
                pass
        expected_exe_path = self._get_interpreter_dest_path(self.venv_path) / ('python.exe' if platform.system() == 'Windows' else 'bin/python3.11')
        if expected_exe_path.exists():
            try:
                result = subprocess.run([str(expected_exe_path), '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'Python 3.11' in result.stdout:
                    return True
            except:
                pass
        bin_dir = self.venv_path / ('Scripts' if platform.system() == 'Windows' else 'bin')
        if bin_dir.exists():
            for possible_name in ['python3.11', 'python']:
                exe_path = bin_dir / (f'{possible_name}.exe' if platform.system() == 'Windows' else possible_name)
                if exe_path.exists():
                    try:
                        result = subprocess.run([str(exe_path), '-c', "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0 and result.stdout.strip() == '3.11':
                            return True
                    except:
                        pass
        return False

    def _get_paths_for_interpreter(self, python_exe_path: str) -> Optional[Dict[str, str]]:
        """
            Runs an interpreter in a subprocess to ask for its version and calculates
            its site-packages path. This is the only reliable way to get paths for an
            interpreter that isn't the currently running one.
            """
        try:
            cmd = [python_exe_path, '-c', "import sys; import json; print(json.dumps({'version': f'{sys.version_info.major}.{sys.version_info.minor}', 'prefix': sys.prefix}))"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
            interp_info = json.loads(result.stdout)
            version = interp_info['version']
            prefix = Path(interp_info['prefix'])
            site_packages = prefix / 'lib' / f'python{version}' / 'site-packages'
            return {'site_packages_path': str(site_packages), 'multiversion_base': str(site_packages / '.omnipkg_versions'), 'python_executable': python_exe_path}
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f'⚠️  Could not determine paths for interpreter {python_exe_path}: {e}')
            return None

    def _align_config_to_interpreter(self, python_exe_path_str: str):
        """
        Updates and saves config paths to match the specified Python executable
        by running it as a subprocess to get its true paths.
        """
        print(_('🔧 Aligning configuration to use Python interpreter: {}').format(python_exe_path_str))
        correct_paths = self._get_paths_for_interpreter(python_exe_path_str)
        if not correct_paths:
            print(f'❌ CRITICAL: Failed to determine paths for {python_exe_path_str}. Configuration not updated.')
            return
        print(_('   - New site-packages path: {}').format(correct_paths['site_packages_path']))
        print(_('   - New Python executable: {}').format(correct_paths['python_executable']))
        self.set('python_executable', correct_paths['python_executable'])
        self.set('site_packages_path', correct_paths['site_packages_path'])
        self.set('multiversion_base', correct_paths['multiversion_base'])
        self.config.update(correct_paths)
        self.multiversion_base = Path(self.config['multiversion_base'])
        print(_('   ✅ Configuration updated and saved successfully.'))

    def _get_venv_root(self) -> Path:
        """
        Reliably finds the root of the virtual environment.
        PRIORITY 1: Check for an override environment variable set during relaunch.
        PRIORITY 2: Search upwards for the pyvenv.cfg file.
        """
        # Priority 1: Check for the override variable set by the gatekeeper.
        venv_root_override = os.environ.get('OMNIPKG_VENV_ROOT')
        if venv_root_override:
            return Path(venv_root_override)

        # Priority 2: Fallback to searching for pyvenv.cfg for the initial run.
        current_dir = Path(sys.executable).resolve().parent
        while current_dir != current_dir.parent:
            if (current_dir / 'pyvenv.cfg').exists():
                return current_dir
            current_dir = current_dir.parent
        
        # Final fallback, should not be hit in a standard venv.
        return Path(sys.prefix)

    def _setup_native_311_environment(self):
        """
        Performs the one-time setup for an environment that already has Python 3.11.
        This primarily involves symlinking and registering the interpreter.
        This function runs AFTER self.config is loaded.
        """
        print('\n' + '=' * 60)
        print('  🚀 Finalizing Environment Setup for Python 3.11')
        print('=' * 60)
        print(_('✅ Detected a suitable Python 3.11 within your virtual environment.'))
        print('   - Registering it with omnipkg for future operations...')
        self._register_and_link_existing_interpreter(Path(sys.executable), f'{sys.version_info.major}.{sys.version_info.minor}')
        registered_311_path = self.get_interpreter_for_version('3.11')
        if registered_311_path:
            self._align_config_to_interpreter(str(registered_311_path))
        else:
            print(_('⚠️ Warning: Could not find registered Python 3.11 path after setup. Config may be incorrect.'))
        self.set('managed_python_setup_complete', True)
        print(_('\n✅ Environment setup is complete!'))

    def _load_path_registry(self):
        """Load path registry (placeholder for your path management)."""
        pass

    def _ensure_proper_registration(self):
        """
        Ensures the current Python 3.11 is properly registered even if already detected.
        """
        if sys.version_info[:2] == (3, 11):
            current_path = Path(sys.executable).resolve()
            registry_path = self.venv_path / '.omnipkg' / 'interpreters' / 'registry.json'
            needs_registration = True
            if registry_path.exists():
                try:
                    with open(registry_path, 'r') as f:
                        registry = json.load(f)
                    registered_311 = registry.get('interpreters', {}).get('3.11')
                    if registered_311 and Path(registered_311).resolve() == current_path:
                        needs_registration = False
                except:
                    pass
            if needs_registration:
                print(_('   - Registering current Python 3.11...'))
                self._register_all_interpreters(self.venv_path)

    def _register_and_link_existing_interpreter(self, interpreter_path: Path, version: str):
        """
        "Adopts" the native venv interpreter by creating a symlink to it inside
        the managed .omnipkg/interpreters directory. It then ensures the registry
        points to this new, centralized symlink.
        """
        print(_('   - Centralizing native Python {} via symlink...').format(version))
        managed_interpreters_dir = self.venv_path / '.omnipkg' / 'interpreters'
        managed_interpreters_dir.mkdir(parents=True, exist_ok=True)
        symlink_dir_name = f'cpython-{version}-venv-native'
        symlink_path = managed_interpreters_dir / symlink_dir_name
        target_for_symlink = interpreter_path.parent.parent
        if not symlink_path.exists():
            symlink_path.symlink_to(target_for_symlink, target_is_directory=True)
            print(_('   - ✅ Created symlink: {} -> {}').format(symlink_path, target_for_symlink))
        elif not (symlink_path.is_symlink() and os.readlink(str(symlink_path)) == str(target_for_symlink)):
            print(_('   - ⚠️  Correcting invalid symlink at {}...').format(symlink_path.name))
            if symlink_path.is_dir():
                shutil.rmtree(symlink_path)
            else:
                symlink_path.unlink()
            symlink_path.symlink_to(target_for_symlink, target_is_directory=True)
        else:
            print(_('   - ✅ Symlink already exists and is correct.'))
        self._register_all_interpreters(self.venv_path)

    def install_python311_in_venv(self):
        print(_('\n🚀 Upgrading environment to Python 3.11...'))
        venv_path = Path(sys.prefix)
        if venv_path == Path(sys.base_prefix):
            print(_('❌ Error: You must be in a virtual environment to use this feature.'))
            sys.exit(1)
        system = platform.system().lower()
        arch = platform.machine().lower()
        try:
            python311_exe = None
            try:
                python311_exe = self._install_managed_python(venv_path, '3.11.6')
            except (AttributeError, Exception) as e:
                print(_('Note: Falling back to platform-specific installation ({})').format(e))
                if system == 'linux':
                    python311_exe = self._install_python_platform(venv_path, arch, 'linux')
                elif system == 'darwin':
                    python311_exe = self._install_python_platform(venv_path, arch, 'macos')
                elif system == 'windows':
                    python311_exe = self._install_python_platform(venv_path, arch, 'windows')
                else:
                    raise OSError(_('Unsupported operating system: {}').format(system))
            if python311_exe and python311_exe.exists():
                self._update_venv_pyvenv_cfg(venv_path, python311_exe)
                print(_('✅ Python 3.11 downloaded and configured.'))
                self._finalize_environment_upgrade(venv_path, python311_exe)
                print(_('\n✅ Success! The environment is now fully upgraded to Python 3.11.'))
                print(' Your current command will now continue on the new version.')
                print('\n IMPORTANT: For the change to stick in your terminal for future commands, please run:')
                activate_script = venv_path / ('Scripts' if system == 'windows' else 'bin') / 'activate'
                print(_(' source "{}"').format(activate_script))
                print(_(' ...after this one finishes.'))
                args = [str(python311_exe), '-m', 'omnipkg.cli'] + sys.argv[1:]
                os.execv(str(python311_exe), args)
            else:
                raise Exception('Python 3.11 executable path was not determined after installation.')
        except Exception as e:
            print(_('❌ Failed to auto-upgrade to Python 3.11: {}').format(e))
            sys.exit(1)

    def _register_all_interpreters(self, venv_path: Path):
        """
        FIXED: Discovers and registers ONLY the Python interpreters that are explicitly
        managed within the .omnipkg/interpreters directory. This is the single
        source of truth for what is "swappable".
        """
        print(_('🔧 Registering all managed Python interpreters...'))
        managed_interpreters_dir = venv_path / '.omnipkg' / 'interpreters'
        managed_interpreters_dir.mkdir(parents=True, exist_ok=True)
        registry_path = managed_interpreters_dir / 'registry.json'
        
        interpreters = {}
        if not managed_interpreters_dir.is_dir():
            print("   ⚠️  Managed interpreters directory not found.")
            return

        for interp_dir in managed_interpreters_dir.iterdir():
            if not (interp_dir.is_dir() or interp_dir.is_symlink()):
                continue

            print(f"   -> Scanning directory: {interp_dir.name}")
            found_exe_path = None
            
            # Define potential paths and executable names to search for
            search_locations = [
                interp_dir / 'bin',
                interp_dir / 'Scripts', # For Windows
                interp_dir 
            ]
            possible_exe_names = [
                'python3.12', 'python3.11', 'python3.10', 'python3.9',
                'python3', 'python', 'python.exe'
            ]

            for location in search_locations:
                if location.is_dir():
                    for exe_name in possible_exe_names:
                        exe_path = location / exe_name
                        if exe_path.is_file() and os.access(exe_path, os.X_OK):
                            version_tuple = self._verify_python_version(str(exe_path))
                            if version_tuple:
                                found_exe_path = exe_path
                                print(f"      ✅ Found valid executable: {found_exe_path}")
                                break # Found it in this location
                if found_exe_path:
                    break # Found it in the search locations

            if found_exe_path:
                version_tuple = self._verify_python_version(str(found_exe_path))
                if version_tuple:
                    version_str = f'{version_tuple[0]}.{version_tuple[1]}'
                    interpreters[version_str] = str(found_exe_path.resolve())

        # Save the findings to the registry
        primary_version = '3.11' if '3.11' in interpreters else (sorted(interpreters.keys(), reverse=True)[0] if interpreters else None)
        registry_data = {
            'primary_version': primary_version,
            'interpreters': {k: v for k, v in interpreters.items()},
            'last_updated': datetime.now().isoformat()
        }
        with open(registry_path, 'w') as f:
            json.dump(registry_data, f, indent=4)

        if interpreters:
            print(_('   ✅ Registered {} managed Python interpreters.').format(len(interpreters)))
            for version, path in sorted(interpreters.items()):
                print(_('      - Python {}: {}').format(version, path))
        else:
            print("   ⚠️  No managed Python interpreters were found or could be registered.")

    def _find_existing_python311(self) -> Optional[Path]:
        """Checks if a managed Python 3.11 interpreter already exists."""
        venv_path = Path(sys.prefix)
        expected_exe_path = self._get_interpreter_dest_path(venv_path) / ('python.exe' if platform.system() == 'windows' else 'bin/python3.11')
        if expected_exe_path.exists() and expected_exe_path.is_file():
            print(_('✅ Found existing Python 3.11 interpreter.'))
            return expected_exe_path
        return None

    def get_interpreter_for_version(self, version: str) -> Optional[Path]:
        """Get the path to a specific Python interpreter version."""
        registry_path = Path(sys.prefix) / '.omnipkg' / 'interpreters' / 'registry.json'
        if not registry_path.exists():
            return None
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            interpreter_path = registry.get('interpreters', {}).get(version)
            if interpreter_path and Path(interpreter_path).exists():
                return Path(interpreter_path)
        except:
            pass
        return None

    # Fix 2: Improved _find_project_root() method
    def _find_project_root(self):
        """
        Find the project root directory by looking for setup.py, pyproject.toml, or .git
        """
        import os
        from pathlib import Path
        
        # Start from current working directory
        current_dir = Path.cwd()
        
        # Also check the directory where this module is located
        module_dir = Path(__file__).parent.parent
        
        # Check both locations
        search_paths = [current_dir, module_dir]
        
        for start_path in search_paths:
            # Walk up the directory tree
            for path in [start_path] + list(start_path.parents):
                # Look for project indicators
                project_files = [
                    'setup.py',
                    'pyproject.toml',
                    'setup.cfg',
                    '.git',
                    'omnipkg.egg-info'  # Specific to your project
                ]
                
                for project_file in project_files:
                    if (path / project_file).exists():
                        print(f"     (Found project root: {path})")
                        return path
        
        print("     (No project root found)")
        return None

    # Fix 3: Updated bootstrap method with better error handling
    def _install_essential_packages(self, python_exe: Path):
        """
        Installs essential packages for a new interpreter, including pip, Redis, and Safety.
        This ensures any interpreter managed by omnipkg is fully equipped from creation.
        """
        print('📦 Bootstrapping essential packages for new interpreter...')

        def run_verbose(cmd: List[str], error_msg: str):
            """Helper to run a command and show its output."""
            print(f"   🔩 Running: {' '.join(cmd)}")
            try:
                # Use check=True to automatically raise an exception on failure
                subprocess.run(
                    cmd, check=True, capture_output=True, text=True, timeout=300
                )
            except subprocess.CalledProcessError as e:
                print(f"   ❌ {error_msg}")
                print("   --- Stderr ---")
                print(e.stderr)
                print("   ----------------")
                raise  # Re-raise the exception to stop the process

        try:
            # STEP 1: Bootstrap pip, setuptools, and wheel
            print("   - Installing pip, setuptools, wheel...")
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as tmp_file:
                script_path = tmp_file.name
                with urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py') as response:
                    tmp_file.write(response.read().decode('utf-8'))
            pip_cmd = [str(python_exe), script_path, '--no-cache-dir', 'pip', 'setuptools', 'wheel']
            run_verbose(pip_cmd, "Failed to bootstrap pip.")
            os.unlink(script_path)
            print('   ✅ Pip bootstrap complete.')

            # STEP 2: Install critical prerequisite (Redis)
            print("   - Installing Redis client...")
            run_verbose([str(python_exe), '-m', 'pip', 'install', '--no-cache-dir', 'redis'], "Failed to install Redis.")
            print('   ✅ Redis client installed.')

            # STEP 3: Install security audit toolkit (safety)
            print("   - Installing security audit toolkit (safety)...")
            run_verbose([str(python_exe), '-m', 'pip', 'install', '--no-cache-dir', 'safety'], "Failed to install safety.")
            print('   ✅ Security toolkit installed.')

            # STEP 4: Install omnipkg itself into the new environment
            print("   - Installing omnipkg...")
            project_root = self._find_project_root()
            if project_root:
                print("     (Developer mode detected: performing editable install)")
                install_cmd = [str(python_exe), '-m', 'pip', 'install', '--no-cache-dir', '-e', str(project_root)]
            else:
                print("     (Standard mode detected: installing from PyPI)")
                install_cmd = [str(python_exe), '-m', 'pip', 'install', '--no-cache-dir', 'omnipkg']
            run_verbose(install_cmd, "Failed to install omnipkg.")
            print('   ✅ omnipkg installed.')

            # STEP 5: Pre-populate the config for the new environment to prevent interactive setup
            print("   - Pre-configuring new environment in config file...")
            new_env_prefix = python_exe.parent.parent
            new_env_id = hashlib.md5(str(new_env_prefix.resolve()).encode()).hexdigest()[:8]
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
            full_config['environments'][new_env_id] = self.config.copy()
            with open(self.config_path, 'w') as f:
                json.dump(full_config, f, indent=4)
            print(f"   ✅ Configuration for new environment (ID: {new_env_id}) saved.")

            # STEP 6: Use the new omnipkg to install its remaining dependencies for proper tracking
            core_deps = _get_core_dependencies()  # This returns a set now
            core_deps.discard('redis')      # Remove already installed packages
            core_deps.discard('omnipkg')
            core_deps.discard('safety')

            if core_deps:
                deps_list = sorted(list(core_deps))
                print(f'   - Tracking {len(deps_list)} remaining core dependencies...')
                deps_cmd = [str(python_exe), '-m', 'omnipkg.cli', 'install'] + deps_list
                run_verbose(deps_cmd, "Failed to install remaining core dependencies.")
                print('   ✅ All core dependencies installed and tracked.')

        except Exception as e:
            print(f'❌ A critical error occurred during the bootstrap process: {e}')
            raise
     
    def _create_omnipkg_executable(self, new_python_exe: Path, venv_path: Path):
        """
        Creates a proper shell script executable that forces the use of the new Python interpreter.
        """
        print(_('🔧 Creating new omnipkg executable...'))
        bin_dir = venv_path / ('Scripts' if platform.system() == 'Windows' else 'bin')
        omnipkg_exec_path = bin_dir / 'omnipkg'
        system = platform.system().lower()
        if system == 'windows':
            script_content = f'@echo off\nREM This script was auto-generated by omnipkg to ensure the correct Python is used.\n"{new_python_exe.resolve()}" -m omnipkg.cli %*\n'
            omnipkg_exec_path = bin_dir / 'omnipkg.bat'
        else:
            script_content = f'#!/bin/bash\n# This script was auto-generated by omnipkg to ensure the correct Python is used.\n\nexec "{new_python_exe.resolve()}" -m omnipkg.cli "$@"\n'
        with open(omnipkg_exec_path, 'w') as f:
            f.write(script_content)
        if system != 'windows':
            omnipkg_exec_path.chmod(493)
        print(_('   ✅ New omnipkg executable created.'))

    def _update_default_python_links(self, venv_path: Path, new_python_exe: Path):
        """Updates the default python/python3 symlinks to point to Python 3.11."""
        print(_('🔧 Updating default Python links...'))
        bin_dir = venv_path / ('Scripts' if platform.system() == 'Windows' else 'bin')
        if platform.system() == 'Windows':
            for name in ['python.exe', 'python3.exe']:
                target = bin_dir / name
                if target.exists():
                    target.unlink()
                shutil.copy2(new_python_exe, target)
        else:
            for name in ['python', 'python3']:
                target = bin_dir / name
                if target.exists() or target.is_symlink():
                    target.unlink()
                target.symlink_to(new_python_exe)
        version_tuple = self._verify_python_version(str(new_python_exe))
        version_str = f'{version_tuple[0]}.{version_tuple[1]}' if version_tuple else 'the new version'
        print(_('   ✅ Default Python links updated to use Python {}.').format(version_str))

    def _auto_register_original_python(self, venv_path: Path) -> None:
        """
        Automatically detects and registers the original Python interpreter that was
        used to create this environment, without moving or copying it.
        """
        print("🔍 Auto-detecting original Python interpreter...")
        
        # Get the current Python executable info
        current_exe = Path(sys.executable).resolve()
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        print(f"   - Detected: Python {current_version} at {current_exe}")
        
        # Check if it's already registered
        interpreters_dir = venv_path / '.omnipkg' / 'interpreters'
        registry_path = venv_path / '.omnipkg' / 'python_registry.json'
        
        # Load existing registry
        registry = {}
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
            except Exception as e:
                print(f"   ⚠️  Warning: Could not load registry: {e}")
                registry = {}
        
        # Check if this version is already registered
        if major_minor in registry:
            print(f"   ✅ Python {major_minor} already registered at: {registry[major_minor]['path']}")
            return
        
        # Create the managed interpreter directory structure
        managed_name = f"original-{current_version}"
        managed_dir = interpreters_dir / managed_name
        managed_dir.mkdir(parents=True, exist_ok=True)
        
        # Create bin directory for symlinks
        bin_dir = managed_dir / 'bin'
        bin_dir.mkdir(exist_ok=True)
        
        # Create symlinks to the original interpreter
        original_links = [
            ('python', current_exe),
            (f'python{sys.version_info.major}', current_exe),
            (f'python{major_minor}', current_exe)
        ]
        
        print(f"   📝 Registering Python {major_minor} (original) without copying...")
        
        for link_name, target in original_links:
            link_path = bin_dir / link_name
            if link_path.exists():
                link_path.unlink()
            try:
                link_path.symlink_to(target)
                print(f"      ✅ Created symlink: {link_name} -> {target}")
            except Exception as e:
                print(f"      ⚠️  Could not create symlink {link_name}: {e}")
        
        # Also symlink pip if it exists
        pip_candidates = [
            current_exe.parent / 'pip',
            current_exe.parent / f'pip{sys.version_info.major}',
            current_exe.parent / f'pip{major_minor}'
        ]
        
        for pip_path in pip_candidates:
            if pip_path.exists():
                pip_link = bin_dir / pip_path.name
                if not pip_link.exists():
                    try:
                        pip_link.symlink_to(pip_path)
                        print(f"      ✅ Created pip symlink: {pip_path.name}")
                        break
                    except Exception as e:
                        print(f"      ⚠️  Could not create pip symlink: {e}")
        
        # Update the registry
        registry[major_minor] = {
            'path': str(bin_dir / f'python{major_minor}'),
            'version': current_version,
            'type': 'original',  # Mark as original, not downloaded
            'source': str(current_exe),
            'managed_dir': str(managed_dir),
            'registered_at': datetime.now().isoformat()
        }
        
        # Save updated registry
        try:
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            print(f"   ✅ Registered Python {major_minor} in registry")
        except Exception as e:
            print(f"   ❌ Failed to save registry: {e}")
            return
        
        # Update the main config to know about this interpreter
        if hasattr(self, 'config') and self.config:
            managed_interpreters = self.config.get('managed_interpreters', {})
            managed_interpreters[major_minor] = str(bin_dir / f'python{major_minor}')
            self.set('managed_interpreters', managed_interpreters)
            print(f"   ✅ Updated main config with Python {major_minor}")

    def _should_auto_register_python(self, version: str) -> bool:
        """
        Determines if we should auto-register the original Python instead of downloading.
        """
        major_minor = '.'.join(version.split('.')[:2])
        current_major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        # If the requested version matches the current running Python, auto-register it
        return major_minor == current_major_minor

    def _enhanced_python_adopt(self, version: str) -> int:
        """
        Enhanced adoption logic that prioritizes registering the original interpreter
        when appropriate, falling back to download only when necessary.
        """
        print(f"🐍 Attempting to adopt Python {version} into the environment...")
        
        # First, check if we should auto-register the current Python
        if self._should_auto_register_python(version):
            print(f"   🎯 Requested version matches current Python {sys.version_info.major}.{sys.version_info.minor}")
            print("   📋 Auto-registering current interpreter instead of downloading...")
            
            try:
                self._auto_register_original_python(self.venv_path)
                print(f"🎉 Successfully registered Python {version} (original interpreter)!")
                print(f"   You can now use 'omnipkg swap python {version}'")
                return 0
            except Exception as e:
                print(f"   ❌ Auto-registration failed: {e}")
                print("   🔄 Falling back to download strategy...")
        
        # If auto-registration isn't applicable or failed, proceed with existing logic
        # (discovery, adoption from other locations, or download)
        return self._existing_adopt_logic(version)

    def _register_all_managed_interpreters(self) -> None:
        """
        Enhanced version that includes original interpreters in the scan.
        """
        print("🔧 Registering all managed Python interpreters...")
        
        interpreters_dir = self.venv_path / '.omnipkg' / 'interpreters'
        if not interpreters_dir.exists():
            print("   ℹ️  No interpreters directory found.")
            return
        
        registry_path = self.venv_path / '.omnipkg' / 'python_registry.json'
        registry = {}
        
        # Load existing registry to preserve metadata
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
            except Exception:
                registry = {}
        
        managed_interpreters = {}
        
        for interpreter_dir in interpreters_dir.iterdir():
            if not interpreter_dir.is_dir():
                continue
                
            print(f"   -> Scanning directory: {interpreter_dir.name}")
            
            # Look for Python executables in bin/ subdirectory
            bin_dir = interpreter_dir / 'bin'
            if not bin_dir.exists():
                print(f"      ⚠️  No bin/ directory found in {interpreter_dir.name}")
                continue
            
            # Find versioned Python executable
            python_exe = None
            for candidate in bin_dir.glob('python[0-9].[0-9]*'):
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    python_exe = candidate
                    break
            
            if not python_exe:
                print(f"      ⚠️  No valid Python executable found in {interpreter_dir.name}")
                continue
            
            # Extract version from executable name or by running it
            try:
                result = subprocess.run([str(python_exe), '--version'], 
                                    capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Parse "Python X.Y.Z" output
                    version_match = re.search(r'Python (\d+\.\d+)', result.stdout)
                    if version_match:
                        major_minor = version_match.group(1)
                        managed_interpreters[major_minor] = str(python_exe)
                        
                        # Preserve or create registry entry
                        if major_minor not in registry:
                            registry[major_minor] = {
                                'path': str(python_exe),
                                'type': 'downloaded' if 'cpython-' in interpreter_dir.name else 'original',
                                'managed_dir': str(interpreter_dir),
                                'registered_at': datetime.now().isoformat()
                            }
                        
                        interpreter_type = registry[major_minor].get('type', 'unknown')
                        print(f"      ✅ Found valid executable: {python_exe} ({interpreter_type})")
                    else:
                        print(f"      ⚠️  Could not parse version from: {result.stdout.strip()}")
                else:
                    print(f"      ⚠️  Failed to get version: {result.stderr.strip()}")
            except Exception as e:
                print(f"      ⚠️  Error testing executable: {e}")
        
        # Save updated registry
        try:
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            print(f"   ⚠️  Could not save registry: {e}")
        
        # Update main config
        if managed_interpreters:
            self.set('managed_interpreters', managed_interpreters)
            print(f"   ✅ Registered {len(managed_interpreters)} managed Python interpreters.")
            for version, path in managed_interpreters.items():
                interpreter_type = registry.get(version, {}).get('type', 'unknown')
                print(f"      - Python {version}: {path} ({interpreter_type})")
        else:
            print("   ℹ️  No managed interpreters found.")

    def _install_managed_python(self, venv_path: Path, full_version: str) -> Path:
        """
        Downloads and installs a specific, self-contained version of Python
        from the python-build-standalone project. Returns the path to the new executable.
        """
        print(_('\n🚀 Installing managed Python {}...').format(full_version))
        system = platform.system().lower()
        arch = platform.machine().lower()
        py_arch_map = {'x86_64': 'x86_64', 'amd64': 'x86_64', 'aarch64': 'aarch64', 'arm64': 'aarch64'}
        py_arch = py_arch_map.get(arch)
        if not py_arch:
            raise OSError(_('Unsupported architecture: {}').format(arch))
        VERSION_TO_RELEASE_TAG_MAP = {'3.12.3': '20240415', '3.11.6': '20231002', '3.10.13': '20231002', '3.9.18': '20231002'}
        release_tag = VERSION_TO_RELEASE_TAG_MAP.get(full_version)
        if not release_tag:
            raise ValueError(f'No known standalone build for Python version {full_version}. Cannot download.')
        py_ver_plus_tag = f'{full_version}+{release_tag}'
        base_url = f'https://github.com/indygreg/python-build-standalone/releases/download/{release_tag}'
        archive_name_templates = {'linux': f'cpython-{py_ver_plus_tag}-{py_arch}-unknown-linux-gnu-install_only.tar.gz', 'macos': f'cpython-{py_ver_plus_tag}-{py_arch}-apple-darwin-install_only.tar.gz', 'windows': f'cpython-{py_ver_plus_tag}-{py_arch}-pc-windows-msvc-shared-install_only.tar.gz'}
        archive_name = archive_name_templates.get(system)
        if not archive_name:
            raise OSError(_('Unsupported operating system: {}').format(system))
        url = f'{base_url}/{archive_name}'
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / archive_name
            print(f'📥 Downloading Python {full_version} for {system.title()}...')
            print(_('   - URL: {}').format(url))
            try:
                urllib.request.urlretrieve(url, archive_path)
                if not archive_path.exists() or archive_path.stat().st_size < 1000000:
                    raise OSError(_('Failed to download or file is too small: {}').format(archive_path))
                print(_('✅ Downloaded {} bytes').format(archive_path.stat().st_size))
                with tarfile.open(archive_path, 'r:gz') as tar:
                    extract_path = Path(temp_dir) / 'extracted'
                    extract_path.mkdir(exist_ok=True)
                    tar.extractall(extract_path)
                source_python_dir = extract_path / 'python'
                if not source_python_dir.is_dir():
                    raise OSError(_("No 'python' directory found in extracted archive"))
                python_dest = venv_path / '.omnipkg' / 'interpreters' / f'cpython-{full_version}'
                python_dest.parent.mkdir(parents=True, exist_ok=True)
                print(_('   - Installing to: {}').format(python_dest))
                shutil.copytree(source_python_dir, python_dest, dirs_exist_ok=True)
                python_exe = python_dest / ('python.exe' if system == 'windows' else 'bin/python3')
                if not python_exe.exists():
                    python_exe = python_dest / ('python.exe' if system == 'windows' else 'bin/python')
                if not python_exe.exists():
                    raise OSError(_('Python executable not found in expected location: {}').format(python_exe.parent))
                if system != 'windows':
                    python_exe.chmod(493)
                    major_minor = '.'.join(full_version.split('.')[:2])
                    versioned_symlink = python_exe.parent / f'python{major_minor}'
                    if not versioned_symlink.exists():
                        versioned_symlink.symlink_to(python_exe.name)
                result = subprocess.run([str(python_exe), '--version'], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    raise OSError(_('Python executable test failed: {}').format(result.stderr))
                print(_('✅ Python installation verified: {}').format(result.stdout.strip()))
                self._install_essential_packages(python_exe)

                # --- ENHANCED FIX: CONTEXT-AWARE KNOWLEDGE BASE REBUILD ---
                print("\n✨ New interpreter bootstrapped. Building its Knowledge Base...")
                
                # Store current context for restoration
                current_python_exe = self.config.get('python_executable')
                
                # Temporarily switch context to the new interpreter for KB rebuild
                major_minor = '.'.join(full_version.split('.')[:2])
                print(f"   🔄 Temporarily switching context to Python {major_minor} for KB rebuild...")
                
                # Update config to point to the new interpreter
                self.set('python_executable', str(python_exe))
                
                try:
                    # Use the new interpreter's context to rebuild the KB
                    rebuild_cmd = [str(python_exe), "-m", "omnipkg.cli", "rebuild-kb", "--force"]
                    
                    # Set up environment for the new interpreter
                    env = os.environ.copy()
                    env['OMNIPKG_PYTHON_EXE'] = str(python_exe)
                    
                    subprocess.run(rebuild_cmd, check=True, capture_output=True, text=True, timeout=300, env=env)
                    print("   ✅ Knowledge Base for the new environment is ready.")
                    
                except subprocess.CalledProcessError as e:
                    print("   ⚠️  KB rebuild failed, attempting recovery...")
                    print(f"      Error: {e.stderr}")
                    
                    # Try a more robust rebuild approach
                    try:
                        # First, try to clean any corrupted state
                        cleanup_cmd = [str(python_exe), "-m", "omnipkg.cli", "reset", "--yes"]
                        subprocess.run(cleanup_cmd, check=True, capture_output=True, text=True, timeout=60, env=env)
                        print("   🧹 Cleaned potentially corrupted KB state.")
                        
                        # Now attempt rebuild again
                        subprocess.run(rebuild_cmd, check=True, capture_output=True, text=True, timeout=300, env=env)
                        print("   ✅ Knowledge Base recovered and rebuilt successfully.")
                        
                    except subprocess.CalledProcessError as recovery_error:
                        print("   ❌ KB rebuild recovery also failed.")
                        print(f"      Recovery error: {recovery_error.stderr}")
                        # Don't fail the entire operation, just warn
                        print("   ⚠️  Proceeding without KB - you may need to run 'omnipkg rebuild-kb' later")
                        
                finally:
                    # Always restore the original context
                    if current_python_exe:
                        print(f"   🔄 Restoring original Python context...")
                        self.set('python_executable', current_python_exe)
                    else:
                        print("   ℹ️  No previous Python context to restore.")
                
                # --- END ENHANCED FIX ---
                
                return python_exe
                
            except Exception as e:
                raise OSError(_('Failed to download or extract Python: {}').format(e))

    def _update_venv_pyvenv_cfg(self, venv_path, python311_exe):
        pyvenv_cfg = venv_path / 'pyvenv.cfg'
        if pyvenv_cfg.exists():
            with open(pyvenv_cfg, 'r') as f:
                lines = f.readlines()
            with open(pyvenv_cfg, 'w') as f:
                for line in lines:
                    if line.startswith('home = '):
                        f.write(f'home = {python311_exe.parent.resolve()}\n')
                    elif line.startswith('executable = '):
                        f.write(f'executable = {python311_exe.resolve()}\n')
                    else:
                        f.write(line)

    def _find_python_interpreters(self) -> Dict[Tuple[int, int], str]:
        """
        Discovers all available Python interpreters on the system.
        Returns a dict mapping (major, minor) version tuples to executable paths.
        """
        if self._python_cache:
            return self._python_cache
        interpreters = {}
        search_patterns = ['python{}.{}', 'python{}{}']
        search_paths = []
        if 'PATH' in os.environ:
            search_paths.extend(os.environ['PATH'].split(os.pathsep))
        common_paths = ['/usr/bin', '/usr/local/bin', '/opt/python*/bin', str(Path.home() / '.pyenv' / 'versions' / '*' / 'bin'), '/usr/local/opt/python@*/bin', 'C:\\Python*', 'C:\\Users\\*\\AppData\\Local\\Programs\\Python\\Python*']
        search_paths.extend(common_paths)
        current_python_dir = Path(sys.executable).parent
        search_paths.append(str(current_python_dir))
        for path_str in search_paths:
            try:
                if '*' in path_str:
                    from glob import glob
                    expanded_paths = glob(path_str)
                    for expanded_path in expanded_paths:
                        if Path(expanded_path).is_dir():
                            search_paths.append(expanded_path)
                    continue
                path = Path(path_str)
                if not path.exists() or not path.is_dir():
                    continue
                for major in range(3, 4):
                    for minor in range(6, 15):
                        for pattern in search_patterns:
                            exe_name = pattern.format(major, minor)
                            exe_path = path / exe_name
                            if platform.system() == 'Windows':
                                exe_path_win = path / f'{exe_name}.exe'
                                if exe_path_win.exists():
                                    exe_path = exe_path_win
                            if exe_path.exists() and exe_path.is_file():
                                version = self._verify_python_version(str(exe_path))
                                if version and version not in interpreters:
                                    interpreters[version] = str(exe_path)
                        for generic_name in ['python', 'python3']:
                            exe_path = path / generic_name
                            if platform.system() == 'Windows':
                                exe_path = path / f'{generic_name}.exe'
                            if exe_path.exists() and exe_path.is_file():
                                version = self._verify_python_version(str(exe_path))
                                if version and version not in interpreters:
                                    interpreters[version] = str(exe_path)
            except (OSError, PermissionError):
                continue
        current_version = sys.version_info[:2]
        interpreters[current_version] = sys.executable
        self._python_cache = interpreters
        return interpreters
        
    def find_true_venv_root(self) -> Path:
        """
        Helper to find the true venv root by looking for pyvenv.cfg,
        which is reliable across different Python interpreters within the same venv.
        """
        current_path = Path(sys.executable).resolve()
        while current_path != current_path.parent:
            if (current_path / 'pyvenv.cfg').exists():
                return current_path
        return Path(sys.prefix) # Fallback

    def _verify_python_version(self, python_path: str) -> Optional[Tuple[int, int]]:
        """
        Verify that a Python executable works and get its version.
        Returns (major, minor) tuple or None if invalid.
        """
        try:
            result = subprocess.run([python_path, '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                major, minor = map(int, version_str.split('.'))
                return (major, minor)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, OSError):
            pass
        return None

    def get_best_python_for_version_range(self, min_version: Tuple[int, int]=None, max_version: Tuple[int, int]=None, preferred_version: Tuple[int, int]=None) -> Optional[str]:
        """Find the best Python interpreter for a given version range."""
        interpreters = self._find_python_interpreters()
        if not interpreters:
            return None
        candidates = {}
        for version, path in interpreters.items():
            if min_version and version < min_version:
                continue
            if max_version and version > max_version:
                continue
            candidates[version] = path
        if not candidates:
            return None
        if preferred_version and preferred_version in candidates:
            return candidates[preferred_version]
        if self._preferred_version in candidates:
            return candidates[self._preferred_version]
        best_version = max(candidates.keys())
        return candidates[best_version]

    def _get_bin_paths(self) -> List[str]:
        """Gets a list of standard binary paths to search for executables."""
        paths = set()
        paths.add(str(Path(sys.executable).parent))
        for path in ['/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin']:
            if Path(path).exists():
                paths.add(path)
        return sorted(list(paths))

    def _get_system_lang_code(self):
        """Helper to get a valid system language code."""
        try:
            lang_code = sys_locale.getlocale()[0]
            if lang_code and '_' in lang_code:
                lang_code = lang_code.split('_')[0]
            return lang_code or 'en'
        except Exception:
            return 'en'

# In omnipkg/core.py - Replace the _get_sensible_defaults method

    def _get_sensible_defaults(self) -> Dict:
        """
        Generates sensible default configuration paths based STRICTLY on the
        currently active virtual environment to ensure safety and prevent permission errors.
        """
        print('💡 Grounding configuration in the current active environment...')
        
        # FIX: Unconditionally use the active environment's Python (`sys.executable`).
        # This is the single most important change to prevent permission errors.
        active_python_exe = sys.executable 
        
        print(_('   ✅ Using: {} (Your active interpreter)').format(active_python_exe))
        
        calculated_paths = self._get_paths_for_interpreter(active_python_exe)
        
        if not calculated_paths:
            print(_('   ⚠️  Falling back to basic path detection within the current environment.'))
            site_packages = str(self._get_actual_current_site_packages())
            calculated_paths = {
                'site_packages_path': site_packages, 
                'multiversion_base': str(Path(site_packages) / '.omnipkg_versions'), 
                'python_executable': sys.executable
            }
        
        return {
            **calculated_paths, 
            'python_interpreters': self.list_available_pythons() or {},  # <- FIXED: Added fallback
            'preferred_python_version': f'{self._preferred_version[0]}.{self._preferred_version[1]}', 
            'builder_script_path': str(Path(__file__).parent / 'package_meta_builder.py'), 
            'redis_host': 'localhost', 
            'redis_port': 6379, 
            'redis_key_prefix': 'omnipkg:pkg:', 
            'install_strategy': 'stable-main', 
            'uv_executable': 'uv', 
            'paths_to_index': self._get_bin_paths(), 
            'language': self._get_system_lang_code(), 
            'enable_python_hotswap': True
        }

    def _get_actual_current_site_packages(self) -> Path:
        """
        Gets the ACTUAL site-packages directory for the currently running Python interpreter.
        This is more reliable than calculating it from sys.prefix when hotswapping is involved.
        """
        import site
        try:
            site_packages_list = site.getsitepackages()
            if site_packages_list:
                current_python_dir = Path(sys.executable).parent.parent
                for sp in site_packages_list:
                    sp_path = Path(sp)
                    try:
                        sp_path.relative_to(current_python_dir)
                        return sp_path
                    except ValueError:
                        continue
                return Path(site_packages_list[0])
        except:
            pass
        python_version = f'python{sys.version_info.major}.{sys.version_info.minor}'
        current_python_path = Path(sys.executable)
        if '.omnipkg/interpreters' in str(current_python_path):
            interpreter_root = current_python_path.parent.parent
            site_packages_path = interpreter_root / 'lib' / python_version / 'site-packages'
        else:
            venv_path = Path(sys.prefix)
            site_packages_path = venv_path / 'lib' / python_version / 'site-packages'
        return site_packages_path

    def list_available_pythons(self) -> Dict[str, str]:
        """
        List all available Python interpreters with their versions.
        FIXED: Prioritize actual interpreters over symlinks, show hotswapped paths correctly.
        """
        interpreters = self._find_python_interpreters()
        result = {}
        for (major, minor), path in sorted(interpreters.items()):
            version_key = f'{major}.{minor}'
            path_obj = Path(path)
            if version_key in result:
                existing_path = Path(result[version_key])
                current_is_hotswapped = '.omnipkg/interpreters' in str(path_obj)
                existing_is_hotswapped = '.omnipkg/interpreters' in str(existing_path)
                current_is_versioned = f'python{major}.{minor}' in path_obj.name
                existing_is_versioned = f'python{major}.{minor}' in existing_path.name
                if current_is_hotswapped and (not existing_is_hotswapped):
                    result[version_key] = str(path)
                elif existing_is_hotswapped and (not current_is_hotswapped):
                    continue
                elif current_is_versioned and (not existing_is_versioned):
                    result[version_key] = str(path)
                elif existing_is_versioned and (not current_is_versioned):
                    continue
                elif len(str(path)) > len(str(existing_path)):
                    result[version_key] = str(path)
            else:
                result[version_key] = str(path)
        return result

    def _first_time_setup(self, interactive=True) -> Dict:
        """Interactive setup for the first time the tool is run."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        defaults = self._get_sensible_defaults()
        final_config = defaults.copy()
        if interactive:
            print(_("🌍 Welcome to omnipkg! Let's get you configured."))
            print('-' * 60)
            available_pythons = defaults['python_interpreters']
            if len(available_pythons) > 1:
                print(_('🐍 Discovered Python interpreters:'))
                for version, path in available_pythons.items():
                    marker = ' ⭐' if version == defaults['preferred_python_version'] else ''
                    print(_('   Python {}: {}{}').format(version, path, marker))
                print()
            print('Auto-detecting paths for your environment. Press Enter to accept defaults.\n')
            print(_('📦 Choose your default installation strategy:'))
            print(_('   1) stable-main:  Prioritize a stable main environment. (Recommended)'))
            print(_('   2) latest-active: Prioritize having the latest versions active.'))
            strategy = input(_('   Enter choice (1 or 2) [1]: ')).strip() or '1'
            final_config['install_strategy'] = 'stable-main' if strategy == '1' else 'latest-active'
            bubble_path = input(f"Path for version bubbles [{defaults['multiversion_base']}]: ").strip() or defaults['multiversion_base']
            final_config['multiversion_base'] = bubble_path
            python_path = input(_('Python executable path [{}]: ').format(defaults['python_executable'])).strip() or defaults['python_executable']
            final_config['python_executable'] = python_path
            while True:
                host_input = input(_('Redis host [{}]: ').format(defaults['redis_host'])) or defaults['redis_host']
                try:
                    # Use a socket to test if the hostname is valid before saving it
                    import socket
                    socket.gethostbyname(host_input)
                    final_config['redis_host'] = host_input
                    break # Exit loop if valid
                except socket.gaierror:
                    print(_("   ❌ Error: Invalid hostname '{}'. Please try again.").format(host_input))
            final_config['redis_port'] = int(input(_('Redis port [{}]: ').format(defaults['redis_port'])) or defaults['redis_port'])
            hotswap_choice = input(_('Enable Python interpreter hotswapping? (y/n) [y]: ')).strip().lower()
            final_config['enable_python_hotswap'] = hotswap_choice != 'n'
        try:
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            full_config = {'environments': {}}
        if 'environments' not in full_config:
            full_config['environments'] = {}
        full_config['environments'][self.env_id] = final_config
        with open(self.config_path, 'w') as f:
            json.dump(full_config, f, indent=4)
        if interactive:
            print(_('\n✅ Configuration saved to {}.').format(self.config_path))
            print(_('   You can edit this file manually later.'))
        rebuild_cmd = [str(python_path), "-m", "omnipkg.cli", "reset", "-y"]
        subprocess.run(rebuild_cmd, check=True, capture_output=True, text=True)
        return final_config

    def _load_or_create_env_config(self) -> Dict:
        """
        Loads the config for the current environment from the global config file.
        If the environment is not registered, triggers the interactive first-time setup for it.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        full_config = {'environments': {}}
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    full_config = json.load(f)
                if 'environments' not in full_config:
                    full_config['environments'] = {}
            except json.JSONDecodeError:
                print(_('⚠️ Warning: Global config file is corrupted. Starting fresh.'))
        if self.env_id in full_config['environments']:
            return full_config['environments'][self.env_id]
        else:
            print(_('👋 New environment detected (ID: {}). Starting first-time setup.').format(self.env_id))
            return self._first_time_setup(interactive=True)

    def get(self, key, default=None):
        """Get a configuration value, with an optional default."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a configuration value for the current environment and save."""
        self.config[key] = value
        try:
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            full_config = {'environments': {}}
        if 'environments' not in full_config:
            full_config['environments'] = {}
        full_config['environments'][self.env_id] = self.config
        with open(self.config_path, 'w') as f:
            json.dump(full_config, f, indent=4)

class InterpreterManager:
    """
    Manages multiple Python interpreters within the same environment.
    Provides methods to switch between interpreters and run commands with specific versions.
    """

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.venv_path = Path(sys.prefix)

    def list_available_interpreters(self) -> Dict[str, Path]:
        """Returns a dict of version -> path for all available interpreters."""
        registry_path = self.venv_path / '.omnipkg' / 'interpreters' / 'registry.json'
        if not registry_path.exists():
            return {}
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            interpreters = {}
            for version, path_str in registry.get('interpreters', {}).items():
                path = Path(path_str)
                if path.exists():
                    interpreters[version] = path
            return interpreters
        except:
            return {}

    def run_with_interpreter(self, version: str, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run a command with a specific Python interpreter version."""
        interpreter_path = self.config_manager.get_interpreter_for_version(version)
        if not interpreter_path:
            raise ValueError(_('Python {} interpreter not found').format(version))
        full_cmd = [str(interpreter_path)] + cmd
        return subprocess.run(full_cmd, capture_output=True, text=True)

    def install_package_with_version(self, package: str, python_version: str):
        """Install a package using a specific Python version."""
        interpreter_path = self.config_manager.get_interpreter_for_version(python_version)
        if not interpreter_path:
            raise ValueError(_('Python {} interpreter not found').format(python_version))
        cmd = [str(interpreter_path), '-m', 'pip', 'install', package]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f'Failed to install {package} with Python {python_version}: {result.stderr}')
        return result

class BubbleIsolationManager:

    def __init__(self, config: Dict, parent_omnipkg):
        self.config = config
        self.parent_omnipkg = parent_omnipkg
        self.site_packages = Path(config['site_packages_path'])
        self.multiversion_base = Path(config['multiversion_base'])
        self.file_hash_cache = {}
        self.package_path_registry = {}
        self.registry_lock = FileLock(self.multiversion_base / 'registry.lock')
        self._load_path_registry()
        self.http_session = http_requests.Session()

    def _load_path_registry(self):
        """Load the file path registry from JSON."""
        if not hasattr(self, 'multiversion_base'):
            return
        registry_file = self.multiversion_base / 'package_paths.json'
        if registry_file.exists():
            with self.registry_lock:
                try:
                    with open(registry_file, 'r') as f:
                        self.package_path_registry = json.load(f)
                except Exception:
                    print(_('    ⚠️ Warning: Failed to load path registry, starting fresh.'))
                    self.package_path_registry = {}

    def _save_path_registry(self):
        """Save the file path registry to JSON with atomic write."""
        registry_file = self.multiversion_base / 'package_paths.json'
        with self.registry_lock:
            temp_file = registry_file.with_suffix(f'{registry_file.suffix}.tmp')
            try:
                registry_file.parent.mkdir(parents=True, exist_ok=True)
                with open(temp_file, 'w') as f:
                    json.dump(self.package_path_registry, f, indent=2)
                os.rename(temp_file, registry_file)
            finally:
                if temp_file.exists():
                    temp_file.unlink()

    def _register_file(self, file_path: Path, pkg_name: str, version: str, file_type: str, bubble_path: Path):
        """Register a file in the registry."""
        file_hash = self._get_file_hash(file_path)
        path_str = str(file_path)
        c_name = pkg_name.lower().replace('_', '-')
        if c_name not in self.package_path_registry:
            self.package_path_registry[c_name] = {}
        if version not in self.package_path_registry[c_name]:
            self.package_path_registry[c_name][version] = []
        self.package_path_registry[c_name][version].append({'path': path_str, 'hash': file_hash, 'type': file_type, 'bubble_path': str(bubble_path)})
        self._save_path_registry()

    def create_isolated_bubble(self, package_name: str, target_version: str) -> bool:
        print(_('🫧 Creating isolated bubble for {} v{}').format(package_name, target_version))
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            if not self._install_exact_version_tree(package_name, target_version, temp_path):
                return False
            installed_tree = self._analyze_installed_tree(temp_path)
            bubble_path = self.multiversion_base / f'{package_name}-{target_version}'
            if bubble_path.exists():
                shutil.rmtree(bubble_path)
            return self._create_deduplicated_bubble(installed_tree, bubble_path, temp_path)

    def _install_exact_version_tree(self, package_name: str, version: str, target_path: Path) -> bool:
        try:
            historical_deps = self._get_historical_dependencies(package_name, version)
            install_specs = ['{}=={}'.format(package_name, version)] + historical_deps
            cmd = [self.config['python_executable'], '-m', 'pip', 'install', '--target', str(target_path)] + install_specs
            print(_('    📦 Installing full dependency tree to temporary location...'))
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(_('    ❌ Failed to install exact version tree: {}').format(result.stderr))
                return False
            return True
        except Exception as e:
            print(_('    ❌ Unexpected error during installation: {}').format(e))
            return False

    def _get_historical_dependencies(self, package_name: str, version: str) -> List[str]:
        print(_('    -> Trying strategy 1: pip dry-run...'))
        deps = self._try_pip_dry_run(package_name, version)
        if deps is not None:
            print(_('    ✅ Success: Dependencies resolved via pip dry-run.'))
            return deps
        print(_('    -> Trying strategy 2: PyPI API...'))
        deps = self._try_pypi_api(package_name, version)
        if deps is not None:
            print(_('    ✅ Success: Dependencies resolved via PyPI API.'))
            return deps
        print(_('    -> Trying strategy 3: pip show fallback...'))
        deps = self._try_pip_show_fallback(package_name, version)
        if deps is not None:
            print(_('    ✅ Success: Dependencies resolved from existing installation.'))
            return deps
        print(_('    ⚠️ All dependency resolution strategies failed for {}=={}.').format(package_name, version))
        print(_('    ℹ️  Proceeding with full temporary installation to build bubble.'))
        return []

    def _try_pip_dry_run(self, package_name: str, version: str) -> Optional[List[str]]:
        req_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(_('{}=={}\n').format(package_name, version))
                req_file = f.name
            cmd = [self.config['python_executable'], '-m', 'pip', 'install', '--dry-run', '--report', '-', '-r', req_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                return None
            if not result.stdout or not result.stdout.strip():
                return None
            stdout_stripped = result.stdout.strip()
            if not (stdout_stripped.startswith('{') or stdout_stripped.startswith('[')):
                return None
            try:
                report = json.loads(result.stdout)
            except json.JSONDecodeError:
                return None
            if not isinstance(report, dict) or 'install' not in report:
                return None
            deps = []
            for item in report.get('install', []):
                try:
                    if not isinstance(item, dict) or 'metadata' not in item:
                        continue
                    metadata = item['metadata']
                    item_name = metadata.get('name')
                    item_version = metadata.get('version')
                    if item_name and item_version and (item_name.lower() != package_name.lower()):
                        deps.append('{}=={}'.format(item_name, item_version))
                except Exception:
                    continue
            return deps
        except Exception:
            return None
        finally:
            if req_file and Path(req_file).exists():
                try:
                    Path(req_file).unlink()
                except Exception:
                    pass

    def _try_pypi_api(self, package_name: str, version: str) -> Optional[List[str]]:
        try:
            import requests
        except ImportError:
            print(_("    ⚠️  'requests' package not found. Skipping PyPI API strategy."))
            return None
        try:
            clean_version = version.split('+')[0]
            url = f'https://pypi.org/pypi/{package_name}/{clean_version}/json'
            headers = {'User-Agent': 'omnipkg-package-manager/1.0', 'Accept': 'application/json'}
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code == 404:
                if clean_version != version:
                    url = f'https://pypi.org/pypi/{package_name}/{version}/json'
                    response = requests.get(url, timeout=10, headers=headers)
            if response.status_code != 200:
                return None
            if not response.text.strip():
                return None
            try:
                pkg_data = response.json()
            except json.JSONDecodeError:
                return None
            if not isinstance(pkg_data, dict):
                return None
            requires_dist = pkg_data.get('info', {}).get('requires_dist')
            if not requires_dist:
                return []
            dependencies = []
            for req in requires_dist:
                if not req or not isinstance(req, str):
                    continue
                if ';' in req:
                    continue
                req = req.strip()
                match = re.match('^([a-zA-Z0-9\\-_.]+)([<>=!]+.*)?', req)
                if match:
                    dep_name = match.group(1)
                    version_spec = match.group(2) or ''
                    dependencies.append(_('{}{}').format(dep_name, version_spec))
            return dependencies
        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None

    def _try_pip_show_fallback(self, package_name: str, version: str) -> Optional[List[str]]:
        try:
            cmd = [self.config['python_executable'], '-m', 'pip', 'show', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return None
            for line in result.stdout.split('\n'):
                if line.startswith('Requires:'):
                    requires = line.replace('Requires:', '').strip()
                    if requires and requires != '':
                        deps = [dep.strip() for dep in requires.split(',')]
                        return [dep for dep in deps if dep]
                    else:
                        return []
            return []
        except Exception:
            return None

    def _classify_package_type(self, files: List[Path]) -> str:
        has_python = any((f.suffix in ['.py', '.pyc'] for f in files))
        has_native = any((f.suffix in ['.so', '.pyd', '.dll'] for f in files))
        if has_native and has_python:
            return 'mixed'
        elif has_native:
            return 'native'
        else:
            return 'pure_python'

    def _find_existing_c_extension(self, file_hash: str) -> Optional[str]:
        """Disabled: C extensions are copied, not symlinked."""
        return None

    def _analyze_installed_tree(self, temp_path: Path) -> Dict[str, Dict]:
        """
        Analyzes the temporary installation, now EXPLICITLY finding executables
        and summarizing file registry warnings instead of printing each one.
        """
        installed = {}
        unregistered_file_count = 0
        for dist_info in temp_path.glob('*.dist-info'):
            try:
                dist = importlib.metadata.Distribution.at(dist_info)
                if not dist:
                    continue
                pkg_files = []
                if dist.files:
                    for file_entry in dist.files:
                        if file_entry.parts and file_entry.parts[0] == 'bin':
                            continue
                        abs_path = Path(dist_info.parent) / file_entry
                        if abs_path.exists():
                            pkg_files.append(abs_path)
                executables = []
                entry_points = dist.entry_points
                console_scripts = [ep for ep in entry_points if ep.group == 'console_scripts']
                if console_scripts:
                    temp_bin_path = temp_path / 'bin'
                    if temp_bin_path.is_dir():
                        for script in console_scripts:
                            exe_path = temp_bin_path / script.name
                            if exe_path.is_file():
                                executables.append(exe_path)
                pkg_name = dist.metadata['Name'].lower().replace('_', '-')
                version = dist.metadata['Version']
                installed[dist.metadata['Name']] = {'version': version, 'files': [p for p in pkg_files if p.exists()], 'executables': executables, 'type': self._classify_package_type(pkg_files)}
                redis_key = _('{}bubble:{}:{}:file_paths').format(self.parent_omnipkg.redis_key_prefix, pkg_name, version)
                existing_paths = set(self.parent_omnipkg.redis_client.smembers(redis_key)) if self.parent_omnipkg.redis_client.exists(redis_key) else set()
                all_package_files_for_check = pkg_files + executables
                for file_path in all_package_files_for_check:
                    if str(file_path) not in existing_paths:
                        unregistered_file_count += 1
            except Exception as e:
                print(_('    ⚠️  Could not analyze {}: {}').format(dist_info.name, e))
        if unregistered_file_count > 0:
            print(_('    ⚠️  Found {} files not in registry. They will be registered during bubble creation.').format(unregistered_file_count))
        return installed

    def _is_binary(self, file_path: Path) -> bool:
        """
        Robustly checks if a file is a binary executable, excluding C extensions.
        Gracefully falls back to a basic check if 'python-magic' is not installed.
        """
        if file_path.suffix in {'.so', '.pyd'}:
            return False
        if not HAS_MAGIC:
            if not getattr(self, '_magic_warning_shown', False):
                print(_("⚠️  Warning: 'python-magic' not installed. Using basic binary detection."))
                self._magic_warning_shown = True
            return file_path.suffix in {'.dll', '.exe'}
        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(str(file_path))
            executable_types = {'application/x-executable', 'application/x-sharedlib', 'application/x-pie-executable'}
            return any((t in file_type for t in executable_types)) or file_path.suffix in {'.dll', '.exe'}
        except Exception:
            return file_path.suffix in {'.dll', '.exe'}

    def _create_deduplicated_bubble(self, installed_tree: Dict, bubble_path: Path, temp_install_path: Path) -> bool:
        """
        Enhanced Version: Fixes flask-login and similar packages with missing submodules.
        
        Key improvements:
        1. Better detection of package internal structure
        2. Conservative approach for packages with submodules
        3. Enhanced failsafe scanning
        4. Special handling for namespace packages
        """
        print(_('    🧹 Creating deduplicated bubble at {}').format(bubble_path))
        bubble_path.mkdir(parents=True, exist_ok=True)
        main_env_hashes = self._get_or_build_main_env_hash_index()
        stats = {'total_files': 0, 'copied_files': 0, 'deduplicated_files': 0, 'c_extensions': [], 'binaries': [], 'python_files': 0, 'package_modules': {}, 'submodules_found': 0}
        c_ext_packages = {pkg_name for pkg_name, info in installed_tree.items() if info.get('type') in ['native', 'mixed']}
        binary_packages = {pkg_name for pkg_name, info in installed_tree.items() if info.get('type') == 'binary'}
        complex_packages = set()
        for pkg_name, pkg_info in installed_tree.items():
            pkg_files = pkg_info.get('files', [])
            py_files_in_subdirs = [f for f in pkg_files if f.suffix == '.py' and len(f.parts) > 2 and (f.parts[-2] != '__pycache__')]
            if len(py_files_in_subdirs) > 1:
                complex_packages.add(pkg_name)
                stats['package_modules'][pkg_name] = len(py_files_in_subdirs)
        if c_ext_packages:
            print(_('    🔬 Found C-extension packages: {}').format(', '.join(c_ext_packages)))
        if binary_packages:
            print(_('    ⚙️  Found binary packages: {}').format(', '.join(binary_packages)))
        if complex_packages:
            print(_('    📦 Found complex packages with submodules: {}').format(', '.join(complex_packages)))
        processed_files = set()
        for pkg_name, pkg_info in installed_tree.items():
            if pkg_name in c_ext_packages:
                should_deduplicate_this_package = False
                print(_('    🔬 {}: C-extension - copying all files').format(pkg_name))
            elif pkg_name in binary_packages:
                should_deduplicate_this_package = False
                print(_('    ⚙️  {}: Binary package - copying all files').format(pkg_name))
            elif pkg_name in complex_packages:
                should_deduplicate_this_package = False
                print(_('    📦 {}: Complex package ({} submodules) - copying all files').format(pkg_name, stats['package_modules'][pkg_name]))
            else:
                should_deduplicate_this_package = True
            pkg_copied = 0
            pkg_deduplicated = 0
            for source_path in pkg_info.get('files', []):
                if not source_path.is_file():
                    continue
                processed_files.add(source_path)
                stats['total_files'] += 1
                is_c_ext = source_path.suffix in {'.so', '.pyd'}
                is_binary = self._is_binary(source_path)
                is_python_module = source_path.suffix == '.py'
                if is_c_ext:
                    stats['c_extensions'].append(source_path.name)
                elif is_binary:
                    stats['binaries'].append(source_path.name)
                elif is_python_module:
                    stats['python_files'] += 1
                should_copy = True
                if should_deduplicate_this_package:
                    if is_python_module and '/__pycache__/' not in str(source_path):
                        should_copy = True
                    else:
                        try:
                            file_hash = self._get_file_hash(source_path)
                            if file_hash in main_env_hashes:
                                should_copy = False
                        except (IOError, OSError):
                            pass
                if should_copy:
                    stats['copied_files'] += 1
                    pkg_copied += 1
                    self._copy_file_to_bubble(source_path, bubble_path, temp_install_path, is_binary or is_c_ext)
                else:
                    stats['deduplicated_files'] += 1
                    pkg_deduplicated += 1
            if pkg_copied > 0 or pkg_deduplicated > 0:
                print(_('    📄 {}: copied {}, deduplicated {}').format(pkg_name, pkg_copied, pkg_deduplicated))
        all_temp_files = {p for p in temp_install_path.rglob('*') if p.is_file()}
        missed_files = all_temp_files - processed_files
        if missed_files:
            print(_('    ⚠️  Found {} file(s) not listed in package metadata.').format(len(missed_files)))
            missed_by_package = {}
            for source_path in missed_files:
                owner_pkg = self._find_owner_package(source_path, temp_install_path, installed_tree)
                if owner_pkg not in missed_by_package:
                    missed_by_package[owner_pkg] = []
                missed_by_package[owner_pkg].append(source_path)
            for owner_pkg, files in missed_by_package.items():
                print(_('    📦 {}: found {} additional files').format(owner_pkg, len(files)))
                for source_path in files:
                    stats['total_files'] += 1
                    is_python_module = source_path.suffix == '.py'
                    is_init_file = source_path.name == '__init__.py'
                    should_deduplicate = owner_pkg not in c_ext_packages and owner_pkg not in binary_packages and (owner_pkg not in complex_packages) and (not self._is_binary(source_path)) and (source_path.suffix not in {'.so', '.pyd'}) and (not is_init_file) and (not is_python_module)
                    should_copy = True
                    if should_deduplicate:
                        try:
                            file_hash = self._get_file_hash(source_path)
                            if file_hash in main_env_hashes:
                                should_copy = False
                        except (IOError, OSError):
                            pass
                    is_c_ext = source_path.suffix in {'.so', '.pyd'}
                    is_binary = self._is_binary(source_path)
                    if is_c_ext:
                        stats['c_extensions'].append(source_path.name)
                    elif is_binary:
                        stats['binaries'].append(source_path.name)
                    else:
                        stats['python_files'] += 1
                    if should_copy:
                        stats['copied_files'] += 1
                        self._copy_file_to_bubble(source_path, bubble_path, temp_install_path, is_binary or is_c_ext)
                    else:
                        stats['deduplicated_files'] += 1
        self._verify_package_integrity(bubble_path, installed_tree, temp_install_path)
        efficiency = stats['deduplicated_files'] / stats['total_files'] * 100 if stats['total_files'] > 0 else 0
        print(_('    ✅ Bubble created: {} files copied, {} deduplicated.').format(stats['copied_files'], stats['deduplicated_files']))
        print(_('    📊 Space efficiency: {}% saved.').format(efficiency))
        if stats['package_modules']:
            print(_('    📦 Complex packages preserved: {} packages with submodules').format(len(stats['package_modules'])))
        self._create_bubble_manifest(bubble_path, installed_tree, stats)
        return True

    def _verify_package_integrity(self, bubble_path: Path, installed_tree: Dict, temp_install_path: Path) -> None:
        """
        Verify that critical package files are present in the bubble.
        This catches issues like missing flask_login.config modules.
        """
        print(_('    🔍 Verifying package integrity...'))
        for pkg_name, pkg_info in installed_tree.items():
            pkg_files = pkg_info.get('files', [])
            package_dirs = set()
            for file_path in pkg_files:
                if file_path.name == '__init__.py':
                    package_dirs.add(file_path.parent)
            for pkg_dir in package_dirs:
                relative_pkg_path = pkg_dir.relative_to(temp_install_path)
                bubble_pkg_path = bubble_path / relative_pkg_path
                if not bubble_pkg_path.exists():
                    print(_('    ⚠️  Missing package directory: {}').format(relative_pkg_path))
                    continue
                expected_py_files = [f for f in pkg_files if f.suffix == '.py' and f.parent == pkg_dir]
                for py_file in expected_py_files:
                    relative_py_path = py_file.relative_to(temp_install_path)
                    bubble_py_path = bubble_path / relative_py_path
                    if not bubble_py_path.exists():
                        print(_('    🚨 CRITICAL: Missing Python module: {}').format(relative_py_path))
                        self._copy_file_to_bubble(py_file, bubble_path, temp_install_path, False)
                        print(_('    🔧 Fixed: Copied missing module {}').format(relative_py_path))

    def _find_owner_package(self, file_path: Path, temp_install_path: Path, installed_tree: Dict) -> Optional[str]:
        """
        Helper to find which package a file belongs to, now supporting .egg-info.
        """
        try:
            for parent in file_path.parents:
                if parent.name.endswith(('.dist-info', '.egg-info')):
                    pkg_name = parent.name.split('-')[0]
                    return pkg_name.lower().replace('_', '-')
        except Exception:
            pass
        return None

    def _copy_file_to_bubble(self, source_path: Path, bubble_path: Path, temp_install_path: Path, make_executable: bool=False):
        """Helper method to copy a file to the bubble with proper error handling."""
        try:
            rel_path = source_path.relative_to(temp_install_path)
            dest_path = bubble_path / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            if make_executable:
                os.chmod(dest_path, 493)
        except Exception as e:
            print(_('    ⚠️ Warning: Failed to copy {}: {}').format(source_path.name, e))

    def _get_or_build_main_env_hash_index(self) -> Set[str]:
        """
        Builds or loads a FAST hash index using package metadata when possible,
        falling back to filesystem scan only when needed.
        """
        if not self.parent_omnipkg.redis_client:
            self.parent_omnipkg.connect_redis()
        redis_key = _('{}main_env:file_hashes').format(self.parent_omnipkg.redis_key_prefix)
        if self.parent_omnipkg.redis_client.exists(redis_key):
            print(_('    ⚡️ Loading main environment hash index from cache...'))
            cached_hashes = set(self.parent_omnipkg.redis_client.sscan_iter(redis_key))
            print(_('    📈 Loaded {} file hashes from Redis.').format(len(cached_hashes)))
            return cached_hashes
        print(_('    🔍 Building main environment hash index...'))
        hash_set = set()
        try:
            print(_('    📦 Attempting fast indexing via package metadata...'))
            installed_packages = self.parent_omnipkg.get_installed_packages(live=True)
            successful_packages = 0
            failed_packages = []
            for pkg_name in tqdm(installed_packages.keys(), desc='    📦 Indexing via metadata', unit='pkg'):
                try:
                    dist = importlib.metadata.distribution(pkg_name)
                    if dist.files:
                        pkg_hashes = 0
                        for file_path in dist.files:
                            try:
                                abs_path = dist.locate_file(file_path)
                                if abs_path and abs_path.is_file() and (abs_path.suffix not in {'.pyc', '.pyo'}) and ('__pycache__' not in abs_path.parts):
                                    hash_set.add(self._get_file_hash(abs_path))
                                    pkg_hashes += 1
                            except (IOError, OSError, AttributeError):
                                continue
                        if pkg_hashes > 0:
                            successful_packages += 1
                        else:
                            failed_packages.append(pkg_name)
                    else:
                        failed_packages.append(pkg_name)
                except Exception:
                    failed_packages.append(pkg_name)
            print(_('    ✅ Successfully indexed {} packages via metadata').format(successful_packages))
            if failed_packages:
                print(_('    🔄 Fallback scan for {} packages: {}{}').format(len(failed_packages), ', '.join(failed_packages[:3]), '...' if len(failed_packages) > 3 else ''))
                potential_files = []
                for file_path in self.site_packages.rglob('*'):
                    if file_path.is_file() and file_path.suffix not in {'.pyc', '.pyo'} and ('__pycache__' not in file_path.parts):
                        file_str = str(file_path).lower()
                        if any((pkg.lower().replace('-', '_') in file_str or pkg.lower().replace('_', '-') in file_str for pkg in failed_packages)):
                            potential_files.append(file_path)
                for file_path in tqdm(potential_files, desc='    📦 Fallback scan', unit='file'):
                    try:
                        hash_set.add(self._get_file_hash(file_path))
                    except (IOError, OSError):
                        continue
        except Exception as e:
            print(_('    ⚠️ Metadata approach failed ({}), falling back to full scan...').format(e))
            files_to_process = [p for p in self.site_packages.rglob('*') if p.is_file() and p.suffix not in {'.pyc', '.pyo'} and ('__pycache__' not in p.parts)]
            for file_path in tqdm(files_to_process, desc='    📦 Full scan', unit='file'):
                try:
                    hash_set.add(self._get_file_hash(file_path))
                except (IOError, OSError):
                    continue
        print(_('    💾 Saving {} file hashes to Redis cache...').format(len(hash_set)))
        if hash_set:
            with self.parent_omnipkg.redis_client.pipeline() as pipe:
                for h in hash_set:
                    pipe.sadd(redis_key, h)
                pipe.execute()
        print(_('    📈 Indexed {} files from main environment.').format(len(hash_set)))
        return hash_set

    def _register_bubble_location(self, bubble_path: Path, installed_tree: Dict, stats: dict):
        """
        Register bubble location and summary statistics in a single batch operation.
        """
        registry_key = '{}bubble_locations'.format(self.parent_omnipkg.redis_key_prefix)
        bubble_data = {'path': str(bubble_path), 'python_version': '{}.{}'.format(sys.version_info.major, sys.version_info.minor), 'created_at': datetime.now().isoformat(), 'packages': {pkg: info['version'] for pkg, info in installed_tree.items()}, 'stats': {'total_files': stats['total_files'], 'copied_files': stats['copied_files'], 'deduplicated_files': stats['deduplicated_files'], 'c_extensions_count': len(stats['c_extensions']), 'binaries_count': len(stats['binaries']), 'python_files': stats['python_files']}}
        bubble_id = bubble_path.name
        self.parent_omnipkg.redis_client.hset(registry_key, bubble_id, json.dumps(bubble_data))
        print(_('    📝 Registered bubble location and stats for {} packages.').format(len(installed_tree)))

    def _get_file_hash(self, file_path: Path) -> str:
        path_str = str(file_path)
        if path_str in self.file_hash_cache:
            return self.file_hash_cache[path_str]
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while (chunk := f.read(8192)):
                h.update(chunk)
        file_hash = h.hexdigest()
        self.file_hash_cache[path_str] = file_hash
        return file_hash

    def _create_bubble_manifest(self, bubble_path: Path, installed_tree: Dict, stats: dict):
        """
        Creates both a local manifest file and registers the bubble in Redis.
        This replaces the old _create_bubble_manifest with integrated registry functionality.
        """
        total_size = sum((f.stat().st_size for f in bubble_path.rglob('*') if f.is_file()))
        size_mb = round(total_size / (1024 * 1024), 2)
        symlink_origins = set()
        for item in bubble_path.rglob('*.so'):
            if item.is_symlink():
                try:
                    real_path = item.resolve()
                    symlink_origins.add(str(real_path.parent))
                except Exception:
                    continue
        stats['symlink_origins'] = sorted(list(symlink_origins), key=len, reverse=True)
        manifest_data = {'created_at': datetime.now().isoformat(), 'python_version': _('{}.{}').format(sys.version_info.major, sys.version_info.minor), 'omnipkg_version': '1.0.0', 'packages': {name: {'version': info['version'], 'type': info['type'], 'install_reason': info.get('install_reason', 'dependency')} for name, info in installed_tree.items()}, 'stats': {'bubble_size_mb': size_mb, 'package_count': len(installed_tree), 'total_files': stats['total_files'], 'copied_files': stats['copied_files'], 'deduplicated_files': stats['deduplicated_files'], 'deduplication_efficiency_percent': round(stats['deduplicated_files'] / stats['total_files'] * 100 if stats['total_files'] > 0 else 0, 1), 'c_extensions_count': len(stats['c_extensions']), 'binaries_count': len(stats['binaries']), 'python_files': stats['python_files'], 'symlink_origins': stats['symlink_origins']}, 'file_types': {'c_extensions': stats['c_extensions'][:10], 'binaries': stats['binaries'][:10], 'has_more_c_extensions': len(stats['c_extensions']) > 10, 'has_more_binaries': len(stats['binaries']) > 10}}
        manifest_path = bubble_path / '.omnipkg_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        registry_key = _('{}bubble_locations').format(self.parent_omnipkg.redis_key_prefix)
        bubble_id = bubble_path.name
        redis_bubble_data = {**manifest_data, 'path': str(bubble_path), 'manifest_path': str(manifest_path), 'bubble_id': bubble_id}
        try:
            with self.parent_omnipkg.redis_client.pipeline() as pipe:
                pipe.hset(registry_key, bubble_id, json.dumps(redis_bubble_data))
                for pkg_name, pkg_info in installed_tree.items():
                    canonical_pkg_name = canonicalize_name(pkg_name)
                    main_pkg_key = f'{self.parent_omnipkg.redis_key_prefix}{canonical_pkg_name}'
                    version_str = pkg_info['version']
                    pipe.hset(main_pkg_key, f'bubble_version:{version_str}', 'true')
                    pipe.sadd(_('{}:installed_versions').format(main_pkg_key), version_str)
                    pipe.sadd(f'{self.parent_omnipkg.redis_key_prefix}index', canonical_pkg_name)
                for pkg_name, pkg_info in installed_tree.items():
                    pkg_version_key = '{}=={}'.format(canonicalize_name(pkg_name), pkg_info['version'])
                    pipe.hset(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix), pkg_version_key, bubble_id)
                size_category = 'small' if size_mb < 10 else 'medium' if size_mb < 100 else 'large'
                pipe.sadd(_('{}bubbles_by_size:{}').format(self.parent_omnipkg.redis_key_prefix, size_category), bubble_id)
                pipe.execute()
            print(_('    📝 Created manifest and registered bubble for {} packages ({} MB).').format(len(installed_tree), size_mb))
        except Exception as e:
            print(_('    ⚠️ Warning: Failed to register bubble in Redis: {}').format(e))
            print(_('    📝 Local manifest created at {}').format(manifest_path))

    def get_bubble_info(self, bubble_id: str) -> dict:
        """
        Retrieves comprehensive bubble information from Redis registry.
        """
        registry_key = _('{}bubble_locations').format(self.parent_omnipkg.redis_key_prefix)
        bubble_data = self.parent_omnipkg.redis_client.hget(registry_key, bubble_id)
        if bubble_data:
            return json.loads(bubble_data)
        return {}

    def find_bubbles_for_package(self, pkg_name: str, version: str=None) -> list:
        """
        Finds all bubbles containing a specific package.
        """
        if version:
            pkg_key = '{}=={}'.format(pkg_name, version)
            bubble_id = self.parent_omnipkg.redis_client.hget(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix), pkg_key)
            return [bubble_id] if bubble_id else []
        else:
            pattern = f'{pkg_name}==*'
            matching_keys = []
            for key in self.parent_omnipkg.redis_client.hkeys(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix)):
                if key.startswith(f'{pkg_name}=='):
                    bubble_id = self.parent_omnipkg.redis_client.hget(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix), key)
                    matching_keys.append(bubble_id)
            return matching_keys

    def cleanup_old_bubbles(self, keep_latest: int=3, size_threshold_mb: float=500):
        """
        Cleanup old bubbles based on size and age, keeping most recent ones.
        """
        registry_key = _('{}bubble_locations').format(self.parent_omnipkg.redis_key_prefix)
        all_bubbles = {}
        for bubble_id, bubble_data_str in self.parent_omnipkg.redis_client.hgetall(registry_key).items():
            bubble_data = json.loads(bubble_data_str)
            all_bubbles[bubble_id] = bubble_data
        by_package = {}
        for bubble_id, data in all_bubbles.items():
            pkg_name = bubble_id.split('-')[0]
            if pkg_name not in by_package:
                by_package[pkg_name] = []
            by_package[pkg_name].append((bubble_id, data))
        bubbles_to_remove = []
        total_size_freed = 0
        for pkg_name, bubbles in by_package.items():
            bubbles.sort(key=lambda x: x[1]['created_at'], reverse=True)
            for bubble_id, data in bubbles[keep_latest:]:
                bubbles_to_remove.append((bubble_id, data))
                total_size_freed += data['stats']['bubble_size_mb']
        for bubble_id, data in all_bubbles.items():
            if (bubble_id, data) not in bubbles_to_remove:
                if data['stats']['bubble_size_mb'] > size_threshold_mb:
                    bubbles_to_remove.append((bubble_id, data))
                    total_size_freed += data['stats']['bubble_size_mb']
        if bubbles_to_remove:
            print(_('    🧹 Cleaning up {} old bubbles ({} MB)...').format(len(bubbles_to_remove), total_size_freed))
            with self.parent_omnipkg.redis_client.pipeline() as pipe:
                for bubble_id, data in bubbles_to_remove:
                    pipe.hdel(registry_key, bubble_id)
                    for pkg_name, pkg_info in data.get('packages', {}).items():
                        pkg_key = '{}=={}'.format(pkg_name, pkg_info['version'])
                        pipe.hdel(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix), pkg_key)
                    size_mb = data['stats']['bubble_size_mb']
                    size_category = 'small' if size_mb < 10 else 'medium' if size_mb < 100 else 'large'
                    pipe.srem(_('{}bubbles_by_size:{}').format(self.parent_omnipkg.redis_key_prefix, size_category), bubble_id)
                    bubble_path = Path(data['path'])
                    if bubble_path.exists():
                        shutil.rmtree(bubble_path, ignore_errors=True)
                pipe.execute()
            print(_('    ✅ Freed {} MB of storage.').format(total_size_freed))
        else:
            print(_('    ✅ No bubbles need cleanup.'))

class ImportHookManager:

    def __init__(self, multiversion_base: str, config: Dict, redis_client=None):
        self.multiversion_base = Path(multiversion_base)
        self.version_map = {}
        self.active_versions = {}
        self.hook_installed = False
        self.redis_client = redis_client
        self.config = config
        self.http_session = http_requests.Session()

    def load_version_map(self):
        if not self.multiversion_base.exists():
            return
        for version_dir in self.multiversion_base.iterdir():
            if version_dir.is_dir() and '-' in version_dir.name:
                pkg_name, version = version_dir.name.rsplit('-', 1)
                if pkg_name not in self.version_map:
                    self.version_map[pkg_name] = {}
                self.version_map[pkg_name][version] = str(version_dir)

    def refresh_bubble_map(self, pkg_name: str, version: str, bubble_path: str):
        """
        Immediately adds a newly created bubble to the internal version map
        to prevent race conditions during validation.
        """
        pkg_name = pkg_name.lower().replace('_', '-')
        if pkg_name not in self.version_map:
            self.version_map[pkg_name] = {}
        self.version_map[pkg_name][version] = bubble_path
        print(_('    🧠 HookManager now aware of new bubble: {}=={}').format(pkg_name, version))

    def remove_bubble_from_tracking(self, package_name: str, version: str):
        """
        Removes a bubble from the internal version map tracking.
        Used when cleaning up redundant bubbles.
        """
        pkg_name = package_name.lower().replace('_', '-')
        if pkg_name in self.version_map and version in self.version_map[pkg_name]:
            del self.version_map[pkg_name][version]
            print(f'    ✅ Removed bubble tracking for {pkg_name}=={version}')
            if not self.version_map[pkg_name]:
                del self.version_map[pkg_name]
                print(f'    ✅ Removed package {pkg_name} from version map (no more bubbles)')
        if pkg_name in self.active_versions and self.active_versions[pkg_name] == version:
            del self.active_versions[pkg_name]
            print(f'    ✅ Removed active version tracking for {pkg_name}=={version}')

    def validate_bubble(self, package_name: str, version: str) -> bool:
        """
        Validates a bubble's integrity by checking for its physical existence
        and the presence of a manifest file.
        """
        bubble_path_str = self.get_package_path(package_name, version)
        if not bubble_path_str:
            print(_("    ❌ Bubble not found in HookManager's map for {}=={}").format(package_name, version))
            return False
        bubble_path = Path(bubble_path_str)
        if not bubble_path.is_dir():
            print(_('    ❌ Bubble directory does not exist at: {}').format(bubble_path))
            return False
        manifest_path = bubble_path / '.omnipkg_manifest.json'
        if not manifest_path.exists():
            print(_('    ❌ Bubble is incomplete: Missing manifest file at {}').format(manifest_path))
            return False
        bin_path = bubble_path / 'bin'
        if not bin_path.is_dir():
            print(_("    ⚠️  Warning: Bubble for {}=={} does not contain a 'bin' directory.").format(package_name, version))
        print(_('    ✅ Bubble validated successfully: {}=={}').format(package_name, version))
        return True

    def install_import_hook(self):
        if self.hook_installed:
            return
        sys.meta_path.insert(0, MultiversionFinder(self))
        self.hook_installed = True

    def set_active_version(self, package_name: str, version: str):
        self.active_versions[package_name.lower()] = version

    def get_package_path(self, package_name: str, version: str=None) -> Optional[str]:
        pkg_name = package_name.lower().replace('_', '-')
        version = version or self.active_versions.get(pkg_name)
        if pkg_name in self.version_map and version in self.version_map[pkg_name]:
            return self.version_map[pkg_name][version]
        if hasattr(self, 'bubble_manager') and pkg_name in self.bubble_manager.package_path_registry:
            if version in self.bubble_manager.package_path_registry[pkg_name]:
                return str(self.multiversion_base / '{}-{}'.format(pkg_name, version))
        return None

class MultiversionFinder:

    def __init__(self, hook_manager: ImportHookManager):
        self.hook_manager = hook_manager
        self.http_session = http_requests.Session()

    def find_spec(self, fullname, path, target=None):
        top_level = fullname.split('.')[0]
        pkg_path = self.hook_manager.get_package_path(top_level)
        if pkg_path and os.path.exists(pkg_path):
            if pkg_path not in sys.path:
                sys.path.insert(0, pkg_path)
        return None

class omnipkg:
    def __init__(self, config_manager: ConfigManager):
        """
        Initializes the Omnipkg core engine with a robust, fail-safe sequence.
        """
        # === STAGE 1: CONFIGURATION SETUP ===
        # The ConfigManager is the ground truth. Its success is paramount.
        self.config_manager = config_manager
        self.config = config_manager.config
        
        # CRITICAL: Halt if configuration failed to load. This prevents all downstream errors.
        if not self.config:
            raise RuntimeError("OmnipkgCore cannot initialize: Configuration is missing or invalid.")

        # === STAGE 2: CORE ATTRIBUTE INITIALIZATION ===
        # These attributes depend ONLY on a valid config object.
        self.env_id = self._get_env_id()
        self.multiversion_base = Path(self.config['multiversion_base'])
        self.redis_client = None
        self._info_cache = {}
        self._installed_packages_cache = None
        self.http_session = http_requests.Session()
        
        # === STAGE 3: EXTERNAL CONNECTIONS AND FILE SYSTEM OPERATIONS ===
        # These operations depend on the attributes from Stage 2.
        
        # Ensure the base directory for version bubbles exists.
        self.multiversion_base.mkdir(parents=True, exist_ok=True)
        
        # Attempt to connect to Redis. If it fails, exit gracefully with a helpful message.
        if not self.connect_redis():
            sys.exit(1)

        # === STAGE 4: INITIALIZE MANAGER CLASSES ===
        # These managers depend on a successful setup from the previous stages.
        
        # FIX: Instantiate InterpreterManager correctly and ONLY ONCE.
        self.interpreter_manager = InterpreterManager(self.config_manager)
        
        self.hook_manager = ImportHookManager(
            str(self.multiversion_base), 
            config=self.config, 
            redis_client=self.redis_client
        )
        self.bubble_manager = BubbleIsolationManager(self.config, self)

        # === STAGE 5: POST-INITIALIZATION TASKS ===
        # Final setup tasks that rely on the fully initialized object.
        
        # Check for and perform Redis key migration if needed.
        migration_flag_key = f'omnipkg:env_{self.env_id}:migration_v2_env_aware_keys_complete'
        if not self.redis_client.get(migration_flag_key):
            old_keys_iterator = self.redis_client.scan_iter('omnipkg:pkg:*', count=1)
            if next(old_keys_iterator, None):
                self._perform_redis_key_migration(migration_flag_key)
            else:
                self.redis_client.set(migration_flag_key, 'true')

        # Load the version map and install the import hook.
        self.hook_manager.load_version_map()
        self.hook_manager.install_import_hook()
        
        print(_('✅ Omnipkg core initialized successfully.'))

    def _perform_redis_key_migration(self, migration_flag_key: str):
        """
        Performs a one-time, automatic migration of Redis keys from the old
        global format to the new environment-and-python-specific format.
        """
        print('🔧 Performing one-time Knowledge Base upgrade for multi-environment support...')
        old_prefix = 'omnipkg:pkg:'
        all_old_keys = self.redis_client.keys(f'{old_prefix}*')
        if not all_old_keys:
            print('   ✅ No old-format data found to migrate. Marking as complete.')
            self.redis_client.set(migration_flag_key, 'true')
            return
        new_prefix_for_current_env = self.redis_key_prefix
        migrated_count = 0
        with self.redis_client.pipeline() as pipe:
            for old_key in all_old_keys:
                new_key = old_key.replace(old_prefix, new_prefix_for_current_env, 1)
                pipe.rename(old_key, new_key)
                migrated_count += 1
            pipe.set(migration_flag_key, 'true')
            pipe.execute()
        print(f'   ✅ Successfully upgraded {migrated_count} KB entries for this environment.')

    def _get_env_id(self) -> str:
        """Creates a short, stable hash from the venv path to uniquely identify it."""
        venv_path = str(Path(sys.prefix).resolve())
        return hashlib.md5(venv_path.encode()).hexdigest()[:8]

    @property
    def redis_key_prefix(self) -> str:
        
        # Get the active Python executable from the single source of truth: the config file.
        python_exe_path = self.config.get('python_executable', sys.executable)
        py_ver_str = 'unknown'

        # Extract the version (e.g., "py3.12") from the path.
        match = re.search(r'python(3\.\d+)', python_exe_path)
        if match:
            py_ver_str = f"py{match.group(1)}"
        else:
            # Fallback if the path is unusual, ask the interpreter itself.
            try:
                result = subprocess.run(
                    [python_exe_path, "-c", "import sys; print(f'py{sys.version_info.major}.{sys.version_info.minor}')"],
                    capture_output=True, text=True, check=True, timeout=2
                )
                py_ver_str = result.stdout.strip()
            except Exception:
                # If all else fails, use the version of the currently running script.
                py_ver_str = f'py{sys.version_info.major}.{sys.version_info.minor}'
        
        # The env_id is a stable property of the ConfigManager.
        return f'omnipkg:env_{self.config_manager.env_id}:{py_ver_str}:pkg:'

    def connect_redis(self) -> bool:
        try:
            self.redis_client = redis.Redis(host=self.config['redis_host'], port=self.config['redis_port'], decode_responses=True, socket_connect_timeout=5)
            self.redis_client.ping()
            return True
        except redis.ConnectionError:
            print(_('❌ Could not connect to Redis. Is the Redis server running?'))
            return False
        except Exception as e:
            print(_('❌ An unexpected Redis connection error occurred: {}').format(e))
            return False

    def reset_configuration(self, force: bool=False) -> int:
        """
        Deletes the config.json file to allow for a fresh setup.
        """
        config_path = Path.home() / '.config' / 'omnipkg' / 'config.json'
        if not config_path.exists():
            print(_('✅ Configuration file does not exist. Nothing to do.'))
            return 0
        print(_('🗑️  This will permanently delete your configuration file at:'))
        print(_('   {}').format(config_path))
        if not force:
            confirm = input(_('\n🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
            if confirm != 'y':
                print(_('🚫 Reset cancelled.'))
                return 1
        try:
            config_path.unlink()
            print(_('✅ Configuration file deleted successfully.'))
            print('\n' + '─' * 60)
            print(_('🚀 The next time you run `omnipkg`, you will be guided through the first-time setup.'))
            print('─' * 60)
            return 0
        except OSError as e:
            print(_('❌ Error: Could not delete configuration file: {}').format(e))
            print(_('   Please check your file permissions for {}').format(config_path))
            return 1

    def reset_knowledge_base(self, force: bool=False) -> int:
        """
        Deletes ALL omnipkg data for the CURRENT environment from Redis,
        as well as any legacy global data. It then triggers a full rebuild.
        """
        if not self.connect_redis():
            return 1
        new_env_pattern = f'{self.redis_key_prefix}*'
        old_global_pattern = 'omnipkg:pkg:*'
        migration_flag_pattern = 'omnipkg:migration:*'
        snapshot_pattern = 'omnipkg:snapshot:*'
        print(_('\n🧠 omnipkg Knowledge Base Reset'))
        print('-' * 50)
        print(_("   This will DELETE all data for the current environment (matching '{}')").format(new_env_pattern))
        print(_('   It will ALSO delete any legacy global data from older omnipkg versions.'))
        print(_('   ⚠️  This command does NOT uninstall any Python packages.'))
        if not force:
            confirm = input(_('\n🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
            if confirm != 'y':
                print(_('🚫 Reset cancelled.'))
                return 1
        print(_('\n🗑️  Clearing knowledge base...'))
        try:
            keys_new_env = self.redis_client.keys(new_env_pattern)
            keys_old_global = self.redis_client.keys(old_global_pattern)
            keys_migration = self.redis_client.keys(migration_flag_pattern)
            keys_snapshot = self.redis_client.keys(snapshot_pattern)
            all_keys_to_delete = set(keys_new_env + keys_old_global + keys_migration + keys_snapshot)
            if all_keys_to_delete:
                delete_command = self.redis_client.unlink if hasattr(self.redis_client, 'unlink') else self.redis_client.delete
                delete_command(*all_keys_to_delete)
                print(_('   ✅ Cleared {} cached entries from Redis.').format(len(all_keys_to_delete)))
            else:
                print(_('   ✅ Knowledge base was already clean.'))
        except Exception as e:
            print(_('   ❌ Failed to clear knowledge base: {}').format(e))
            return 1
        self._info_cache.clear()
        self._installed_packages_cache = None
        return self.rebuild_knowledge_base(force=True)

    def rebuild_knowledge_base(self, force: bool=False):
        """
        FIXED: Rebuilds the knowledge base by directly invoking the metadata gatherer
        in-process, avoiding subprocess argument limits and ensuring all discovered
        packages are processed correctly.
        """
        print(_('🧠 Forcing a full rebuild of the knowledge base...'))
        if not self.connect_redis():
            return 1
        try:
            # Instantiate the gatherer here, ensuring it runs in the same context.
            from .package_meta_builder import omnipkgMetadataGatherer
            gatherer = omnipkgMetadataGatherer(
                config=self.config,
                env_id=self.env_id,
                force_refresh=force
            )
            # Pass the existing, connected Redis client.
            gatherer.redis_client = self.redis_client
        
            # The gatherer's run method now contains the full, correct discovery logic.
            # Calling it with no arguments triggers a full scan.
            gatherer.run()
        
            # Clear local caches to force a reload from Redis on next use.
            self._info_cache.clear()
            self._installed_packages_cache = None
            print(_('✅ Knowledge base rebuilt successfully.'))
            return 0
        
        except Exception as e:
            print(_('    ❌ An unexpected error occurred during knowledge base rebuild: {}').format(e))
            import traceback
            traceback.print_exc()
            return 1
        
    def _analyze_rebuild_needs(self) -> dict:
        project_files = []
        for ext in ['.py', 'requirements.txt', 'pyproject.toml', 'Pipfile']:
            pass
        return {'auto_rebuild': len(project_files) > 0, 'components': ['dependency_cache', 'metadata', 'compatibility_matrix'], 'confidence': 0.95, 'suggestions': []}

    def _rebuild_component(self, component: str) -> None:
        if component == 'metadata':
            print(_('   🔄 Rebuilding core package metadata...'))
            try:
                cmd = [self.config['python_executable'], self.config['builder_script_path'], '--force']
                subprocess.run(cmd, check=True)
                print(_('   ✅ Core metadata rebuilt.'))
            except Exception as e:
                print(_('   ❌ Metadata rebuild failed: {}').format(e))
        else:
            print(_('   (Skipping {} - feature coming soon!)').format(component))

    def prune_bubbled_versions(self, package_name: str, keep_latest: Optional[int]=None, force: bool=False):
        """
        Intelligently removes old bubbled versions of a package.
        """
        self._synchronize_knowledge_base_with_reality()
        c_name = canonicalize_name(package_name)
        all_installations = self._find_package_installations(c_name)
        active_version_info = next((p for p in all_installations if p['type'] == 'active'), None)
        bubbled_versions = [p for p in all_installations if p['type'] == 'bubble']
        if not bubbled_versions:
            print(_("✅ No bubbles found for '{}'. Nothing to prune.").format(c_name))
            return 0
        bubbled_versions.sort(key=lambda x: parse_version(x['version']), reverse=True)
        to_prune = []
        if keep_latest is not None:
            if keep_latest < 0:
                print(_("❌ 'keep-latest' must be a non-negative number."))
                return 1
            to_prune = bubbled_versions[keep_latest:]
            kept_count = len(bubbled_versions) - len(to_prune)
            print(_('🔎 Found {} bubbles. Keeping the latest {}, pruning {} older versions.').format(len(bubbled_versions), kept_count, len(to_prune)))
        else:
            to_prune = bubbled_versions
            print(_("🔎 Found {} bubbles to prune for '{}'.").format(len(to_prune), c_name))
        if not to_prune:
            print(_('✅ No bubbles match the pruning criteria.'))
            return 0
        print(_('\nThe following bubbled versions will be permanently deleted:'))
        for item in to_prune:
            print(_('  - v{} (bubble)').format(item['version']))
        if active_version_info:
            print(_('🛡️  The active version (v{}) will NOT be affected.').format(active_version_info['version']))
        if not force:
            confirm = input(_('\n🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
            if confirm != 'y':
                print(_('🚫 Prune cancelled.'))
                return 1
        specs_to_uninstall = [f"{item['name']}=={item['version']}" for item in to_prune]
        for spec in specs_to_uninstall:
            print('-' * 20)
            self.smart_uninstall([spec], force=True)
        print(_("\n🎉 Pruning complete for '{}'.").format(c_name))
        return 0

    def _synchronize_knowledge_base_with_reality(self):
        """
        Self-healing function. Compares the file system (ground truth) with Redis (cache)
        and reconciles any differences. This function relies on the globally imported `_`
        for translations and should NOT assign any value to it locally.
        """
        print(_('🧠 Performing self-healing sync of knowledge base...'))
        if not self.redis_client:
            self.connect_redis()
        all_known_packages = self.redis_client.smembers('{}index'.format(self.redis_key_prefix))
        packages_to_check = set(all_known_packages)
        if self.multiversion_base.exists():
            for bubble_dir in self.multiversion_base.iterdir():
                if bubble_dir.is_dir():
                    try:
                        dir_pkg_name, _version = bubble_dir.name.rsplit('-', 1)
                        packages_to_check.add(canonicalize_name(dir_pkg_name))
                    except ValueError:
                        continue
        if not packages_to_check:
            print(_('   ✅ Knowledge base is empty or no packages found to sync.'))
            return
        fixed_count = 0
        with self.redis_client.pipeline() as pipe:
            for pkg_name in packages_to_check:
                main_key = f'{self.redis_key_prefix}{pkg_name}'
                real_active_version = None
                try:
                    real_active_version = importlib.metadata.version(pkg_name)
                except importlib.metadata.PackageNotFoundError:
                    pass
                real_bubbled_versions = set()
                if self.multiversion_base.exists():
                    for bubble_dir in self.multiversion_base.iterdir():
                        if not bubble_dir.is_dir():
                            continue
                        try:
                            dir_pkg_name, version = bubble_dir.name.rsplit('-', 1)
                            if dir_pkg_name == pkg_name:
                                real_bubbled_versions.add(version)
                        except ValueError:
                            continue
                cached_data = self.redis_client.hgetall(main_key)
                cached_active_version = cached_data.get('active_version')
                cached_bubbled_versions = {k.replace('bubble_version:', '') for k in cached_data if k.startswith('bubble_version:')}
                if real_active_version and real_active_version != cached_active_version:
                    pipe.hset(main_key, 'active_version', real_active_version)
                    fixed_count += 1
                elif not real_active_version and cached_active_version:
                    pipe.hdel(main_key, 'active_version')
                    fixed_count += 1
                stale_bubbles = cached_bubbled_versions - real_bubbled_versions
                for version in stale_bubbles:
                    pipe.hdel(main_key, 'bubble_version:{}'.format(version))
                    fixed_count += 1
                missing_bubbles = real_bubbled_versions - cached_bubbled_versions
                for version in missing_bubbles:
                    pipe.hset(main_key, 'bubble_version:{}'.format(version), 'true')
                    fixed_count += 1
            pipe.execute()
        if fixed_count > 0:
            print(_('   ✅ Sync complete. Reconciled {} discrepancies.').format(fixed_count))
        else:
            print(_('   ✅ Knowledge base is already in sync with the environment.'))

    def _update_hash_index_for_delta(self, before: Dict, after: Dict):
        """Surgically updates the cached hash index in Redis after an install."""
        if not self.redis_client:
            self.connect_redis()
        redis_key = _('{}main_env:file_hashes').format(self.redis_key_prefix)
        if not self.redis_client.exists(redis_key):
            return
        print(_('🔄 Updating cached file hash index...'))
        uninstalled_or_changed = {name: ver for name, ver in before.items() if name not in after or after[name] != ver}
        installed_or_changed = {name: ver for name, ver in after.items() if name not in before or before[name] != ver}
        with self.redis_client.pipeline() as pipe:
            for name, ver in uninstalled_or_changed.items():
                try:
                    dist = importlib.metadata.distribution(name)
                    if dist.files:
                        for file in dist.files:
                            pipe.srem(redis_key, self.bubble_manager._get_file_hash(dist.locate_file(file)))
                except (importlib.metadata.PackageNotFoundError, FileNotFoundError):
                    continue
            for name, ver in installed_or_changed.items():
                try:
                    dist = importlib.metadata.distribution(name)
                    if dist.files:
                        for file in dist.files:
                            pipe.sadd(redis_key, self.bubble_manager._get_file_hash(dist.locate_file(file)))
                except (importlib.metadata.PackageNotFoundError, FileNotFoundError):
                    continue
            pipe.execute()
        print(_('✅ Hash index updated.'))

    def get_installed_packages(self, live: bool=False) -> Dict[str, str]:
        if live:
            try:
                cmd = [self.config['python_executable'], '-m', 'pip', 'list', '--format=json']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                live_packages = {pkg['name'].lower(): pkg['version'] for pkg in json.loads(result.stdout)}
                self._installed_packages_cache = live_packages
                return live_packages
            except Exception as e:
                print(_('    ⚠️  Could not perform live package scan: {}').format(e))
                return self._installed_packages_cache or {}
        if self._installed_packages_cache is None:
            if not self.redis_client:
                self.connect_redis()
            self._installed_packages_cache = self.redis_client.hgetall(_('{}versions').format(self.redis_key_prefix))
        return self._installed_packages_cache

    def _detect_downgrades(self, before: Dict[str, str], after: Dict[str, str]) -> List[Dict]:
        downgrades = []
        for pkg_name, old_version in before.items():
            if pkg_name in after:
                new_version = after[pkg_name]
                try:
                    if parse_version(new_version) < parse_version(old_version):
                        downgrades.append({'package': pkg_name, 'good_version': old_version, 'bad_version': new_version})
                except InvalidVersion:
                    continue
        return downgrades

    def _detect_upgrades(self, before: Dict[str, str], after: Dict[str, str]) -> List[Dict]:
        """Identifies packages that were upgraded."""
        upgrades = []
        for pkg_name, old_version in before.items():
            if pkg_name in after:
                new_version = after[pkg_name]
                try:
                    if parse_version(new_version) > parse_version(old_version):
                        upgrades.append({'package': pkg_name, 'old_version': old_version, 'new_version': new_version})
                except InvalidVersion:
                    continue
        return upgrades

    def _run_metadata_builder_for_delta(self, before: Dict, after: Dict):
        """
        FIXED: Atomically updates the knowledge base by directly invoking the metadata
        gatherer in-process for all targeted updates, mirroring the robust logic
        from the successful rebuild_knowledge_base function.
        """
        # Determine which packages were added, upgraded, or changed.
        changed_specs = [f'{name}=={ver}' for name, ver in after.items() if name not in before or before[name] != ver]
        uninstalled = {name: ver for name, ver in before.items() if name not in after}
    
        if not changed_specs and not uninstalled:
            print(_('✅ Knowledge base is already up to date.'))
            return
    
        print(_('🧠 Updating knowledge base for changes...'))
        try:
            # --- START: THE CRITICAL FIX ---
            # If there are packages that were installed or changed, update them in-process.
            if changed_specs:
                print(_('   -> Processing {} changed/new package(s)...').format(len(changed_specs)))
                
                gatherer = omnipkgMetadataGatherer(
                    config=self.config,
                    env_id=self.env_id,
                    force_refresh=True
                )
                gatherer.redis_client = self.redis_client
                
                # --- THE FIX IS HERE ---
                # Tell the gatherer which packages are new for an efficient, targeted security scan.
                newly_active_packages = {
                    canonicalize_name(spec.split('==')[0]): spec.split('==')[1]
                    for spec in changed_specs if canonicalize_name(spec.split('==')[0]) in after
                }
                gatherer.run(targeted_packages=changed_specs, newly_active_packages=newly_active_packages)
            # --- END: THE CRITICAL FIX ---
    
            # Handle packages that were uninstalled.
            if uninstalled:
                print(_('   -> Cleaning up {} uninstalled package(s) from Redis...').format(len(uninstalled)))
                with self.redis_client.pipeline() as pipe:
                    for pkg_name, uninstalled_version in uninstalled.items():
                        c_name = canonicalize_name(pkg_name)
                        main_key = f'{self.redis_key_prefix}{c_name}'
                        version_key = f'{main_key}:{uninstalled_version}'
                        versions_set_key = f'{main_key}:installed_versions'
                        
                        # Delete the detailed version key
                        pipe.delete(version_key)
                        # Remove the version from the set of installed versions
                        pipe.srem(versions_set_key, uninstalled_version)
                        
                        # If the uninstalled version was the active one, remove the active flag
                        if self.redis_client.hget(main_key, 'active_version') == uninstalled_version:
                            pipe.hdel(main_key, 'active_version')
                        
                        # Remove any bubble flag for this version
                        pipe.hdel(main_key, f'bubble_version:{uninstalled_version}')
                    pipe.execute()
    
            # Clear local caches to force a fresh read from Redis.
            self._info_cache.clear()
            self._installed_packages_cache = None
            print(_('✅ Knowledge base updated successfully.'))
            
        except Exception as e:
            print(_('    ⚠️ Failed to update knowledge base for delta: {}').format(e))
            import traceback
            traceback.print_exc()

    def show_package_info(self, package_spec: str) -> int:
        if not self.connect_redis():
            return 1
        self._synchronize_knowledge_base_with_reality()
        try:
            pkg_name, requested_version = self._parse_package_spec(package_spec)
            if requested_version:
                print(f'\n' + '=' * 60)
                print(_('📄 Detailed info for {} v{}').format(pkg_name, requested_version))
                print('=' * 60)
                self._show_version_details(pkg_name, requested_version)
            else:
                self._show_enhanced_package_data(pkg_name)
            return 0
        except Exception as e:
            print(_('❌ An unexpected error occurred while showing package info: {}').format(e))
            import traceback
            traceback.print_exc()
            return 1

    def _clean_and_format_dependencies(self, raw_deps_json: str) -> str:
        """Parses the raw dependency JSON, filters out noise, and formats it for humans."""
        try:
            deps = json.loads(raw_deps_json)
            if not deps:
                return 'None'
            core_deps = [d.split(';')[0].strip() for d in deps if ';' not in d]
            if len(core_deps) > 5:
                return _('{}, ...and {} more').format(', '.join(core_deps[:5]), len(core_deps) - 5)
            else:
                return ', '.join(core_deps)
        except (json.JSONDecodeError, TypeError):
            return 'Could not parse.'

    def _show_enhanced_package_data(self, package_name: str):
        r = self.redis_client
        overview_key = '{}{}'.format(self.redis_key_prefix, package_name.lower())
        if not r.exists(overview_key):
            print(_("\n📋 KEY DATA: No Redis data found for '{}'").format(package_name))
            return
        print(_("\n📋 KEY DATA for '{}':").format(package_name))
        print('-' * 40)
        overview_data = r.hgetall(overview_key)
        active_ver = overview_data.get('active_version', 'Not Set')
        print(_('🎯 Active Version: {}').format(active_ver))
        bubble_versions = [key.replace('bubble_version:', '') for key in overview_data if key.startswith('bubble_version:') and overview_data[key] == 'true']
        if bubble_versions:
            print(_('🫧 Bubbled Versions: {}').format(', '.join(sorted(bubble_versions))))
        available_versions = []
        if active_ver != 'Not Set':
            available_versions.append(active_ver)
        available_versions.extend(sorted(bubble_versions))
        if available_versions:
            print(_('\n📦 Available Versions:'))
            for i, ver in enumerate(available_versions, 1):
                status_indicators = []
                if ver == active_ver:
                    status_indicators.append('active')
                if ver in bubble_versions:
                    status_indicators.append('in bubble')
                status_str = f" ({', '.join(status_indicators)})" if status_indicators else ''
                print(_('  {}) {}{}').format(i, ver, status_str))
            print(_('\n💡 Want details on a specific version?'))
            try:
                choice = input(_('Enter number (1-{}) or press Enter to skip: ').format(len(available_versions)))
                if choice.strip():
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(available_versions):
                            selected_version = available_versions[idx]
                            print(f'\n' + '=' * 60)
                            print(_('📄 Detailed info for {} v{}').format(package_name, selected_version))
                            print('=' * 60)
                            self._show_version_details(package_name, selected_version)
                        else:
                            print(_('❌ Invalid selection.'))
                    except ValueError:
                        print(_('❌ Please enter a number.'))
            except KeyboardInterrupt:
                print(_('\n   Skipped.'))
        else:
            print(_('📦 No installed versions found in Redis.'))

    def get_all_versions(self, package_name: str) -> List[str]:
        """Get all versions (active + bubbled) for a package"""
        overview_key = f'{self.redis_key_prefix}{package_name.lower()}'
        overview_data = self.redis_client.hgetall(overview_key)
        active_ver = overview_data.get('active_version')
        bubble_versions = [key.replace('bubble_version:', '') for key in overview_data if key.startswith('bubble_version:') and overview_data[key] == 'true']
        versions = []
        if active_ver:
            versions.append(active_ver)
        versions.extend(bubble_versions)
        return sorted(versions, key=lambda v: v)

    def _show_version_details(self, package_name: str, version: str):
        r = self.redis_client
        version_key = f'{self.redis_key_prefix}{package_name.lower()}:{version}'
        if not r.exists(version_key):
            print(_('❌ No detailed data found for {} v{}').format(package_name, version))
            return
        data = r.hgetall(version_key)
        important_fields = [('name', '📦 Package'), ('Version', '🏷️  Version'), ('Summary', '📝 Summary'), ('Author', '👤 Author'), ('Author-email', '📧 Email'), ('License', '⚖️  License'), ('Home-page', '🌐 Homepage'), ('Platform', '💻 Platform'), ('dependencies', '🔗 Dependencies'), ('Requires-Dist', '📋 Requires')]
        print(_('The data is fetched from Redis key: {}').format(version_key))
        for field_name, display_name in important_fields:
            if field_name in data:
                value = data[field_name]
                if field_name in ['dependencies', 'Requires-Dist']:
                    try:
                        dep_list = json.loads(value)
                        print(_('{}: {}').format(display_name.ljust(18), ', '.join(dep_list) if dep_list else 'None'))
                    except (json.JSONDecodeError, TypeError):
                        print(_('{}: {}').format(display_name.ljust(18), value))
                else:
                    print(_('{}: {}').format(display_name.ljust(18), value))
        security_fields = [('security.issues_found', '🔒 Security Issues'), ('security.audit_status', '🛡️  Audit Status'), ('health.import_check.importable', '✅ Importable')]
        print(_('\n---[ Health & Security ]---'))
        for field_name, display_name in security_fields:
            value = data.get(field_name, 'N/A')
            print(_('   {}: {}').format(display_name.ljust(18), value))
        meta_fields = [('last_indexed', '⏰ Last Indexed'), ('checksum', '🔐 Checksum'), ('Metadata-Version', '📋 Metadata Version')]
        print(_('\n---[ Build Info ]---'))
        for field_name, display_name in meta_fields:
            value = data.get(field_name, 'N/A')
            if field_name == 'checksum' and len(value) > 24:
                value = f'{value[:12]}...{value[-12:]}'
            print(_('   {}: {}').format(display_name.ljust(18), value))
        print(_('\n💡 For all raw data, use Redis key: "{}"').format(version_key))

    def _save_last_known_good_snapshot(self):
        """Saves the current environment state to Redis."""
        print(_("📸 Saving snapshot of the current environment as 'last known good'..."))
        try:
            current_state = self.get_installed_packages(live=True)
            snapshot_key = f'{self.redis_key_prefix}snapshot:last_known_good'
            self.redis_client.set(snapshot_key, json.dumps(current_state))
            print(_('   ✅ Snapshot saved.'))
        except Exception as e:
            print(_('   ⚠️ Could not save environment snapshot: {}').format(e))

    def _sort_packages_for_install(self, packages: List[str], strategy: str) -> List[str]:
        """
        Sorts packages for installation based on the chosen strategy.
        - 'latest-active': Sorts oldest to newest to ensure the last one installed is the latest.
        - 'stable-main': Sorts newest to oldest to minimize environmental changes.
        """
        from packaging.version import parse as parse_version, InvalidVersion
        import re

        def get_version_key(pkg_spec):
            """Extracts a sortable version key from a package spec."""
            match = re.search('(==|>=|<=|>|<|~=)(.+)', pkg_spec)
            if match:
                version_str = match.group(2).strip()
                try:
                    return parse_version(version_str)
                except InvalidVersion:
                    return parse_version('0.0.0')
            return parse_version('9999.0.0')
        should_reverse = strategy == 'stable-main'
        return sorted(packages, key=get_version_key, reverse=should_reverse)
        
    def adopt_interpreter(self, version: str) -> int:
        """
        Safely adopts a Python version by copying it into the environment.
        """
        print(f'🐍 Attempting to adopt Python {version} into the environment...')
        discovered_pythons = self.config_manager.list_available_pythons()
        source_path_str = discovered_pythons.get(version)
        
        if not source_path_str:
            print(f'   - No local Python {version} found. Falling back to download strategy.')
            return self._fallback_to_download(version)
        
        source_exe_path = Path(source_path_str)
        
        try:
            # Step 1: Get the Python installation root (sys.prefix)
            cmd = [str(source_exe_path), '-c', 'import sys; print(sys.prefix)']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            source_root_raw = result.stdout.strip()
            
            # Step 2: Resolve to canonical paths (handles symlinks, relative paths, etc.)
            source_root = Path(os.path.realpath(source_root_raw))
            current_venv_root = Path(os.path.realpath(str(self.config_manager.venv_path)))
            
            print(f'   - Source root: {source_root}')
            print(f'   - Current venv: {current_venv_root}')
            
            # SAFETY CHECK 1: Prevent recursive copy of our own environment
            if self._is_same_or_child_path(source_root, current_venv_root):
                print('   - ⚠️  SAFETY: Source is within current environment. Skipping copy.')
                return self._fallback_to_download(version)
            
            # SAFETY CHECK 2: Validate source directory structure
            if not self._is_valid_python_installation(source_root, source_exe_path):
                print('   - ⚠️  SAFETY: Source doesn\'t look like a valid Python installation.')
                return self._fallback_to_download(version)
            
            # SAFETY CHECK 3: Size check to prevent copying massive directories
            estimated_size = self._estimate_directory_size(source_root)
            if estimated_size > 2 * 1024 * 1024 * 1024:  # 2GB limit
                print(f'   - ⚠️  SAFETY: Source directory too large ({estimated_size / (1024*1024*1024):.1f}GB). Skipping.')
                return self._fallback_to_download(version)
            
            # SAFETY CHECK 4: Prevent copying system-critical directories
            if self._is_system_critical_path(source_root):
                print(f'   - ⚠️  SAFETY: Source is a system-critical directory. Skipping.')
                return self._fallback_to_download(version)
            
            # Prepare destination
            dest_root = self.config_manager.venv_path / '.omnipkg' / 'interpreters' / f'cpython-{version}'
            
            # Check if already exists
            if dest_root.exists():
                print(f'   - ✅ Adopted copy of Python {version} already exists.')
                self.config_manager._register_all_interpreters(self.config_manager.venv_path)
                return 0
            
            # Perform the safe copy
            print(f'   - Starting safe copy operation...')
            return self._perform_safe_copy(source_root, dest_root, version)
            
        except Exception as e:
            print(f'   - ❌ Copy operation failed: {e}')
            return self._fallback_to_download(version)

    def _is_same_or_child_path(self, source: Path, target: Path) -> bool:
        """Check if source is the same as target or a child of target."""
        try:
            source = source.resolve()
            target = target.resolve()
            if source == target:
                return True
            try:
                source.relative_to(target)
                return True
            except ValueError:
                return False
        except (OSError, RuntimeError):
            return True

    def _is_valid_python_installation(self, root: Path, exe_path: Path) -> bool:
        """Validate that the source looks like a proper Python installation."""
        try:
            if not exe_path.exists():
                return False
            try:
                exe_path.resolve().relative_to(root.resolve())
            except ValueError:
                return False
            expected_dirs = ['lib', 'bin']
            if sys.platform == 'win32':
                expected_dirs = ['Lib', 'Scripts']
            has_expected_structure = any((root / d).exists() for d in expected_dirs)
            test_cmd = [str(exe_path), '-c', 'import sys, os']
            test_result = subprocess.run(test_cmd, capture_output=True, timeout=5)
            return has_expected_structure and test_result.returncode == 0
        except Exception:
            return False

    def _estimate_directory_size(self, path: Path, max_files_to_check: int = 1000) -> int:
        """Estimate directory size with early termination for safety."""
        total_size = 0
        file_count = 0
        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith(('.git', '__pycache__', '.mypy_cache', 'node_modules'))]
                for file in files:
                    if file_count >= max_files_to_check:
                        return total_size * 10
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except (OSError, IOError):
                        continue
        except Exception:
            return float('inf')
        return total_size

    def _is_system_critical_path(self, path: Path) -> bool:
        """Check if path is a system-critical directory that shouldn't be copied."""
        critical_paths = [
            Path('/'), Path('/usr'), Path('/usr/local'), Path('/System'), Path('/Library'),
            Path('/opt'), Path('/bin'), Path('/sbin'), Path('/etc'), Path('/var'),
            Path('/tmp'), Path('/proc'), Path('/dev'), Path('/sys'),
        ]
        if sys.platform == 'win32':
            critical_paths.extend([
                Path('C:\\Windows'), Path('C:\\Program Files'),
                Path('C:\\Program Files (x86)'), Path('C:\\System32'),
            ])
        try:
            resolved_path = path.resolve()
            for critical in critical_paths:
                if resolved_path == critical.resolve():
                    return True
            return False
        except Exception:
            return True

    def _perform_safe_copy(self, source: Path, dest: Path, version: str) -> int:
        """Perform the actual copy operation with additional safety measures."""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            def ignore_patterns(dir, files):
                ignored = []
                for file in files:
                    if file in {'.git', '__pycache__', '.mypy_cache', '.pytest_cache', 
                                '.tox', '.coverage', 'node_modules', '.DS_Store'}:
                        ignored.append(file)
                    try:
                        filepath = os.path.join(dir, file)
                        if os.path.isfile(filepath) and os.path.getsize(filepath) > 50 * 1024 * 1024:
                            ignored.append(file)
                    except OSError:
                        pass
                return ignored
            print(f'   - Copying {source} -> {dest}')
            shutil.copytree(source, dest, symlinks=True, ignore=ignore_patterns, dirs_exist_ok=False)
            copied_python = self._find_python_executable_in_dir(dest)
            if not copied_python or not copied_python.exists():
                print('   - ❌ Copy completed but Python executable not found in destination')
                shutil.rmtree(dest, ignore_errors=True)
                return self._fallback_to_download(version)
            test_cmd = [str(copied_python), '-c', 'import sys; print(sys.version)']
            test_result = subprocess.run(test_cmd, capture_output=True, timeout=10)
            if test_result.returncode != 0:
                print('   - ❌ Copied Python executable failed basic test')
                shutil.rmtree(dest, ignore_errors=True)
                return self._fallback_to_download(version)
            print(f'   - ✅ Copy successful and verified!')
            self.config_manager._register_all_interpreters(self.config_manager.venv_path)
            print(f'\n🎉 Successfully adopted Python {version} from local source!')
            print(f"   You can now use 'omnipkg swap python {version}'")
            return 0
        except Exception as e:
            print(f'   - ❌ Copy operation failed: {e}')
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            return self._fallback_to_download(version)

    def _find_python_executable_in_dir(self, directory: Path) -> Path:
        """Find the Python executable in a copied directory."""
        possible_names = ['python', 'python3', 'python.exe']
        possible_dirs = ['bin', 'Scripts', '.']
        for subdir in possible_dirs:
            for name in possible_names:
                candidate = directory / subdir / name
                if candidate.exists() and candidate.is_file():
                    return candidate
        return None

    def _fallback_to_download(self, version: str) -> int:
        """Fallback to downloading Python using your existing download mechanism."""
        print('\n--- Falling back to download strategy ---')
        try:
            full_versions = {'3.12': '3.12.3', '3.10': '3.10.13', '3.9': '3.9.18', '3.11': '3.11.6'}
            full_version = full_versions.get(version)
            if not full_version:
                print(f'❌ Error: No known standalone build for Python {version}.')
                return 1
            dest_path = self.config_manager.venv_path / '.omnipkg' / 'interpreters' / f'cpython-{full_version}'
            if dest_path.exists():
                print(f'✅ Downloaded version of Python {full_version} already exists.')
            else:
                self.config_manager._install_managed_python(self.config_manager.venv_path, full_version)
            self.config_manager._register_all_interpreters(self.config_manager.venv_path)
            print(f'\n🎉 Successfully adopted Python {full_version} via download!')
            print(f"   You can now use 'omnipkg swap python {version}'")
            return 0
        except Exception as e:
            print(f'❌ Download strategy failed: {e}')
            return 1

    def smart_install(self, packages: List[str], dry_run: bool=False) -> int:
        if not self.connect_redis():
            return 1
        if dry_run:
            print(_('🔬 Running in --dry-run mode. No changes will be made.'))
            return 0
        if not packages:
            print('🚫 No packages specified for installation.')
            return 1
        install_strategy = self.config.get('install_strategy', 'stable-main')
        packages_to_process = list(packages)
        for pkg_spec in list(packages_to_process):
            pkg_name, requested_version = self._parse_package_spec(pkg_spec)
            self._synchronize_knowledge_base_with_reality()
            if pkg_name.lower() == 'omnipkg':
                packages_to_process.remove(pkg_spec)
                active_omnipkg_version = self.get_active_version_from_environment('omnipkg')
                if not active_omnipkg_version:
                    print('⚠️ Warning: Cannot determine active omnipkg version. Proceeding with caution.')
                if requested_version and active_omnipkg_version and (parse_version(requested_version) == parse_version(active_omnipkg_version)):
                    print('✅ omnipkg=={} is already the active omnipkg. No bubble needed.'.format(requested_version))
                    continue
                print("✨ Special handling: omnipkg '{}' requested. This will be installed into an isolated bubble, not as the active omnipkg.".format(pkg_spec))
                if not requested_version:
                    print('  (No version specified for omnipkg; attempting to bubble the latest stable version)')
                    print("  Skipping bubbling of 'omnipkg' without a specific version for now.")
                    continue
                bubble_dir_name = 'omnipkg-{}'.format(requested_version)
                target_bubble_path = Path(self.config['multiversion_base']) / bubble_dir_name
                wheel_url = self.get_wheel_url_from_pypi(pkg_name, requested_version)
                if not wheel_url:
                    print('❌ Could not find a compatible wheel for omnipkg=={}. Cannot create bubble.'.format(requested_version))
                    continue
                if not self.extract_wheel_into_bubble(wheel_url, target_bubble_path, pkg_name, requested_version):
                    print('❌ Failed to create bubble for omnipkg=={}.'.format(requested_version))
                    continue
                self.register_package_in_knowledge_base(pkg_name, requested_version, str(target_bubble_path), 'bubble')
                print('✅ omnipkg=={} successfully bubbled.'.format(requested_version))
                print('🧠 Updating knowledge base for bubbled omnipkg...')
                fake_before = {}
                fake_after = {pkg_name: requested_version}
                self.run_metadata_builder_for_delta(fake_before, fake_after)
                print('✅ Knowledge base updated for bubbled omnipkg.')
        if not packages_to_process:
            print(_('\n🎉 All package operations complete.'))
            return 0
        print("🚀 Starting install with policy: '{}'".format(install_strategy))
        resolved_packages = self._resolve_package_versions(packages_to_process)
        if not resolved_packages:
            print(_('❌ Could not resolve any packages to install. Aborting.'))
            return 1
        sorted_packages = self._sort_packages_for_install(resolved_packages, strategy=install_strategy)
        if sorted_packages != resolved_packages:
            print('🔄 Reordered packages for optimal installation: {}'.format(', '.join(sorted_packages)))
        user_requested_cnames = {canonicalize_name(self._parse_package_spec(p)[0]) for p in packages}
        any_installations_made = False
        for package_spec in sorted_packages:
            print('\n' + '─' * 60)
            print('📦 Processing: {}'.format(package_spec))
            print('─' * 60)
            satisfaction_check = self._check_package_satisfaction([package_spec], strategy=install_strategy)
            if satisfaction_check['all_satisfied']:
                print('✅ Requirement already satisfied: {}'.format(package_spec))
                continue
            packages_to_install = satisfaction_check['needs_install']
            if not packages_to_install:
                continue
            print(_('\n📸 Taking LIVE pre-installation snapshot...'))
            packages_before = self.get_installed_packages(live=True)
            print('    - Found {} packages'.format(len(packages_before)))
            print('\n⚙️ Running pip install for: {}...'.format(', '.join(packages_to_install)))
            return_code = self._run_pip_install(packages_to_install)
            if return_code != 0:
                print('❌ Pip installation failed for {}. Continuing...'.format(package_spec))
                continue
            any_installations_made = True
            print('✅ Installation completed for: {}'.format(package_spec))
            print(_('\n🔬 Analyzing post-installation changes...'))
            packages_after = self.get_installed_packages(live=True)
            replacements = self._detect_version_replacements(packages_before, packages_after)
            if replacements:
                for rep in replacements:
                    self._cleanup_version_from_kb(rep['package'], rep['old_version'])
            bubbled_packages = []
            main_env_updates = []
            if install_strategy == 'stable-main':
                downgrades_to_fix = self._detect_downgrades(packages_before, packages_after)
                upgrades_to_fix = self._detect_upgrades(packages_before, packages_after)
                all_changes_to_fix = []
                for fix in downgrades_to_fix:
                    all_changes_to_fix.append({'package': fix['package'], 'old_version': fix['good_version'], 'new_version': fix['bad_version'], 'change_type': 'downgraded'})
                for fix in upgrades_to_fix:
                    all_changes_to_fix.append({'package': fix['package'], 'old_version': fix['old_version'], 'new_version': fix['new_version'], 'change_type': 'upgraded'})
                if all_changes_to_fix:
                    print(_('\n🛡️ STABILITY PROTECTION ACTIVATED!'))
                    for fix in all_changes_to_fix:
                        print('    -> Protecting stable env. Bubbling {} version: {} v{}'.format(fix['change_type'], fix['package'], fix['new_version']))
                        bubble_created = self.bubble_manager.create_isolated_bubble(fix['package'], fix['new_version'])
                        if bubble_created:
                            bubbled_packages.append({'name': fix['package'], 'version': fix['new_version']})
                            print('    ✅ Tracked {} v{} for KB update'.format(fix['package'], fix['new_version']))
                            bubble_path_str = str(self.multiversion_base / f"{fix['package']}-{fix['new_version']}")
                            self.hook_manager.refresh_bubble_map(fix['package'], fix['new_version'], bubble_path_str)
                            self.hook_manager.validate_bubble(fix['package'], fix['new_version'])
                            print("    🔄 Restoring '{}' to stable version v{} in main environment...".format(fix['package'], fix['old_version']))
                            restore_result = subprocess.run([self.config['python_executable'], '-m', 'pip', 'install', '--quiet', f"{fix['package']}=={fix['old_version']}"], capture_output=True, text=True)
                            if restore_result.returncode == 0:
                                main_env_updates.append({'name': fix['package'], 'version': fix['old_version']})
                                print('    ✅ Successfully restored {} v{} to main environment'.format(fix['package'], fix['old_version']))
                            else:
                                print('    ❌ Failed to restore {} v{} to main environment'.format(fix['package'], fix['old_version']))
                        else:
                            print('    ❌ Failed to create bubble for {} v{}. Skipping KB update for this package.'.format(fix['package'], fix['new_version']))
                    print(_('\n✅ Stability protection complete!'))
                else:
                    print(_('✅ No changes to existing packages detected. Installation completed safely.'))
                    for pkg_name, version in packages_after.items():
                        if pkg_name not in packages_before:
                            main_env_updates.append({'name': pkg_name, 'version': version})
            elif install_strategy == 'latest-active':
                versions_to_bubble = []
                for pkg_name in set(packages_before.keys()) | set(packages_after.keys()):
                    old_version = packages_before.get(pkg_name)
                    new_version = packages_after.get(pkg_name)
                    if old_version and new_version and (old_version != new_version):
                        change_type = 'upgraded' if parse_version(new_version) > parse_version(old_version) else 'downgraded'
                        versions_to_bubble.append({'package': pkg_name, 'version_to_bubble': old_version, 'version_staying_active': new_version, 'change_type': change_type, 'user_requested': canonicalize_name(pkg_name) in user_requested_cnames})
                    elif not old_version and new_version:
                        print('    ✅ New package installed: {} v{} (active in main environment)'.format(pkg_name, new_version))
                        main_env_updates.append({'name': pkg_name, 'version': new_version})
                if versions_to_bubble:
                    print(_('\n🛡️ LATEST-ACTIVE STRATEGY: Preserving replaced versions in bubbles'))
                    for item in versions_to_bubble:
                        request_type = 'requested' if item['user_requested'] else 'dependency'
                        print('    -> Bubbling replaced {} version: {} v{} (keeping v{} active)'.format(request_type, item['package'], item['version_to_bubble'], item['version_staying_active']))
                        bubble_created = self.bubble_manager.create_isolated_bubble(item['package'], item['version_to_bubble'])
                        if bubble_created:
                            bubbled_packages.append({'name': item['package'], 'version': item['version_to_bubble']})
                            bubble_path_str = str(self.multiversion_base / f"{item['package']}-{item['version_to_bubble']}")
                            self.hook_manager.refresh_bubble_map(item['package'], item['version_to_bubble'], bubble_path_str)
                            self.hook_manager.validate_bubble(item['package'], item['version_to_bubble'])
                            main_env_updates.append({'name': item['package'], 'version': item['version_staying_active']})
                            print('    ✅ Successfully bubbled {} v{}'.format(item['package'], item['version_to_bubble']))
                        else:
                            print('    ❌ Failed to bubble {} v{}'.format(item['package'], item['version_to_bubble']))
                    print(_('\n✅ Latest-active complete! Requested versions active, previous versions preserved.'))
                else:
                    print(_('✅ No version changes detected.'))
            print('\n🧠 Updating knowledge base for main environment...')
            current_main_state = self.get_installed_packages(live=True)
            packages_actually_installed = set(packages_after.keys()) - set(packages_before.keys())
            packages_with_version_changes = {pkg for pkg in packages_after.keys() if pkg in packages_before and packages_before[pkg] != packages_after[pkg]}
            all_packages_needing_kb_update = packages_actually_installed | packages_with_version_changes
            if all_packages_needing_kb_update or any_installations_made:
                self._run_metadata_builder_for_delta(packages_before, current_main_state)
                self._update_hash_index_for_delta(packages_before, current_main_state)
                print(_('✅ Knowledge base updated successfully.'))
            else:
                print(_('✅ Knowledge base is already up to date.'))
            if main_env_updates:
                print('🧠 Updating knowledge base for {} restored/modified package(s) in main environment...'.format(len(main_env_updates)))
                for restored_pkg in main_env_updates:
                    fake_before = {}
                    fake_after = {restored_pkg['name']: restored_pkg['version']}
                    print('    -> Updating KB for {} v{} in main environment...'.format(restored_pkg['name'], restored_pkg['version']))
                    self._run_metadata_builder_for_delta(fake_before, fake_after)
                print('✅ Knowledge base updated for restored packages in main environment.')
            if bubbled_packages:
                print('🧠 Updating knowledge base for {} bubbled package(s)...'.format(len(bubbled_packages)))
                for bubbled_pkg in bubbled_packages:
                    print('    -> Updating KB for bubbled package: {} v{}...'.format(bubbled_pkg['name'], bubbled_pkg['version']))
                    fake_before = {}
                    fake_after = {bubbled_pkg['name']: bubbled_pkg['version']}
                    self._run_metadata_builder_for_delta(fake_before, fake_after)
                    print('    ✅ KB update completed for {} v{}'.format(bubbled_pkg['name'], bubbled_pkg['version']))
                print('✅ Knowledge base updated for bubbled packages.')
            else:
                print(_('ℹ️ No packages were bubbled during this installation.'))
        if not any_installations_made:
            print(_('\n✅ All requirements were already satisfied.'))
            self._synchronize_knowledge_base_with_reality()
            return 0
        print(_('\n🧹 Performing final cleanup of redundant bubbles...'))
        final_active_packages = self.get_installed_packages(live=True)
        for pkg_name, active_version in final_active_packages.items():
            bubble_path = self.multiversion_base / f'{pkg_name}-{active_version}'
            if bubble_path.exists() and bubble_path.is_dir():
                print("    -> Found redundant bubble for active package '{0}=={1}'. Removing...".format(pkg_name, active_version))
                try:
                    import shutil
                    shutil.rmtree(bubble_path)
                    print(_('    ✅ Removed redundant bubble directory: {}').format(bubble_path))
                    if hasattr(self, 'hook_manager'):
                        self.hook_manager.remove_bubble_from_tracking(pkg_name, active_version)
                except Exception as e:
                    print(_('    ❌ Failed to remove bubble directory: {}').format(e))
        print('\n' + '=' * 60)
        print(_('🎉 All package operations complete.'))
        self._save_last_known_good_snapshot()
        self._synchronize_knowledge_base_with_reality()
        return 0

    def _get_active_version_from_environment(self, pkg_name: str) -> Optional[str]:
        """
        Gets the version of a package actively installed in the current Python environment
        using pip show.
        """
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', pkg_name], capture_output=True, text=True, check=True)
            output = result.stdout
            for line in output.splitlines():
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
            return None
        except subprocess.CalledProcessError:
            return None
        except Exception as e:
            print(_('Error getting active version of {}: {}').format(pkg_name, e))
            return None

    def _detect_version_replacements(self, before: Dict, after: Dict) -> List[Dict]:
        """
        Identifies packages that were replaced (uninstalled and a new version installed).
        This is different from a simple upgrade/downgrade list.
        """
        replacements = []
        for pkg_name, old_version in before.items():
            if pkg_name in after and after[pkg_name] != old_version:
                replacements.append({'package': pkg_name, 'old_version': old_version, 'new_version': after[pkg_name]})
        return replacements

    def _cleanup_version_from_kb(self, package_name: str, version: str):
        """
        Surgically removes all traces of a single, specific version of a package
        from the Redis knowledge base.
        """
        print(_('   -> Cleaning up replaced version from knowledge base: {} v{}').format(package_name, version))
        c_name = canonicalize_name(package_name)
        main_key = f'{self.redis_key_prefix}{c_name}'
        version_key = f'{main_key}:{version}'
        versions_set_key = f'{main_key}:installed_versions'
        with self.redis_client.pipeline() as pipe:
            pipe.delete(version_key)
            pipe.srem(versions_set_key, version)
            pipe.hdel(main_key, f'bubble_version:{version}')
            if self.redis_client.hget(main_key, 'active_version') == version:
                pipe.hdel(main_key, 'active_version')
            pipe.execute()

    def _restore_from_snapshot(self, snapshot: Dict, current_state: Dict):
        """Restores the main environment to the exact state of a given snapshot."""
        print(_('🔄 Restoring main environment from snapshot...'))
        snapshot_keys = set(snapshot.keys())
        current_keys = set(current_state.keys())
        to_uninstall = [pkg for pkg in current_keys if pkg not in snapshot_keys]
        to_install_or_fix = ['{}=={}'.format(pkg, ver) for pkg, ver in snapshot.items() if pkg not in current_keys or current_state.get(pkg) != ver]
        if not to_uninstall and (not to_install_or_fix):
            print(_('   ✅ Environment is already in its original state.'))
            return
        if to_uninstall:
            print(_('   -> Uninstalling: {}').format(', '.join(to_uninstall)))
            self._run_pip_uninstall(to_uninstall)
        if to_install_or_fix:
            print(_('   -> Installing/Fixing: {}').format(', '.join(to_install_or_fix)))
            self._run_pip_install(to_install_or_fix + ['--no-deps'])
        print(_('   ✅ Environment restored.'))

    def _extract_wheel_into_bubble(self, wheel_url: str, target_bubble_path: Path, pkg_name: str, pkg_version: str) -> bool:
        """
        Downloads a wheel and extracts its content directly into a bubble directory.
        Does NOT use pip install.
        """
        print(_('📦 Downloading wheel for {}=={}...').format(pkg_name, pkg_version))
        try:
            response = self.http_session.get(wheel_url, stream=True)
            response.raise_for_status()
            target_bubble_path.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                for member in zf.namelist():
                    if member.startswith((_('{}-{}.dist-info').format(pkg_name, pkg_version), _('{}-{}.data').format(pkg_name, pkg_version))):
                        continue
                    try:
                        zf.extract(member, target_bubble_path)
                    except Exception as extract_error:
                        print(_('⚠️ Warning: Could not extract {}: {}').format(member, extract_error))
                        continue
            print(_('✅ Extracted {}=={} to {}').format(pkg_name, pkg_version, target_bubble_path.name))
            return True
        except http_requests.exceptions.RequestException as e:
            print(_('❌ Failed to download wheel from {}: {}').format(wheel_url, e))
            return False
        except zipfile.BadZipFile:
            print(_('❌ Downloaded file is not a valid wheel: {}').format(wheel_url))
            return False
        except Exception as e:
            print(_('❌ Error extracting wheel for {}=={}: {}').format(pkg_name, pkg_version, e))
            return False

    def _get_wheel_url_from_pypi(self, pkg_name: str, pkg_version: str) -> Optional[str]:
        """Fetches the wheel URL for a specific package version from PyPI."""
        pypi_url = f'https://pypi.org/pypi/{pkg_name}/{pkg_version}/json'
        try:
            response = self.http_session.get(pypi_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            py_major = sys.version_info.major
            py_minor = sys.version_info.minor
            wheel_priorities = [lambda f: f'py{py_major}{py_minor}' in f and 'manylinux' in f, lambda f: any((compat in f for compat in [f'py{py_major}', 'py2.py3', 'py3'])) and 'manylinux' in f, lambda f: 'py2.py3-none-any' in f or 'py3-none-any' in f, lambda f: True]
            for priority_check in wheel_priorities:
                for url_info in data.get('urls', []):
                    if url_info['packagetype'] == 'bdist_wheel' and priority_check(url_info['filename']):
                        print(_('🎯 Found compatible wheel: {}').format(url_info['filename']))
                        return url_info['url']
            for url_info in data.get('urls', []):
                if url_info['packagetype'] == 'sdist':
                    print(_('⚠️ Only source distribution available for {}=={}').format(pkg_name, pkg_version))
                    print(_('   This may require compilation and is not recommended for bubbling.'))
                    return None
            print(_('❌ No compatible wheel or source found for {}=={} on PyPI.').format(pkg_name, pkg_version))
            return None
        except http_requests.exceptions.RequestException as e:
            print(_('❌ Failed to fetch PyPI data for {}=={}: {}').format(pkg_name, pkg_version, e))
            return None
        except KeyError as e:
            print(_('❌ Unexpected PyPI response structure: missing {}').format(e))
            return None
        except Exception as e:
            print(_('❌ Error parsing PyPI data: {}').format(e))
            return None

    def _parse_package_spec(self, pkg_spec: str) -> tuple[str, Optional[str]]:
        """
        Parse a package specification like 'package==1.0.0' or 'package>=2.0'
        Returns (package_name, version) where version is None if no version specified.
        """
        version_separators = ['==', '>=', '<=', '>', '<', '~=', '!=']
        for separator in version_separators:
            if separator in pkg_spec:
                parts = pkg_spec.split(separator, 1)
                if len(parts) == 2:
                    pkg_name = parts[0].strip()
                    version = parts[1].strip()
                    if separator == '==':
                        return (pkg_name, version)
                    else:
                        print(_("⚠️ Version specifier '{}' detected in '{}'. Exact version required for bubbling.").format(separator, pkg_spec))
                        return (pkg_name, None)
        return (pkg_spec.strip(), None)

    def _register_package_in_knowledge_base(self, pkg_name: str, version: str, bubble_path: str, install_type: str):
        """
        Register a bubbled package in the knowledge base.
        This integrates with your existing knowledge base system.
        """
        try:
            package_info = {'name': pkg_name, 'version': version, 'install_type': install_type, 'path': bubble_path, 'created_at': self._get_current_timestamp()}
            key = 'package:{}:{}'.format(pkg_name, version)
            if hasattr(self, 'redis_client') and self.redis_client:
                import json
                self.redis_client.set(key, json.dumps(package_info))
                print(_('📝 Registered {}=={} in knowledge base').format(pkg_name, version))
            else:
                print(_('⚠️ Could not register {}=={}: No Redis connection').format(pkg_name, version))
        except Exception as e:
            print(_('❌ Failed to register {}=={} in knowledge base: {}').format(pkg_name, version, e))

    def _get_current_timestamp(self) -> str:
        """Helper to get current timestamp for knowledge base entries."""
        import datetime
        return datetime.datetime.now().isoformat()

    def _find_package_installations(self, package_name: str) -> List[Dict]:
        """
        Find all installations of a package by querying the Redis knowledge base.
        This is the single source of truth for omnipkg's state.
        """
        found = []
        c_name = canonicalize_name(package_name)
        main_key = f'{self.redis_key_prefix}{c_name}'
        package_data = self.redis_client.hgetall(main_key)
        if not package_data:
            return []
        for key, value in package_data.items():
            if key == 'active_version':
                found.append({'name': package_data.get('name', c_name), 'version': value, 'type': 'active', 'path': 'Main Environment'})
            elif key.startswith('bubble_version:') and value == 'true':
                version = key.replace('bubble_version:', '')
                bubble_path = self.multiversion_base / '{}-{}'.format(package_data.get('name', c_name), version)
                found.append({'name': package_data.get('name', c_name), 'version': version, 'type': 'bubble', 'path': str(bubble_path)})
        return found

    def smart_uninstall(self, packages: List[str], force: bool=False, install_type: Optional[str]=None) -> int:
        if not self.connect_redis():
            return 1
        self._synchronize_knowledge_base_with_reality()
        for pkg_spec in packages:
            print(_('\nProcessing uninstall for: {}').format(pkg_spec))
            pkg_name, specific_version = self._parse_package_spec(pkg_spec)
            exact_pkg_name = canonicalize_name(pkg_name)
            all_installations_found = self._find_package_installations(exact_pkg_name)
            if all_installations_found:
                all_installations_found.sort(key=lambda x: (x['type'] != 'active', parse_version(x.get('version', '0'))), reverse=False)
            if not all_installations_found:
                print(_("🤷 Package '{}' not found.").format(pkg_name))
                continue
            to_uninstall = all_installations_found
            if specific_version:
                to_uninstall = [inst for inst in to_uninstall if inst['version'] == specific_version]
                if not to_uninstall:
                    print(_("🤷 Version '{}' of '{}' not found.").format(specific_version, pkg_name))
                    continue
            if install_type:
                to_uninstall = [inst for inst in to_uninstall if inst['type'] == install_type]
                if not to_uninstall:
                    print(_('🤷 No installations match the specified criteria.').format(pkg_name))
                    continue
            elif not force and len(all_installations_found) > 1 and (not (specific_version or install_type)):
                print(_("Found multiple installations for '{}':").format(pkg_name))
                numbered_installations = []
                for i, inst in enumerate(to_uninstall):
                    is_protected = inst['type'] == 'active' and (canonicalize_name(inst['name']) == 'omnipkg' or canonicalize_name(inst['name']) in OMNIPKG_CORE_DEPS)
                    status_tags = [inst['type']]
                    if is_protected:
                        status_tags.append('PROTECTED')
                    numbered_installations.append({'index': i + 1, 'installation': inst, 'is_protected': is_protected})
                    print(_('  {}) v{} ({})').format(i + 1, inst['version'], ', '.join(status_tags)))
                if not numbered_installations:
                    print(_('🤷 No versions available for selection.'))
                    continue
                try:
                    choice = input(_("🤔 Enter numbers to uninstall (e.g., '1,2'), 'all', or press Enter to cancel: ")).lower().strip()
                    if not choice:
                        print(_('🚫 Uninstall cancelled.'))
                        continue
                    selected_indices = []
                    if choice == 'all':
                        selected_indices = [item['index'] for item in numbered_installations if not item['is_protected']]
                    else:
                        try:
                            selected_indices = {int(idx.strip()) for idx in choice.split(',')}
                        except ValueError:
                            print(_('❌ Invalid input.'))
                            continue
                    to_uninstall = [item['installation'] for item in numbered_installations if item['index'] in selected_indices]
                except (KeyboardInterrupt, EOFError):
                    print(_('\n🚫 Uninstall cancelled.'))
                    continue
            final_to_uninstall = []
            for item in to_uninstall:
                is_protected = item['type'] == 'active' and (canonicalize_name(item['name']) == 'omnipkg' or canonicalize_name(item['name']) in OMNIPKG_CORE_DEPS)
                if is_protected:
                    print(_('⚠️  Skipping protected package: {} v{} (active)').format(item['name'], item['version']))
                else:
                    final_to_uninstall.append(item)
            if not final_to_uninstall:
                print(_('🤷 No versions selected for uninstallation after protection checks.'))
                continue
            print(_("\nPreparing to remove {} installation(s) for '{}':").format(len(final_to_uninstall), exact_pkg_name))
            for item in final_to_uninstall:
                print(_('  - v{} ({})').format(item['version'], item['type']))
            if not force:
                confirm = input(_('🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
                if confirm != 'y':
                    print(_('🚫 Uninstall cancelled.'))
                    continue
            for item in final_to_uninstall:
                if item['type'] == 'active':
                    print(_("🗑️ Uninstalling '{}=={}' from main environment via pip...").format(item['name'], item['version']))
                    self._run_pip_uninstall([f"{item['name']}=={item['version']}"])
                elif item['type'] == 'bubble':
                    bubble_dir = Path(item['path'])
                    if bubble_dir.exists():
                        print(_('🗑️  Deleting bubble directory: {}').format(bubble_dir.name))
                        shutil.rmtree(bubble_dir)
                print(_('🧹 Cleaning up knowledge base for {} v{}...').format(item['name'], item['version']))
                c_name = canonicalize_name(item['name'])
                main_key = f'{self.redis_key_prefix}{c_name}'
                version_key = f"{main_key}:{item['version']}"
                versions_set_key = _('{}:installed_versions').format(main_key)
                with self.redis_client.pipeline() as pipe:
                    pipe.delete(version_key)
                    pipe.srem(versions_set_key, item['version'])
                    if item['type'] == 'active':
                        pipe.hdel(main_key, 'active_version')
                    else:
                        pipe.hdel(main_key, f"bubble_version:{item['version']}")
                    pipe.execute()
                if self.redis_client.scard(versions_set_key) == 0:
                    print(_("    -> Last version of '{}' removed. Deleting all traces.").format(c_name))
                    self.redis_client.delete(main_key, versions_set_key)
                    self.redis_client.srem(f'{self.redis_key_prefix}index', c_name)
            print(_('✅ Uninstallation complete.'))
            self._save_last_known_good_snapshot()
        return 0

    def revert_to_last_known_good(self, force: bool=False):
        """Compares the current env to the last snapshot and restores it."""
        if not self.connect_redis():
            return 1
        snapshot_key = f'{self.redis_key_prefix}snapshot:last_known_good'
        snapshot_data = self.redis_client.get(snapshot_key)
        if not snapshot_data:
            print(_("❌ No 'last known good' snapshot found. Cannot revert."))
            print(_('   Run an `omnipkg install` or `omnipkg uninstall` command to create one.'))
            return 1
        print(_('⚖️  Comparing current environment to the last known good snapshot...'))
        snapshot_state = json.loads(snapshot_data)
        current_state = self.get_installed_packages(live=True)
        snapshot_keys = set(snapshot_state.keys())
        current_keys = set(current_state.keys())
        to_install = ['{}=={}'.format(pkg, ver) for pkg, ver in snapshot_state.items() if pkg not in current_keys]
        to_uninstall = [pkg for pkg in current_keys if pkg not in snapshot_keys]
        to_fix = [f'{pkg}=={snapshot_state[pkg]}' for pkg in snapshot_keys & current_keys if snapshot_state[pkg] != current_state[pkg]]
        if not to_install and (not to_uninstall) and (not to_fix):
            print(_('✅ Your environment is already in the last known good state. No action needed.'))
            return 0
        print(_('\n📝 The following actions will be taken to restore the environment:'))
        if to_uninstall:
            print(_('  - Uninstall: {}').format(', '.join(to_uninstall)))
        if to_install:
            print(_('  - Install: {}').format(', '.join(to_install)))
        if to_fix:
            print(_('  - Fix Version: {}').format(', '.join(to_fix)))
        if not force:
            confirm = input(_('\n🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
            if confirm != 'y':
                print(_('🚫 Revert cancelled.'))
                return 1
        print(_('\n🚀 Starting revert operation...'))
        original_strategy = self.config.get('install_strategy', 'multiversion')
        strategy_changed = False
        try:
            if original_strategy != 'latest-active':
                print(_('   ⚙️  Temporarily setting install strategy to latest-active for revert...'))
                try:
                    result = subprocess.run(['omnipkg', 'config', 'set', 'install_strategy', 'latest-active'], capture_output=True, text=True, check=True)
                    strategy_changed = True
                    print(_('   ✅ Install strategy temporarily set to latest-active'))
                    from omnipkg.core import ConfigManager
                    self.config = ConfigManager().config
                except Exception as e:
                    print(_('   ⚠️  Failed to set install strategy to latest-active: {}').format(e))
                    print(_('   ℹ️  Continuing with current strategy: {}').format(original_strategy))
            else:
                print(_('   ℹ️  Install strategy already set to latest-active'))
            if to_uninstall:
                self.smart_uninstall(to_uninstall, force=True)
            packages_to_install = to_install + to_fix
            if packages_to_install:
                self.smart_install(packages_to_install)
            print(_('\n✅ Environment successfully reverted to the last known good state.'))
            return 0
        finally:
            if strategy_changed and original_strategy != 'latest-active':
                print(_('   🔄 Restoring original install strategy: {}').format(original_strategy))
                try:
                    result = subprocess.run(['omnipkg', 'config', 'set', 'install_strategy', original_strategy], capture_output=True, text=True, check=True)
                    print(_('   ✅ Install strategy restored to: {}').format(original_strategy))
                    from omnipkg.core import ConfigManager
                    self.config = ConfigManager().config
                except Exception as e:
                    print(_('   ⚠️  Failed to restore install strategy to {}: {}').format(original_strategy, e))
                    print(_('   💡 You may need to manually restore it with: omnipkg config set install_strategy {}').format(original_strategy))
            elif not strategy_changed:
                print(_('   ℹ️  Install strategy unchanged: {}').format(original_strategy))

    def _check_package_satisfaction(self, packages: List[str], strategy: str) -> dict:
        """
        ### THE DEFINITIVE FIX ###
        Checks if a list of requirements is satisfied by querying the Redis Knowledge Base,
        which is the single source of truth for omnipkg.
        """
        satisfied_specs = set()
        needs_install_specs = []
        for package_spec in packages:
            is_satisfied = False
            try:
                pkg_name, requested_version = self._parse_package_spec(package_spec)
                if not requested_version:
                    needs_install_specs.append(package_spec)
                    continue
                c_name = canonicalize_name(pkg_name)
                main_key = f'{self.redis_key_prefix}{c_name}'
                version_key = f'{main_key}:{requested_version}'
                if not self.redis_client.exists(version_key):
                    needs_install_specs.append(package_spec)
                    continue
                package_data = self.redis_client.hgetall(main_key)
                if package_data.get('active_version') == requested_version:
                    is_satisfied = True
                if not is_satisfied and strategy == 'stable-main':
                    if package_data.get(f'bubble_version:{requested_version}') == 'true':
                        is_satisfied = True
                if is_satisfied:
                    satisfied_specs.add(package_spec)
                else:
                    needs_install_specs.append(package_spec)
            except Exception:
                needs_install_specs.append(package_spec)
        return {'all_satisfied': len(needs_install_specs) == 0, 'satisfied': sorted(list(satisfied_specs)), 'needs_install': needs_install_specs}

    def get_package_info(self, package_name: str, version: str) -> Optional[Dict]:
        if not self.redis_client:
            self.connect_redis()
        main_key = f'{self.redis_key_prefix}{package_name.lower()}'
        if version == 'active':
            version = self.redis_client.hget(main_key, 'active_version')
            if not version:
                return None
        version_key = f'{main_key}:{version}'
        return self.redis_client.hgetall(version_key)

    def switch_active_python(self, version: str) -> int:
        """
        Switches the active Python context for the entire environment.
        This updates the config file and the default `python` symlinks.
        """
        print(_('🐍 Switching active Python context to version {}...').format(version))
        managed_interpreters = self.interpreter_manager.list_available_interpreters()
        target_interpreter_path = managed_interpreters.get(version)
        if not target_interpreter_path:
            print(_('❌ Error: Python version {} is not managed by this environment.').format(version))
            print(_("   Run 'omnipkg list python' to see managed interpreters."))
            print(f"   If Python {version} is 'Discovered', first adopt it with: omnipkg python adopt {version}")
            return 1
        target_interpreter_str = str(target_interpreter_path)
        print(_('   - Found managed interpreter at: {}').format(target_interpreter_str))
        new_paths = self.config_manager._get_paths_for_interpreter(target_interpreter_str)
        if not new_paths:
            print(f'❌ Error: Could not determine paths for Python {version}. Aborting switch.')
            return 1
        print(_('   - Updating configuration to new context...'))
        self.config_manager.set('python_executable', new_paths['python_executable'])
        self.config_manager.set('site_packages_path', new_paths['site_packages_path'])
        self.config_manager.set('multiversion_base', new_paths['multiversion_base'])
        print(_('   - ✅ Configuration saved.'))
        print(_('   - Updating default `python` symlinks...'))
        venv_path = Path(sys.prefix)
        try:
            self.config_manager._update_default_python_links(venv_path, target_interpreter_path)
        except Exception as e:
            print(_('   - ❌ Failed to update symlinks: {}').format(e))
        print(_('\n🎉 Successfully switched omnipkg context to Python {}!').format(version))
        print('   The configuration has been updated. To activate the new interpreter')
        print(_('   in your shell, you MUST re-source your activate script:'))
        print(_('\n      source {}\n').format(venv_path / 'bin' / 'activate'))
        print(_('Just kidding, omnipkg handled it for you automatically!'))
        return 0

    def adopt_interpreter(self, version: str) -> int:
        """
        Safely adopts a Python version by copying it into the environment.
        """
        print(f'🐍 Attempting to adopt Python {version} into the environment...')
        discovered_pythons = self.config_manager.list_available_pythons()
        source_path_str = discovered_pythons.get(version)
        
        if not source_path_str:
            print(f'   - No local Python {version} found. Falling back to download strategy.')
            return self._fallback_to_download(version)
        
        source_exe_path = Path(source_path_str)
        discovered_pythons = self.config_manager.list_available_pythons()
        source_path_str = discovered_pythons.get(version)
        
        if not source_path_str:
            print(f'   - No local Python {version} found. Falling back to download.')
            return self._fallback_to_download(version)
        
        source_exe_path = Path(source_path_str)
        print(f'   - Found potential source at: {source_exe_path}')
        
        try:
            # Step 1: Get the Python installation root (sys.prefix)
            cmd = [str(source_exe_path), '-c', 'import sys; print(sys.prefix)']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            source_root_raw = result.stdout.strip()
            
            # Step 2: Resolve to canonical paths (handles symlinks, relative paths, etc.)
            source_root = Path(os.path.realpath(source_root_raw))
            current_venv_root = Path(os.path.realpath(str(self.config_manager.venv_path)))
            
            print(f'   - Source root: {source_root}')
            print(f'   - Current venv: {current_venv_root}')
            
            # SAFETY CHECK 1: Prevent recursive copy of our own environment
            if self._is_same_or_child_path(source_root, current_venv_root):
                print('   - ⚠️  SAFETY: Source is within current environment. Skipping copy.')
                return self._fallback_to_download(version)
            
            # SAFETY CHECK 2: Validate source directory structure
            if not self._is_valid_python_installation(source_root, source_exe_path):
                print('   - ⚠️  SAFETY: Source doesn\'t look like a valid Python installation.')
                return self._fallback_to_download(version)
            
            # SAFETY CHECK 3: Size check to prevent copying massive directories
            estimated_size = self._estimate_directory_size(source_root)
            if estimated_size > 2 * 1024 * 1024 * 1024:  # 2GB limit
                print(f'   - ⚠️  SAFETY: Source directory too large ({estimated_size / (1024*1024*1024):.1f}GB). Skipping.')
                return self._fallback_to_download(version)
            
            # SAFETY CHECK 4: Prevent copying system-critical directories
            if self._is_system_critical_path(source_root):
                print(f'   - ⚠️  SAFETY: Source is a system-critical directory. Skipping.')
                return self._fallback_to_download(version)
            
            # Prepare destination
            dest_root = self.config_manager.venv_path / '.omnipkg' / 'interpreters' / f'cpython-{version}'
            
            # Check if already exists
            if dest_root.exists():
                print(f'   - ✅ Adopted copy of Python {version} already exists.')
                self.config_manager._register_all_interpreters(self.config_manager.venv_path)
                return 0
            
            # Perform the safe copy
            print(f'   - Starting safe copy operation...')
            return self._perform_safe_copy(source_root, dest_root, version)
            
        except Exception as e:
            print(f'   - ❌ Copy operation failed: {e}')
            return self._fallback_to_download(version)

    def _is_same_or_child_path(self, source: Path, target: Path) -> bool:
        """Check if source is the same as target or a child of target."""
        try:
            # Convert both to absolute paths
            source = source.resolve()
            target = target.resolve()
            
            # Check if they're identical
            if source == target:
                return True
                
            # Check if source is a child of target
            try:
                source.relative_to(target)
                return True
            except ValueError:
                return False
                
        except (OSError, RuntimeError):
            # If we can't resolve paths, err on the side of caution
            return True

    def _is_valid_python_installation(self, root: Path, exe_path: Path) -> bool:
        """Validate that the source looks like a proper Python installation."""
        try:
            # Check that the executable exists and is within the root
            if not exe_path.exists():
                return False
                
            # The executable should be within the installation root
            try:
                exe_path.resolve().relative_to(root.resolve())
            except ValueError:
                return False
            
            # Look for typical Python installation structure
            expected_dirs = ['lib', 'bin']  # Unix-like
            if sys.platform == 'win32':
                expected_dirs = ['Lib', 'Scripts']
                
            has_expected_structure = any((root / d).exists() for d in expected_dirs)
            
            # Additional check: try to run a simple command
            test_cmd = [str(exe_path), '-c', 'import sys, os']
            test_result = subprocess.run(test_cmd, capture_output=True, timeout=5)
            
            return has_expected_structure and test_result.returncode == 0
            
        except Exception:
            return False

    def _estimate_directory_size(self, path: Path, max_files_to_check: int = 1000) -> int:
        """Estimate directory size with early termination for safety."""
        total_size = 0
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(path):
                # Skip common large directories that aren't needed
                dirs[:] = [d for d in dirs if not d.startswith(('.git', '__pycache__', '.mypy_cache', 'node_modules'))]
                
                for file in files:
                    if file_count >= max_files_to_check:
                        # Extrapolate based on what we've seen so far
                        return total_size * 10  # Conservative estimate
                        
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except (OSError, IOError):
                        continue  # Skip files we can't read
                        
        except Exception:
            return float('inf')  # If we can't estimate, assume it's too big
            
        return total_size

    def _is_system_critical_path(self, path: Path) -> bool:
        """Check if path is a system-critical directory that shouldn't be copied."""
        critical_paths = [
            Path('/'),
            Path('/usr'),
            Path('/usr/local'),
            Path('/System'),  # macOS
            Path('/Library'),  # macOS
            Path('/opt'),
            Path('/bin'),
            Path('/sbin'),
            Path('/etc'),
            Path('/var'),
            Path('/tmp'),
            Path('/proc'),
            Path('/dev'),
            Path('/sys'),
        ]
        
        # Windows critical paths
        if sys.platform == 'win32':
            critical_paths.extend([
                Path('C:\\Windows'),
                Path('C:\\Program Files'),
                Path('C:\\Program Files (x86)'),
                Path('C:\\System32'),
            ])
        
        try:
            resolved_path = path.resolve()
            for critical in critical_paths:
                if resolved_path == critical.resolve():
                    return True
            return False
        except Exception:
            return True  # If we can't resolve, assume it's critical

    def _perform_safe_copy(self, source: Path, dest: Path, version: str) -> int:
        """Perform the actual copy operation with additional safety measures."""
        try:
            # Create destination parent directory
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy with progress tracking and size limits
            def copy_function(src, dst, *, follow_symlinks=True):
                # Additional per-file size check
                try:
                    if os.path.getsize(src) > 100 * 1024 * 1024:  # 100MB per file limit
                        print(f'   - ⚠️  Skipping large file: {src}')
                        return dst
                except OSError:
                    pass
                
                return shutil.copy2(src, dst, follow_symlinks=follow_symlinks)
            
            # Use copytree with custom copy function and ignore patterns
            def ignore_patterns(dir, files):
                ignored = []
                for file in files:
                    # Skip common unnecessary directories/files
                    if file in {'.git', '__pycache__', '.mypy_cache', '.pytest_cache', 
                            '.tox', '.coverage', 'node_modules', '.DS_Store'}:
                        ignored.append(file)
                    # Skip very large files that are probably unnecessary
                    try:
                        filepath = os.path.join(dir, file)
                        if os.path.isfile(filepath) and os.path.getsize(filepath) > 50 * 1024 * 1024:
                            ignored.append(file)
                    except OSError:
                        pass
                return ignored
            
            print(f'   - Copying {source} -> {dest}')
            shutil.copytree(
                source, 
                dest, 
                symlinks=True,  # Preserve symlinks
                ignore=ignore_patterns,
                dirs_exist_ok=False  # Fail if destination exists (we checked above)
            )
            
            # Verify the copy worked
            copied_python = self._find_python_executable_in_dir(dest)
            if not copied_python or not copied_python.exists():
                print('   - ❌ Copy completed but Python executable not found in destination')
                shutil.rmtree(dest, ignore_errors=True)
                return self._fallback_to_download(version)
            
            # Test the copied Python
            test_cmd = [str(copied_python), '-c', 'import sys; print(sys.version)']
            test_result = subprocess.run(test_cmd, capture_output=True, timeout=10)
            
            if test_result.returncode != 0:
                print('   - ❌ Copied Python executable failed basic test')
                shutil.rmtree(dest, ignore_errors=True)
                return self._fallback_to_download(version)
            
            print(f'   - ✅ Copy successful and verified!')
            self.config_manager._register_all_interpreters(self.config_manager.venv_path)
            print(f'\n🎉 Successfully adopted Python {version} from local source!')
            print(f"   You can now use 'omnipkg swap python {version}'")
            return 0
            
        except Exception as e:
            print(f'   - ❌ Copy operation failed: {e}')
            # Clean up partial copy
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            return self._fallback_to_download(version)

    def _find_python_executable_in_dir(self, directory: Path) -> Path:
        """Find the Python executable in a copied directory."""
        # Common Python executable names and locations
        possible_names = ['python', 'python3', 'python.exe']
        possible_dirs = ['bin', 'Scripts', '.']  # Unix, Windows, root
        
        for subdir in possible_dirs:
            for name in possible_names:
                candidate = directory / subdir / name
                if candidate.exists() and candidate.is_file():
                    return candidate
        
        return None

    def _fallback_to_download(self, version: str) -> int:
        """Fallback to downloading Python using your existing download mechanism."""
        print('\n--- Falling back to download strategy ---')
        try:
            # Your existing download logic here
            full_versions = {'3.12': '3.12.3', '3.10': '3.10.13', '3.9': '3.9.18', '3.11': '3.11.6'}
            full_version = full_versions.get(version)
            if not full_version:
                print(f'❌ Error: No known standalone build for Python {version}.')
                return 1
                
            dest_path = self.config_manager.venv_path / '.omnipkg' / 'interpreters' / f'cpython-{full_version}'
            if dest_path.exists():
                print(f'✅ Downloaded version of Python {full_version} already exists.')
            else:
                self.config_manager._install_managed_python(self.config_manager.venv_path, full_version)
            
            self.config_manager._register_all_interpreters(self.config_manager.venv_path)
            print(f'\n🎉 Successfully adopted Python {full_version} via download!')
            print(f"   You can now use 'omnipkg swap python {version}'")
            return 0
            
        except Exception as e:
            print(f'❌ Download strategy failed: {e}')
            return 1

    def _resolve_package_versions(self, packages: List[str]) -> List[str]:
        """
        Takes a list of packages and ensures every entry has an explicit version.
        Uses the PyPI API to find the latest version for packages specified without one.
        """
        print(_('🔎 Resolving package versions via PyPI API...'))
        resolved_packages = []
        for pkg_spec in packages:
            if '==' in pkg_spec:
                resolved_packages.append(pkg_spec)
                continue
            pkg_name = self._parse_package_spec(pkg_spec)[0]
            print(_("    -> Finding latest version for '{}'...").format(pkg_name))
            target_version = self._get_latest_version_from_pypi(pkg_name)
            if target_version:
                new_spec = f'{pkg_name}=={target_version}'
                print(_("    ✅ Resolved '{}' to '{}'").format(pkg_name, new_spec))
                resolved_packages.append(new_spec)
            else:
                print(_("    ⚠️  Could not resolve a version for '{}' via PyPI. Skipping.").format(pkg_name))
        return resolved_packages

    def _run_pip_install(self, packages: List[str]) -> int:
        if not packages:
            return 0
        try:
            cmd = [self.config['python_executable'], '-m', 'pip', 'install'] + packages
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(_('❌ Pip install command failed with exit code {}:').format(e.returncode))
            print(e.stderr)
            return e.returncode
        except Exception as e:
            print(_('    ❌ An unexpected error occurred during pip install: {}').format(e))
            return 1

    def _run_pip_uninstall(self, packages: List[str]) -> int:
        """Runs `pip uninstall` for a list of packages."""
        if not packages:
            return 0
        try:
            cmd = [self.config['python_executable'], '-m', 'pip', 'uninstall', '-y'] + packages
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            print(result.stdout)
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(_('❌ Pip uninstall command failed with exit code {}:').format(e.returncode))
            print(e.stderr)
            return e.returncode
        except Exception as e:
            print(_('    ❌ An unexpected error occurred during pip uninstall: {}').format(e))
            return 1

    def _run_uv_install(self, packages: List[str]) -> int:
        """Runs `uv install` for a list of packages."""
        if not packages:
            return 0
        try:
            cmd = [self.config['uv_executable'], 'install', '--quiet'] + packages
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)
            return result.returncode
        except FileNotFoundError:
            print(_("❌ Error: 'uv' executable not found. Please ensure uv is installed and in your PATH."))
            return 1
        except subprocess.CalledProcessError as e:
            print(_('❌ uv install command failed with exit code {}:').format(e.returncode))
            print(e.stderr)
            return e.returncode
        except Exception as e:
            print(_('    ❌ An unexpected error toccurred during uv install: {}').format(e))
            return 1

    def _run_uv_uninstall(self, packages: List[str]) -> int:
        """Runs `uv pip uninstall` for a list of packages."""
        if not packages:
            return 0
        try:
            cmd = [self.config['uv_executable'], 'pip', 'uninstall'] + packages
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            print(result.stdout)
            return result.returncode
        except FileNotFoundError:
            print(_("❌ Error: 'uv' executable not found. Please ensure uv is installed and in your PATH."))
            return 1
        except subprocess.CalledProcessError as e:
            print(_('❌ uv uninstall command failed with exit code {}:').format(e.returncode))
            print(e.stderr)
            return e.returncode
        except Exception as e:
            print(_('    ❌ An unexpected error occurred during uv uninstall: {}').format(e))
            return 1

    def _get_latest_version_from_pypi(self, package_name: str) -> Optional[str]:
        """
        Fetches the latest version of a package directly from the PyPI JSON API.
        This is more reliable than `pip dry-run` as it correctly handles pre-releases.
        """
        try:
            url = f'https://pypi.org/pypi/{canonicalize_name(package_name)}/json'
            response = self.http_session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'releases' in data and data['releases']:
                versions = [parse_version(v) for v in data['releases'].keys() if not parse_version(v).is_prerelease]
                if not versions:
                    versions = [parse_version(v) for v in data['releases'].keys()]
                if versions:
                    return str(max(versions))
            return data.get('info', {}).get('version')
        except Exception as e:
            print(_("    ⚠️  API Error while fetching version for '{}': {}").format(package_name, e))
            return None

    def get_available_versions(self, package_name: str) -> List[str]:
        """
        Correctly gets all available versions (active and bubbled) for a package
        by checking all relevant keys in the knowledge base.
        """
        c_name = canonicalize_name(package_name)
        main_key = f'{self.redis_key_prefix}{c_name}'
        versions = set()
        try:
            versions.update(self.redis_client.smembers(_('{}:installed_versions').format(main_key)))
            active_version = self.redis_client.hget(main_key, 'active_version')
            if active_version:
                versions.add(active_version)
            return sorted(list(versions), key=parse_version, reverse=True)
        except Exception as e:
            print(_('⚠️ Could not retrieve versions for {}: {}').format(package_name, e))
            return []

    def list_packages(self, pattern: str=None) -> int:
        if not self.connect_redis():
            return 1
        self._synchronize_knowledge_base_with_reality()
        all_pkg_names = self.redis_client.smembers(f'{self.redis_key_prefix}index')
        if pattern:
            all_pkg_names = {name for name in all_pkg_names if pattern.lower() in name.lower()}
        print(_('📋 Found {} matching package(s):').format(len(all_pkg_names)))
        for pkg_name in sorted(list(all_pkg_names)):
            main_key = f'{self.redis_key_prefix}{pkg_name}'
            package_data = self.redis_client.hgetall(main_key)
            display_name = package_data.get('name', pkg_name)
            active_version = package_data.get('active_version')
            all_versions = self.get_available_versions(pkg_name)
            print(_('\n- {}:').format(display_name))
            if not all_versions:
                print(_('  (No versions found in knowledge base)'))
                continue
            for version in all_versions:
                if version == active_version:
                    print(_('  ✅ {} (active)').format(version))
                else:
                    print(_('  🫧 {} (bubble)').format(version))
        return 0

    def show_multiversion_status(self) -> int:
        if not self.connect_redis():
            return 1
        self._synchronize_knowledge_base_with_reality()
        print(_('🔄 omnipkg System Status'))
        print('=' * 50)
        print(_("🛠️ Environment broken by pip or uv? Run 'omnipkg revert' to restore the last known good state! 🚑"))
        try:
            pip_version = version('pip')
            print(_('\n🔒 Pip in Jail (main environment)'))
            print(_('    😈 Locked up for causing chaos in the main env! 🔒 (v{})').format(pip_version))
        except importlib.metadata.PackageNotFoundError:
            print(_('\n🔒 Pip in Jail (main environment)'))
            print(_('    🚫 Pip not found in the main env. Escaped or never caught!'))
        try:
            uv_version = version('uv')
            print(_('🔒 UV in Jail (main environment)'))
            print(_('    😈 Speedy troublemaker locked up in the main env! 🔒 (v{})').format(uv_version))
        except importlib.metadata.PackageNotFoundError:
            print(_('🔒 UV in Jail (main environment)'))
            print(_('    🚫 UV not found in the main env. Too fast to catch!'))
        print(_('\n🌍 Main Environment:'))
        site_packages = Path(self.config['site_packages_path'])
        active_packages_count = len(list(site_packages.glob('*.dist-info')))
        print(_('  - Path: {}').format(site_packages))
        print(_('  - Active Packages: {}').format(active_packages_count))
        print(_('\n📦 izolasyon Alanı (Bubbles):'))
        if not self.multiversion_base.exists() or not any(self.multiversion_base.iterdir()):
            print(_('  - No isolated package versions found.'))
            return 0
        print(_('  - Bubble Directory: {}').format(self.multiversion_base))
        print(_('  - Import Hook Installed: {}').format('✅' if self.hook_manager.hook_installed else '❌'))
        version_dirs = list(self.multiversion_base.iterdir())
        total_bubble_size = 0
        print(_('\n📦 Isolated Package Versions ({} bubbles):').format(len(version_dirs)))
        for version_dir in sorted(version_dirs):
            if version_dir.is_dir():
                size = sum((f.stat().st_size for f in version_dir.rglob('*') if f.is_file()))
                total_bubble_size += size
                size_mb = size / (1024 * 1024)
                warning = ' ⚠️' if size_mb > 100 else ''
                formatted_size_str = '{:.1f}'.format(size_mb)
                print(_('  - 📁 {} ({} MB){}').format(version_dir.name, formatted_size_str, warning))
                if 'pip' in version_dir.name.lower():
                    print(_('    😈 Pip is locked up in a bubble, plotting chaos like a Python outlaw! 🔒'))
                elif 'uv' in version_dir.name.lower():
                    print(_('    😈 UV is locked up in a bubble, speeding toward trouble! 🔒'))
        total_bubble_size_mb = total_bubble_size / (1024 * 1024)
        formatted_total_size_str = '{:.1f}'.format(total_bubble_size_mb)
        print(_('  - Total Bubble Size: {} MB').format(formatted_total_size_str))
        return 0