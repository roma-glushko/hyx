from fastapi import FastAPI

from hyx.ratelimit import tokenbucket

# app is an instance of framework like Flask or FastAPI
app = FastAPI()


@app.post("/projects/")
@tokenbucket(max_executions=20, per_time_secs=60)  # permitting 20 req/min
def create_new_project():
    """
    Create a new project
    """
    ...
