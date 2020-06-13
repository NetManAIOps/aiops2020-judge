#!/usr/bin/env python3
'''
Compare result with answer.
'''
import json
import sys
import warnings

import dateutil.parser


class Result():  # pylint: disable=too-few-public-methods
    '''Consumer of submitted answer'''

    def __init__(self, data, quota=24, window=10 * 60):
        self._data = data
        self._total = len(data)
        self._index = 0  # next answer
        self._quota = quota
        self._window = window

    def find(self, timestamp):
        '''Find answer for the fault which arises at given time'''
        submitted_at = None
        target = None

        # Find the first answer which is after the given time
        while self._quota > 0 and self._index < self._total \
                and self._data[self._index][0] < timestamp:
            self._index += 1
            self._quota -= 1

        while self._quota > 0 and self._index < self._total \
                and self._data[self._index][0] <= timestamp + self._window:
            submitted_at, target = self._data[self._index]
            self._index += 1
            self._quota -= 1

        return submitted_at, target


def _parse_indices(indices):
    # pylint: disable=unnecessary-comprehension
    return {(cmdb_id, index) for cmdb_id, index in indices}


def _load_answer(path):
    data = []
    with open(path) as obj:
        for timestamp, indices in json.load(obj):
            data.append((int(timestamp), _parse_indices(indices)))

    data.sort(key=lambda item: item[0])
    return data


def _load_data(path):
    data = []
    with open(path) as obj:
        for line in obj:
            if ' ' not in line:
                continue
            try:
                sep = line.index(' ')
                timestamp = dateutil.parser.parse(line[:sep]).timestamp()
                data.append((timestamp, _parse_indices(json.loads(line[sep:]))))
            except:  # pylint: disable=bare-except
                warnings.warn('Failed to parse "%s"' % (line.strip(), ))

    data.sort(key=lambda item: item[0])
    return data


def judge(answer_path, result_path, quota=24, window=10 * 60):
    '''
    Compare the submitted answer with ground truth, with a grade returned.
    '''
    # 1. Prepare data
    answers = _load_answer(answer_path)
    results = Result(_load_data(result_path), quota=quota, window=window)

    # 2. Grade
    grade = 0.0

    for timestamp, indices in answers:
        submitted_at, result = results.find(timestamp)
        if not result or not result <= indices:
            # No answer or any wrong index
            grade += 6 * 60 * 60  # 6 hours
        else:
            recall = float(len(result)) / len(indices)
            grade += (submitted_at - timestamp) / recall

    if answers:
        grade /= len(answers)

    return grade


def main(argv):
    '''Entrance'''
    if len(argv) < 3:
        return

    answer = argv[1]
    result = argv[2]
    print(answer, result)

    grade = '%.04f minutes / fault' % (judge(answer, result) / 60, )
    print(grade)


if __name__ == '__main__':
    main(sys.argv)
