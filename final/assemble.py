#!/usr/bin/env python3
'''
Judge for teams.
'''
import argparse
import os
import warnings

import judge


def rank(data, size, beta):  # pylint: disable=too-many-locals
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
                # f beta score
                factor = (1 + beta) * correct / (submitted + beta * num)
                time /= factor
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


def fscore(data, size, beta):
    '''
    For each fault, a team gets grade based on f-score.
    '''
    score = {team: 0.0 for team in data}

    for i in range(size):
        for team in data:
            time, submitted, correct, num = data[team][i]
            correct = float(correct)
            if correct:
                # f beta score
                factor = (1 + beta) * correct / (submitted + beta * num)
                time /= factor
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
    beta = parameters.beta ** 2

    if parameters.score == 'rank':
        print(rank(data, size, beta))
    else:
        print(fscore(data, size, beta))


if __name__ == '__main__':
    main()
