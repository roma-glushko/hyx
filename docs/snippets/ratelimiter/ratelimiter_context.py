from hyx.ratelimit import tokenbucket

# app is an instance of framework like Flask or FastAPI
limiter = tokenbucket(max_execs=20, time_period_secs=60, bucket_size=20)


@app.post("/projects/")
def create_new_project():
    """
    Create a new project
    """
    async with limiter:
        ...
