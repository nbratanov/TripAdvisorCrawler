import re

import scrapy
from scrapy import Request

from common.domain.review import Review
from common.domain.reviews import Reviews
from textblob import TextBlob

from google_trans_new import google_translator

import time

BASE_URL = "https://www.tripadvisor.com"
translator = google_translator()
start_time = time.time()


class TripAdvisorSpider(scrapy.Spider):
    name = "tripadvisor"

    start_urls = [
        "https://www.tripadvisor.com/Hotel_Review-d"
    ]

    def start_requests(self):
        # base_url = "https://www.tripadvisor.com/Hotel_Review-d"
        # base_url = "https://www.tripadvisor.com/Hotel_Review-g293974-d1674691-Reviews-or460-Hotel_Amira_Istanbul-Istanbul.html"
        # base_url = "https://www.tripadvisor.com/Hotel_Review-g186338-d8147345-Reviews-InterContinental_London_The_O2-London_England.html"
        # base_url = "https://www.tripadvisor.com/Hotel_Review-g318870-d551018-Reviews-Kempinski_Hotel_Grand_Arena-Bansko_Blagoevgrad_Province.html"
        # base_url = "https://www.tripadvisor.com/Hotel_Review-g187514-d4719800-Reviews-Only_YOU_Boutique_Hotel_Madrid-Madrid.html"
        base_url = "https://www.tripadvisor.com/Hotel_Review-g294452-d530275-Reviews-Grand_Hotel_Sofia-Sofia_Sofia_Region.html"
        initial_hotel_id = 1674691
        last_hotel_id = 1674692
        for hotel_id in range(initial_hotel_id, last_hotel_id):
            yield Request(base_url + str(hotel_id), self.parse)

    def parse(self, response, **kwargs):
        page = response.url.split('/')[-1]  # not used?
        filename = "./../../../data/hotel-reviews.csv"

        reviews = self.parse_reviews(response)
        hotel_name = self.get_hotel_name(response).lower()
        single_filename = "./../../../data/" + hotel_name + '.txt'

        with open(filename, 'a', encoding="utf-8-sig") as f:
            with open(single_filename, 'a', encoding="utf-8-sig") as single_file:
                string_reviews = reviews.stringify()
                string_reviews = autocorrect(string_reviews)

                if reviews.is_translation_needed is True:
                    string_reviews = translator.translate(string_reviews)
                f.write(string_reviews)
                single_file.write(string_reviews)

        next_page_link = self.get_next_page_link(response)
        if next_page_link is not None:
            yield Request(BASE_URL + next_page_link, callback=self.parse)

        estimated_time = time.time() - start_time
        print(f"Time to complete parsing all reviews for hotel {hotel_name} is : {estimated_time}")

    def get_hotel_name(self, response):
        return response.xpath('//h1[@id="HEADING"]//text()').get()

    def get_next_page_link(self, response):
        next_page_button = response.xpath('//a[@class="ui_button nav next primary "]')
        if next_page_button:
            return next_page_button.attrib['href']
        return None

    def parse_reviews(self, response):

        reviews = crawl_reviews_in_json(response)

        try:
            review_ids = re.findall('[[,]{"id":([0-9]+?),"url"', reviews)
            texts = re.findall(',"text":"(.+?)","username"', reviews)
            city_locations = re.findall('"parentGeoId":.+?"geo":"(.+?)",', reviews)
            hotel_publish_dates = re.findall('"publishedDate":"(.+?)"', reviews)
            ratings = re.findall(',"rating":(.+?),', reviews)
            languages = re.findall('"language":"(.+?)",', reviews)
            original_languages = re.findall('"original":"(.+?)",', reviews)
            translation_types = re.findall('"translationType":"(.+?)",', reviews)
            # reviewer_hometowns = re.findall('"location":(.+?),', reviews)
            trip_infos = re.findall('"tripInfo":(.+?),"additionalRatings"', reviews)
            reviewer_stay_dates = get_reviewer_stay_dates(trip_infos)
            trip_types = get_reviewer_trip_types(trip_infos)
            like_counts = re.findall('"likeCount":(.+?),', reviews)

        except AttributeError:
            raise AttributeError("Some of the fields were not specified.")

        reviews = Reviews()
        for i in range(len(review_ids)):
            review = Review(review_ids[i], texts[i], city_locations[0], hotel_publish_dates[i], ratings[i],
                            languages[i], original_languages[i], translation_types[i],
                            reviewer_stay_dates[i], trip_types[i], like_counts[i])
            reviews.add(review)

        return reviews


def crawl_reviews_in_json(response):
    review_id = response.xpath('//div[@class="oETBfkHU"]').attrib['data-reviewid']
    first_review = f'//script[contains(., "{review_id}")]'
    prefix = '{ "reviews": '
    suffix = "}"

    reviews = prefix + response.xpath(first_review).re_first(r'"reviews":(.*)},"reviewAggregations":') + suffix
    reviews = reviews.replace('null', '"null"')
    reviews = re.sub(r'"mgmtResponse":.+?},"text"', '"text"', reviews)
    return reviews


def get_reviewer_stay_dates(trip_infos):
    reviewer_stay_dates = []
    for trip_info in trip_infos:
        stay_date = re.findall('"stayDate":"(.+?)",', trip_info)
        if stay_date:
            reviewer_stay_dates.append(stay_date[0])
        else:
            reviewer_stay_dates.append("null")

    return reviewer_stay_dates


def get_reviewer_trip_types(trip_infos):
    trip_types = []
    for trip_info in trip_infos:
        trip_type = re.findall('"tripType":"(.+?)"', trip_info)
        if trip_type:
            trip_types.append(trip_type[0])
        else:
            trip_types.append("null")

    return trip_types


def autocorrect(reviews):
    text_blob = TextBlob(reviews)
    reviews = str(text_blob.correct())
    return reviews
