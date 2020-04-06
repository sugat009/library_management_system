import json
import logging
import os
import sys
import random
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from PIL import Image
from dateutil.parser import parse
from django.core.files import File
from django.utils.crypto import get_random_string
from django.db.models import Sum

from accounts.models import Member
from .models import Book, Ratings, Category, Publisher, Profession

first_name_choices = ["James", "Michael", "Keith", "Jason", "Michelle", "Harvey",
                      "Rocco", "Sugat", "Erik", "Russell", "Kevin", "Lebron",
                      "Dwyane", "David", "Abban", "Adaue", "ROBERT", "WILLIAM",
                      "CHARLES", "CHRISTOPHER", "THOMAS", "EDWARD", "BRIAN", "TIMOTHY",
                      "JOSE", "STEPHEN", "GREGORY", ]
last_name_choices = ["Bajracharya", "Bond", "Specter", "Litt", "Blake", "Williams",
                     "Peterson", "Goldman", "Brady", "Beckham", "Hernandez", "Smith",
                     "Johnson", "Brown", "Miller", "Wilson", "Anderson", "Torres",
                     "Martinez", "Hayes", "Turner", ]

category_choices = ["Fiction", "Action", "Adventure", "Novel", "Horror", "Psychological",
                    "Thriller", "Cliffhanger", "Fantasy", ]

profession_choices = ["Doctor", "Engineer", "Dentist", "Athlete", "Philantropist", "Actor",
                      "Politician", "Social Worker", "Writer", "Teacher", ]

logger = logging.getLogger(__name__)

BASE_DIR = os.getcwd()


def add_category():
    for i in category_choices:
        cats, _ = Category.objects.get_or_create(title=i)
    logger.info("categories created")


def add_publishers():
    for i in range(1, 30):
        obj = Publisher.objects.create(
            title=get_random_string(length=4) + " "
            + get_random_string(length=5)
        )
    logger.info("publishers added")


def add_books():
    publisher_number = Publisher.objects.all().count()
    for i in range(100):
        try:
            book = Book.objects.create(
                title=get_random_string(length=12),
                author=get_random_string(length=6),
                category=Category.objects.get(pk=random.randint(1, 9)),
                avg_rating=round(random.uniform(1.0, 10.0), 2),
                isbn=get_random_string(length=13),
                publisher=Publisher.objects.get(
                    pk=random.randint(1, publisher_number)),
                published_date=datetime.now().date(),
                available=True,
                number_in_stock=random.randint(1, 100)
            )
        except Exception as e:
            logger.error(e)
            pass
    logger.info("book adding finished")


def add_members():
    for i in range(20):
        obj = Member.objects.create(
            first_name=random.choice(first_name_choices),
            last_name=random.choice(last_name_choices),
            username=get_random_string(length=12),
            email=get_random_string(length=8) + "@" +
            get_random_string(length=5) + ".com",
            address=get_random_string(length=12),
            phone_number=random.randint(100, 10000000000000)
        )
        for i in range(5):
            try:
                obj.category_interests.add(
                    Category.objects.get(pk=random.randint(1, 9)))
            except Exception as e:
                logger.error(e)
                pass
    logger.info("members added")


def add_ratings():
    n_users = Member.objects.filter(deleted_at__isnull=True).count()
    n_books = Book.objects.filter(deleted_at__isnull=True).count()
    print("Adding ratings: ")
    print(n_users * n_books)

    for i in range(2, n_users + 2):
        for j in range(1, n_books + 1):
            random_int = random.randint(1, 100)
            if random_int % 2 == 0:
                continue
            else:
                try:
                    obj = Ratings.objects.get_or_create(
                        user=Member.objects.get(pk=i),
                        book=Book.objects.get(pk=j),
                        ratings=random.randint(1, 5)
                    )
                except Exception as e:
                    logger.error(e)
                    logger.error("Error for member id: {}".format(i))
                    logger.error("Error for book id: {}".format(j))
                    print(e)
    logger.info("ratings added")


def call_all():
    add_category()
    add_publishers()
    add_books()
    add_members()
    add_ratings()


