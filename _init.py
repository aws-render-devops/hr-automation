import asyncio

if __name__ == "__main__":
    from app.services.tasks import initial_task

    asyncio.run(initial_task())
