import logging
import json
from itertools import chain

from django.db.models import Q

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from accounts.models import Member
from my_app.models import (JaccardSimilarity, Book,
                           Ratings, ItemBasedSimilar, UserBasedSimilar)

logger = logging.getLogger(__name__)


def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection / union)


def calculate_jaccard_similarity(user):
    other_users = Member.objects.filter(
        deleted_at__isnull=True).exclude(id=user.id)
    user_interests = list(user.category_interests.all().values('title'))
    user_interests = [x['title'] for x in user_interests]
    user_interests.append(user.profession.title)
    if len(user_interests) == 0:
        return []
    similarity_list = []
    for other_user in other_users:
        other_user_interests = list(
            other_user.category_interests.all().values('title'))
        other_user_interests = [x['title'] for x in other_user_interests]
        other_user_interests.append(other_user.profession.title)
        similarity = jaccard_similarity(user_interests, other_user_interests)
        similarity_list.append(
            {"user_id": other_user.id, "similarity": similarity})
        similarity_list = sorted(
            similarity_list, key=lambda x: x['similarity'], reverse=True)
        similarity_list = similarity_list[:30]
    return similarity_list


def insert_update_jaccard_similarity_table(user):
    try:
        similarity_list = calculate_jaccard_similarity(user)
        if len(similarity_list) > 0:
            jacc, _ = JaccardSimilarity.objects.get_or_create(user=user)
            jacc.top_thirty_users = json.dumps(similarity_list)
            jacc.save()
            return True
        else:
            logger.error("No similarity returned for user {}".format(user))
            return False

    except Exception as e:
        logger.error(e, exc_info=True)
        return False


# Loading data
# books = pd.read_csv('BX-CSV-Dump/BX-Books.csv', sep=';',
#                     error_bad_lines=False, encoding="latin-1")
# books.columns = ['ISBN', 'bookTitle', 'bookAuthor', 'yearOfPublication',
#                  'publisher', 'imageUrlS', 'imageUrlM', 'imageUrlL']
#
# users = pd.read_csv('BX-CSV-Dump/BX-Users.csv', sep=';',
#                     error_bad_lines=False, encoding="latin-1")
# users.columns = ['userID', 'Location', 'Age']
#
# ratings = pd.read_csv('BX-CSV-Dump/BX-Book-Ratings.csv', sep=';',
#                       error_bad_lines=False, encoding="latin-1")
# ratings.columns = ['userID', 'ISBN', 'bookRating']
#
# # checking shapes of the datasets
# print(books.shape)
# print(users.shape)
# print(ratings.shape)
#
# # Exploring books dataset
# print(books.head())

