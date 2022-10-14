"""
parse log file to different task log

useage: 
    print task information: python parse_log.py log_file summary
    print special task logs: python parse_log.py log_file logs analysis_id task_id1,task_id2
    print special task logs: python parse_log.py log_file options analysis_id task_id
"""

import sys
import argparse
from dateutil import parser

class LogLine:
    """
    Log line 
    """
    def __init__(self, line):
        self._task_id = ''
        self._analysis_id = ''
        self._line = line.rstrip()

        # 2022-06-15 05:42:35,838	INFO	1	strategy:155	Task celery_task_analysis[306b9f0a-4011-4141-8c4f-75b4c5997d00] received
        # 2022-06-15 05:42:36,000	WARNING	49	task_runner:82	TaskRunnerProc task_project_init_0 started.
        # 2022-06-15 05:42:36,294	WARNING	49	tasks:44	task_project_init_0 stop, analysis_id: 744c240c-7bb9-4739-abc7-080a6a042f06, git_url: ssh://git-server/git-server/custom-repos/test.git
        # 2022-06-22 01:03:16,365	WARNING	131	celery_task:41	celery_task_analysis, celery_task_id: 6ac7d1bd-4cd0-4c6a-ace0-1019bd1d6111 analysis_id: 63e40410-3051-4b63-89d6-d47885f1045c git_url: https://github.com/yangbobo2021/test_debug_demo2.git

        vl = line.strip().replace('\t', ' ').split(' ')

        #if len(vl) > 7 and vl[5] == 'Task' and vl[-1] == 'received':
        if len(vl) > 7 and vl[-2] == 'git_url:' and vl[-4] == 'analysis_id:' and vl[-6] == 'celery_task_id:':
            self._analysis_id = vl[-3]
            self._git_url = vl[-1]
        if len(vl) > 4 and len(vl[0].split('-')) == 3 and len(vl[1].split(':')) == 3:
            try:
                tid = int(vl[3])
                self._task_id = vl[3]
            except Exception as e:
                pass

    def is_analysis_start(self):
        return self._analysis_id != ''
    def analysis_id(self):
        return self._analysis_id

    def git_url(self):
        return self._git_url

    def task_id(self):
        return self._task_id

    def content(self):
        return self._line

