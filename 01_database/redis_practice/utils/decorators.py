import time
from functools import wraps


def measure_time(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = f(*args, **kwargs)
        end = time.perf_counter() - start
        print(f"{wrapper.__name__} 소요시간: {end:.03f}초")
        return result
    return wrapper
