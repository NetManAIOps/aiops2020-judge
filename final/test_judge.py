'''
Test suite for judge.py
'''
import os

import pytest

import judge


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
WINDOW = 6 * 60 * 60
SAMPLE_ANSWER = os.path.join(BASE_DIR, 'sample_answer.json')
SAMPLE_RESULT = os.path.join(BASE_DIR, 'sample_result.log')


@pytest.mark.parametrize(('quota', 'expectation'), [
    (2, WINDOW),
    (3, 600.0),
    (4, WINDOW),
    (5, 540.0),
    (6, 540.0),
])
def test_judge(quota, expectation):
    '''Test judge.judge'''
    grade = judge.judge(SAMPLE_ANSWER, SAMPLE_RESULT, quota=quota, window=WINDOW)
    grade = judge.score(grade)
    assert grade == pytest.approx(expectation, 1e-4)


def test_function():
    '''SmokeTest for judge.main'''
    judge.main(['judge.py', SAMPLE_ANSWER, SAMPLE_RESULT])
