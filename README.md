# Web scrapping

Scrapping scripts for specific websites.

## Usage

```bash
git clone https://github.com/TeMU-BSC/web-scrapping.git
cd web-scrapping
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ISCIII's Portal FIS: <https://portalfis.isciii.es/es/Paginas/inicio.aspx>
cd portalfis
pytest -s test_portalfis.py

# Agència Catalana de Notícies: <https://www.acn.cat/>
sudo apt install xvfb
cd acn
xvfb-run pytest -s test_acn.py

deactivate
```

## Testing and further development

Download [Selenium IDE for Firefox](https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/).

Open Selenium IDE plugin in Firefox and load the desired *.side file from this repo.