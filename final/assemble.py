#!/usr/bin/env python3
'''
Judge for teams.
'''
import argparse
import math
import os
import warnings

import judge


DEFAULT_TIME = 6 * 60 * 60  # 6 hours


class FBetaScore():  # pylint: disable=too-few-public-methods
    '''
    Calculate F-beta-score.
    '''

    def __init__(self, beta):
        self.beta = beta ** 2

    def calculate(self, correct, submitted, num):
        '''
        correct: number of correct answers among submitted ones
        submitted: number of submitted answers
        num: number of standard answers, which are ground truth
        '''
        if not correct or not submitted or not num:
            return 0.0

        correct = float(correct)
        precision = correct / submitted
        recall = correct / num
        return (1 + self.beta) / (1 / precision + self.beta / recall)


def rank(data, size, scorer, selector):
    '''
    For each fault, a team gets grade based on ranking among teams.
    '''
    score = {team: 0.0 for team in data}

    for i in range(size):
        turn = []
        for team in data:
            turn.append((team, selector([scorer(*item) for item in data[team][i]])))
        turn.sort(key=lambda item: item[1])
        j = 0
        grade = 10
        num = len(turn)
        while j < num and grade > 0:
            team, time = turn[j]
            if time >= DEFAULT_TIME:
                break
            current_grade = grade
            current_time = time
            while j < num and time == current_time:
                score[team] += current_grade
                grade -= 1
                j += 1
                if j >= num:
                    break
                team, time = turn[j]
    return score


def fscore(data, size, scorer, selector):
    '''
    For each fault, a team gets grade based on f-score.
    '''
    score = {team: 0.0 for team in data}

    for i in range(size):
        for team in data:
            score[team] += selector([scorer(*item) for item in data[team][i]])
    for team in data:
        score[team] /= size
    return score


def _get_last(data):
    if data:
        return data[-1]
    return DEFAULT_TIME


def _get_best(data):
    if data:
        return min(data)
    return DEFAULT_TIME


def trunc(value, base, minimum):
    '''
    Reserve precision for float.

    value: float
    base: the given precision
    '''
    value = math.ceil(value / base) * base
    if value < minimum:
        value = minimum
    return value


def create_scorer(beta):
    '''
    Combine f-beta-score with time to detect fault.
    '''
    f_scorer = FBetaScore(beta)

    def scorer(time, submitted, correct, num):
        correct = float(correct)
        if submitted and correct / submitted >= 0.5:  # precision >= 0.5
            time /= f_scorer.calculate(correct, submitted, num)
            time = trunc(time / correct, 10, 0)
        else:
            time = DEFAULT_TIME
        return time

    return scorer


def main():
    '''Entrance'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--quota', type=int, default=24, required=False)
    parser.add_argument('--window', type=int, default=600, required=False)
    parser.add_argument('--team-list', dest='team', type=str,
                        default='team.csv', required=False)
    parser.add_argument('--result-dir', dest='result', type=str,
                        default='result', required=False)
    parser.add_argument('--answer', type=str, required=True)
    parser.add_argument('--score', choices=['rank', 'fscore'],
                        default='rank', required=False)
    parser.add_argument('--selector', choices=['last', 'best'],
                        default='last', required=False)
    parser.add_argument('--beta', type=float, default=0.5, required=False)
    parameters = parser.parse_args()

    data = {}
    with open(parameters.team) as obj:
        for line in obj:
            team = line.strip()
            path = os.path.join(parameters.result, '%s.log' % (team, ))
            if not os.path.exists(path):
                warnings.warn('Result for team "%s" not found' % (team, ))
                continue

            data[team] = judge.judge(parameters.answer, path,
                                     quota=parameters.quota,
                                     window=parameters.window)
    size = set()
    for team in data:
        size.add(len(data[team]))
    if len(size) > 1:
        warnings.warn('Results vary in size!')
        return
    size = size.pop()
    scorer = create_scorer(parameters.beta)


    selector = _get_last
    if parameters.selector == 'best':
        selector = _get_best

    if parameters.score == 'rank':
        print(rank(data, size, scorer, selector))
    else:
        print(fscore(data, size, scorer, selector))


if __name__ == '__main__':
    main()
