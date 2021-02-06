import csv
from flask import Flask, request
import implicit
import numpy as np
from scipy.sparse import csr_matrix


app = Flask(__name__)


DB_FILENAME = 'db.csv'


def load_item_user_matix():
    with open(DB_FILENAME) as f:
        csv_data = list(csv.reader(f))
    users = np.array([int(user) for user, _ in csv_data])
    trips = np.array([int(trip) for _, trip in csv_data])
    row = np.array(trips, dtype=int)
    col = np.array(users, dtype=int)
    data = np.array([1 for _ in csv_data], dtype=float)
    matrix = csr_matrix((data, (row, col)), shape=(
        max(row) + 1,
        max(col) + 1,
    ), dtype=int)
    return matrix


def append_data(row):
    with open(DB_FILENAME, 'a') as f:
        c = csv.writer(f)
        c.writerow(row)


def build_model(item_user_matrix):
    model = implicit.als.AlternatingLeastSquares(factors=50)
    model.fit(item_user_matrix)
    return model


def predict(model, user, user_item_matrix):
    return model.recommend(user, user_item_matrix)
    

@app.route('/<user>/submit/', methods=['POST'])
def user_input(user):
    trip = request.get_json().get('trip', None)
    print(trip)
    if trip:
        append_data([user, trip])
        return 'Added'
    return 'Submit using trip'


@app.route('/<user>/')
def recommendations(user):
    item_user_matrix  = load_item_user_matix()
    model = build_model(item_user_matrix)
    user_item_matrix = item_user_matrix.T.tocsr()
    prediction = predict(model, int(user), user_item_matrix)
    return repr(prediction)

