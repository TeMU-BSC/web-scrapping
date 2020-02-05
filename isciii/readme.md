# Web scrapping of ISCIII webpage

<https://portalfis.isciii.es/es/Paginas/inicio.aspx>

## Requisites

`python >= 3.7`

## Usage

```bash
git clone https://github.com/TeMU-BSC/web-scrapping.git
cd web-scrapping/isciii/
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
pytest test_portalfis.py
deactivate
```
