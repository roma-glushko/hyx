from hyx.ratelimit import tokenbucket


# app is an instance of framework like Flask or FastAPI

@app.post("/projects/")
@tokenbucket(max_execs=20, time_period_secs=60, bucket_size=20)
def create_new_project():
    """
    Create a new project
    """
    ...
