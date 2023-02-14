from hyx.bulkhead import bulkhead

# app is an instance of framework like Flask or FastAPI

@app.post("/projects/")
@bulkhead(max_concurrency=10, max_capacity=100)
def create_new_project():
    """
    Create a new project
    """
    ...
