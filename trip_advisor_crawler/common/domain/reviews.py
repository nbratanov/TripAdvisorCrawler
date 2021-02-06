from marshmallow_dataclass import dataclass
from typing import List
from .review import Review


@dataclass
class Reviews:
    reviews: List[Review]

    def __init__(self):
        self.reviews = list()

    def add(self, review):
        self.reviews.append(review)

    def print(self):
        for review in self.reviews:
            print(review.id + ": " + review.text + "\n")

    def stringify(self):
        string_view = ""
        for review in self.reviews:
            if review.text is not None:
                string_view += review.text + "\n"
        return string_view


def object_decoder(obj):
    if '__type__' in obj and obj['__type__'] == 'User':
        return Review(obj['id'], obj['text'])
    return obj
