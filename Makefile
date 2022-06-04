ifneq (,$(wildcard .env))
    include .env
    export
endif


dev-run-frontend:
	cd frontend && npm start

dev-run-backend:
	uvicorn uc_semantic_layer.backend.server:app --reload

integration-test-backend:
	cd uc-semantic-layer && pytest tests