def data_preprocess(user, interest_categories):
    """
        function that calculates all the necessary stuff for recommendation
        :args
        :: interest_categories=list of categories of interest of user
        :: method=item based similarity or user based similarity
        :returns
        :: returns book dataframe and ratings matrix
    """
    logger.info("=======================================")
    logger.info("Beginning of data preprocessing")
    books = Book.objects.filter(
        deleted_at__isnull=True, category_id__in=interest_categories)
    books = pd.DataFrame(
        list(books.values('id', 'title', 'author', 'published_date', 'isbn', )))
    logger.info("Shape of books:")
    logger.info(books.shape)

    jaccard_object = JaccardSimilarity.objects.get(user=user)
    top_thirty_users = json.loads(jaccard_object.top_thirty_users)
    top_thirty_users_ids = [x["user_id"] for x in top_thirty_users]
    logger.info("Top thirty users: ")
    logger.info(top_thirty_users_ids)

    users = Member.objects.filter(
        deleted_at__isnull=True, id__in=top_thirty_users_ids)
    users = pd.DataFrame(list(users.values('id', 'username')))
    logger.info("Shape of users: ")
    logger.info(users.shape)

    ratings = Ratings.objects.filter(deleted_at__isnull=True).filter(
        Q(user_id__in=top_thirty_users_ids) | Q(user_id=user.id))
    ratings = pd.DataFrame(
        list(ratings.values('id', 'user__id', 'book__isbn', 'ratings')))
    logger.info("Shape of ratings")
    logger.info(ratings.shape)

    logger.info("Printing user ids to make sure that they are unique")
    logger.info("User ids: ")
    logger.info(users.id.values)
    # it can be seen that these are unique

    # ratings dataset will have n_users*n_books entries if every user rated every item, this shows that the dataset is very sparse
    n_users = users.shape[0]
    n_books = books.shape[0]
    logger.info("No of user * no. of books: ")
    logger.info(str(n_users * n_books))

    # ratings dataset should have books only which exist in our books dataset, unless new books are added to books dataset
    ratings_new = ratings[ratings.book__isbn.isin(books.isbn)]

    logger.info("Ratings shape(unfiltered): ")
    logger.info(ratings.shape)
    logger.info("Ratings shape(filtered): ")
    logger.info(ratings_new.shape)
    # it can be seen that many rows having book ISBN not part of books dataset got dropped off

    # ratings dataset should have ratings from users which exist in users dataset, unless new users are added to users dataset
    ratings = ratings[ratings.user__id.isin(users.id)]

    logger.info("Ratings shape(unfiltered): ")
    logger.info(ratings.shape)
    logger.info("Ratings shape(filtered): ")
    logger.info(ratings_new.shape)
    # no new users added, hence we will go with above dataset
    # we will be using the new dataset ratings_new

    logger.info("number of users: " + str(n_users))
    logger.info("number of books: " + str(n_books))

    # Sparsity of dataset in %
    sparsity = 1.0 - len(ratings_new) / float(n_users * n_books)
    logger.info('The sparsity level of Book Crossing dataset is ' +
                str(sparsity * 100) + ' %')

    # Note: Rating 0 indicates that the book hasnt been rated rather than puttings null
    # which causes trouble in recommendation

    # Hence segragating implicit and explict ratings datasets
    ratings_explicit = ratings_new[ratings_new.ratings != 0]
    ratings_implicit = ratings_new[ratings_new.ratings == 0]

    # checking shapes
    logger.info("Ratings shape(whole): ")
    logger.info(ratings_new.shape)
    logger.info("Ratings shape(explicit): ")
    logger.info(ratings_explicit.shape)
    logger.info("Ratings shape(implicit): ")
    logger.info(ratings_implicit.shape)

    # Similarly segregating users who have given explicit ratings from 1-10 and those whose implicit behavior was tracked
    users_exp_ratings = users[users.id.isin(ratings_explicit.user__id)]
    users_imp_ratings = users[users.id.isin(ratings_implicit.user__id)]

    # checking shapes
    logger.info("Shape of user df: ")
    logger.info(users.shape)
    logger.info("Shape of user explicit ratings: ")
    logger.info(users_exp_ratings.shape)
    logger.info("Shape of user implicit ratings: ")
    logger.info(users_imp_ratings.shape)

    # To cope up with computing power I have and to reduce the dataset size, I am considering users who have rated atleast 100 books
    # and books which have atleast 100 ratings
    # counts1 = ratings_explicit['userID'].value_counts()
    # ratings_explicit = ratings_explicit[ratings_explicit['userID'].isin(
    #     counts1[counts1 >= 100].index)]
    # counts = ratings_explicit['bookRating'].value_counts()
    # ratings_explicit = ratings_explicit[ratings_explicit['bookRating'].isin(
    #     counts[counts >= 100].index)]

    logger.info("Rating matrix explicit: ")
    logger.info(ratings_explicit)
    # new_df = pd.DataFrame({'id': [ratings_explicit.iloc[0]['id']], 'user__id': [user.id], 'book__isbn': [ratings_explicit.iloc[0]['book__isbn']], 'ratings': None})
    # ratings_explicit=ratings_explicit.append(new_df, ignore_index=True, sort=True)

    # Generating ratings matrix from explicit ratings table
    ratings_matrix = ratings_explicit.pivot(
        index='user__id', columns='book__isbn', values='ratings')
    user_id = ratings_matrix.index
    isbn = ratings_matrix.columns
    logger.info("shape of ratings matrix after pivoting: ")
    logger.info(ratings_matrix.shape)
    logger.info("head of ratings matrix: ")
    logger.info(ratings_matrix.head())

    # Notice that most of the values are NaN (undefined) implying absence of ratings
    # considering only those users who gave explicit ratings
    n_users = ratings_matrix.shape[0]
    n_books = ratings_matrix.shape[1]
    logger.info("Check number of users and books from rating matrix: ")
    logger.info("No of users: " + str(n_users))
    logger.info("No of books: " + str(n_books))

    # since NaNs cannot be handled by training algorithms, replacing these by 0, which indicates absence of ratings
    # setting data type
    ratings_matrix.fillna(0, inplace=True)
    ratings_matrix = ratings_matrix.astype(np.int32)

    # checking first few rows
    logger.info("Checking ratings matrix after filling na with 0")
    logger.info(ratings_matrix)

    # rechecking the sparsity
    sparsity = 1.0 - len(ratings_explicit) / \
        float(users_exp_ratings.shape[0] * n_books)
    logger.info('The sparsity level of Book Crossing dataset is ' +
                str(sparsity * 100) + ' %')
    logger.info("Returning from data preprocessing-------")
    return books, ratings_matrix


