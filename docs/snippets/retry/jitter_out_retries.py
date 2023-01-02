import asyncio

from hyx.retry import jitters


async def run_worker(delay_between_tasks_secs: float = 10) -> None:
    """
    The Worker's Logic
    """
    while True:
        # pull tasks from the database and process it
        await asyncio.sleep(jitters.full(delay_between_tasks_secs))


async def run_worker_pool(workers: int = 5, schedule_delay_secs: float = 5) -> None:
    """
    Worker Manager
    Schedules a set of workers with jittering their startup times
    """
    tasks: list[asyncio.Task] = []

    for _ in range(workers):
        tasks.append(asyncio.create_task(run_worker()))
        await asyncio.sleep(jitters.full(schedule_delay_secs))

    await asyncio.gather(*tasks)


asyncio.run(run_worker_pool())
