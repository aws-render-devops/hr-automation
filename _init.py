import asyncio

if __name__ == "__main__":
    from app.services.tasks import initial_task

    try:
        asyncio.run(initial_task())
    except Exception as e:
        print(e)
