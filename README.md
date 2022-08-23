# Social Finance Building Register

We need to keep a register of staff in the building in case of fire or emergency. 
At the moment, this is kept on paper in the reception. 

The idea of this website is to make it quicker and easier for regular staff to 
sign-in and out, in particular for those arriving by bike and using the other
entrance.

We can also use it to notify staff members in the building of any day-to-day 
issues, and send out notifications in case of emergencies.

This project is entirely "homemade" and your help will make it better for everyone!

You don't need to know how to code to get involved. Suggestions for improvements, 
user interface ideas, bug reports, every little suggestion will help us 
make this tool better and signing-in easier.

If you have a suggested improvement, please submit them in our [issues log][issues].

## What do I need?

Patience. And a few tools. Most importantly you need [Python][python]. Follow the links
to download a recent version and install this.

Next, we use [Poetry][poetry] for dependency management. Once you have 
working python version installed, installing Poetry should be as easy as following
the steps on [this page][poetry-install].

However, it's not always that easy. If those steps don't work, download the installer 
from [this link][poetry-script]. Find your downloaded file, and the launch it 
by running `python install-poetry.py` where `install-poetry.py` is the name of the 
downloaded file.

Now you are ready to check out this project. If you're not familiar with GIT, try
one of the many tutorials available online. For windows, I can recommend 
[this one][git-tutorial].

Once you have checked out this repository, install the required libraries:

```shell
poetry install
```

if that has worked, you can create a local database instance with:

```shell
poetry run python manage.py migrate
```

and then you are ready to launch the project itself:

```shell
poetry run python manage.py runserver
```

By default you can log in using any 'name' and you will see the-sign in code printed
out in the python console.

Once signed-in, try to make some changes to some of the page 
[templates](./register/templates/register) or [views](./register/views).

You can create a superuser by running:

```shell
poetry run python manage.py createsuperuser
```

And then log in via the admin page that you can find on 
http://127.0.0.1:8000/admin/

The exact URL may vary depending on your settings, so check the URL that is printed 
out when the server starts and add /admin/ to the end of it.

If you want to create a public test server for your changes, please follow 
these steps:

1. Create a [fork][github-fork] of the project repository to hold your changes.
2. Make your changes and commit them to your fork.
3. Sign up for a [free Heroku account][heroku-signup]

Once you are signed in to your new Heroku account, navigate to this page on
your GitHub fork, and click this button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Design ideas

* Simple sign in, using phone✅, email✅ or SF account
* Long-lasting session cookie / identity cookie to make sign in quick
* Reminder to sign out towards the end of the day
* Admin view showing who is currently in the building✅

To be considered:

* Data retention of records
* Non-intrusive reminders to make data accurate
* Those who are signed-in can see others who are signed in? 
  * Community pressure? 
  * An accurate in-office slack channel?
  
[issues]: https://github.com/SocialFinanceDigitalLabs/building-register/issues

[python]: https://www.python.org/downloads/
[poetry]: https://python-poetry.org/
[poetry-install]: https://python-poetry.org/docs/master/#installation
[poetry-script]: https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py

[git-tutorial]: https://www.computerhope.com/issues/ch001927.htm
[github-fork]: https://docs.github.com/en/get-started/quickstart/fork-a-repo

[heroku-signup]: https://signup.heroku.com/
