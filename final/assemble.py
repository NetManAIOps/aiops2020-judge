#!/usr/bin/env python3
'''
Judge for teams.
'''
import argparse
import os
import warnings

import judge


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


def rank(data, size, scorer):
    '''
    For each fault, a team gets grade based on ranking among teams.
    '''
    score = {team: 0.0 for team in data}

    for i in range(size):
        turn = []
        for team in data:
            time, submitted, correct, num = data[team][i]
            correct = float(correct)
            if submitted and correct / submitted >= 0.5:  # precision >= 0.5
                time /= scorer.calculate(correct, submitted, num)
                turn.append((team, time))
        turn.sort(key=lambda item: item[1])
        j = 0
        grade = 10
        num = len(turn)
        while j < num and grade > 0:
            team, time = turn[j]
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


def fscore(data, size, scorer):
    '''
    For each fault, a team gets grade based on f-score.
    '''
    score = {team: 0.0 for team in data}

    for i in range(size):
        for team in data:
            time, submitted, correct, num = data[team][i]
            correct = float(correct)
            if correct:
                time /= scorer.calculate(correct, submitted, num)
            else:
                time = 6 * 60 * 60
            score[team] += time
    return score


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
    scorer = FBetaScore(parameters.beta)

    if parameters.score == 'rank':
        print(rank(data, size, scorer))
    else:
        print(fscore(data, size, scorer))


if __name__ == '__main__':
    main()
