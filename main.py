from aiohttp import web


import aiocron
from settings import settings
from datetime import datetime


_pool = None


async def start_background_tasks(app):
    # Schedule the cron task to run every 30 minutes
    # app['my_cron_job'] = aiocron.crontab('*/30 * * * *', func=<function_name>, start=True)
    ...


async def cleanup_background_tasks(app):
    # Stop the cron job when the application is shutting down
    app["my_cron_job"].stop()


async def handle(request):
    name = request.match_info.get("name", "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def health(request):
    return web.Response(text="OK")


app = web.Application()
app.add_routes([web.get("/", handle), web.get("/{name}", handle)])
app.add_routes([web.get("/-/health", health)])

app.on_startup.append(start_background_tasks)
app.on_shutdown.append(cleanup_background_tasks)


if __name__ == "__main__":
    web.run_app(app)