def load_categories():
    df = pd.read_csv("dump/BX-Books.csv", sep=';',
                     error_bad_lines=False, encoding="latin-1")
    for idx, row in df.iterrows():
        print("Requesting google API")
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes?q=isbn:" + str(row['ISBN']))
        print("Got response")
        print("Response received: {}".format(response.status_code))
        if response.status_code == 200:
            try:
                print("Got category as {}".format(json.loads(response.content)[
                    'items'][0]['volumeInfo']['categories'][0]))
                category = json.loads(response.content)[
                    'items'][0]['volumeInfo']['categories'][0]
                category = category.split("-")[0].split(",")[0].split(" ")[0]
                obj = Category.objects.get_or_create(title=category)
            except Exception as e:
                logger.error(
                    "Error for row {0} ------ book {1}".format(idx, row['Book-Title']))
                logger.error(json.loads(response.content))
                logger.error(e, exc_info=True)
        elif response.status_code == 403:
            break


def load_publishers():
    df = pd.read_csv("dump/BX-Books.csv", sep=';',
                     error_bad_lines=False, encoding="latin-1")
    for idx, row in df.iterrows():
        if Publisher.objects.all().count() >= 50:
            break
        else:
            publisher = Publisher.objects.get_or_create(title=row['Publisher'])


def load_books():
    df = pd.read_csv("dump/BX-Books.csv", sep=';',
                     error_bad_lines=False, encoding="latin-1")
    category_count = Category.objects.all().count()
    publisher_count = Publisher.objects.all().count()
    for idx, row in df.iterrows():
        if Book.objects.all().count() >= 1000:
            break
        else:
            try:
                filename = str(row['Image-URL-L'])
                filepath = Path(BASE_DIR + "/dump/images/" + filename)
                if not filepath.is_file():
                    response = urllib.request.urlretrieve(
                        row['Image-URL-L'], BASE_DIR + "/dump/images/" + str(row['Image-URL-L'].split("/")[-1]))
                book, created = Book.objects.get_or_create(title=row['Book-Title'], isbn=row['ISBN'],
                                                           author=row['Book-Author'],
                                                           published_date=parse(str(
                                                               row['Year-Of-Publication'])),
                                                           available=True,
                                                           number_in_stock=random.randint(
                                                               5, 100),
                                                           category=Category.objects.get(
                                                               pk=random.randint(1, category_count)),
                                                           publisher_id=random.randint(
                                                               1, publisher_count))

                img = Image.open(BASE_DIR + "/dump/images/"
                                 + row['Image-URL-L'].split("/")[-1])
                if img.format == "JPEG" or img.format == "PNG" or img.format == "JPG":
                    book.image.save(row['Image-URL-L'].split("/")[-1], File(
                        open(BASE_DIR + "/dump/images/" + row['Image-URL-L'].split("/")[-1], 'rb')))
            except Exception as e:
                logger.error("Error for row {}".format(idx))
                logger.error(e, exc_info=True)


def create_professions():
    for profession in profession_choices:
        obj, _ = Profession.objects.get_or_create(title=profession)


def load_members():
    df = pd.read_csv("dump/BX-Users.csv", sep=';',
                     error_bad_lines=False, encoding="latin-1")
    category_count = Category.objects.all().count()
    profession_count = Profession.objects.all().count()

    for idx, row in df.iterrows():
        if Member.objects.all().count() >= 100:
            break
        else:
            try:
                first_name = random.choice(first_name_choices)
                last_name = random.choice(last_name_choices)
                username = first_name.lower() + last_name.lower() + str(random.randint(1, 999))
                member = Member.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    phone_number=random.randint(1000000000, 9999999999),
                    email=username + "@mymail.com",
                    address=row['Location'],
                    profession=Profession.objects.get(pk=random.randint(1, profession_count))
                )
                for i in range(1, random.randint(2, 7)):
                    try:
                        member.category_interests.add(
                            Category.objects.get(pk=random.randint(1, category_count)))
                    except Exception as e:
                        logger.error(e)
                        pass
            except Exception as e:
                logger.error(e, exc_info=True)


def change_average_ratings():
    books = Book.objects.all()
    for book in books:
        book_ratings = Ratings.objects.filter(
            book=book).aggregate(Sum('ratings'))
        book_count = Ratings.objects.filter(book=book).count()
        avg_ratings = book_ratings / book_count
        book.ratings = avg_ratings
        book.save()


def fill_database():
    load_categories()
    add_category()
    load_publishers()
    load_books()
    create_professions()
    load_members()
    add_ratings()
