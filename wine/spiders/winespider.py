import scrapy
from wine.items import WineItem


class WinespiderSpider(scrapy.Spider):
    name = "winespider"
    allowed_domains = ["www.vivino.com"]
    explore_base_url = "https://www.vivino.com/api/explore/explore"
    parameters = {
        "country_code": "KR",
        "currency_code": "KRW",
        "grape_filter": "varietal",
        "min_rating": 1,
        "price_range_max": 500000,
        "price_range_min": 0,
        "wine_type_ids[]": [1, 2],
        "language": "en",
        "page": 1,
    }
    headers = {
        "Accept": "*/*",
    }
    start_count = 0
    end_count = 0

    def start_requests(self):
        explore_url = create_url(self.explore_base_url, self.parameters)
        yield scrapy.Request(explore_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        data = response.json()['explore_vintage']

        wine_datas = data['matches']
        for wine_data in wine_datas:
            wine = WineItem()
            self.start_count += 1
            if self.start_count > data['records_matched']:
                break

            year = wine_data['vintage']['year']
            try:
                wine['name'] = wine_data['vintage']['wine']['name'] + \
                    ' ' + str(year)
            except:
                wine['name'] = None

            try:
                wine['winery'] = wine_data['vintage']['wine']['winery']['name']
            except:
                wine['winery'] = None

            try:
                rating = wine_data['vintage']['statistics']['ratings_average']
                wine['rating'] = rating if rating != 0 else wine_data['vintage']['statistics']['wine_ratings_average']
            except:
                wine['rating'] = None

            try:
                region_url = "https://www.vivino.com/api/regions/" + \
                    str(wine_data['vintage']['wine']['region']['id'])
                parameters = {
                    "language": "en",
                }
                region_url = create_url(region_url, parameters)

                price_url = "https://www.vivino.com/api/prices"
                parameters = {
                    "vintage_ids[]": wine_data['vintage']['id'],
                    "language": "en",
                }
                price_url = create_url(price_url, parameters)

                flavor_url = f"https://www.vivino.com/api/wines/{wine_data['vintage']['wine']['id']}/tastes"
                parameters = {
                    "language": "en",
                }
                flavor_url = create_url(flavor_url, parameters)

                reviews_url = f"https://www.vivino.com/api/wines/{wine_data['vintage']['wine']['id']}/reviews"
                parameters = {
                    "per_page": 2,
                    "year": year,
                    "language": "en",
                }
                reviews_url = create_url(reviews_url, parameters)

                meta = {
                    "wine": wine,
                    'urls': [reviews_url, flavor_url, price_url],
                }
                yield scrapy.Request(region_url, headers=self.headers, callback=self.parse_region, meta=meta, dont_filter=True)
            except:
                self.end_count += 1

    def parse_region(self, response):
        wine = response.meta['wine']
        price_url = response.meta['urls'].pop()
        data = response.json()

        try:
            wine['region'] = [data['region']['name']]
            for parent_region in data['region']['parent_regions']:
                wine['region'].append(parent_region['name'])
            wine['region'].append(data['region']['country']['name'])
        except:
            wine['region'] = None

        yield scrapy.Request(price_url, headers=self.headers, callback=self.parse_price, meta=response.meta, dont_filter=True)

    def parse_price(self, response):
        wine = response.meta['wine']
        flavor_url = response.meta['urls'].pop()

        try:
            data = response.json()
            wine['price'] = list(data['prices']['vintages'].values())[0]['median']['amount']
        except:
            wine['price'] = None

        yield scrapy.Request(flavor_url, headers=self.headers, callback=self.parse_flavor, meta=response.meta, dont_filter=True)

    def parse_flavor(self, response):
        wine = response.meta['wine']
        reviews_url = response.meta['urls'].pop()
        try:
            data = response.json()['tastes']

            try:
                wine['taste'] = {
                    "acidity": data['structure']['acidity'],
                    "fizzness": data['structure']['fizziness'],
                    "intensity": data['structure']['intensity'],
                    "sweetness": data['structure']['sweetness'],
                    "tannin": data['structure']['tannin'],
                }
            except:
                wine['taste'] = None

            try:
                wine['flavor'] = []
                for flavor_data in data['flavor'][:3]:
                    wine['flavor'].append({
                        "group": flavor_data['group'],
                        "keyword": [keyword_data['name'] for keyword_data in flavor_data['primary_keywords'][:3]]
                    })
            except:
                wine['flavor'] = None
        except:
            wine['taste'] = None
            wine['flavor'] = None

        yield scrapy.Request(reviews_url, headers=self.headers, callback=self.parse_reviews, meta=response.meta, dont_filter=True)

    def parse_reviews(self, response):
        wine = response.meta['wine']

        try:
            data = response.json()
            wine['reviews'] = []
            for review in data['reviews']:
                wine['reviews'].append({
                    "note": review['note'],
                    "rating": review['rating']
                })
        except:
            wine['reviews'] = None

        yield wine

        self.end_count += 1
        print(f'saved {self.end_count} : {wine["name"]}')

        if self.end_count == 25 * self.parameters['page']:
            self.parameters['page'] += 1
            explore_url = create_url(self.explore_base_url, self.parameters)
            yield scrapy.Request(explore_url, headers=self.headers, callback=self.parse)


def create_url(base_url, parameters):
    url = base_url + '?'
    parameter_strings = []
    for key, values in parameters.items():
        if isinstance(values, list):
            for value in values:
                parameter_strings.append(f'{key}={value}')
        else:
            parameter_strings.append(f'{key}={values}')
    url += '&'.join(parameter_strings)
    return url
