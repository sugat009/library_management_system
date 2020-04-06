# prediction = predict_itembased(4, '104761', ratings_matrix)

# # This function utilizes above functions to recommend items for item/user based approach and cosine/correlation.
# # Recommendations are made if the predicted rating for an item is >= to 6,and the items have not been rated already
# def recommendItem(user_id, ratings, metric=metric):
#     if (user_id not in ratings.index.values) or type(user_id) is not int:
#         print("User id should be a valid integer from this list :\n\n {} ".format(
#             re.sub('[\[\]]', '', np.array_str(ratings_matrix.index.values))))
#     else:
#         ids = ['Item-based (correlation)', 'Item-based (cosine)',
#                'User-based (correlation)', 'User-based (cosine)']
#
#         # select = widgets.Dropdown(
#         #     options=ids, value=ids[0], description='Select approach', width='1000px')
#
#         def on_change(change):
#             # clear_output(wait=True)
#             prediction = []
#             if change['type'] == 'change' and change['name'] == 'value':
#                 if (select.value == 'Item-based (correlation)') | (select.value == 'User-based (correlation)'):
#                     metric = 'correlation'
#                 else:
#                     metric = 'cosine'
#                 # with suppress_stdout():
#                 if (select.value == 'Item-based (correlation)') | (select.value == 'Item-based (cosine)'):
#                     for i in range(ratings.shape[1]):
#                         # not rated already
#                         if (ratings[str(ratings.columns[i])][user_id] != 0):
#                             prediction.append(predict_itembased(
#                                 user_id, str(ratings.columns[i]), ratings, metric))
#                         else:
#                             # for already rated items
#                             prediction.append(-1)
#                 else:
#                     for i in range(ratings.shape[1]):
#                         # not rated already
#                         if (ratings[str(ratings.columns[i])][user_id] != 0):
#                             prediction.append(predict_userbased(
#                                 user_id, str(ratings.columns[i]), ratings, metric))
#                         else:
#                             # for already rated items
#                             prediction.append(-1)
#                 prediction = pd.Series(prediction)
#                 prediction = prediction.sort_values(ascending=False)
#                 recommended = prediction[:10]
#                 print("As per {0} approach....Following books are recommended...").format(
#                     select.value)
#                 for i in range(len(recommended)):
#                     print("{0}. {1}").format(
#                         i + 1, books.bookTitle[recommended.index[i]].encode('utf-8'))
#                 # select.observe(on_change)
#                 # display(select)
#                 return prediction
#
#
# # checking for incorrect entries
# # print(recommendItem(999999, ratings_matrix))
# #
# # print(recommendItem(4385, ratings_matrix))
# #
# # print(recommendItem(4385, ratings_matrix))
#
# # print(predict_itembased(4385, '0001056107', ratings=ratings_matrix, metric="cosine", k = 10))
#
# user_id = 4
# metric = 'cosine'
