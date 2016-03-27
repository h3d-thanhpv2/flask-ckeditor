# encoding: utf-8

"""
    flask-ckeditor
    ~~~~~~~~~~~~~~

        Flask love CKEditor
"""

from flask import request, url_for, make_response
from werkzeug import secure_filename, SharedDataMiddleware
import os
import random
import datetime


class CKEditor(object):
    """
    class CKEditor
    ~~~~~~~~~~~~~~

        from flask import Flask
        from flask.ext.ckeditor import CKEditor
        from flask.ext.wtf import Form
        from wtforms import SubmitField, TextareaField

        app = Flask(__name__)

        class EditForm(Form, CKEditor):
            body = TextareaField()
            submit = SubmitField('submit')

        @app.route('/ckupload/', methods=['POST'])
        def ckupload():
            form = EditForm()
            response = form.upload(endpoint=app)
            return response

    """
    def __init__(self):
        pass

    def gen_rnd_filename(self):
        """generate a random filename"""
        filename_prefix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return "%s%s" % (filename_prefix, str(random.randrange(1000, 10000)))

    def upload(self, endpoint=None, path=None, folder='upload',\
            allowed_extensions=None, max_size=None):
        """
        img or file upload methods
        endpoint: 调用的端点
        path: 自定义上传路径, 然后该路径会被写入flask的规则
        folder: 自定义上传文件夹的名字, 默认是'upload'
        allowed_extensions: 允许上传的文件扩展名集合
        max_size: 允许上传的文件的最大大小
        现在的问题就是POST的url有问题: So How 2 solve it
        /undefined: 从来没见过这种错误!
        """
        error = ''
        url = ''
        callback = request.args.get("CKEditorFuncNum")

        if request.method == 'POST' and 'upload' in request.files:
            fileobj = request.files['upload']
            fname, fext = os.path.splitext(fileobj.filename)
            if allowed_extensions and \
                fext not in allowed_extensions:
                    error = '%s not in the allowed extensions!' % fext
            rnd_name = '%s%s' % (self.gen_rnd_filename(), fext)

            if not path:
                filepath = os.path.join(endpoint.static_folder, 'upload', rnd_name)
            else:
                filepath = path
                app.add_url_rule('/ckupload/<filename>', 'uploaded_file',
                        build_only=True)
                app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
                    '/ckupload/': path
                })

            dirname = os.path.dirname(filepath)
            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except:
                    error = 'path <%s> not exist!' % filepath
            elif not os.access(dirname, os.W_OK):
                error = 'path <%s> not writable' % filepath
            if not error:
                fileobj.save(filepath)
                if not path:
                    url = url_for('.static', filename='%s/%s' % (folder, rnd_name))
                else:
                    url = url_for('.uploaded_file', filename='%s/%s' % (folder, rnd_name))
        else:
            error = 'post error'

        res = """
                <script type="text/javascript">
                window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
                </script>
             """ % (callback, url, error)

        response = make_response(res)
        response.headers["Content-Type"] = "text/html"
        return response

