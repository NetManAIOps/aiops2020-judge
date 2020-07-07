'''
Test suite for assemble.py
'''
import pytest

from assemble import FBetaScore


@pytest.mark.parametrize(
    ('beta', 'correct', 'submitted', 'num', 'expectation'),
    [
        (0.5, 1, 2, 1, 0.5556),
        (0.5, 0, 2, 1, 0),
    ]
)
def test_fbetascore(beta, correct, submitted, num, expectation):
    '''Test assemble.FBetaScore.calculate'''
    scorer = FBetaScore(beta)
    score = scorer.calculate(correct, submitted, num)
    assert score == pytest.approx(expectation, 1e-4)
