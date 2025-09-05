from __future__ import annotations

from runchain.commands import cli


def test_run_success(mock_subprocess, runner, home_dir, test_script):
    """
    Test running a chain successfully.
    """
    # Add a script to create the chain
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    
    result = runner.invoke(cli, ["run", "testchain"])
    assert result.exit_code == 0
    assert "Running 10-test_script.sh..." in result.output
    assert "Chain 'testchain' completed successfully" in result.output
    
    # Check subprocess.run was called
    mock_subprocess.assert_called_once()


def test_run_script_failure(mock_subprocess, runner, home_dir, test_script):
    """
    Test running a chain with failing script.
    """
    mock_subprocess.return_value.returncode = 1
    
    # Add a script to create the chain
    runner.invoke(cli, ["add", "testchain", str(test_script), "10"])
    
    result = runner.invoke(cli, ["run", "testchain"])
    assert result.exit_code == 1
    assert "Running 10-test_script.sh..." in result.output
    assert "failed with exit code 1" in result.output


def test_run_multiple_scripts_in_order(mock_subprocess, runner, home_dir, test_script):
    """
    Test running multiple scripts in alphabetical order.
    """
    # Add multiple scripts
    runner.invoke(cli, ["add", "testchain", str(test_script), "30-third"])
    runner.invoke(cli, ["add", "testchain", str(test_script), "10-first"])  
    runner.invoke(cli, ["add", "testchain", str(test_script), "20-second"])
    
    result = runner.invoke(cli, ["run", "testchain"])
    assert result.exit_code == 0
    
    # Check they ran in alphabetical order
    output_lines = result.output.strip().split('\n')
    running_lines = [line for line in output_lines if line.startswith("Running")]
    assert "Running 10-first..." in running_lines[0]
    assert "Running 20-second..." in running_lines[1]
    assert "Running 30-third..." in running_lines[2]


def test_run_stops_on_failure(mock_subprocess, runner, home_dir, test_script):
    """
    Test that running stops on first script failure.
    """
    # First call succeeds, second fails
    mock_subprocess.side_effect = [
        type('', (), {'returncode': 0})(),  # First script succeeds
        type('', (), {'returncode': 1})(),  # Second script fails
    ]
    
    # Add multiple scripts
    runner.invoke(cli, ["add", "testchain", str(test_script), "10-first"])
    runner.invoke(cli, ["add", "testchain", str(test_script), "20-second"])
    runner.invoke(cli, ["add", "testchain", str(test_script), "30-third"])
    
    result = runner.invoke(cli, ["run", "testchain"])
    assert result.exit_code == 1
    
    # Should have run first two scripts but not the third
    assert "Running 10-first..." in result.output
    assert "Running 20-second..." in result.output
    assert "Running 30-third..." not in result.output
    assert "failed with exit code 1" in result.output


def test_run_nonexistent_chain(runner, home_dir):
    """
    Test running a nonexistent chain.
    """
    result = runner.invoke(cli, ["run", "nonexistent"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_run_invalid_chain_name(runner, home_dir):
    """
    Test running with invalid chain name.
    """
    result = runner.invoke(cli, ["run", "invalid-name"])
    assert result.exit_code != 0
    assert "must contain only lowercase letters" in result.output


def test_run_empty_chain(mock_subprocess, runner, home_dir):
    """
    Test running an empty chain.
    """
    # Create empty chain directory
    runchain_dir = home_dir / ".runchain"
    runchain_dir.mkdir()
    (runchain_dir / "empty").mkdir()
    
    result = runner.invoke(cli, ["run", "empty"])
    assert result.exit_code == 0
    
    # Should complete successfully with no scripts to run
    mock_subprocess.assert_not_called()