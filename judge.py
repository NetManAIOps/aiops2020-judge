#!/usr/bin/env python3
'''
Compare result with answer.
'''
import argparse
import json
import os
import warnings


class Answer():
    '''Structure of ground truth'''

    __slots__ = ['category', 'cmdb_id', 'candidates']

    def __init__(self, category, cmdb_id, candidates):
        self.category = category
        self.cmdb_id = cmdb_id
        self.candidates = set(candidates)


class Result():
    '''Structure of submitted answer'''

    __slots__ = ['category', 'cmdb_id', 'index']

    def __init__(self, category, cmdb_id, index):
        self.category = category
        self.cmdb_id = cmdb_id
        self.index = index

    def is_correct(self, answer):
        '''
        Compare result with ground truth.
        '''
        return self.category == answer.category and \
            self.cmdb_id == answer.cmdb_id and \
            self.index in answer.candidates


def load_data(path):
    '''
    Load data from a file, each line of which is a json object.
    '''
    data = {}
    with open(path) as obj:
        try:
            data = json.load(obj)
        except json.decoder.JSONDecodeError:
            warnings.warn('Failed to parse "%s"' % (path, ))
    return data


def get_rank(results, answer):
    '''Get the rank of correct result'''
    for index, result in enumerate(results):
        if result.is_correct(answer):
            return index
    return None


def judge(answer_path, result_path, grade_gradient=(100, 20)):
    '''
    Compare the submitted answer with ground truth, with a grade returned.
    '''
    print('"%s" is to be submitted, judged by "%s"' %
          (result_path, answer_path))
    # 1. Prepare data
    answers = load_data(answer_path)
    results = load_data(result_path)
    print('Fault Count: %d. Result Count: %d' %
          (len(answers), len(results)))

    # 2. Grade
    grade = 0
    for i in answers:
        if i not in results:
            continue
        answer = Answer(*answers[i])
        result = [Result(*item) for item in results[i]]
        rank = get_rank(result, answer)
        if rank is not None and rank < len(grade_gradient):
            grade += grade_gradient[rank]

    return grade


def _dump_data(data, path):
    if os.path.exists(path):
        warnings.warn('"%s" already exsits' % (path, ))
        return False
    with open(path, 'w') as obj:
        json.dump(data, obj, indent=2)
    return True


def _demo(answer_path, result_path):
    print('Create sample gound truth at: "%s"' % (answer_path, ))
    ground_truth = {
        1: ('os', 'os_020', ('CPU_user_time', 'CPU_util_pct')),
        2: ('docker', 'docker_001', (None, )),  # Network error
        3: ('db', 'db_003', ('User_Commit', )),
        4: ('os', 'os_019', ('Memory_free', )),
    }
    _dump_data(ground_truth, answer_path)

    print('Create submitted answer at: "%s"' % (result_path, ))
    submitted_answer = {
        1: [('docker', 'docker_001', None), ],
        2: [('docker', 'docker_001', None), ],  # Network error
        3: [('db', 'db_003', None), ('db', 'db_003', 'User_Commit')],
    }
    _dump_data(submitted_answer, result_path)

    print('Now, re-run with an action of "judge" to get a grade of 120')


def main():
    '''Entrance'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--answer', dest='answer', type=str,
                        default='answer.json', required=False,
                        help='File with ground truth.')
    parser.add_argument('-r', '--result', dest='result', type=str,
                        default='result.json', required=False,
                        help='File with your answer.')
    parser.add_argument('action', choices=['judge', 'demo'],
                        help='Choose "demo" for demonstration.')
    parameters = parser.parse_args()

    if parameters.action == 'demo':
        _demo(parameters.answer, parameters.result)
    elif parameters.action == 'judge':
        print('Grade: %d' % (judge(parameters.answer, parameters.result), ))


if __name__ == '__main__':
    main()
