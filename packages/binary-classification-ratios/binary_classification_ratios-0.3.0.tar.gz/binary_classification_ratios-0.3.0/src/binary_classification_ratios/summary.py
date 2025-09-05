"""."""

from typing import Dict, Union


class BinaryClassificationSummary:
    """."""

    def __init__(self) -> None:
        """."""
        self.accuracy_fmt = '.5f'
        self.fmt = '.3f'
        self.confusion_matrix_prefix = 'Confusion matrix'

    def get_summary(self, dct: Dict[str, Union[int, float]]) -> str:
        """Return a human-readable summary of the quality metrics.

        Returns:
            str: A formatted string summarizing the classification metrics.
        """
        tp = dct.get('tp', '?')
        tn = dct.get('tn', '?')
        fp = dct.get('fp', '?')
        fn = dct.get('fn', '?')
        lines = [f'{self.confusion_matrix_prefix} TP {tp} TN {tn} FP {fp} FN {fn}']
        accuracy = dct.get('accuracy', None)
        recall = dct.get('recall', None)
        precision = dct.get('precision', None)
        f1_score = dct.get('f1_score', None)

        if accuracy is not None:
            lines.append(f'     accuracy {accuracy:{self.accuracy_fmt}}')
        if precision is not None:
            lines.append(f'    precision {precision:{self.fmt}}')
        if recall is not None:
            lines.append(f'       recall {recall:{self.fmt}}')
        if f1_score is not None:
            lines.append(f'     f1-score {f1_score:{self.fmt}}')

        summary = '\n'.join(lines)
        return summary
