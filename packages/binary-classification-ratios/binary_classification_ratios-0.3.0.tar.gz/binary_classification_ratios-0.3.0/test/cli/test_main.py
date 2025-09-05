"""."""

import pytest

from binary_classification_ratios.cli.main import run


def test_run(capsys: pytest.CaptureFixture) -> None:
    """."""
    f1 = run(
        ['-tp', '1', '-tn', '2', '-fp', '3', '-fn', '4', '--fmt', '.4f', '--accuracy-fmt', '.6f']
    )
    assert f1 == pytest.approx(0.222222222222222222)
    stdout = capsys.readouterr().out
    assert 'Confusion matrix TP 1 TN 2 FP 3 FN 4' in stdout
    assert 'accuracy 0.300000' in stdout
    assert 'f1-score 0.2222' in stdout