# This function finds k similar users given the user_id and ratings matrix
# These similarities are same as obtained via using pairwise_distances
def findksimilarusers(user_id, ratings, metric, k):
    similarities = []
    indices = []
    model_knn = NearestNeighbors(metric=metric, algorithm='brute')
    model_knn.fit(ratings)
    loc = ratings.index.get_loc(user_id)
    distances, indices = model_knn.kneighbors(
        ratings.iloc[loc, :].values.reshape(1, -1), n_neighbors=k + 1)
    similarities = 1 - distances.flatten()
    return similarities, indices


# This function predicts rating for specified user-item combination based on user-based approach
def predict_userbased(user_id, item_id, ratings, metric, k):
    prediction = 0
    user_loc = ratings.index.get_loc(user_id)
    item_loc = ratings.columns.get_loc(item_id)

    # similar users based on cosine similarity
    similarities, indices = findksimilarusers(user_id, ratings, metric, k)

    # to adjust for zero based indexing
    mean_rating = ratings.iloc[user_loc, :].mean()
    sum_wt = np.sum(similarities) - 1
    product = 1
    wtd_sum = 0

    for i in range(0, len(indices.flatten())):
        if indices.flatten()[i] == user_loc:
            continue
        else:
            ratings_diff = ratings.iloc[indices.flatten(
            )[i], item_loc] - np.mean(ratings.iloc[indices.flatten()[i], :])
            product = ratings_diff * (similarities[i])
            wtd_sum = wtd_sum + product

    # in case of very sparse datasets, using correlation metric for collaborative based approach
    # may give negative ratings
    # which are handled here as below
    if prediction <= 0:
        prediction = 1
    elif prediction > 5:
        prediction = 5

    prediction = int(round(mean_rating + (wtd_sum / sum_wt)))
    logger.info(
        '\nPredicted rating for user {0} -> item {1}: {2}'.format(user_id, item_id, prediction))

    return prediction, item_id


# This function finds k similar items given the item_id and ratings matrix
def findksimilaritems(item_id, ratings, metric, k):
    similarities = []
    indices = []
    ratings = ratings.T
    loc = ratings.index.get_loc(item_id)
    model_knn = NearestNeighbors(metric=metric, algorithm='brute')
    model_knn.fit(ratings)

    distances, indices = model_knn.kneighbors(
        ratings.iloc[loc, :].values.reshape(1, -1), n_neighbors=k + 1)
    similarities = 1 - distances.flatten()
    return similarities, indices


# This function predicts the rating for specified user-item combination based on item-based approach
def predict_itembased(user_id, item_id, ratings, metric, k):
    prediction = wtd_sum = 0
    user_loc = ratings.index.get_loc(user_id)
    item_loc = ratings.columns.get_loc(item_id)

    # similar users based on correlation coefficients
    similarities, indices = findksimilaritems(item_id, ratings, metric, k)

    sum_wt = np.sum(similarities) - 1
    product = 1

    for i in range(0, len(indices.flatten())):
        if indices.flatten()[i] == item_loc:
            continue
        else:
            product = ratings.iloc[user_loc,
                                   indices.flatten()[i]] * (similarities[i])
            wtd_sum = wtd_sum + product
    prediction = int(round(wtd_sum / sum_wt))

    # in case of very sparse datasets, using correlation metric for collaborative based
    # approach may give negative ratings
    # which are handled here as below //code has been validated without the code snippet below,
    # below snippet is to avoid negative
    # predictions which might arise in case of very sparse datasets when using correlation metric
    if prediction <= 0:
        prediction = 1
    elif prediction > 5:
        prediction = 5

    logger.info(
        '\nPredicted rating for user {0} -> item {1}: {2}'.format(user_id, item_id, prediction))

    return prediction, item_id


def get_predictions_itembased(ratings_matrix, user_id, metric):
    prediction = []

    logger.info(ratings_matrix.columns.values)
    if len(ratings_matrix.columns.values) < 10:
        k = len(ratings_matrix.columns.values) - 1
    else:
        k = 10

    for i in range(ratings_matrix.shape[1]):
        # not rated already
        if (ratings_matrix[str(ratings_matrix.columns[i])][user_id] == 0):
            prediction.append(predict_itembased(
                user_id, str(ratings_matrix.columns[i]), ratings_matrix, metric, k))
        else:
            # for already rated items
            prediction.append((-1, str(ratings_matrix.columns[i])))
    logger.info(prediction)
    return prediction


def get_predictions_userbased(ratings_matrix, user_id, metric):
    prediction = []

    if ratings_matrix.shape[0] > 10:
        k = 10
    else:
        k = ratings_matrix.shape[0] - 1

    for i in range(ratings_matrix.shape[1]):
        # not rated already
        if (ratings_matrix[str(ratings_matrix.columns[i])][user_id] == 0):
            prediction.append(predict_userbased(
                user_id, str(ratings_matrix.columns[i]), ratings_matrix, metric, k))
        else:
            # for already rated items
            prediction.append((-1, str(ratings_matrix.columns[i])))
    logger.info(prediction)
    return prediction


