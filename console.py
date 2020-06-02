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



class myPython(code.InteractiveInterpreter):
    """docstring for myPython"""
    def __init__(self):
        super(myPython, self).__init__()
        self.error_data = []
        self.out = []
        self.has_error = False
    def runsource(self, source, filename="<input>", symbol="exec"):

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
    
    def runCode(self,cookie,code):
        console = self.getConsole(cookie)
        console.runsource(code)
        error_data = console.error_data
        error_line = []
        for er in error_data:
            match_res = re.findall('ine (\d*)',er)
            match_int = [int(e) for e in match_res]

            error_line += match_int

        return console.has_error, console.error_data, console.out,error_line

    def getLocals(self,cookie):
        code = """
for key in locals():
    print(key,'\t',locals[key])
        """
        has_error,error_data,out,error_line = self.runCode(cookie,code)
        return out

    def deleteConsole(self,cookie):
        console = self.getConsole(cookie)

        delete_console = self.console_dict.pop(cookie)
        del console

        return cookie in self.console_dict
        

if __name__ == '__main__':
    myconsole = myPython()
    code = """i=[0,1,2]
for j in i :
  # print(x)
  # print(y)
  print(j)
{1,2}
"""
    # myLocal_dict = {}
    rst = myconsole.runsource(code)
    print(myconsole.has_error)
    print(myconsole.error_data)
    print(myconsole.out)
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

