"""
Compare performance on different AE version
"""
import csv
from typing import List
import parse_logs as pl

VERSION_LOG_A = 'indicator_logs_20221011_develop_performance_debug_3.log'
VERSION_LOG_B = 'indicator_logs_20221011_develop_debug_1.log' #'indicator_logs_20221008_develop_debug_4.log' #'indicator_logs_20221008_develop_debug_3.log'

RESULT_ANALYSIS_TIME = 'compare_analysis_time.csv'
RESULT_TASK_TYPE_TIME = 'compare_task_type_time.csv'
RESULT_TASK_TIME = 'compare_task_time.csv'
RESULT_UNIT_EVENT_TIME = 'compare_unit_event_time.csv'
RESULT_TASK_UNIT_EVENT_TIME = 'compare_task_unit_event_time.csv'
RESULT_COMMIT_TIME = 'compare_commit_time.csv'
RESULT_FILE_TIME = 'compare_file_time.csv'


def save_repos(repos, repo_file):
    """
    写入CSV结果文件
    """
    with open(repo_file, 'w', newline='') as csvfile:
        fieldnames = list(repos[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for repo in repos:
            writer.writerow(repo)

class CompareResult:
    """
    Performance compare result
    """
    def __init__(self, git_url):
        self._git_url = git_url
        self._version_a_time = -1
        self._version_b_time = -1
        self._type_time = {}
        self._unit_event_time = {}
        self._task_unit_event_time = {}
        self._commit_time = {}
        self._file_time = {}
        self._task_time = {}

    def set_analysis_time(self, version_a_time, version_b_time):
        self._version_a_time = version_a_time
        self._version_b_time = version_b_time

    def set_task_time_by_type(self, task_type, version_a_time, version_b_time):
        self._type_time[task_type] = (version_a_time, version_b_time)

    def set_task_time(self, task, version_a_time, version_b_time):
        self._task_time[task] = (version_a_time, version_b_time)

    def set_analysis_time_by_unit_event(self, unit_event, version_a_time, version_b_time):
        self._unit_event_time[unit_event] = (version_a_time, version_b_time)

    def set_analysis_time_by_task_unit_event(self, task, unit_event, version_a_time, version_b_time):
        if task not in self._task_unit_event_time:
            self._task_unit_event_time[task] = {}
        if unit_event not in self._task_unit_event_time[task]:
            self._task_unit_event_time[task][unit_event] = [0, 0]
        self._task_unit_event_time[task][unit_event][0] += version_a_time
        self._task_unit_event_time[task][unit_event][1] += version_b_time

    def set_commit_time(self, commit, time_a, time_b):
        self._commit_time[commit] = (time_a, time_b)

    def set_file_time(self, file, time_a, time_b):
        self._file_time[file] = (time_a, time_b)

    @property
    def git_url(self):
        return self._git_url

    @property
    def analysis_time(self):
        return [{'git_url': self._git_url, 'analysis_time_a': self._version_a_time, 'analysis_time_b': self._version_b_time}]
    
    @property
    def task_type_time(self):
        task_type_time = []
        for v in self._type_time:
            task_type_time.append({
                'git_url': self._git_url,
                'task_type': v,
                'task_type_time_a': self._type_time[v][0],
                'task_type_time_b': self._type_time[v][1],
            })
        return task_type_time

    @property
    def task_time(self):
        task_time = []
        for v in self._task_time:
            task_time.append({
                'git_url': self._git_url,
                'task': v,
                'task_time_a': self._task_time[v][0],
                'task_time_b': self._task_time[v][1],
            })
        return task_time

    @property
    def unit_event_time(self):
        unit_event_time = []
        for v in self._unit_event_time:
            unit_event_time.append({
                'git_url': self._git_url,
                'unit_event': v,
                'unit_event_time_a': self._unit_event_time[v][0],
                'unit_event_time_b': self._unit_event_time[v][1],
            })
        
        return sorted(unit_event_time, key=lambda k:k['unit_event'])

    @property
    def task_unit_event_time(self):
        task_unit_event_time = []
        for task in self._task_unit_event_time:
            for v in self._task_unit_event_time[task]:
                task_unit_event_time.append({
                    'git_url': self._git_url,
                    'task': task,
                    'unit_event': v,
                    'unit_event_time_a': self._task_unit_event_time[task][v][0],
                    'unit_event_time_b': self._task_unit_event_time[task][v][1],
                })
        
        return sorted(task_unit_event_time, key=lambda k:k['unit_event'])
    
    @property
    def commit_time(self):
        commit_time = []
        for v in self._commit_time:
            commit_time.append({
                'git_url': self._git_url,
                'commit': v,
                'commit_time_a': self._commit_time[v][0],
                'commit_time_b': self._commit_time[v][1],
            })
        return commit_time

    @property
    def file_time(self):
        file_time = []
        for v in self._file_time:
            file_time.append({
                'git_url': self._git_url,
                'file': v,
                'file_time_a': self._file_time[v][0],
                'file_time_b': self._file_time[v][1],
            })
        return file_time


# parse version log file to LogFile object
log_file: pl.LogFile = pl.LogFile(VERSION_LOG_A)
log_file2: pl.LogFile = pl.LogFile(VERSION_LOG_B)


compare_results: List[CompareResult] = []


git_2_analysis_a = {}
git_2_analysis_b = {}

for analysis in log_file._analysis:
    git_2_analysis_a[analysis.git_url] = analysis
for analysis in log_file2._analysis:
    git_2_analysis_b[analysis.git_url] = analysis


for git_url in git_2_analysis_a:
    if git_url not in git_2_analysis_b:
        continue

    analysis_a = git_2_analysis_a[git_url]
    analysis_b = git_2_analysis_b[git_url]

    compare_result = CompareResult(git_url)
    compare_result.set_analysis_time(analysis_a.spent_time, analysis_b.spent_time)

    task_time = {}
    task_type_time = {}
    for task in analysis_a.tasks():
        task_time[task.name] = [task.spent_time, 0]

        task_type = task.name[: task.name.rfind('_')]
        if task_type not in task_type_time:
            task_type_time[task_type] = [0, 0]
        task_type_time[task_type][0] += task.spent_time
    for task in analysis_b.tasks():
        if task.name not in task_time:
            task_time[task.name] = [0, task.spent_time]
        else:
            task_time[task.name][1] = task.spent_time

        task_type = task.name[: task.name.rfind('_')]
        if task_type not in task_type_time:
            task_type_time[task_type] = [0, 0]
        task_type_time[task_type][1] += task.spent_time
    
    for task_type in task_type_time:
        compare_result.set_task_time_by_type(task_type, task_type_time[task_type][0] if task_type_time[task_type][0]>0 else -50, task_type_time[task_type][1] if task_type_time[task_type][1]>0 else -50)
    for task in task_time:
        compare_result.set_task_time(task, task_time[task][0], task_time[task][1])
    
    unit_event_time = {}
    for task in analysis_a.tasks():
        task_name = task.name.split('_')[-2] if len(task.name.split('_'))>2 else task.name.split('_')[-1]
        for unit_event in task._spent_time_info:
            unit_event_t = unit_event
            unit_event = unit_event + '::' + task_name
            if unit_event not in unit_event_time:
                unit_event_time[unit_event] = [0, 0]
            unit_event_time[unit_event][0] += task._spent_time_info[unit_event_t]
            compare_result.set_analysis_time_by_task_unit_event(task.name, unit_event_t, task._spent_time_info[unit_event_t], 0)
    for task in analysis_b.tasks():
        task_name = task.name.split('_')[-2] if len(task.name.split('_'))>2 else task.name.split('_')[-1]
        for unit_event in task._spent_time_info:
            unit_event_t = unit_event
            unit_event = unit_event + '::' + task_name
            if unit_event not in unit_event_time:
                unit_event_time[unit_event] = [0, 0]
            unit_event_time[unit_event][1] += task._spent_time_info[unit_event_t]
            compare_result.set_analysis_time_by_task_unit_event(task.name, unit_event_t, 0, task._spent_time_info[unit_event_t])

    for unit_event in unit_event_time:
        compare_result.set_analysis_time_by_unit_event(unit_event, unit_event_time[unit_event][0] if unit_event_time[unit_event][0]>0 else -50, unit_event_time[unit_event][1] if unit_event_time[unit_event][1]>0 else -50)


    commit_time = {}
    for task in analysis_a.tasks():
        for commit in task._on_commits:
            if commit['commit'] not in commit_time:
                commit_time[commit['commit']] = [0, 0]
            commit_time[commit['commit']][0] += (commit['end_time'] - commit['start_time']).total_seconds() if 'end_time' in commit else 0
    for task in analysis_b.tasks():
        for commit in task._on_commits:
            if commit['commit'] not in commit_time:
                commit_time[commit['commit']] = [0, 0]
            commit_time[commit['commit']][1] += (commit['end_time'] - commit['start_time']).total_seconds() if 'end_time' in commit else 0

    for commit in commit_time:
        compare_result.set_commit_time(commit, commit_time[commit][0] if commit_time[commit][0]>0 else -50, commit_time[commit][1] if commit_time[commit][1]>0 else -50)


    file_time = {}
    for task in analysis_a.tasks():
        for file in task._on_files:
            if file['file'] not in file_time:
                file_time[file['file']] = [0, 0]
            file_time[file['file']][0] += (file['end_time'] - file['start_time']).total_seconds() if 'end_time' in file else 0
    for task in analysis_b.tasks():
        for file in task._on_files:
            if file['file'] not in file_time:
                file_time[file['file']] = [0, 0]
            file_time[file['file']][1] += (file['end_time'] - file['start_time']).total_seconds() if 'end_time' in file else 0

    for file in file_time:
        compare_result.set_file_time(file, file_time[file][0] if file_time[file][0]>0 else -50, file_time[file][1] if file_time[file][1]>0 else -50)
    
    compare_results.append(compare_result)


analysis_time = []
task_type_time = []
task_time = []
unit_event_time = []
task_unit_event_time = []
commit_time = []
file_time   = []

for cr in compare_results:
    analysis_time.extend(cr.analysis_time)
    task_type_time.extend(cr.task_type_time)
    task_time.extend(cr.task_time)
    unit_event_time.extend(cr.unit_event_time)
    task_unit_event_time.extend(cr.task_unit_event_time)
    commit_time.extend(cr.commit_time)
    file_time.extend(cr.file_time)

save_repos(analysis_time, RESULT_ANALYSIS_TIME)
save_repos(task_type_time, RESULT_TASK_TYPE_TIME)
save_repos(task_time, RESULT_TASK_TIME)
save_repos(unit_event_time, RESULT_UNIT_EVENT_TIME)
save_repos(task_unit_event_time, RESULT_TASK_UNIT_EVENT_TIME)
save_repos(commit_time, RESULT_COMMIT_TIME)
save_repos(file_time, RESULT_FILE_TIME)