def store_prediction_into_table(books, prediction_tuple_list, user_id):
    sorted_prediction_list = sorted(
        prediction_tuple_list, key=lambda x: x[0], reverse=True)
    recommended = sorted_prediction_list[:10]

    print("As per {0} approach....Following books are recommended...".format(
        "itembased(cosine)"))

    try:
        user = Member.objects.get(pk=user_id)
        item_based_similar_books = user.item_based_similar_member.all().filter(
            deleted_at__isnull=True).order_by('-prediction')
        for i in recommended:
            print("{0}. {1}".format(
                '*', books.loc[books['isbn'] == i[1]]['title'].values[0]))
            # Item based similar books are retrieved from db inside loop because if a recommended book
            # is deleted then, the list needs to be refreshed
            item_based_similar_books = user.item_based_similar_member.all().filter(
                deleted_at__isnull=True).order_by('-prediction')
            book = Book.objects.get(isbn=i[1])
            if item_based_similar_books.count() >= 10 and i[0] >= 0:
                for item in item_based_similar_books:
                    if i[0] >= item.prediction:
                        least_prediction_item = ItemBasedSimilar.objects.filter(
                            user=user).order_by('prediction').first()
                        # Just a sanity check because sometimes it throws error
                        if least_prediction_item:
                            least_prediction_item.remove()
                        obj, _ = ItemBasedSimilar.objects.get_or_create(
                            user=user, book=book, prediction=i[0])
                    break
            else:
                if i[0] >= 0:
                    obj, _ = ItemBasedSimilar.objects.get_or_create(
                        user=user, book=book, prediction=i[0])
        return True
    except Exception as e:
        logger.error(e, exc_info=True)
        return False


def store_user_based_prediction_into_table(books, prediction_tuple_list, user_id):
    sorted_prediction_list = sorted(
        prediction_tuple_list, key=lambda x: x[0], reverse=True)
    recommended = sorted_prediction_list[:10]

    print("As per {0} approach....Following books are recommended...".format(
        "userbased(cosine)"))

    try:
        user = Member.objects.get(pk=user_id)
        for i in recommended:
            book = Book.objects.get(isbn=i[1])
            print("{0}. {1}".format(
                '*', books.loc[books['isbn'] == i[1]]['title'].values[0]))
            # The recommended books are retrieved inside the loop because if any recommened item is deleted then,
            # the list needs to be refreshed again
            user_based_similar_books = user.user_based_similar_member.all().filter(
                deleted_at__isnull=True).order_by('-prediction')
            if user_based_similar_books.count() >= 10 and i[0] >= 0:
                for item in user_based_similar_books:
                    if i[0] >= item.prediction:
                        least_prediction_item = UserBasedSimilar.objects.filter(
                            user=user).order_by('prediction').first()
                        # Sanity check
                        if least_prediction_item:
                            least_prediction_item.remove()
                        obj, _ = UserBasedSimilar.objects.get_or_create(
                            user=user, book=book, prediction=i[0])
                    break
            else:
                if i[0] >= 0:
                    obj, _ = UserBasedSimilar.objects.get_or_create(
                        user=user, book=book, prediction=i[0])
        return True
    except Exception as e:
        logger.error(e, exc_info=True)
        return False


def handle_new_users(user, method):
    jaccard_object = JaccardSimilarity.objects.get(user=user)
    if jaccard_object.top_thirty_users:
        top_thirty_users = json.loads(jaccard_object.top_thirty_users)
        top_thirty_users_ids = [x["user_id"] for x in top_thirty_users]

        book_list = list()
        for id in top_thirty_users_ids[:10]:
            other_member = Member.objects.get(id=id)
            item_based_similar_books = other_member.item_based_similar_member.all(
            ).order_by('-book__avg_rating')
            if not item_based_similar_books.count() == 0:
                for book in item_based_similar_books:
                    if book in book_list:
                        break
                    book_list.append(book.book)
        book_list = list(set(book_list))
        if len(book_list) > 0:
            if method == 'itembased':
                for book in book_list[:10]:
                    obj, created = ItemBasedSimilar.objects.get_or_create(
                        user=user, book=book)
            else:
                for book in book_list[:10]:
                    obj, created = UserBasedSimilar.objects.get_or_create(
                        user=user, book=book)
        else:
            new_books = Book.objects.filter(
                deleted_at__isnull=True).order_by('-created_at')[:10]
            if method == 'itembased':
                for book in new_books:
                    obj, created = ItemBasedSimilar.objects.get_or_create(
                        user=user, book=book)
            else:
                for book in new_books:
                    obj, created = UserBasedSimilar.objects.get_or_create(
                        user=user, book=book)
    logger.info("No jaccard similarity list found for %s", user)
