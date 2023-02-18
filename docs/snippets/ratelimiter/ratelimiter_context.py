from hyx.ratelimit import tokenbucket

# app is an instance of framework like Flask or FastAPI
limiter = tokenbucket(max_executions=20, per_time_secs=60)  # permitting 20 req/min


@app.post("/projects/")  # type: ignore[F821]
def create_new_project():
    """
    Create a new project
    """
    async with limiter:
        ...
