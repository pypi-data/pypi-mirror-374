from __future__ import annotations

from runchain.commands import cli


def test_list_no_chains(runner, home_dir):
    """
    Test listing when no chains exist.
    """
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No chains found." in result.output


def test_list_all_chains(runner, home_dir):
    """
    Test listing all chains.
    """
    # Create some chain directories
    runchain_dir = home_dir / ".runchain"
    runchain_dir.mkdir()
    (runchain_dir / "backup").mkdir()
    (runchain_dir / "deploy").mkdir()
    (runchain_dir / "maintenance").mkdir()

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "Chains found:" in result.output
    assert "backup" in result.output
    assert "deploy" in result.output
    assert "maintenance" in result.output


def test_list_chain_scripts_empty(runner, home_dir):
    """
    Test listing scripts in an empty chain.
    """
    runchain_dir = home_dir / ".runchain"
    runchain_dir.mkdir()
    (runchain_dir / "testchain").mkdir()

    result = runner.invoke(cli, ["list", "testchain"])
    assert result.exit_code == 0
    assert "No scripts found in chain 'testchain'." in result.output


def test_list_chain_scripts_with_files(runner, home_dir):
    """
    Test listing scripts in a chain with files.
    """
    runchain_dir = home_dir / ".runchain"
    runchain_dir.mkdir()
    chain_dir = runchain_dir / "testchain"
    chain_dir.mkdir()
    
    # Create some test scripts
    script1 = chain_dir / "10-backup.sh"
    script1.write_text("#!/bin/bash\necho test")
    script1.chmod(0o755)
    
    script2 = chain_dir / "20-deploy.py"
    script2.write_text("#!/usr/bin/env python3\nprint('test')")
    # Don't make this one executable

    result = runner.invoke(cli, ["list", "testchain"])
    assert result.exit_code == 0
    assert "Scripts in chain testchain:" in result.output
    assert "10-backup.sh (executable)" in result.output
    assert "20-deploy.py (not executable)" in result.output


def test_list_invalid_chain_name(runner, home_dir):
    """
    Test listing with invalid chain name.
    """
    result = runner.invoke(cli, ["list", "invalid-name"])
    assert result.exit_code != 0
    assert "must contain only lowercase letters" in result.output