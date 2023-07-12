import asyncio
from app import app
from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
    app.run(host=app.config.get("HOST", "0.0.0.0"), port=app.config.get("PORT", 5000))
    from app.services.tasks import initial_task

    asyncio.run(initial_task())