class LogTask:
    """
    Task information
    """
    def __init__(self, id):
        self._id = id
        self._status = ''
        self._task_name = ''
        self._errors = 0
        self.task_options = {}
        self.project_options = {}
        self.analysis_options = {}
        self._start_time = None
        self._last_time = None
        self._on_commits = []
        self._on_files = []
        self._spent_time_info = {}

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._task_name

    @property
    def spent_time(self):
        if self._start_time is not None:
            return (self._last_time - self._start_time).total_seconds()
        else:
            return -1

    def update(self, line):
        # 2022-06-15 05:42:35,880	WARNING	48	celery_task:41	celery_task_analysis, celery_task_id: 306b9f0a-4011-4141-8c4f-75b4c5997d00 analysis_id: 744c240c-7bb9-4739-abc7-080a6a042f06 git_url: ssh://git-server/git-server/custom-repos/test.git
        # 2022-06-15 05:42:35,880	WARNING	48	celery_task:41	celery_task_analysis, celery_task_id: 306b9f0a-4011-4141-8c4f-75b4c5997d00 analysis_id: 744c240c-7bb9-4739-abc7-080a6a042f06 git_url: ssh://git-server/git-server/custom-repos/test.git
        # 2022-06-15 05:42:36,000	WARNING	49	task_runner:82	TaskRunnerProc task_project_init_0 started.
        # 2022-06-15 05:42:36,294	WARNING	49	tasks:44	task_project_init_0 stop, analysis_id: 744c240c-7bb9-4739-abc7-080a6a042f06, git_url: ssh://git-server/git-server/custom-repos/test.git
        # _logger.info(f'task_options: {json.dumps(task_options_dict)}')
        # _logger.info(f'project_options: {project_options.json()}')
        # _logger.info(f'analysis_options: {analysis_options.json()}')
        # 2022-09-22 02:21:21,869 INFO    72      analysis:279    start commit(b1fe498eb975d112b06814253f9b9e8dc561d91f) analysis
        # 2022-09-22 02:21:22,053 INFO    72      analysis:494    [Progress update] task_name: task_analyze_commits_2 progress: 90%
        # 2022-09-22 02:21:22,096 INFO    72      time_measure:56 [Time Context] Analysis each commit, duration: 21.081202447996475, memory: 950.15234375
        # 2022-09-22 02:21:22,096 INFO    72      analysis:494    [Progress update] task_name: task_analyze_commits_2 progress: 100%
        # 2022-09-22 02:21:22,527 INFO    72      time_measure:56 [Time Context] Analysis all commits event, duration: 0.4305837609572336, memory: 950.15234375
        # 2022-09-22 02:28:44,958	INFO	17673	analysis:325	start file(conf/locale/locale_vi-VN.ini) analysis
        # 2022-09-22 02:28:44,985	INFO	15884	analysis:494	[Progress update] task_name: task_analyze_commits_106 progress: 54%
        # 2022-09-22 02:28:45,007	INFO	15884	analysis:279	start commit(958d8b6bb4c2da66859325695b91d871e567a4fa) analysis
        # 2022-09-22 02:28:45,043	INFO	17673	analysis:325	start file(docker/runtime/backup-rotator.sh) analysis
        # 2022-09-22 02:28:45,107	INFO	17673	analysis:325	start file(docs/admin/lfs.md) analysis
        time_str = line[:23]
        try:
            t1 = parser.parse(time_str)
            if self._start_time is None:
                self._start_time = t1
            self._last_time = t1
        except Exception as e:
            pass

        vl = line.strip().replace('\t', ' ').split(' ')
        if len(vl)>3 and vl[-1] == 'started.' and vl[-3] == 'TaskRunnerProc':
            self._status = 'started'
            self._task_name = vl[-2]
        elif len(vl)>5 and vl[-2] == 'git_url:' and vl[-4] == 'analysis_id:' and vl[-5] == 'stop,':
            self._status = 'stop'
        elif len(vl) > 8 and vl[5] == 'celery_task_analysis,' and vl[6] == 'celery_task_id:':
            self._status = 'started'
            self._task_name = 'celery_task_analysis'

        if len(vl)>5 and vl[5] == 'task_options:':
            self.task_options = line[line.find('task_options:')+len('task_options:'):].strip()
        elif len(vl)>5 and vl[5] == 'project_options:':
            self.project_options = line[line.find('project_options:')+len('project_options:'):].strip()
        elif len(vl)>5 and vl[5] == 'analysis_options:':
            self.analysis_options = line[line.find('analysis_options:')+len('analysis_options:'):].strip()

        if len(self._on_commits) > 0 and 'end_time' not in self._on_commits and (line.find('start commit(') > 0 or line.find('Analysis each commit') > 0 or line.find('Finish analyze commits') > 0):
            #if len(self._on_commits) > 0:
            self._on_commits[-1]['end_time'] = self._last_time
        if len(self._on_files) > 0 and 'end_time' not in self._on_files[-1] and (line.find('start file(') > 0 or line.find('Time spent:') > 0 or line.find('Finish analyze commits') > 0):
            #if len(self._on_files) > 0:
            self._on_files[-1]['end_time'] = self._last_time
            
        if line.find('start commit(') > 0:
            pos1 = line.find('start commit(')
            pos2 = line.find(')', pos1)
            commit = {
                'commit': line[pos1+len('start commit('):pos2],
                'start_time': self._last_time
            }
            self._on_commits.append(commit)

        if line.find('start file(') > 0:
            pos1 = line.find('start file(')
            pos2 = line.find(')', pos1)
            file = {
                'file': line[pos1+len('start file('):pos2],
                'start_time': self._last_time
            }
            self._on_files.append(file)

        if line.find('Time spent: analyzer') >= 0:
            pos1 = line.find('[')
            pos2 = line.find(']', pos1)
            pos3 = line.find('[', pos2)
            pos4 = line.find(']', pos3)
            pos5 = line.find('[', pos4)
            pos6 = line.find(']', pos5)

            name = line[pos1+1:pos2]
            time_v = float(line[pos3+1:pos4])
            event = line[pos5+1:pos6]

            event = event[1:event.find(' ')]
            event = event.split('.')[-1]

            key = name+'::'+event
            self._spent_time_info[key] = time_v


        if len(vl)>3:
            if vl[2] == 'ERROR':
                self._errors += 1

    def is_stop(self):
        return self._status == 'stop'

    def print(self):
        print(f'    task id: {self._id} name: {self._task_name} status: {self._status} error: {self._errors}')

    def print_options(self):
        print(f'task_options = \'{self.task_options}\'')
        print(f'project_options = \'{self.project_options}\'')
        print(f'analysis_options = \'{self.analysis_options}\'')

    def print_on_commit_time(self):
        """
        output time spent on on_commit event
        """
        for commit in self._on_commits:
            if 'end_time' in commit:
                print(commit['commit'], (commit['end_time'] - commit['start_time']).total_seconds())

