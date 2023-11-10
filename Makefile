test:
	curl http://localhost:8881/v1/list?title=trigun


# jmeter:
# 	cd script && sh ./run_jmeter.sh
k6:
	docker compose run k6 run /scripts/ewoks.js
