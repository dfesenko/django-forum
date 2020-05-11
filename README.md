# django-forum
Forum application developed with Django, PostgreSQL, Celery, and Redis

*Note: the app is still in the development stage*


## About
The website was developed for the learning purposes. The focus was on the backend side.
The app consists from several functionality groups: 
* User registration:
  * Sign up
  * Login / Logout
  * Email validation
  * Password reset
  * Password change
* User profiles
* Messages between users
* Forum with categories, topics, and posts
* User feeds


## Technology stack
The following major technologies were used:
* Django 3.0.3
* PostgreSQL 11.7
* Celery 4.4.2
* Redis 3.0.6
* Boostrap 4.4.1
* jQuery 3.4.1


## How to run
1. Clone the repo: `git clone https://github.com/dfesenko/django-forum.git`. 
Go inside the `django-forum` folder: `cd django-forum`.
2. Create virtual environment: `python -m venv venv`.
3. Activate virtual environment: `source venv/bin/activate`.
4. Install dependencies into virtual environment: `pip install -r requirements.txt`.
5. Install Redis:  `sudo apt update`, `sudo apt install redis-server`.
6. Run Redis  (in a separate Terminal window): `redis-server`.
7. Go inside the `forum` directory: `cd forum/`.
8. Set the credentials for your email that you want to use for sending emails for users.
This should be done in the `forum/settings.py` file (find variables that 
start from the word `EMAIL`).
9. Create PostgreSQL database.
10. Set credentials for the database in the `forum/settings.py` file 
(inside the `DATABASES` parameter.
11. Run Celery workers (in a separate Terminal window, but with activated virtual 
environment and from the `django-forum/forum` directory): 
`celery worker -A forum --loglevel=debug --concurrency=4`.
12. Run Django server: `python manage.py runserver`.
13. The application should be available in browser: `localhost:8000`.


## Application structure in more details
todo
