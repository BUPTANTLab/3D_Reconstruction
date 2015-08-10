#!/usr/bin/env python
import time
import datetime
import os
from subprocess import Popen, PIPE
import sys
import signal
import shutil

HTML = '/var/www/html/'
CMDDIR = '/home/tomas/bingo/Bundler-master/'

def simLog(f, m):
        f.write(m + '\n')
        print m

def sh(cd, f):
        simLog(f, 'CMD: ' + ' '.join(cd))
        simLog(f, 'DIR: ' + HTML + 'upload/')
        sub = Popen(cd, cwd = HTML + 'upload/', stdout = PIPE, stderr = PIPE, stdin = PIPE, close_fds=True, preexec_fn = os.setsid)

        try:
                print 'Sub Id: ', sub.pid
#               while sub.poll() is None:
                while True:
                        sub.stdout.flush()
                        tstr = sub.stdout.readline()
                        if sub.poll() is not None and not tstr:
                                break
                        simLog(f, tstr.strip('\n'))
                        f.flush()
                        time.sleep(0.1)
                retcode = sub.poll()
                simLog(f, 'Poll: ' + str(retcode))
                retcode = sub.wait()
                simLog(f, 'Wait: ' + str(retcode))
                f.flush()
        except KeyboardInterrupt:
                sub.send_signal(signal.SIGTERM)
                sub.terminate()
                sub.kill()
                os.killpg(sub.pid,signal.SIGTERM)
                sub.wait()
                print 'Kill Sub'
        except Exception, ex:
                print ex

while 1:
        if os.path.exists(HTML + 'upload/ok'):
                with open(HTML + 'upload/ok','r') as f:
                        ok = f.read()
                print 'Get OK: ', ok

                f = open('log', 'w')
                d1 = datetime.datetime.now()
                simLog(f, 'Start: ' + str(d1))

                sh([CMDDIR + 'RunSFM_MT.sh', ok], f)
                sh(['/home/tomas/zxyqwe/poisson/filter_poisson', HTML + 'upload/pmvs/models/option-0000.ply', HTML + '3d.ply'], f)

                d2 = datetime.datetime.now()
                simLog(f, 'End: ' + str(d2))
                d = d2 - d1
                simLog(f, 'Duration: ' + str(d))
                simLog(f, 'ok'*5)
                f.close()

                time.sleep(5)

                if os.path.exists(HTML + 'upload/ok'):
                        shutil.copy(HTML + 'log', HTML + 'upload/log')
                        t = HTML + 'result/' + time.strftime('%Y-%m-%d-%H-%M-%S') + os.sep
                        os.mkdir(t)
                        for i in os.walk(HTML + 'upload/'):
                                for m in i[1]:
                                        os.rename(HTML + 'upload/' + m, t + m)
                                for m in i[2]:
                                        os.rename(HTML + 'upload/' + m, t + m)

                print 'exit'
        time.sleep(1)
