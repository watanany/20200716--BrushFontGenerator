# -*- coding: utf-8 -*-
import time
import threading

# class TestThread(threading.Thread):
#     def __init__(self, *args, **kwds):
#         super(TestThread, self).__init__(*args, **kwds)
    
#     def run(self):
#         for i in range(1000):
#             print 'Name: ' + self.name, i
#             time.sleep(1)


# thread_list = [TestThread(name=str(i)) for i in range(3)]

# for thread in thread_list:
#     thread.start()

# for thread in thread_list:
#     thread.join(timeout=10)




def f(event):
    for i in range(1000):
        event.clear()
        print i
        event.wait()

event = threading.Event()
thread = threading.Thread(target=f, args=(event,))

thread.start()

while True:
    time.sleep(3)
    event.set()

    
