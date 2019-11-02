from celery import Celery

"""
app = Celery('tasks', backend='rpc', broker='amqp://')


@app.task(ignore_result=True)
def print_hello():
    print('hello there')


@app.task
def gen_prime(x):
    multiples = []
    results = []
    for i in xrange(2, x+1):
        if i not in multiples:
            results.append(i)
            for j in xrange(i*i, x+1, i):
                multiples.append(j)
    return results
"""

app = Celery(__name__, backend="rpc://", broker="pyamqp://")


@app.task
def add(x, y):
    return x + y
