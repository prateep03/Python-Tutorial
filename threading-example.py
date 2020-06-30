import threading
from threading import Thread, Lock
import time

tLock = Lock()

def calc_square(nums):
    tLock.acquire()
    print('Calculate square of nums')
    for num in nums:
        time.sleep(0.2)
        print('square:', num * num)
    tLock.release()

def calc_cube(nums):
    tLock.acquire()
    print('Calculate cube of nums')
    for num in nums:
        time.sleep(0.2)
        print('cube:', num * num * num)
    tLock.release()

def calc_power_50(nums):
    tLock.acquire()
    print('Calculate power 50 of nums')
    for num in nums:
        time.sleep(0.2)
        print('p50:', num ** 50)
    tLock.release()

# def timer(name, delay, repeat):
#     print('Timer: ', name, ' Started')
#     tLock.acquire()
#     print(name, ' has acquired lock')
#     while repeat > 0:
#         time.sleep(delay)
#         print(name, ': ', str(time.ctime(time.time())))
#         repeat -= 1
#     print(name, ' is releasing lock')
#     tLock.release()
#     print('Timer: ', name, ' Completed')

def Main():
    # t1 = Thread(target=timer, args=("Timer 1", 3, 5))
    # t2 = Thread(target=timer, args=("Timer 2", 2, 5))
    # t1.start()
    # t2.start()

    nums = [2,3,8,9]
    #result = [4, 64, 9, 81]

    # tstart = time.time()
    # calc_square(nums)
    # calc_cube(nums)
    # calc_power_50(nums)
    # print('Time taken :', time.time() - tstart)

    t1 = Thread(target=calc_square, args=(nums,))
    t2 = Thread(target=calc_cube, args=(nums,))
    t3 = Thread(target=calc_power_50, args=(nums,))

    tstart = time.time()

    t1.start()
    t2.start()
    t3.start()

    print('Count %d' % threading.active_count())

    t1.join()
    t2.join()
    t3.join()

    print('Time taken :', time.time() - tstart)

    print("Main completed")

if __name__ == "__main__":
    Main()