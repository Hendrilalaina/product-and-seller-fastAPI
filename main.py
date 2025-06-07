from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return "Hello world"

@app.get('/movies/{id}')
def movie(id):
    return {f"This is the movie of {id}"}

@app.get('/movies')
def movies():
    return {'movie list': ['Movie 1', 'Movie 2']}
