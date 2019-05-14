import functools

def log(text):
    def decorator1(func):
        @functools.wraps(func)
        def wrapper(label,*args, **kw):
            print( '%s %s():' % (text, func.__name__))
            if(label == 'func2'):
                return myfunc2(*args,**kw)
            return func(label,*args, **kw)
        return wrapper
    return decorator1

@log('exec')
def myfunc(s):
    print('print ' +s);
    return

def myfunc2():
    print('fun2 reached')
    return
