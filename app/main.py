from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


@app.get("/sqlalchemy")
def test(db: Session = Depends(get_db)):
    return {"message": "success"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts ORDER BY id""")
    #posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_200_OK)
def create_post(post: Post, db: Session = Depends(get_db)):
    #cursor.execute("""INSERT INTO posts (title, content, published) 
    #        VALUES (%s, %s, %s) RETURNING * """, 
    #        (post.title, post.content, post.published))
    #new_post = cursor.fetchone()
    #conn.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/post/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id), ))
    #post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id:{id} was not found")
    return {"post_detail": post}


@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id), ))
    #deleted_post = cursor.fetchone()
    #conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id:{id} was not found")
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/post/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):
    #cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
    #    (post.title, post.content, post.published, str(id)))
    #updated_post = cursor.fetchone()
    #conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id:{id} was not found")
    post_query.update(post.dict(), synchronize_session=False)

    db.commit()

    return {"data": post_query.first()}
