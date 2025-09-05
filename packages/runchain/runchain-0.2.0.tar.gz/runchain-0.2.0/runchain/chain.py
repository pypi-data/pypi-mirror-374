from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

from crondir import Crondir
from runchain.exceptions import ChainError


def list_chains(base_dir: Path | str | None = None) -> list[str]:
    """List all available chains."""
    if base_dir is None:
        base_dir = os.environ.get("RUNCHAIN_PATH", Path.home() / ".runchain")
    base_path = Path(base_dir)
    
    if not base_path.exists():
        return []
    
    chains = []
    for path in base_path.iterdir():
        if path.is_dir() and re.match(r'^[a-z]+$', path.name):
            chains.append(path.name)
    return sorted(chains)


class Chain:
    """Represents a single runchain chain."""
    
    def __init__(self, name: str, base_dir: Path | str | None = None):
        """
        Initialize Chain instance.
        
        Args:
            name: Name of the chain
            base_dir: Base directory for chains. Defaults to RUNCHAIN_PATH env var or ~/.runchain
        """
        if not re.match(r'^[a-z]+$', name):
            raise ChainError(f"Chain name '{name}' must contain only lowercase letters (a-z)")
        
        self.name = name
        
        if base_dir is None:
            base_dir = os.environ.get("RUNCHAIN_PATH", Path.home() / ".runchain")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        self.path = self.base_dir / name
    
    def _create(self) -> None:
        """Create the chain directory."""
        self.path.mkdir(exist_ok=True)
    
    def log(self, message: str) -> None:
        """Log a message."""
        print(message)
    
    def exists(self) -> bool:
        """Check if this chain exists."""
        return self.path.exists() and self.path.is_dir()
    
    def list(self) -> list[str]:
        """List all scripts in this chain in alphabetical order."""
        if not self.exists():
            return []
        
        scripts = []
        for script_path in sorted(self.path.iterdir()):
            if script_path.is_file():
                executable = os.access(script_path, os.X_OK)
                status = " (executable)" if executable else " (not executable)"
                scripts.append(f"{script_path.name}{status}")
        return scripts
    
    def add_file(self, script_path: str, target: str | None = None) -> str:
        """
        Add a script to this chain.
        
        Args:
            script_path: Path to the script file to add
            target: Optional naming specification
        
        Returns:
            The final filename in the chain
        """
        source_path = Path(script_path)
        if not source_path.exists():
            raise ChainError(f"Script file '{script_path}' does not exist")
        
        # Create chain directory if it doesn't exist
        if not self.exists():
            self._create()
        
        # Determine target filename
        if target is None:
            # Must already follow NN-* format
            basename = source_path.name
            if not re.match(r'^\d+-', basename):
                raise ChainError(f"Script basename '{basename}' must start with NN- format when no target specified")
            target_name = basename
        elif target.isdigit():
            # Number provided - use NN-basename format
            target_name = f"{target}-{source_path.name}"
        elif re.match(r'^\d+-', target):
            # Full name starting with NN- provided
            target_name = target
        else:
            # Invalid format
            raise ChainError(f"Target '{target}' must be a number or start with NN- format")
        
        target_path = self.path / target_name
        
        # Copy script and make executable
        shutil.copy2(source_path, target_path)
        target_path.chmod(target_path.stat().st_mode | stat.S_IEXEC)
        
        return target_name
    
    def add_string(self, *contents: str, target: str) -> str:
        """
        Add a script string to this chain.
        
        Args:
            contents: Script content lines
            target: Required naming specification (number or NN-name format)
        
        Returns:
            The final filename in the chain
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh") as temp_file:
            temp_file.write("\n".join(contents))
            temp_file.flush()
            return self.add_file(temp_file.name, target)
    
    def remove(self, script: str, target: str | None = None) -> None:
        """Remove a script from this chain."""
        if not self.exists():
            raise ChainError(f"Chain '{self.name}' does not exist")
        
        # Use exact filename match only
        filename = target if target is not None else script
        target_path = self.path / filename
        
        if not target_path.exists():
            raise ChainError(f"Script '{filename}' not found in chain '{self.name}'")
        
        target_path.unlink()
        
        # Delete chain directory if empty
        if not any(self.path.iterdir()):
            self.path.rmdir()
    
    def destroy(self) -> None:
        """Remove this entire chain."""
        if not self.exists():
            raise ChainError(f"Chain '{self.name}' does not exist")
        
        shutil.rmtree(self.path)
    
    def cron(self, schedule: str) -> None:
        """Schedule this chain to run with crondir."""
        if not self.exists():
            raise ChainError(f"Chain '{self.name}' does not exist")
        
        # Create cron entry string
        cron_content = f"{schedule} runchain run {self.name}"
        
        # Use crondir Python API
        crondir = Crondir()
        crondir.add_string(
            cron_content,
            snippet=f'runchain-{self.name}',
            force=True
        )
    
    def run(self) -> bool:
        """
        Execute all scripts in this chain in alphabetical order.
        
        Returns:
            True if all scripts succeeded, False if any failed
        """
        if not self.exists():
            raise ChainError(f"Chain '{self.name}' does not exist")
        
        # Execute each script in alphabetical order
        for script_path in sorted(self.path.iterdir()):
            self.log(f"Running {script_path.name}...")
            
            result = subprocess.run([str(script_path)], 
                                  cwd=script_path.parent,
                                  capture_output=False)
            
            if result.returncode != 0:
                self.log(f"Script {script_path.name} failed with exit code {result.returncode}")
                return False
        
        self.log(f"Chain '{self.name}' completed successfully")
        return True