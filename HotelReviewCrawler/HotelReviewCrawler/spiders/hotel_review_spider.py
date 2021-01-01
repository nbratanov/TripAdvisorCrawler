import json

import scrapy
from scrapy import Request
from . import reviews_model
from google_trans_new import google_translator

BASE_URL = "https://www.tripadvisor.com"

class HotelReviewSpider(scrapy.Spider):
    name = "tripadvisor"

    # start_urls = [
    #     "https://www.tripadvisor.com/Hotel_Review-g488299-d202929-Reviews-Caesar_Augustus_Hotel"
    #     "-Anacapri_Island_of_Capri_Province_of_Naples_Campania.html",
    #     "https://www.tripadvisor.com/Hotel_Review-g187791-d205044-Reviews-Hotel_Artemide-Rome_Lazio.html"
    # ]
    start_urls = [
        "https://www.tripadvisor.com/Hotel_Review-d"
    ]

    def start_requests(self):
        base_url = "https://www.tripadvisor.com/Hotel_Review-d"
        initial_hotel_id = 1674691
        last_hotel_id = 1674692
        for hotel_id in range(initial_hotel_id, last_hotel_id):
            yield scrapy.Request(base_url + str(hotel_id), self.parse)


    def parse(self, response, **kwargs):
        page = response.url.split('/')[-1]
        filename = "hotel-reviews.csv"
        translator = google_translator()

        review_schema = self.parse_reviews(response)

        with open(filename, 'a', encoding="utf-8") as f:
            for review in review_schema['reviews']:
                f.write(translator.translate(review['text']) + "\n")

        next_page_link = response.xpath('//a[@class="ui_button nav next primary "]').attrib['href']
        if next_page_link is not None:
            yield Request(BASE_URL + next_page_link, callback=self.parse)

    def parse_reviews(self, response):
        """
        old version
        reviews = response.xpath('//q[@class="IRsGHoPm"]//span').getall()
        reviews = list(map(lambda r: r.replace('<span>', '').replace('</span>', ''), reviews))

        """

        review_id = response.xpath('//div[@class="oETBfkHU"]').attrib['data-reviewid']
        print(review_id)

        first_review = f'//script[contains(., "{review_id}")]'
        print(type(first_review))
        regex = r'"reviews":(.*)},"reviewAggregations":'
        print("\n" + first_review)
        prefix = '{ "reviews": '
        suffix = "}"

        reviews = prefix + response.xpath(first_review).re_first(r'"reviews":(.*)},"reviewAggregations":') + suffix

        # review_schema = reviews_model.Reviews.Schema().load(json.loads(reviews))
        review_schema = json.loads(reviews)

        return review_schema
