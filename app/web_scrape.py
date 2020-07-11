# from bs4 import BeautifulSoup
# import requests
#
#
# class Scraper:
#     def __init__(self, url):
#         self.url = url
#         self.scraped_data = None
#
#     def __str__(self):
#         return str(self.scraped_data.prettify())
#
#     def data_is_current(self):
#         return self.scraped_data == True
#
#     def scrape(self):
#         self.scraped_data = BeautifulSoup(requests.get(self.url).text, 'lxml')
#
#     def find_tags(self, tag, classes):
#         if not self.scraped_data:
#             self.scrape()
#         return self.scraped_data.find(tag, class_=classes)
#
#     def find_all_tags(self, tag, classes):
#         if not self.scraped_data:
#             self.scrape()
#         return self.scraped_data.find_all(tag, class_=classes)
#
#     def sort_data_from_tags(self, tag, classes):
#         dict_data = {}
#         to_sort = self.find_all_tags(tag, classes)
#
#         for each in to_sort:
#             try:
#                 dict_data[each.find('div', class_='card-header').h4.strong.text] = each.find('div',
#                                                                                              class_='card-body').text
#             except Exception as e:
#                 pass
#
#         return dict_data
#
#
# test_scrape = Scraper('https://thewizardslair.us/docs.html')
#
# print(test_scrape.sort_data_from_tags('div', 'card'))

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
            self.data = BeautifulSoup(requests.get(self.target_url).text, 'lxml')
        return self.process_data(**options)

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
            result.append(self.data.find_all(options.get('tag'), {'class': class_}))
        return result

    def find_first_tag(self, **options):
        return self.data.find(options.get('tag'), {'class': options.get('classes')})


test = Scraper('https://thewizardslair.us/docs.html')
# print(test.scrape(method='find_first_tag', tag='div', classes='card-body'))
# test.test_proxies()
