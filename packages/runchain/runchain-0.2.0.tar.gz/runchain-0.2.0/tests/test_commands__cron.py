from __future__ import annotations

from runchain.commands import cli


def test_cron_success(mock_crondir, runner, home_dir, test_script):
    """
    Test scheduling a chain with cron.
    """
    # Add a script to create the chain
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    
    result = runner.invoke(cli, ["cron", "testchain", "0 2 * * *"])
    assert result.exit_code == 0
    assert "Scheduled chain 'testchain' with crondir" in result.output
    
    # Check crondir was called correctly
    mock_crondir.add_string.assert_called_once_with(
        "0 2 * * * runchain run testchain",
        snippet="runchain-testchain",
        force=True
    )


def test_cron_nonexistent_chain(runner, home_dir):
    """
    Test scheduling a nonexistent chain.
    """
    result = runner.invoke(cli, ["cron", "nonexistent", "0 2 * * *"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_cron_invalid_chain_name(runner, home_dir):
    """
    Test scheduling with invalid chain name.
    """
    result = runner.invoke(cli, ["cron", "invalid-name", "0 2 * * *"])
    assert result.exit_code != 0
    assert "must contain only lowercase letters" in result.output