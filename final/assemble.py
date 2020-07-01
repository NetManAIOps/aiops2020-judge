#!/usr/bin/env python3
'''
Judge for teams.
'''
import argparse
import os
import warnings

import judge


def rank(data, size):
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
                recall = correct / num
                time /= recall
            turn.append((team, time))
        turn.sort(key=lambda item: item[1])
        j = 0
        grade = 10
        num = len(data)
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


def fscore(data, size):
    '''
    For each fault, a team gets grade based on f-score.
    '''
    score = {team: 0.0 for team in data}

    for i in range(size):
        for team in data:
            time, submitted, correct, num = data[team][i]
            correct = float(correct)
            if submitted:
                factor = 2 * correct / (submitted + num)
                time /= factor
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
    parser.add_argument('--score', choices=['rank', 'f1-score'],
                        default='rank', required=False)
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

    if parameters.score == 'rank':
        print(rank(data, size))
    else:
        print(fscore(data, size))


if __name__ == '__main__':
    main()
