# Social Finance Building Register

The Social Finance Building Register is a Django web application designed to streamline the process of staff signing in and out of the building. The application replaces the traditional paper-based system in the reception area, making it quicker and easier for regular staff to sign in and out, especially for those arriving by bike and using the other entrance.

## Features

- Simple sign-in process using phone, email, or SF account
- Long-lasting session cookie for quick sign-in
- Reminders to sign out towards the end of the day
- Admin view showing who is currently in the building
- Notifications to staff members about day-to-day issues and emergencies

## Key Components

### Models

- `ContactDetails`: Stores contact information (email or phone) for each user
- `ContactValidationCode`: Manages validation codes sent to users for authentication
- `AuditRecord`: Tracks user actions and IP addresses for auditing purposes
- `SignInRecord`: Maintains a record of user sign-ins and sign-outs
- `LongLivedToken`: Generates and stores long-lived authentication tokens for users
- `UserSettings`: Holds additional user settings, such as the "ricked" flag

### Views

- `index`: Displays the main sign-in/sign-out page for authenticated users
- `login`, `login_form`, `login_token`, `logout`: Handle user authentication and token-based login
- `profile`, `create_url`: Allow users to update their contact details and generate long-lived login URLs
- `report`, `report_json`: Provide an admin view of users currently signed in and their records
- `app_login`, `app_status`: API endpoints for mobile app integration

### Management Commands

- `clean-old-records`: Cleans up old sign-in records, user records, and audit records based on a specified number of days
- `send-reminders`: Sends reminders to signed-in users to sign out at the end of the day
- `stats`: Generates statistics about user sign-ins and sign-outs
- `visits`: Outputs a detailed report of user visits, including sign-in and sign-out times

## Task Scheduler

The application uses the Django Q library to schedule and run background tasks. There are two main scheduled tasks:

1. `send_reminders`: This task is responsible for sending reminders to signed-in users to sign out at the end of the day. It retrieves the signed-in users and their contact details, and then sends a reminder message using the configured token method (e.g., email or SMS).

2. `clean_old_records`: This task cleans up old records in the database, including sign-in records, user records, and audit records. It removes records older than a specified number of days to keep the database size manageable.

The scheduled tasks are defined in the `register/tasks.py` file and are configured to run at specific intervals using the Django Q scheduler.

### Configuration

To configure the task scheduler, you need to set up the following in your Django settings:

```python
Q_CLUSTER = {
    'name': 'building-register',
    'workers': 2,
    'recycle': 500,
    'timeout': 600,
    'retry': 660,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'Django Q',
    'orm': 'default',
}
```

These settings define the behavior of the Django Q cluster, including the number of workers, task timeout, retry interval, and other optimizations.

### Running the Scheduler

To start the task scheduler, you need to run the Django Q cluster using the following management command:

```shell
python manage.py qcluster
```

This command will start the Django Q cluster and begin executing the scheduled tasks based on their defined intervals.

### Task Definitions

The `send_reminders` task is defined in the `register/tasks.py` file. It retrieves the signed-in users and their contact details, and then sends a reminder message using the configured token method (e.g., email or SMS). The task is scheduled to run at a specific time each day.

The `clean_old_records` task is also defined in the `register/tasks.py` file. It removes old records from the database, including sign-in records, user records, and audit records. The task is scheduled to run at a regular interval (e.g., daily) to keep the database size manageable.

### Scheduler - Management Commands

In addition to the scheduled tasks, there are management commands available to manually trigger the tasks:

- `python manage.py send-reminders`: Sends reminders to signed-in users to sign out.
- `python manage.py clean-old-records`: Cleans up old records in the database.

These management commands can be useful for testing or manually triggering the tasks when needed.

By leveraging the Django Q library and configuring the scheduled tasks, the application automates the process of sending reminders to users and cleaning up old records, ensuring a smooth and efficient user experience.

### Integration with Email and Twilio

The application supports sending notifications and reminders to users via email and SMS using the following integrations:

1. Email: The `Office365EmailService` class in `register/util/tokens/office365_email.py` handles sending emails using the Microsoft Graph API. It requires the necessary Office 365 configuration settings, such as the client ID, client secret, tenant ID, and sender email address.

2. Twilio SMS: The `TwilioSMSService` class in `register/util/tokens/twilio_sms.py` handles sending SMS messages using the Twilio API. It requires the Twilio account SID and auth token to be configured in the application settings.

Both email and SMS services are used for sending login codes and reminders to users based on their preferred contact method.

## Slack Integration

The application supports sending notifications and reminders to users via Slack using the following integration:

1. Slack Webhooks: The `SLACK_WEBHOOKS` setting in `register/util/signals/slack.py` handles sending messages to Slack channels using incoming webhooks. It requires the necessary webhook URLs to be configured in the application settings.

The Slack integration is used for sending notifications when users sign in and out of the building. The `slack_send_signin` and `slack_send_signout` functions in `register/util/signals/slack.py` are connected to the `user_signed_in` and `user_signed_out` signals respectively. These functions send a message to the configured Slack channels whenever a user signs in or out.

### Slack - Configuration

To configure the Slack integration, you need to set up the following in your Django settings:

```python
SLACK_WEBHOOKS = [
    url for url in os.environ.get("SLACK_SIGNIN_WEBHOOKS", "").split(" ") if url
]
```

The `SLACK_WEBHOOKS` setting should be a list of Slack incoming webhook URLs. You can provide multiple webhook URLs by separating them with spaces in the `SLACK_SIGNIN_WEBHOOKS` environment variable.

### Notifications

When a user signs in or out, the application sends a notification to the configured Slack channels. The notification includes the following information:

- User's first name and last name
- Action (signed in or signed out)
- Total number of users currently signed in

The notifications provide real-time updates to the team about the presence of users in the building.

By leveraging the Slack integration, the application automates the process of notifying team members about user sign-ins and sign-outs, ensuring everyone stays informed about the current occupancy of the building.

## Getting involved

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
