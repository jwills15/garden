import time

n = 0

try:
    while n < 100:
        n += 1
        print(n)
        time.sleep(1)
except KeyboardInterrupt:
    pass
