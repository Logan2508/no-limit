.PHONY: install run share clean

install:
	uv venv --python 3.11 && uv pip install -r requirements.txt

run:
	uv run --with streamlit streamlit run app.py

# Affiche l'URL à ouvrir sur le téléphone (même Wi-Fi)
ip:
	@hostname -I | awk '{print "http://"$$1":8501"}'
