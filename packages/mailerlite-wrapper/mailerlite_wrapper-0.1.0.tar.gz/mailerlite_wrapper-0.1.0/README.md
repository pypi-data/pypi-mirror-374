# Python MailerLite Wrapper

A simple, class-based Python wrapper to make common MailerLite API calls more convenient.

## Installation

Install the package from PyPI:

```bash
pip install mailerlite-wrapper

# USAGE
from mailerlite_wrapper import MailerLiteWrapper
import os

# It's recommended to load your API key from environment variables
# and not to hard-code it in your script.
API_KEY = os.getenv("MAILER_LITE_API_KEY")

# Initialize the wrapper
ml = MailerLiteWrapper(api_key=API_KEY)

# Now you can use the helper methods
try:
    # Get all active subscribers
    subscribers = ml.get_all_active_subscribers()
    print("Fetched subscribers.")

    # Create a new subscriber
    new_subscriber = ml.create_subscriber(
        email="new.subscriber@example.com",
        name="John",
        last_name="Doe"
    )
    print("Created a new subscriber.")

except Exception as e:
    print(f"An error occurred: {e}")

# License

from mailerlite_wrapper import MailerLiteWrapper
import os

# It's recommended to load your API key from environment variables
# and not to hard-code it in your script.
API_KEY = os.getenv("MAILER_LITE_API_KEY")

# Initialize the wrapper
ml = MailerLiteWrapper(api_key=API_KEY)

# Now you can use the helper methods
try:
    # Get all active subscribers
    subscribers = ml.get_all_active_subscribers()
    print("Fetched subscribers.")

    # Create a new subscriber
    new_subscriber = ml.create_subscriber(
        email="new.subscriber@example.com",
        name="John",
        last_name="Doe"
    )
    print("Created a new subscriber.")

except Exception as e:
    print(f"An error occurred: {e}")
