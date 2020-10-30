# Web scrapping

Scrapping scripts for specific websites.

## Usage

> Note: Replace `SCRAPPING_PROJECT` by the desired subdirectory of this repository.

```bash
cd SCRAPPING_PROJECT
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Read the docstring at the top of each python script to know how to run each scrapper.
# ...

deactivate
```

## Testing and further development

Download [Selenium IDE for Firefox](https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/).

Open Selenium IDE plugin in Firefox browser.
If the project has a file with `.side` extension, you can load it into Selenium IDE.