#!/usr/bin/env python3
'''
Compare result with answer.
'''
import datetime
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
        '''Find answers for the fault which arises at given time'''
        self._quota -= self.move(timestamp)

        data = []
        while self._quota > 0 and self._index < self._total \
                and self._data[self._index][0] <= timestamp + self._window:
            submitted_at, target = self._data[self._index]
            data.append((submitted_at, target))
            self._index += 1
            self._quota -= 1

        return data

    def move(self, timestamp):
        '''Move to the first answer after given time'''
        quota = 0
        while self._index < self._total \
                and self._data[self._index][0] < timestamp:
            self._index += 1
            quota += 1
        return quota


def _parse_indices(indices):
    # pylint: disable=unnecessary-comprehension
    return {(cmdb_id, index) for cmdb_id, index in indices}


def _get_timestamp(date):
    date -= datetime.datetime(year=1970, month=1, day=1, tzinfo=dateutil.tz.UTC)
    return date.total_seconds()


def _load_answer(path):
    answers = []
    with open(path) as obj:
        data = json.load(obj)
        start_time = data['startTime']
        for timestamp, indices in data['data']:
            answers.append((int(timestamp), _parse_indices(indices)))

    answers.sort(key=lambda item: item[0])
    return start_time, answers


def _load_data(path):
    data = []
    with open(path) as obj:
        for line in obj:
            if ' ' not in line:
                continue
            try:
                sep = line.index(' ')
                # Work in python3 only
                # timestamp = dateutil.parser.parse(line[:sep]).timestamp()
                timestamp = _get_timestamp(dateutil.parser.parse(line[:sep]))
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
    start_time, answers = _load_answer(answer_path)
    results = Result(_load_data(result_path), quota=quota, window=window)
    _ = results.move(start_time)

    # 2. Summary
    data = []

    for timestamp, indices in answers:
        num = len(indices)
        data.append([(submitted_at - timestamp,
                      len(result),
                      len(result.intersection(indices)),
                      num) for submitted_at, result in results.find(timestamp)])

    return data


def score(results):
    '''Convert the output of judge as a single grade.'''
    grade = 0.0
    for window_results in results:
        if window_results:
            # Get the last one
            interval, submitted, correct, num = window_results[-1]
        else:
            correct = 0

        if correct == 0 or correct < submitted:
            # No answer or any wrong index
            grade += 6 * 60 * 60  # 6 hours
        else:
            recall = float(correct) / num
            grade += interval / recall
    if results:
        grade /= len(results)
    return grade


def main(argv):
    '''Entrance'''
    if len(argv) < 3:
        return

    answer = argv[1]
    result = argv[2]
    print(answer, result)

    grade = '%.04f minutes / fault' % (score(judge(answer, result)) / 60, )
    print(grade)


if __name__ == '__main__':
    main(sys.argv)
