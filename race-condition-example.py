import threading
from threading import Thread, Lock, Semaphore

# tLock = Lock()
tSemaphore = Semaphore()
x = 0

# critical condition: shared task between different threads
def incr():
    global x
    x += 1

def thread_task():
    
#     print("hi")
#     tLock.acquire()
    tSemaphore.acquire()
    ## critical condition
    for i in range(100000):
        incr()
    tSemaphore.release()
#     tLock.release()

def Piyali():

    global x
    x = 0

    # n_threads = 8
    # t = []
    # for t in range(n_threads):
    #   th = Thread(target=thread_task)
    #   t.append(th)
    #
    # for th in t:
    #   th.start()
    #  
    # .. give threads sufficient time to execute ..
    # 
    # for th in t:
    #  th.join()
    
    t1 = Thread(target=thread_task)
    t2 = Thread(target=thread_task)

    t1.start()
    t2.start()

    # print(threading.active_count())
    # print(threading.TIMEOUT_MAX)

    t1.join()
    t2.join()

if __name__ == '__main__': # C: int main(int argc, char* argv[]) {}, Java: public void main() {}
    for i in range(10):
        Piyali()
        print('Iter {}: x = {}'.format(i, x))
    
    
# MATLAB: f.m
#   function f = (a, b)   <-
#     return a + b
#
#  function g = (c, d)
#    return c * d