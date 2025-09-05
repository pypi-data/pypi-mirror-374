from __future__ import annotations

from runchain.commands import cli


def test_remove_script(runner, home_dir, test_script):
    """
    Test removing a script from a chain.
    """
    # First add a script
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    
    # Then remove it
    result = runner.invoke(cli, ["remove", "testchain", "10-test_script.sh"])
    assert result.exit_code == 0
    assert "Removed script from chain 'testchain'" in result.output
    
    # Check file was removed
    chain_dir = home_dir / ".runchain" / "testchain"
    target_file = chain_dir / "10-test_script.sh"
    assert not target_file.exists()


def test_remove_script_removes_empty_chain(runner, home_dir, test_script):
    """
    Test that removing the last script removes the empty chain directory.
    """
    # Add a script
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    chain_dir = home_dir / ".runchain" / "testchain"
    assert chain_dir.exists()
    
    # Remove the script
    runner.invoke(cli, ["remove", "testchain", "10-test_script.sh"])
    
    # Chain directory should be gone
    assert not chain_dir.exists()


def test_remove_nonexistent_script(runner, home_dir, test_script):
    """
    Test removing a script that doesn't exist.
    """
    # Create chain with a script
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    
    result = runner.invoke(cli, ["remove", "testchain", "nonexistent.sh"])
    assert result.exit_code != 0
    assert "not found in chain" in result.output


def test_remove_chain_empty(runner, home_dir):
    """
    Test removing an empty chain.
    """
    # Create empty chain
    runchain_dir = home_dir / ".runchain"
    runchain_dir.mkdir()
    (runchain_dir / "testchain").mkdir()
    
    result = runner.invoke(cli, ["remove", "testchain"])
    assert result.exit_code == 0
    assert "Removed chain 'testchain'" in result.output
    assert not (runchain_dir / "testchain").exists()


def test_remove_chain_with_scripts_confirm_yes(runner, home_dir, test_script):
    """
    Test removing a chain with scripts, confirming yes.
    """
    # Add a script to create the chain
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    
    # Remove chain with confirmation
    result = runner.invoke(cli, ["remove", "testchain"], input="y\n")
    assert result.exit_code == 0
    assert "Removed chain 'testchain'" in result.output
    
    chain_dir = home_dir / ".runchain" / "testchain"
    assert not chain_dir.exists()


def test_remove_chain_with_scripts_confirm_no(runner, home_dir, test_script):
    """
    Test removing a chain with scripts, confirming no.
    """
    # Add a script to create the chain
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    
    # Remove chain, decline confirmation
    result = runner.invoke(cli, ["remove", "testchain"], input="n\n")
    assert result.exit_code == 0
    assert "Removed chain 'testchain'" not in result.output
    
    # Chain should still exist
    chain_dir = home_dir / ".runchain" / "testchain"
    assert chain_dir.exists()


def test_remove_chain_force(runner, home_dir, test_script):
    """
    Test removing a chain with --force flag.
    """
    # Add a script to create the chain
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    
    # Remove chain with force
    result = runner.invoke(cli, ["remove", "testchain", "--force"])
    assert result.exit_code == 0
    assert "Removed chain 'testchain'" in result.output
    
    chain_dir = home_dir / ".runchain" / "testchain"
    assert not chain_dir.exists()


def test_remove_nonexistent_chain(runner, home_dir):
    """
    Test removing a nonexistent chain.
    """
    result = runner.invoke(cli, ["remove", "nonexistent"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_remove_invalid_chain_name(runner, home_dir):
    """
    Test removing with invalid chain name.
    """
    result = runner.invoke(cli, ["remove", "invalid-name"])
    assert result.exit_code != 0
    assert "must contain only lowercase letters" in result.output