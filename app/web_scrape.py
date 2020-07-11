import requests
from bs4 import BeautifulSoup
from lxml.html import fromstring
from itertools import cycle


class Scraper:
    proxies = None
    proxy_pool = None
    proxy_test_url = 'https://httpbin.org/ip'

    def __init__(self, target_url, **kwargs):
        self.target_url = target_url
        self.data = None
        self.get_proxies()

    def get_proxies(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                # Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
        self.proxies = proxies
        self.proxy_pool = cycle(proxies)

    def test_proxies(self):
        print(f'Available Proxies: {self.proxies}')
        for i in range(10):
            proxy = next(self.proxy_pool)
            print("Request #%d" % i)
            try:
                response = requests.get(self.proxy_test_url, proxies={"http": f'http://{proxy}', "https": f'https://{proxy}'})
                print(response.json())
            except:
                print("Skipping. Connnection error")

    def scrape(self, **options):
        if not self.data:
            proxy = next(self.proxy_pool)
            try:
                self.data = BeautifulSoup(
                    requests.get(self.target_url, proxies={"https": f'https://{proxy}'}).text,
                    'lxml'
                )

                return self.process_data(**options)

            except Exception as e:
                raise e

    def process_data(self, **options):
        method = options.get('method')
        if method:
            methods = {
                'find_all_tags': self.find_all_tags,
                'find_first_tag': self.find_first_tag,
            }
            method_to_call = methods.get(method)
            if method_to_call:
                return method_to_call(**options)
            else:
                raise KeyError("No method found matching that name")
        else:
            raise KeyError("Specify method for **options")

    def find_all_tags(self, **options):
        result = []
        for class_ in options.get('classes'):
            result.append(self.data.find_all(options.get('tag'), {'class': class_}).prettify())
        return result

    def find_first_tag(self, **options):
        return self.data.find(options.get('tag'), {'class': options.get('classes')}).prettify()


test_scraper = Scraper('https://thewizardslair.us/docs.html')
print(test_scraper.scrape(method='find_first_tag', tag='div', classes='card-body'))
