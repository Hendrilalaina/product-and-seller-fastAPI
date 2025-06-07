from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return "Hello world"

@app.get('/user/admin')
def admin():
    return {"Your are in the admin route"}

@app.get('/user/{username}')
def profile(username: str):
    return {f"This is a profile page for {username}"}

@app.get('/movies/{id}')
def movie(id):
    return {f"This is the movie of {id}"}

@app.get('/movies')
def movies():
    return {'movie list': ['Movie 1', 'Movie 2']}
