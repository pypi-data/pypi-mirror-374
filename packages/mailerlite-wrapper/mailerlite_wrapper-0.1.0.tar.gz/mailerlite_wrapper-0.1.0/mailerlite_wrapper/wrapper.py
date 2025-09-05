import mailerlite as MailerLite

class MailerLiteWrapper:
    """A Python wrapper class to simplify interactions with the MailerLite API."""

    def __init__(self, api_key: str):
        """
        Initializes the MailerLite client.
        
        Args:
            api_key (str): Your MailerLite API key.
        """
        if not api_key or not isinstance(api_key, str):
            raise ValueError("A valid MailerLite API key string is required.")
        self.client = MailerLite.Client({'api_key': api_key})

    # --- Subscribers ---
    def get_all_active_subscribers(self):
        """Fetches all active subscribers from MailerLite."""
        return self.client.subscribers.list(filter={'status': 'active'})

    def create_subscriber(self, email: str, name: str, last_name: str):
        """Creates a new subscriber in MailerLite."""
        return self.client.subscribers.create(email, fields={'name': name, 'last_name': last_name})

    def update_subscriber(self, email: str, name: str, last_name: str):
        """Updates an existing subscriber in MailerLite."""
        return self.client.subscribers.update(email, fields={'name': name, 'last_name': last_name})

    def get_specific_subscriber(self, email: str):
        """Fetches a specific subscriber from MailerLite."""
        return self.client.subscribers.get(email)

    def delete_subscriber(self, subscriber_id: int):
        """Deletes a subscriber from MailerLite."""
        return self.client.subscribers.delete(subscriber_id)

    # --- Groups ---
    def list_groups(self, group_name: str):
        """Fetches all groups from MailerLite."""
        return self.client.groups.list(filter={'name': group_name}, sort='name')

    def create_group(self, group_name: str):
        """Creates a new group in MailerLite."""
        return self.client.groups.create(group_name)

    def update_group(self, group_id: int, new_group_name: str):
        """Updates an existing group in MailerLite."""
        return self.client.groups.update(group_id, {'name': new_group_name})

    def delete_group(self, group_id: int):
        """Deletes a group from MailerLite."""
        return self.client.groups.delete(group_id)

    def get_subscriber_from_group(self, group_id: int):
        """Fetches all subscribers from a specific group in MailerLite."""
        return self.client.groups.get_group_subscribers(group_id)

    def assign_subscriber_to_group(self, subscriber_id: int, group_id: int):
        """Assigns a subscriber to a specific group in MailerLite."""
        return self.client.groups.assign_subscriber_to_group(group_id, subscriber_id)

    def unsubscribe_subscriber_from_group(self, subscriber_id: int, group_id: int):
        """Unsubscribes a subscriber from a specific group in MailerLite."""
        return self.client.subscribers.unassign_subscriber_from_group(subscriber_id, group_id)

    # --- Segments ---
    def list_segments(self):
        """Fetches all segments from MailerLite."""
        return self.client.segments.list()

    def update_segment(self, segment_id: int, new_segment_name: str):
        """Updates an existing segment in MailerLite."""
        return self.client.segments.update(segment_id, {'name': new_segment_name})

    def delete_segment(self, segment_id: int):
        """Deletes a segment from MailerLite."""
        return self.client.segments.delete(segment_id)

    def get_segment_info(self, segment_id: int):
        """Fetches information about a specific segment in MailerLite."""
        return self.client.segments.get(segment_id)

    def get_segment_subscribers(self, segment_id: int):
        """Fetches all subscribers from a specific segment in MailerLite."""
        return self.client.segments.get_subscribers(segment_id)

    # --- Fields ---
    def list_fields(self):
        """Fetches all custom fields from MailerLite."""
        return self.client.fields.list()

    def create_field(self, field_name: str, field_type: str):
        """Creates a new custom field in MailerLite."""
        return self.client.fields.create({'name': field_name, 'type': field_type})

    def update_field(self, field_id: int, new_field_name: str):
        """Updates an existing custom field in MailerLite."""
        return self.client.fields.update(field_id, new_field_name)

    def delete_field(self, field_id: int):
        """Deletes a custom field from MailerLite."""
        return self.client.fields.delete(field_id)

    # --- Automations ---
    def list_automations(self):
        """Fetches all automations from MailerLite."""
        return self.client.automations.list()

    def get_specific_automation(self, automation_id: int):
        """Fetches a specific automation from MailerLite."""
        return self.client.automations.get(automation_id)

    def get_automation_activity(self, automation_id: int, page: int = 1, limit: int = 10, filter_params: dict = None):
        """Get subscribers activity for a specific automation."""
        return self.client.automations.activity(automation_id, page=page, limit=limit, filter=filter_params)

    # --- Campaigns ---
    def list_campaigns(self, page: int = 1, limit: int = 10, filter_params: dict = None):
        """List all campaigns."""
        return self.client.campaigns.list(limit=limit, page=page, filter=filter_params)

    def get_campaign(self, campaign_id: int):
        """Get a single campaign by its ID."""
        return self.client.campaigns.get(campaign_id)

    def create_campaign(self, campaign_data: dict):
        """Create a new campaign."""
        return self.client.campaigns.create(campaign_data)

    def update_campaign(self, campaign_id: int, campaign_data: dict):
        """Update an existing campaign."""
        return self.client.campaigns.update(campaign_id, campaign_data)

    def schedule_campaign(self, campaign_id: int, schedule_data: dict):
        """Schedule a campaign for delivery."""
        return self.client.campaigns.schedule(campaign_id, schedule_data)

    def cancel_campaign(self, campaign_id: int):
        """Cancel a scheduled campaign."""
        return self.client.campaigns.cancel(campaign_id)

    def delete_campaign(self, campaign_id: int):
        """Delete a campaign."""
        return self.client.campaigns.delete(campaign_id)

    def get_campaign_activity(self, campaign_id: int):
        """Get subscriber activity for a campaign."""
        return self.client.campaigns.activity(campaign_id)

    # --- Forms ---
    def list_forms(self, page: int = 1, limit: int = 10, sort: str = 'name', filter_params: dict = None):
        """List all forms."""
        return self.client.forms.list(limit=limit, page=page, sort=sort, filter=filter_params)

    def get_form(self, form_id: int):
        """Get a single form by its ID."""
        return self.client.forms.get(form_id)

    def update_form(self, form_id: int, new_name: str):
        """Update the name of a form."""
        return self.client.forms.update(form_id, new_name)

    def delete_form(self, form_id: int):
        """Delete a form."""
        return self.client.forms.delete(form_id)

    def get_form_subscribers(self, form_id: int, page: int = 1, limit: int = 10, filter_params: dict = None):
        """Get subscribers who signed up to a specific form."""
        return self.client.forms.get_subscribers(form_id, page=page, limit=limit, filter=filter_params)

    # --- Batching ---
    def create_batch_request(self, requests: list):
        """Create a new batch request."""
        return self.client.batches.request(requests)

    # --- Webhooks ---
    def list_webhooks(self):
        """List all webhooks."""
        return self.client.webhooks.list()

    def get_webhook(self, webhook_id: int):
        """Get a single webhook by its ID."""
        return self.client.webhooks.get(webhook_id)

    def create_webhook(self, events: list, url: str, name: str):
        """Create a new webhook."""
        return self.client.webhooks.create(events, url, name)

    def update_webhook(self, webhook_id: int, events: list = None, url: str = None, name: str = None, enabled: bool = None):
        """Update an existing webhook."""
        return self.client.webhooks.update(webhook_id, events=events, url=url, name=name, enabled=enabled)

    def delete_webhook(self, webhook_id: int):
        """Delete a webhook."""
        return self.client.webhooks.delete(webhook_id)

    # --- Timezones ---
    def list_timezones(self):
        """Get a list of available timezones."""
        return self.client.timezone.list()

    # --- Campaign Languages ---
    def list_campaign_languages(self):
        """Get a list of available campaign languages."""
        return self.client.campaigns.languages()