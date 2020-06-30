import threading
from threading import Thread, Lock, Semaphore

tLock = Lock()
# tsemaphore = Semaphore()
x = 0

# critical condition: shared task between different threads
def incr():
    global x
    x += 1

def thread_task():

    tLock.acquire()
    ## critical condition
    for i in range(100000):
        incr()
    tLock.release()

def Main():

    global x
    x = 0

    t1 = Thread(target=thread_task)
    t2 = Thread(target=thread_task)

    t1.start()
    t2.start()

    # print(threading.active_count())
    # print(threading.TIMEOUT_MAX)

    t1.join()
    t2.join()

if __name__ == '__main__':
    for i in range(10):
        Main()
        print('Iter {}: x = {}'.format(i, x))