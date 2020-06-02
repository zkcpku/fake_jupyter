from flask import Flask,request,render_template,session,redirect,url_for,make_response,jsonify
from console import *
import random
app=Flask("__name__")
app.config['SECRET_KEY'] = 'zkcpku'
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

console_list = consoleList()

def createTable(file_data,title,cols):
	thead = ['<th>' + e + '</th>' for e in cols]
	thead = ''.join(thead)
	thead = '<tr>' + thead + '</tr>'
	thead = '<thead>' + thead + '</thead>'
	tbodys = [['<th>' + e + '</th>' for e in data] for data in file_data]
	tbodys = ['<tr>' + ''.join(e) + '</tr>' for e in tbodys]
	tbodys = ''.join(tbodys)
	tbodys = '<tbody>' + tbodys + '</tbody>'

	table_content = '<table style="">' + thead + tbodys + "</table>"
	table_content = '<p>'+ table_content + '</p>'
	return table_content


@app.route("/")
def myroot():
	resp = make_response(render_template("index.html"))
	resp.set_cookie('cookie', str(random.random()))
	cookie_num = request.cookies.get("cookie")
	myconsole = console_list.getConsole(str(cookie_num))
	return resp

@app.route("/runCode",methods = ("POST",))
def myCode():
	cookie_num = request.cookies.get("cookie")

	this_code = request.form['code']
	out_rst = console_list.runCode(cookie_num,this_code)
	# print(this_code)


	out_code = ""
	this_codes = this_code.split('\n')
	for i in range(len(this_codes)):
		if (i+1) in out_rst[3]:
			out_code += ("<mark>" + this_codes[i] + "</mark>" + '\n')
		else:
			out_code += (this_codes[i] + '\n')
	
	out_dict = {'has_error':out_rst[0],'error_data':out_rst[1],'out':out_rst[2],'error_line':out_rst[3],'error_code':out_code}

	return jsonify(out_dict)

@app.route("/runLocal")
def myLocal():
	cookie_num = request.cookies.get("cookie")

	out_rst = console_list.getLocals(cookie_num)
	# print(this_code)
	# print(out_rst)
	if len(out_rst) == 0:
		out_rst = ''
	else:
		out_rst = out_rst[0]
	table_data = []
	for line in out_rst.split('\n'):
		key = line.split('\t')[0]
		value = ''.join(line.split('\t')[1:])
		table_data.append([key,value])
	col_data = ['key','value']

	table_content = createTable(table_data,'变量',col_data)
	# out_dict = {'out_rst':out_rst}

	return table_content






if __name__ == '__main__':
	app.jinja_env.auto_reload = True
	app.run(debug=True)


# python pdb 来自pytutor https://docs.python.org/3/library/pdb.html
# python code 可查阅文档https://docs.python.org/zh-cn/3.7/library/code.html#
# subprocess https://zhuanlan.zhihu.com/p/39079645
# exec
# byterun https://www.cnblogs.com/xyou/p/8861935.html https://github.com/nedbat/byterun


# https://blog.csdn.net/W_Meng_H/article/details/89399270 代码补全

# 当前的环境变量https://www.jb51.net/article/66439.htm

# print装饰https://www.jianshu.com/p/d485bb30c5bb
# 重定向https://www.cnblogs.com/zzhaolei/p/11068112.html
