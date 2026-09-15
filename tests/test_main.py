import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

from adaptive_scheduler.main import parse_args, main


def test_parse_args_defaults():
    """Test default CLI argument assignments."""
    args = parse_args([])
    assert args.scenarios == ["light", "medium", "heavy"]
    assert args.seed == 42
    assert args.output_dir == "outputs/evaluation"


def test_parse_args_custom():
    """Test custom CLI argument flags."""
    args = parse_args(["--scenarios", "light", "--seed", "123", "--output-dir", "custom_out"])
    assert args.scenarios == ["light"]
    assert args.seed == 123
    assert args.output_dir == "custom_out"


@patch("adaptive_scheduler.main.run_benchmark")
@patch("adaptive_scheduler.main.generate_benchmark_plots")
def test_main_execution_flow(mock_plots, mock_benchmark, tmp_path):
    """Test full execution flow with mocked benchmark functions."""
    mock_df = pd.DataFrame({"scenario": ["light"], "algorithm": ["Adaptive"], "makespan": [10.0]})
    mock_benchmark.return_value = mock_df

    out_dir = str(tmp_path / "test_outputs")
    exit_code = main(["--scenarios", "light", "--seed", "99", "--output-dir", out_dir])

    assert exit_code == 0
    mock_benchmark.assert_called_once_with(scenarios=["light"], seed=99)
    mock_plots.assert_called_once_with(mock_df, output_dir=out_dir)
    assert Path(out_dir).exists()
