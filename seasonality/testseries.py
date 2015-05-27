
import os
import sys
import glob
import routes
from multiprocessing import Queue, Process
import multiprocessing


class Runner(Process):

    def __init__(self, queue):
        Process.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            cmd = self.queue.get()
            if cmd:
                os.system(cmd)
            else:
                self.queue.put(None)
                break


def main(args):
    configs = glob.glob(routes.tests['dir'] + '/*')

    process_queue = Queue()
    for config in configs:
        process_queue.put("python manage.py " + config)
    process_queue.put(None)

    runners = []
    for i in xrange(multiprocessing.cpu_count()):
        runners.append(Runner(process_queue))
    for runner in runners:
        runner.start()
    for runner in runners:
        runner.join()


if __name__ == "__main__":
    main(sys.argv[1:])
