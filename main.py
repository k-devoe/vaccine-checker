# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime

import constants

import json

from flask import Flask, render_template, request

# [START gae_python38_datastore_store_and_fetch_times]
# [START gae_python3_datastore_store_and_fetch_times]
from google.cloud import datastore

datastore_client = datastore.Client('cs361-vchecker')

# [END gae_python3_datastore_store_and_fetch_times]
# [END gae_python38_datastore_store_and_fetch_times]
app = Flask(__name__)


# [START gae_python38_datastore_store_and_fetch_times]
# [START gae_python3_datastore_store_and_fetch_times]
def store_time(dt):
    entity = datastore.Entity(key=datastore_client.key('visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)


def fetch_times(limit):
    query = datastore_client.query(kind='visit')
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times
# [END gae_python3_datastore_store_and_fetch_times]
# [END gae_python38_datastore_store_and_fetch_times]


# [START gae_python38_datastore_render_times]
# [START gae_python3_datastore_render_times]
@app.route('/')
def root():
    # Store the current access time in Datastore.
    store_time(datetime.datetime.now(tz=datetime.timezone.utc))

    # Fetch the most recent 10 access times from Datastore.
    times = fetch_times(10)

    return render_template(
        'index.html', times=times)
# [END gae_python3_datastore_render_times]
# [END gae_python38_datastore_render_times]

@app.route('/users', methods=['GET'])
def users_get_post():

    if request.method == 'GET':
        query = datastore_client.query(kind='User')
        results = list(query.fetch())
        print("GET called, data: ", json.dumps(results))
        return render_template("displayInfo.html", results=results)

    else:
        return 'Method not recognized'

@app.route('/userID', methods=['GET'])
def userID_get_post():

    if request.method == 'GET':
        user_id = int(request.args.get("user_id"))
        user_key = datastore_client.key('User', user_id)

        fullName = datastore_client.get(user_key)

        if fullName is not None:
            fullName = fullName["fullName"]

        query = datastore_client.query(kind='User_Vaccine')
        query.add_filter("UserID", "=", user_id)
        records = list(query.fetch())

        vaccinations = []

        for record in records:

            # Get the date in readable format
            date = record["Date"].date()
            date = str(date.month) + '/' + str(date.day) + '/' + str(date.year)

            # Get the vaccine organization name
            vaccineID = int(record["VaccineID"])
            vaccine_key = datastore_client.key('Vaccine', vaccineID)
            vaccine = datastore_client.get(vaccine_key)

            vaccinations.append({"Date": date, "Vaccine_Type": vaccine["Organization"]})


        print(vaccinations)
    
        return render_template("displayInfo.html", fullName=fullName, vaccinations=vaccinations)

    else:
        return 'Method not recognized'

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
