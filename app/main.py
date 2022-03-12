from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from decouple import config
import psycopg2
from psycopg2.extras import RealDictCursor
import time


DATABASE_HOST = config('HOST')
DATABASE_NAME = config('DATABASE')
DATABASE_USER = config('USER')
DATABASE_PASSWORD = config('PASSWORD')


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True

while True:
    try:
        conn = psycopg2.connect(host=DATABASE_HOST, database=DATABASE_NAME,
                user=DATABASE_USER, password=DATABASE_PASSWORD,
                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull!")
        break
    except Exception as error:
        print("Connection to database failed")
        print("Error:", error)
        time.sleep(2)



# my_posts = [
#         {"title": "fist title", "content": "first content", "rating": 4, "id": 1},
#         {"title": "second title", "content": "second content", "published": False, "id": 2}
# ]


# def find_post(id):
#     """Find post with post id and return post"""
#     for p in my_posts:
#         if p['id'] == id:
#             return p

# def find_index_post(id):
#     for i, p in enumerate(my_posts):
#         if p['id'] == id:
#             return i


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts ORDER BY id""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_200_OK)
def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) 
            VALUES (%s, %s, %s) RETURNING * """, 
            (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/post/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id), ))
    post = cursor.fetchone()
    if not post:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id:{id} was not found")
    return {"post_detail": post}


@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id), ))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id:{id} was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/post/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
        (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id:{id} was not found")
    return {"data": updated_post}
