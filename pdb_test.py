import sys
import inspect


class Tracer:
    def dump(self, frame, event, arg):
        line = frame.f_lineno
        code = frame.f_code
        module = inspect.getmodule(code)
        module_name = ""
        module_path = ""
        if module:
            module_path = module.__file__
            module_name = module.__name__
        print(event,code.co_name, frame.f_lineno, frame.f_locals, arg)

    def trace(self, frame, event, arg):
        self.dump(frame, event, arg)
        # print("line:",frame.f_lineno)
        # print("code:",frame.f_code)
        return self.trace

    def collect(self, func, *args, **kwargs):
        sys.settrace(self.trace)
        func(*args, **kwargs)
        sys.settrace(None)

    def runsource(self, code):
        sys.settrace(self.trace)
        exec(code)
        sys.settrace(None)


if __name__ == "__main__":
    t = Tracer()
    code = """i=[0,1,2]
for j in i :
  # print(x)
  # print(y)
  print(j)
# {1,2}
"""
    t.runsource(code)
