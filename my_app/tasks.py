import logging
from datetime import timedelta, datetime

from django.utils import timezone
from django.db.models import Q

from celery.task.schedules import crontab
from celery.decorators import periodic_task, task
from celery.utils.log import get_task_logger
from notifications.models import Notification
from notifications.signals import notify
from notifications.views import AllNotificationsList, UnreadNotificationsList

from .recommender import (data_preprocess, predict_itembased,
                          predict_userbased, get_predictions_itembased,
                          get_predictions_userbased,
                          store_prediction_into_table, store_user_based_prediction_into_table,
                          handle_new_users, insert_update_jaccard_similarity_table)
from .models import Booking, Ratings

from accounts.models import Member

celery_logger = get_task_logger(__name__)
logger = logging.getLogger(__name__)


@periodic_task(
    run_every=(crontab()),
    # run_every=(timedelta(minutes=1)),
    name="check_return_date",
    ignore_result=True
)
def check_return_date():
    bookings = Booking.objects.filter(deleted_at__isnull=True, status=2)
    for booking in bookings:
        if datetime.now().date() > booking.return_date:
            booking.fine += float(5)
            booking.save()
            notify.send(booking, recipient=booking.user, action_object=booking.book,
                        verb="You have been fined for exceeding the return date of book " +
                        str(booking.book),
                        description="Fined")


@periodic_task(
    # run_every=(crontab(minute=0, hour=0)),
    run_every=(timedelta(minutes=1)),
    name="calculate_jaccard_similarity"
)
def task_calculate_jaccard_similarity():
    users = Member.objects.filter(deleted_at__isnull=True)
    for user in users:
        status = insert_update_jaccard_similarity_table(user)
        if status:
            logger.info(
                "Succesfully inserted or updated jaccard similarity table")
        else:
            logger.error("Something went wrong")


@periodic_task(
    # run_every=(crontab(minute=0, hour=1)),
    run_every=(timedelta(minutes=1)),
    name="calculate_item_based_similarity"
)
def calculate_item_based_similarity():
    metric = 'cosine'
    users = Member.objects.filter(
        deleted_at__isnull=True).exclude(ratings_user=None)

    for user in users:
        interest_categories = list(user.category_interests.all().filter(
            deleted_at__isnull=True).values_list('id', flat=True))
        if len(interest_categories) > 0:
            if Ratings.objects.filter(deleted_at__isnull=True, user=user).count() > 0:
                books, ratings_matrix = data_preprocess(user, interest_categories)
                prediction = get_predictions_itembased(
                    ratings_matrix=ratings_matrix, user_id=user.id, metric=metric)
                logger.info(prediction)
                status = store_prediction_into_table(
                    books=books, prediction_tuple_list=prediction, user_id=user.id)
                if not status:
                    logger.error("Couldn't store prediction into table")
            else:
                handle_new_users(user, 'itembased')

    other_users = Member.objects.filter(
        deleted_at__isnull=True).exclude(~Q(ratings_user=None))
    for user in other_users:
        handle_new_users(user, 'itembased')


@periodic_task(
    # run_every=(crontab(minute=0, hour=2)),
    run_every=(timedelta(minutes=1)),
    name="calculate_user_based_similarity"
)
def calculate_user_based_similarity():
    metric = 'cosine'
    users = Member.objects.filter(
        deleted_at__isnull=True).exclude(ratings_user=None)
    
    for user in users:
        interest_categories = list(user.category_interests.all().filter(
            deleted_at__isnull=True).values_list('id', flat=True))
        if len(interest_categories) > 0:
            if Ratings.objects.filter(deleted_at__isnull=True, user=user).count() > 0:
                books, ratings_matrix = data_preprocess(user, interest_categories)
                prediction = get_predictions_userbased(
                    ratings_matrix=ratings_matrix, user_id=user.id, metric=metric)
                status = store_user_based_prediction_into_table(
                    books=books, prediction_tuple_list=prediction, user_id=user.id)
                if not status:
                    logger.error("Couldn;t store user based prediction into table")
            else:
                handle_new_users(user, 'userbased')

    # other_users = Member.objects.filter(
    #     deleted_at__isnull=True).exclude(~Q(ratings_user=None))
    # for user in other_users:
    #     handle_new_users(user, 'userbased')


@periodic_task(
    # run_every=(crontab()),
    run_every=(timedelta(minutes=1)),
    name="notify_users_one"
)
def notify_users_one():
    members = Member.objects.filter(deleted_at__isnull=True)
    for member in members:
        bookings = Booking.objects.filter(
            deleted_at__isnull=True, status=2, user=member)
        for booking in bookings:
            if (booking.return_date - datetime.now().date()) <= timedelta(3):
                notify.send(booking, recipient=member, action_object=booking.book, verb="Return Date for " + str(booking.book) + " is only 3 days away.",
                            description="return date near")


@periodic_task(
    # run_every=(crontab()),
    run_every=(timedelta(minutes=1)),
    name="notify_users_two"
)
def notify_users_two():
    members = Member.objects.filter(deleted_at__isnull=True)
    for member in members:
        bookings = Booking.objects.filter(
            deleted_at__isnull=True, status=1, user=member)
        for booking in bookings:
            if (datetime.now().date() - booking.created_at.date()) >= timedelta(5):
                booking.deleted_at = timezone.now()
                notify.send(booking, recipient=member, action_object=booking.book, verb="Your booking for book "
                            + str(booking.book) + " has been cancelled.", description="booking cancelled")


@periodic_task(
    # run_every=(crontab()),
    run_every=(timedelta(minutes=1)),
    name="check_user_category_interests"
)
def check_user_category_interests():
    users = Member.objects.filter(deleted_at__isnull=True)
    user_interests = user.category_interests.all()
    for user in users:
        for category in user_interests:
            latest_booking = Booking.objects.filter(
                deleted_at__isnull=True, book__category=category).order_by("-created_at").first()
            if (datetime.date.now() - latest_booking.created_at.date()) > timedelta(days=30):
                user.category_interests.remove(category)
                user.semi_possible_interests.add(category)
