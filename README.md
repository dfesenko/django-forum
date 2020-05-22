# django-forum
Forum application developed with Django, PostgreSQL, Celery, and Redis

*Note: the app is still in the development stage*


## About
The website was developed for learning purposes. The focus was on the backend side.
The app consists of several functionality groups: 
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
2. Create a virtual environment: `python -m venv venv`.
3. Activate virtual environment: `source venv/bin/activate`.
4. Install dependencies into the virtual environment: `pip install -r requirements.txt`.
5. Install Redis:  `sudo apt update`, `sudo apt install redis-server`.
6. Run Redis  (in a separate Terminal window): `redis-server`.
7. Set the credentials for your email that you want to use for sending emails for users.
This should be done in the `forum/settings.py` file (find variables that 
start from the word `EMAIL`).
8. Create a PostgreSQL database.
9. Set credentials for the database in the `forum/settings.py` file 
(inside the `DATABASES` parameter.
10. Perform migrations: `python manage.py makemigrations`, `python manage.py migrate`.
11. Run Celery workers (in a separate Terminal window, but with activated virtual 
environment and from the `django-forum/` directory): 
`celery worker -A forum --loglevel=debug --concurrency=4`.
13. Run Django server: `python manage.py runserver`.
14. The application should be available in the browser: `localhost:8000`.


## Application structure in more details
- **Index page** has information about 5 latest updated topics, 5 new topics, 
and 5 most popular topics. If the user is a superuser, the index page also provides a list
with all registered users (for convenience during development).  

- **Forum page** has a button for new topic creation and the dropdown menu for selecting the category.
If no category is selected, all existing topics are displayed ordered by the last updated date. 
There is also information about topics authors, dates of creation, and the number of posts in each
of the topics.
 
- To **create new topic** user needs to click on the corresponding button, specify the category and 
topic name, and write the text of the first post.  

- Each **topic** has a form for adding new posts. Posts are ordered by the date of creation. Users can
**subscribe** and **unsubscribe** to the topic. Subscription is for user's feed. Users can like or 
dislike each post published by other users.

- User's **feed** is the place where all new posts from the topics the user is subscribed to 
are displayed (except those posts that are published by the user). 
User can **mark posts as "Read"** to remove them from the feed.  

- **Mails** section of the website is for direct communication between users. There are **inbox, 
outbox, and bucket** (a place where deleted messages are stored before the user decides 
to delete them permanently). Messages can be **marked as read or unread** for the user's convenience.
Messages from the bucket can be **deleted permanently** or **restored**. 

- **Message page** contains information about the particular message: sender, receiver, date, 
subject, message body. Also, all actions with messages (deleting, restoring, marking as read, reply)
can be performed there.

- Each **user's profile page** contains information about the user: first name, last name, username,
location, "About me" section, amount of posts published by the user on the forum, latest forum 
activity, user's avatar. Note, that some information could be missed if the user didn't specify it.
To **send a message** to the user press the corresponding button in the profile page of the needed user.

- It is possible to access more detailed information about the **users forum activity** from 
the user's profile page. There you can see user's posts with dates, topics, votes, and 
posts body.

- If the user views his/her **own profile**, it is possible to **edit** it (edit or add information,
upload avatar) or **change password**.

- It is possible to **reset users passwords** if they forgot them. 

- When a new user is **signing up**, he/she should **verify the account** by following the link 
from the email. **Emails are sent asynchronously**, by using **Celery** with **Redis** backend.

- **PostgreSQL** is the database that this application uses. 
**Django ORM** is used for interaction with the database.

- **jQuery** library is used for performing AJAX requests in liking/disliking features, as well as for
in subscribing/unsubscribing features.

- **Bootstrap** is used for providing a basic user interface. **django-crispy-forms** package was used
to ensure seamless integration between Django and Bootstrap when building web forms.

- There are **tests** for models and views in *discussions* app.
