#!/bin/sh

echo "initialise database..."
python init_db.py

nc -z localhost 5000 &> flask.log
IS_APP_RUNNING=$?

if [ $IS_APP_RUNNING -eq 1 ]
then
  echo "start Flask app on port 5000..."
  flask --app=flaskr run &> flask.log &
  FLASK_PID=$!
else
  echo "Flask is already running on port 5000"
fi

echo "run tests...\n"
nosetests --processes=30

if [ $IS_APP_RUNNING -eq 1 ]
then
  echo "kill Flask app..."
  kill $FLASK_PID
fi
