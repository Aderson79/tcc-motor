PY ?= .venv/bin/python

setup:            ## ambiente Python + dependências
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -e .
data:             ## baixa e confere o O*NET 31.0
	cd data/raw && curl -sSO https://www.onetcenter.org/dl_files/database/db_31_0_csv.zip \
	 && sha256sum -c db_31_0_csv.zip.sha256 && unzip -q -o db_31_0_csv.zip
db:               ## PostgreSQL + pgvector
	docker compose up -d
catalog:
	$(PY) -m tcc.catalog
index:            ## embeddings do catálogo no pgvector (busca exata)
	$(PY) -m tcc.embed
test:
	$(PY) -m pytest -q
check:            ## confere chaves e modelos
	$(PY) -m tcc.check
dev:              ## pipeline completo no conjunto de desenvolvimento (30 perfis)
	$(PY) -m tcc.sampling dev
	$(PY) -m tcc.profiles dev
	$(PY) -m tcc.gold dev
	$(PY) -m tcc.run dev
	$(PY) -m tcc.report dev
eval:             ## SÓ depois da tag lock-v1
	git rev-parse --verify -q lock-v1 >/dev/null || (echo "Crie a tag lock-v1 antes da avaliação." && exit 1)
	$(PY) -m tcc.sampling eval
	$(PY) -m tcc.profiles eval
	$(PY) -m tcc.gold eval
	$(PY) -m tcc.run eval
	$(PY) -m tcc.report eval
.PHONY: setup data db catalog index test check dev eval
