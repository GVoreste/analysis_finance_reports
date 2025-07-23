from pathlib import Path
import shutil
from lxml import etree
from freeports_analysis.main import get_targets

out_dir = Path(__file__).parent / "output/"
data_dir = Path(__file__).parent / "data/"

try:
    shutil.rmtree(out_dir)
except FileNotFoundError:
    pass
out_dir.mkdir()

url_example_formats = {
    "AMUNDI": "https://www.amundi.com/dl/doc/annual-report/LU1883342377/ENG/ITA/20240630?inline",
    "AMUNDI2": "https://www.amundi.it/dl/doc/annual-report/IT0005491680/ITA/ITA/20241230",
    "EURIZON": "https://www.eurizonam.hr/UserDocsImages//LUX/SAR_HR_en_LU1341630033_YES_2023-06-30.pdf",
    "ANIMA": "https://www.animasgr.it/d/EN/downloads/Documents/Anima%20Funds%20plc%2031%20December%202023%20Financials.pdf",
    "FIDEURAM": "https://www.fideuramassetmanagement.ie/upload/File/pdf/Policy_FAMI/WILLERFUNDS/DOC/FIDEURAM_WILLERFUNDS_Semi-Annual%2028.02.2023.pdf",
    "EURIZON_OLD": "https://www.fundsquare.net/download/dl?siteId=FSQ&v=8R3GVJJluMrT1vWzWKb2+2y6bAdM4PonP+u32Js1vq7RbUzoOUpWj9+xriJFNnBxAFS14hLTev85fvgpgbDFQEJJfw8puksMVK/oWiK71T9YU0KjYpAH3l1VIKUAV4rPjwPaPQ7DDY4yhqF+o4MlHw==",
    "MEDIOLANUM": "https://www.mediolanumgestionefondi.it/static-assets/documenti/file/it/2025/05/02//Relazione_di_gestione_annuale_al_%2030122024.pdf",
    "ARCA": "https://docs.arcafondi.it/docs/getdoc/documenti/RENDICONTO_ANNUALE_IT0005419103.pdf",
}

single_page_tests = {
    "ANIMA": [544],
    "AMUNDI": [43],
    "ASTERIA": [78],
    "AMUNDI2": [558],
    "FIDEURAM": [51, 33],
    "EURIZON_OLD": [97],
    "MEDIOLANUM": [55],
    "EURIZON_IT": [29],
    "ARCA": [20],
    "EURIZON": [254],
    "ASTERIA_2023": [21, 26],
    "MEDIOLANUM_ES24": [39, 40],
}

xml_parser = etree.XMLParser(recover=True)
targets = get_targets()

conf = {
    "VERBOSITY": 2,
    "N_WORKERS": 1,
    "BATCH": None,
    "OUT_CSV": None,
    "SAVE_PDF": False,
    "URL": None,
    "PDF": None,
    "FORMAT": None,
    "CONFIG_FILE": None,
    "PREFIX_OUT": None,
    "SEPARATE_OUT_FILES": None,
}
