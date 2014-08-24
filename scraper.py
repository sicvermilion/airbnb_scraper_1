import codecs
import json
import random
import sys
import time

import lxml.html
import requests
import scraperwiki


class AirbnbScraper:
    def __init__(self, debug=True):
        self.cookies = {}
        self.debug = debug

    def listing_url(self, price_min,price_max,offset):
        return ('https://m.airbnb.com/api/-/v1/listings/search?location=bali&price_min=%s&price_max=%s&number_of_guests=1&offset=%s&guests=1&items_per_page=20'
                % (price_min,price_max,offset))

    def get(self, url, referer='', min_sleep=30, max_add=120, xhr=False):
        if self.debug:
            print url

        time.sleep(random.randint(0, max_add) + min_sleep)

        headers = {'User-agent': 'Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9',
                   'referer': referer}
        if xhr:
            headers['x-requested-with'] = 'XMLHttpRequest'

        r = requests.get(url, headers=headers, cookies=self.cookies)
        self.cookies = r.cookies

        return r

    def crawl(self):
        price_min = 0
        while price_min < 401:
            if price_min == 400:
                price_max = 9999
            else:
                price_max = price_min + 24

            offset = 0
            count = 999
            while offset < count:
                r = self.get(self.listing_url(price_min,price_max,offset), referer='https://m.airbnb.com/s/bali')
                list_arr = []

                try:
                    js = json.loads(r.content)
                    count = js['listings_count']

                    if len(js['listings']) == 0:
                        break
                    else:
                        for listing1 in js['listings']:
                            listing = listing1['listing']
                            list_off = {
                                "id": listing['id'],
                                "city": listing['city'],
                                "picture_url": listing['picture_url'],
                                "user_id": listing['user_id'],
                                "price": listing['price'],
                                "price_native": listing['price_native'],
                                "lat": listing['lat'],
                                "lng": listing['lng'],
                                "name": listing['name'],
                                "address": listing['address'],
                                "property_type": listing['property_type'],
                                "room_type_category": listing['room_type_category'],
                                "smart_location": listing['smart_location'],
                                "reviews_count": listing['reviews_count'],
                                "user_name": listing['user']['user']['first_name'],
                                "bedsroom": listing['bedsroom'],
                                "url": "https://www.airbnb.com/rooms/" + str(listing['id']),
                                "date_added": time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            list_arr.append(list_off)
                            
                    offset += 20
                    scraperwiki.sqlite.save(["id"],list_arr)
                    if self.debug:
                        print "new offset", offset

                except ValueError as e:
                    print >> sys.stderr, 'received ValueError:', e
                    print >> sys.stderr, 'error: could not parse response'
                    sys.exit(1)

            price_min += 25

if __name__ == "__main__":
    ab = AirbnbScraper()
    ab.crawl()
