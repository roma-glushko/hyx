from hyx.bulkhead import bulkhead

# app is an instance of framework like Flask or FastAPI
limiter = bulkhead(max_concurrency=10, max_capacity=100)


@app.post("/projects/")
def create_new_project():
    """
    Create a new project
    """
    async with limiter:
        ...
