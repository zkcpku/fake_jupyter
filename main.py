from flask import Flask,request,render_template,session,redirect,url_for


app=Flask("__name__")
app.config['SECRET_KEY'] = 'zkcpku'
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)





if __name__ == '__main__':
	app.jinja_env.auto_reload = True
	app.run(debug=True)


# python pdb 来自pytutor https://docs.python.org/3/library/pdb.html
# python code 可查阅文档https://docs.python.org/zh-cn/3.7/library/code.html#
# subprocess https://zhuanlan.zhihu.com/p/39079645
# exec
# byterun https://www.cnblogs.com/xyou/p/8861935.html https://github.com/nedbat/byterun


# https://blog.csdn.net/W_Meng_H/article/details/89399270 代码补全