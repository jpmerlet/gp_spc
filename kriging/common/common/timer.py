# -*- coding: utf-8 -*-
import time


def timeit(method):

    def aux(*args, **kwargs):
        ini = time.time()
        result = method(*args, **kwargs)
        end = time.time()

        print ('%s %.2f sec' % (method.__name__, end-ini))

        return result

    return aux


def timeit_hires(method):
    def aux(*args, **kwargs):
        ini = time.clock()
        
        # for i in range(10):
        result = method(*args, **kwargs)
        
        end = time.clock()

        print ('%s %.6f' % (method.__name__ + ", ", (end-ini)*1000.0))

        return result

    return aux
    

if __name__ == '__main__':
    @timeit
    def aux():
        time.sleep(1)
    aux()
