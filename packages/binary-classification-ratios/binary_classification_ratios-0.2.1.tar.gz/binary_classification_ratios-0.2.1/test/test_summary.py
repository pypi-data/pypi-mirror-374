"""."""

import pytest

from binary_classification_ratios.summary import BinaryClassificationSummary


@pytest.fixture
def bcs() -> BinaryClassificationSummary:
    """."""
    summary = BinaryClassificationSummary()
    return summary


def test_get_summary(bcs: BinaryClassificationSummary) -> None:
    """."""
    dct = {
        'tp': 10,
        'tn': 9,
        'fp': 8,
        'fn': 7,
        'accuracy': 0.5588256789012345,
        'precision': 0.5561234,
        'recall': 0.5881234,
        'f1_score': 0.57101234,
    }
    ref = """Confusion matrix TP 10 TN 9 FP 8 FN 7
     accuracy 0.5588
    precision 0.56
       recall 0.59
     f1-score 0.57"""
    bcs.accuracy_fmt = '.4f'
    bcs.fmt = '.2f'
    assert bcs.get_summary(dct) == ref
