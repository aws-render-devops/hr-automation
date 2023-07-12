build:
	docker build -t hrscript .

run:
	docker run -p 8000:8000 --env-file=.env -d --name hr hrscript

init:
	docker exec -it hr python _init.py

start:
	docker exec -it  hr gunicorn main:app --bind 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker
