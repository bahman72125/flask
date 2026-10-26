from flask_pymongo import PyMongo
from datetime import datetime

myClient = None  

def init_db(app):
    global myClient
    myClient = PyMongo(app)
    


#Auto Increment
def get_next_id(colection_name):
    NextId = myClient.db['keys'].find_one_and_update(
        {"_id": colection_name},  
        {"$inc": {"value": 1}},  
        upsert=True, 
        return_document=True
    )
    return NextId["value"]


#-----------Post--------------

def add_post(title, content, image=None):
    post = {
        "_id": get_next_id('posts'),
        "title": title,
        "content": content,
        "created_at": datetime.utcnow()
    }
    if image:
        post['image']=image
    myClient.db.posts.insert_one(post)

def get_posts():
    return myClient.db.posts.find().sort({"_id":-1})

def get_post_by_id(post_id):  
    return myClient.db.posts.find_one({"_id": post_id})

def update_post( post_id, title , content):
    myClient.db.posts.update_one({"_id": post_id}, {
            "$set": {
                "title": title,
                "content":content 
            }
        })

def delete_post_from_db(post_id):
    result = myClient.db.posts.delete_one({"_id": post_id})
    return result.deleted_count > 0  

#----------Comments------------

def add_comment(post_id, author, text):
    comment = {
        "author": author,
        "text": text,
        "is_active": True,  
        "created_at": datetime.utcnow()
    }
    myClient.db.posts.update_one(
        {"_id": post_id},
        {"$push": {"comments": comment}}
    )

def get_comments(post_id):
    post = myClient.db.posts.find_one({"_id": post_id})
    if post:
        return post.get("comments", [])
    return []

def update_comment_status(post_id, comment_index):
    post = myClient.db.posts.find_one({"_id": post_id})
    if not post:
        return False 

    comments = post.get("comments", [])
    if 0 <= comment_index < len(comments):
        comments[comment_index]["is_active"] = not comments[comment_index].get("is_active", True)
        myClient.db.posts.update_one({"_id":post_id}, {"$set": {"comments": comments}})
        return True
    return False

def update_post(post_id ,title,content):
    myClient.db.posts.update_one({"_id":post_id},{
        "$set":{
            "title":title,
            "content":content
        }
    })



def delete_comment_from_db(post_id, comment_index):
    post = myClient.db.posts.find_one({"_id": post_id})
    if not post:
        return False 

    comments = post.get("comments", [])
    if 0 <= comment_index < len(comments):
        comments.pop(comment_index)
        myClient.db.posts.update_one({"_id": post_id}, {"$set": {"comments": comments}})
        return True
    return False
