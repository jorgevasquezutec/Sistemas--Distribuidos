curl:
	curl http://localhost:8881/v1/list?title=trigun

test:
	docker compose run k6 run /scripts/ewoks.js

k6s:
	docker compose run k6 run /scripts/ewoks-simple.js 

copydb:
	cp -r ./cron/anime_data.db ./api/anime_data.db

donw:
	docker compose down

up:
	docker compose up -d

clean: donw copydb up
