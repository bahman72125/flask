from flask import Flask ,render_template ,session,request,redirect
from markupsafe import escape
from datetime import timedelta
from app.database2 import *
import os

app = Flask(__name__)
app.secret_key=os.getenv('sk')
app.config['PERMANENT_SESSION_LIFETIME']=timedelta(minutes=30 , hours=2 , seconds=30)

app.config["MONGO_URI"]="mongodb://localhost:27017/blog"
init_db(app)

@app.route("/")
def home():
    posts=get_posts()
    return render_template('index.html ',posts=posts)


@app.route("/login/",methods=['POST' ,'GET'])
def login():
    if request.method =='GET':
        return render_template('login.html')
    else:
        inusername=request.form['username']    
        inpassword=request.form['password'] 
        if inusername=='admin'and  inpassword=='1234':
            session['admin']=True
            session['username']= inusername
            return redirect ('/')
        else:
            return render_template('login.html', errormsg='invalid username or password...')           

@app.route("/logout/")
def logout():
        session['admin']=False
        session['username']='Guest'
        return redirect ('/')   

@app.route("/newpost/",methods=['POST' ,'GET'])
def newpost():
    import os
    import time
    if not session.get('admin'):
        return redirect ('/login')
    
    if request.method =='GET':
        return render_template('newpost.html')
    else:
        title=request.form['title']    
        content=request.form['content'] 
        image=None
        if request.files['image'].filename:
            file=request.files['image']
            myfilename=f'{time.time()}{request.files['image'].filename}'
            newfile=os.path.join(app.root_path,'static','upload',myfilename)
            file.save(newfile)
            image=myfilename
        add_post(title=title , content=content,image=image)
        return redirect ('/')
  #  return render_template('newpost.html')


@app.route("/editpost/<int:post_id>",methods=['POST' ,'GET'])
def edit_post(post_id:int):
    if not session.get('admin'):
        return redirect ('/login')
    if request.method =='GET':
        post=get_post_by_id(post_id)
        if not post:
            return redirect ('/')
        return render_template('editpost.html',post= post)
    else:
        title=request.form['title']    
        content=request.form['content'] 
        update_post(post_id=post_id ,title=title , content=content)
        return redirect ('/')
    
@app.route("/view_comments/<int:post_id>",methods=['POST' ,'GET'])
def view_comments(post_id:int):
    if request.method =='GET':
        post=get_post_by_id(post_id)
        if not post:
            return redirect ('/page404')
        comments=get_comments(post_id)
        return render_template('comments.html',post= post, comments=comments)
    else:
        author=request.form['author']    
        text=request.form['comment'] 
        add_comment(post_id=post_id ,author=author , text=text)
        return redirect (f'/view_comments/{post_id}')
    
@app.route("/deletepost/<int:post_id>",methods=['POST' ,'GET'])
def delete_post(post_id:int):
    if not session.get('admin'):
        return redirect ('/login')
    if request.method =='GET':
        post=get_post_by_id(post_id)
        if not post:
            return redirect ('/')
       # return render_template('deletepost.html',post= post)
        delete_post_from_db(post_id=post_id)
        return redirect ('/')

if __name__ == '__main__':
    app.run(debug = True)

    #   {% if posts[0] > 0 %}    
    # {% else %}
    # {% endif %}