from flask import Flask,request,render_template,session,redirect,url_for,make_response,jsonify
from console import *
import random
import keyword
from getast import *

app=Flask("__name__")
app.config['SECRET_KEY'] = 'zkcpku'
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

console_list = consoleList()

def createTable(file_data,title = '变量',cols = ['key','value']):
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
		# print(line)
		# print(line.split('\t')[1:])
		key = line.split('\t')[0]
		value = ''.join(line.split('\t')[1:]).replace('<','"').replace('>','"')
		# print(str(value))
		table_data.append([str(key),str(value)])
	col_data = ['key','value']

	table_content = createTable(table_data,'变量',col_data)
	# out_dict = {'out_rst':out_rst}

	return table_content

@app.route("/getKeywords",methods = ("POST",))
def getKeywords():
	cookie_num = request.cookies.get("cookie")
	this_code = request.form['code']

	this_code = [e for e in this_code.split('\n') if len(e) > 0] # 最后一行
	if len(this_code) == 0:
		this_code = ''
	else:
		this_code = this_code[-1]
	this_code = this_code.replace('\t','').replace(' ','')
	# print(this_code)
	variables = re.findall('[a-zA-Z_][a-zA-Z_0-9]*',this_code)
	if len(variables) == 0:
		variables = ['']

	all_var = keyword.kwlist + []
	out_rst = console_list.getLocals(cookie_num)
	if len(out_rst) == 0:
		out_rst = ''
	else:
		out_rst = out_rst[0]
	for line in out_rst.split('\n'):
		# print(line)
		# print(line.split('\t')[1:])
		key = line.split('\t')[0]
		all_var.append(str(key))
	# print(all_var)
	# print(variables)
	if len(variables[-1]) == 0:
		maybe_var = []
	else:
		maybe_var = [e + '\t' for e in all_var if e.find(variables[-1]) != -1]
	# print(maybe_var)
	maybe_var.sort()
	maybe_rst = ''.join(maybe_var)
	return maybe_rst


def mark_code(line_nums, this_code, color = 'red'):
	# if line_num <= 0:
	# 	return this_code
	out_code = ""
	this_codes = this_code.split('\n')
	for i in range(len(this_codes)):
		if (i+1) in line_nums:
			out_code += ("<mark style='background-color:" + color + ";'>" + this_codes[i] + "</mark>" + '\n')
		else:
			out_code += (this_codes[i] + '\n')
	return out_code

@app.route("/runStep",methods = ("POST",))
def myStep():
	cookie_num = request.cookies.get("cookie")

	this_code = request.form['code']
	out_rst = console_list.runCode(cookie_num,this_code,True)
	# print(this_code)

	out_code = ""
	this_codes = this_code.split('\n')
	for i in range(len(this_codes)):
		if (i+1) in out_rst[3]:
			out_code += ("<mark>" + this_codes[i] + "</mark>" + '\n')
		else:
			out_code += (this_codes[i] + '\n')
	
	out_dict = {'has_error':out_rst[0],'error_data':out_rst[1],'out':out_rst[2],'error_line':out_rst[3],'error_code':out_code}

	step_out = []

	if out_rst[0] == False:
		out_rsts = out_rst[2][0].split('\n')
		for step_rst in out_rsts:
			# print(step_rst)
			if step_rst[:10] == '_____event':
				# 说明是trace
				if step_rst.split('\t')[1].strip() != 'line': # 存疑？
					continue

				step_line = re.findall('line: (\d*)',step_rst)
				if len(step_line) > 0:
					step_line = int(step_line[0])
				else:
					step_line = -1

				step_dict = re.findall("locals: ({.*})",step_rst)
				if len(step_dict) > 0:
					step_dict = step_dict[0].replace("<",'"').replace(">",'"')
					step_dict = eval(step_dict)
				else:
					step_dict = {}
				table_data = []
				for k in step_dict:
					table_data.append([str(k),str(step_dict[k])])

				step_this_out = ""
				if len(step_out) > 0:
					step_this_out += step_out[-1]['out']


				step_msg = {'code':mark_code([step_line],this_code),'local_table':createTable(table_data),'out':step_this_out}
				step_out.append(step_msg)
			else:
				step_out[-1]['out'] += (step_rst + '\n')

	out_dict['step_out'] = step_out




	return jsonify(out_dict)

@app.route("/getAST",methods = ("POST",))
def myAST():
	cookie_num = request.cookies.get("cookie")

	this_code = request.form['code']
	out_dict = get_ast_dict(this_code)

	return jsonify(out_dict)


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
