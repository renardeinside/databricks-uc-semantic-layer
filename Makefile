ifneq (,$(wildcard .env))
    include .env
    export
endif


dev-run-frontend:
	cd frontend && npm start

dev-run-backend:
	uvicorn uc_semantic_layer.backend.server:app --reload --log-config=uc-semantic-layer/conf/server_log.yml

integration-test-backend:
	cd uc-semantic-layer && pytest tests

launch:
	docker-compose up --build
