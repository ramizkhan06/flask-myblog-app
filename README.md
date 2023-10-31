# MyBlog

## Step 1: Start Virtual Environment
            * .\virt\Scripts\activate

## Step 2: Install flask
            * pip install flask

## Step 3: Install all the requirements
            * pip install -r requirements.txt

## Step 4: Create Database
            * python create_db.py

## Step 5: Set up the Environment
            For Windows Terminal
            * set FLASK_APP=app.py
            * set FLASK_ENV=development
            * set FLASK_DEBUG=1

            For Git Bash Terminal
            * export FLASK_APP=app.py
            * export FLASK_ENV=development
            * export FLASK_DEBUG=1

## Step 6 : Start the application
             * flask run

### This will start application on port 5000
            * http://localhost:5000 or http://127.0.0.1:5000