class LogAnalysis:
    """
    Analysis information
    """
    def __init__(self, id, git_url):
        self._id = id
        self._tasks = {}
        self._git_url = git_url
        self._start_time = None
        self._last_time = None
    def update(self, task_id, line):
        time_str = line[:23]
        try:
            t1 = parser.parse(time_str)
            if self._start_time is None:
                self._start_time = t1
            self._last_time = t1
        except Exception as e:
            pass

        if task_id not in self._tasks:
            self._tasks[task_id] = LogTask(task_id)
        # if self._tasks[task_id]._status == 'stop':
        #     print('----> ', task_id, self._git_url, line)
        self._tasks[task_id].update(line)
    def print(self):
        print('analysis id:', self._id)
        print('  all tasks:')
        for t in self._tasks:
            self._tasks[t].print()

    def task(self, id):
        if id in self._tasks:
            return self._tasks[id]
        return None

    def tasks(self):
        return [self._tasks[t] for t in self._tasks]


    @property
    def id(self):
        return self._id

    @property
    def git_url(self):
        return self._git_url

    @property
    def spent_time(self):
        if self._start_time is not None:
            return (self._last_time - self._start_time).total_seconds()
        else:
            return -1

class LogFile:
    """
    Log file
    """
    def __init__(self, logfile):
        self._analysis = []
        self._lines = []

        with open(logfile, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            log_line = LogLine(line)
            self._lines.append(log_line)

            if log_line.is_analysis_start():
                self._analysis.append(LogAnalysis(log_line.analysis_id(), log_line.git_url()))

            task_id = log_line.task_id()
            if task_id != '':
                if len(self._analysis) == 0:
                    self._analysis.append(LogAnalysis('', ''))
                self._analysis[-1].update(task_id, log_line.content())
            
    def analysis(self, id) -> LogAnalysis:
        for a in self._analysis:
            if a.id == id:
                return a
        return None

    def last_analysis(self):
        if len(self._analysis) > 0:
            return self._analysis[-1]
        return None

    def print(self):
        print('--> all analysis:')
        for a in self._analysis:
            a.print()

    def logs(self, analysis_id, task_ids):
        got = False
        for line in self._lines:
            if got and line.is_analysis_start():
                break
            if line.analysis_id() == analysis_id:
                got = True
            if got and (line.task_id() in task_ids or line.task_id() == ''):
                print(line.content())

def output_summary(log_file_name):
    log_file = LogFile(log_file_name)
    log_file.print()

def output_logs(log_file_name, analysis_id, task_ids):
    log_file = LogFile(log_file_name)
    log_file.logs(analysis_id, task_ids) 

def output_task_options(log_file_name, analysis_id, task_ids):
    log_file = LogFile(log_file_name)

    analysis = log_file.analysis(analysis_id)
    if analysis is None:
        print(f'Not found analysis by {analysis_id}')
        return 

    for task_id in task_ids:
        task = analysis.task(task_id)
        if task is None:
            print(f'Not found task by {task_id}')
            continue 

        task.print_options() 



if __name__ == '__main__':
    try:
        # arguments process
        parser = argparse.ArgumentParser(description='AE Log parse analyzer.')
        parser.add_argument('file', action='store', nargs=1, 
                            help='log file path')
        parser.add_argument('--action', action='store', required=True, choices=['summary', 'task', 'options'], default=[],
                            help='summary: show summary logs  task: show log filtered by task id   options: show task options')
        parser.add_argument('--analysisid', action='store', required=False,
                            help='specify analysis di')        
        parser.add_argument('--taskids', action='store', required=False,
                            help='specify task ids, e.g. 10,20 ')


        args = parser.parse_args()


        if args.action == 'task' or args.action == 'options':
            if args.analysisid is None:
                print('Missed --analysisid option') 
                exit(0)
            if args.taskids is None:
                print('Missed --taskids option') 
                exit(0)

        if args.action == 'summary':
            output_summary(args.file[0])
        elif args.action == 'task':
            output_logs(args.file[0], args.analysisid, args.taskids.split(','))
        elif args.action == 'options':
            output_task_options(args.file[0], args.analysisid, args.taskids.split(','))
        else:
            print('unknow action: ', args.action)
    except Exception as e:
        print(e)




