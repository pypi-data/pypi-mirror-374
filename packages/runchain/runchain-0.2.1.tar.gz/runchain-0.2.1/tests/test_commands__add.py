from __future__ import annotations

import os

from runchain.commands import cli


def test_add_with_number(runner, home_dir, test_script):
    """
    Test adding a script with a number.
    """
    result = runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    assert result.exit_code == 0
    assert "Added 10-test_script.sh to chain 'testchain'" in result.output
    
    # Check file was created and is executable
    chain_dir = home_dir / ".runchain" / "testchain"
    target_file = chain_dir / "10-test_script.sh"
    assert target_file.exists()
    assert os.access(target_file, os.X_OK)


def test_add_with_full_name(runner, home_dir, test_script):
    """
    Test adding a script with full NN-name format.
    """
    result = runner.invoke(cli, ["add", "testchain", str(test_script), "20-backup"])
    assert result.exit_code == 0
    assert "Added 20-backup to chain 'testchain'" in result.output
    
    chain_dir = home_dir / ".runchain" / "testchain"
    target_file = chain_dir / "20-backup"
    assert target_file.exists()
    assert os.access(target_file, os.X_OK)


def test_add_numbered_script_no_target(runner, home_dir, numbered_script):
    """
    Test adding a script that already has NN- format without target.
    """
    result = runner.invoke(cli, ["add", "testchain", str(numbered_script)])
    assert result.exit_code == 0
    assert "Added 10-numbered.py to chain 'testchain'" in result.output


def test_add_script_no_target_invalid(runner, home_dir, test_script):
    """
    Test adding a script without NN- format and no target fails.
    """
    result = runner.invoke(cli, ["add", "testchain", str(test_script)])
    assert result.exit_code != 0
    assert "must start with NN- format when no target specified" in result.output


def test_add_nonexistent_script(runner, home_dir):
    """
    Test adding a script that doesn't exist.
    """
    result = runner.invoke(cli, ["add", "testchain", "/nonexistent/script.sh", "10"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_add_invalid_target(runner, home_dir, test_script):
    """
    Test adding with invalid target format.
    """
    result = runner.invoke(cli, ["add", "testchain", str(test_script), "invalid"])
    assert result.exit_code != 0
    assert "must be a number or start with NN- format" in result.output


def test_add_creates_chain(runner, home_dir, test_script):
    """
    Test that adding a script creates the chain directory.
    """
    chain_dir = home_dir / ".runchain" / "newchain"
    assert not chain_dir.exists()
    
    result = runner.invoke(cli, ["add", "newchain", str(test_script), "10"])
    assert result.exit_code == 0
    assert chain_dir.exists()


def test_add_invalid_chain_name(runner, home_dir, test_script):
    """
    Test adding with invalid chain name.
    """
    result = runner.invoke(cli, ["add", "invalid-name", str(test_script), "10"])
    assert result.exit_code != 0
    assert "must contain only lowercase letters" in result.output