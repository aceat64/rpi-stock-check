from flask import Flask
from flask import render_template
from lxml import html
import requests
import re
import yaml
import os, sys
import pyqrcode
import png

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html', products=check_stock())

def check_stock():
    with open(os.path.join(sys.path[0], 'config.yaml'), "r", encoding="utf8") as yaml_file:
        config = yaml.safe_load(yaml_file)

    jar = requests.cookies.RequestsCookieJar()
    jar.set('storeSelected', str(config['store']), domain='microcenter.com', path='/')

    product_data = []

    for product in config['products']:
        product_id = re.search(".*/product/([0-9]*)/", product).group(1)
        page = requests.get(product, cookies=jar)
        tree = html.fromstring(page.content)
        qr_code = pyqrcode.create(product)
        product_data.append({
            'url': product,
            # 'qr_code': base64.b64encode(s.getvalue()).decode("ascii"),
            'qr_code': qr_code.png_as_base64_str(scale=6),
            'name': tree.xpath('//span[@class="ProductLink_'+product_id+'"]/text()')[0],
            'price': tree.xpath('//span[@class="ProductLink_'+product_id+'"]')[0].attrib['data-price'],
            'stock': tree.xpath('//span[@class="inventoryCnt"]/text()')[0],
            'image': tree.xpath('//img[@class="productImageZoom"]')[0].attrib['src'],
            'mfg_logo': tree.xpath('//img[@id="mfgLogo"]')[0].attrib['src'],
        })

    return product_data
