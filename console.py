# 用于创建console类以及对其管理的类
# 即用于代码运行的类与环境

import code
import ast
import sys
import traceback
from codeop import CommandCompiler, compile_command
import re
import sys
from io import StringIO
import contextlib

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

# 对输出进行重定向操作
# 参考：
# https://stackoverflow.com/questions/37237034/how-to-get-results-out-of-a-python-exec-eval-call
# https://stackoverflow.com/questions/23917776/how-do-i-get-the-return-value-when-using-python-exec-on-the-code-object-of-a-fun
# https://stackoverflow.com/questions/3906232/python-get-the-print-output-in-an-exec-statement
def myExec(code,locals = None):
    with stdoutIO() as s:
        try:
            exec(code, locals)
        except Exception as e:
            print(e)
            print("[ERROR] Something wrong with function myExec")
            # raise
            # raise
    return s.getvalue()


def trace_func(frame, event, arg):
    line = frame.f_lineno
    code = frame.f_code
    mylocal = {k:frame.f_locals[k] for k in frame.f_locals if k[0] != '_'}
    print("_____event:\t",event,"\t","code:\t",code.co_name,"\t","line:",line,"\t","locals:",mylocal)

    return trace_func


class myPython(code.InteractiveInterpreter):
    """docstring for myPython"""
    def __init__(self):
        super(myPython, self).__init__()
        self.error_data = []
        self.out = []
        self.has_error = False
    def runsource(self, source, run_step = False ,filename="<input>", symbol="exec"):

        self.has_error = False
        self.out = []
        self.error_data = []
        # symbol有三种状态：指定编译代码的种类，可以指定为 exec, eval, single。
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):

            self.showsyntaxerror(filename)
            return False
        if code is None:
            return True

        if run_step:
            self.runcode_step(code)
        else:
            self.runcode(code)
        return True
    
    # 两个异常处理函数
    def showsyntaxerror(self, filename=None):
        self.has_error = True
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb
        if filename and type is SyntaxError:
            try:
                msg, (dummy_filename, lineno, offset, line) = value.args
            except ValueError:
                pass
            else:
                value = SyntaxError(msg, (filename, lineno, offset, line))
                # print(msg)
                sys.last_value = value

        lines = traceback.format_exception_only(type, value)
        self.write(''.join(lines))

    def showtraceback(self):
        self.has_error = True
        sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
        sys.last_traceback = last_tb
        try:
            lines = traceback.format_exception(ei[0], ei[1], last_tb.tb_next)
            self.write(''.join(lines))
        finally:
            last_tb = ei = None

            
#             sys.excepthook(type, value, tb)
    # def runcode(self, code):
    #     try:
    #         out = myExec(code, self.locals)
    #         print('out:',out)
    #     except SystemExit:
    #         print("[ERROR] SystemExit")
    #         # raise
    #     except:
    #         self.showtraceback()

    def runcode(self, code):
        with stdoutIO() as s:
            try:
                exec(code, self.locals)
                self.out.append(s.getvalue())
            except SystemExit:
                self.error_data.append("[ERROR] SystemExit")
                # raise
            except:
                self.showtraceback()

    def runcode_step(self, code):
        locals_backup = self.locals

        with stdoutIO() as s:
            try:
                sys.settrace(trace_func)
                exec(code, locals_backup)
                sys.settrace(None)
                self.out.append(s.getvalue())
            except SystemExit:
                sys.settrace(None)
                self.error_data.append("[ERROR] SystemExit")
                # raise
            except:
                sys.settrace(None)
                self.showtraceback()

            
    def write(self,data):
        # print(data)
        self.error_data.append(data)
        # sys.stderr.write(data)
#         return data


class consoleList():
    """docstring for consoleList"""
    def __init__(self):
        super(consoleList, self).__init__()
        self.console_dict = {}

    def getConsole(self,cookie):
        if cookie in self.console_dict:
            return self.console_dict[cookie]
        else:
            self.console_dict[cookie] = myPython()
            return self.console_dict[cookie]
    
    def runCode(self,cookie,code, run_step = False):
        console = self.getConsole(cookie)
        console.runsource(code, run_step)
        error_data = console.error_data
        error_line = []
        for er in error_data:
            match_res = re.findall('ine (\d*)',er)
            match_int = [int(e) for e in match_res]

            error_line += match_int

        return console.has_error, console.error_data, console.out,error_line

    def getLocals(self,cookie):
        code = """
for _e in dir():
    if _e in locals().keys() and _e[0] != '_':
        print(_e,'\t',locals()[_e])
        """
        has_error,error_data,out,error_line = self.runCode(cookie,code)
        # print(error_data)
        return out

    def deleteConsole(self,cookie):
        console = self.getConsole(cookie)

        delete_console = self.console_dict.pop(cookie)
        del console

        return cookie in self.console_dict
        
def generate_trace_data(src_code):
    output_data = []
    each_line_src_code = src_code.split('\n')
    # print(each_line_src_code)
    # assert False
    myconsole = myPython()
    exec_rst = myconsole.runsource(code,True)
    if myconsole.has_error:
        raise Exception('code cannot be executed, please check your code')
    exec_trace_out = myconsole.out[0]
    # print(exec_trace_out)
    exec_trace_out = exec_trace_out.strip().split('\n')
    # print(exec_trace_out)
    # assert False
    # 这里面包括两种输出，一种是traceback，另一种是代码本身的print输出
    for each_out in exec_trace_out:
        if each_out.startswith('_____event:'):
            # 这是traceback输出
            line_num = int(re.findall('line: (\d*)',each_out)[0])
            # print(each_line_src_code[line_num-1]) # 打印这一行的源代码
            output_data.append({'source_code':each_line_src_code[line_num-1]})
            states = re.findall('locals: (.*)',each_out)[0]
            states = eval(states)
            # print("states:",states)
            output_data.append({'states':states})
        else:
            # 这是代码本身的print输出
            # print("output:", each_out)
            output_data.append({'output':each_out})
    return output_data

if __name__ == '__main__':
    myconsole = myPython()
    code = """i=[0,1,2]
for j in i:
  # print(x)
  # print(y)
  print(j)
# print(x)
"""
    output_data = generate_trace_data(code)
    for e in output_data:
        if 'source_code' in e:
            # 代码
            print(e['source_code'])
        elif 'states' in e:
            # 当前trace状态
            print(e['states'])
        elif 'output' in e:
            # 当前代码的print输出
            print(e['output'])


    # myLocal_dict = {}
    # rst = myconsole.runsource(code,True)
    # # print(myconsole.has_error)
    # # print(myconsole.error_data)
    # print(myconsole.out[0] if len(myconsole.out) > 0 else [])


    # rst = myconsole.runsource('print(i)')
    # print(myconsole.has_error)
    # print(myconsole.error_data)
    # print(myconsole.out[0] if len(myconsole.out) > 0 else [])
    # print(s.getvalue())


    # # codes = code.split('\n')
    # # print(codes)
    # # for c in codes:
    # #     myconsole.runsource(c + '\n')
    # out = myExec('x = 1',myLocal_dict)
    # print(out)
    # # print(myLocal_dict)
    # out = myExec('print(x)',myLocal_dict)
    # print(out)
    # out = myExec('{1,2}',myLocal_dict)
    # print(out)

