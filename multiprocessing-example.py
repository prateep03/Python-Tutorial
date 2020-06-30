import os
import multiprocessing as mp
from multiprocessing import Process, Pool #, Queue
import time

def f1(name):
    # # if hasattr(os, 'getppid'):
    # print(os.getpid())
    print('hello {}'.format(name))

def Main1():
    p = Process(target=f1, args=('bob',))
    p.start()
    p.join()

    print("Main1 complete")


'''
def f2(q):
    q.put([42, None, 'hello'])

def Main2():
    q = Queue()
    p = Process(target=f2, args=(q,))
    p.start()
    print(q.get())
    p.join()
'''

'''
Multiprocessing Pool
'''

# work = (["A",5], ["B", 2], ["C", 3], ["D", 4])

# def work_log(work_data):
#     print(" Process %s waiting %s seconds" % (work_data[0], work_data[1]))
#     time.sleep(int(work_data[1]))
#     print(" Process %s Finished" % work_data[0])
'''
def fpool(x):
    # time.sleep(2)
    return x * x

def pool_handler():
    p = Pool(2) # multiple processes
    nums = [i for i in range(10)]
    res = p.map(func=fpool, iterable=nums)
    p.close()
    p.join()

    print(res)
'''

'''
    Multiprocessing apply_async example
'''

def fpool(x):
    time.sleep(2)
    return x * x

results = []

def callback_fpool(result):
    results.append(result)

def apply_async():
    p = mp.Pool(2)
    for i in range(10):
        async_res = p.apply_async(fpool, args=(i, ))
        print(str(async_res))
        results.append(async_res.get())

    p.close()
    p.join()
    print(results)

if __name__ == "__main__":
    # Main1()
    # print(mp.cpu_count())
    # Main2()
    # pool_handler()
    apply_async()