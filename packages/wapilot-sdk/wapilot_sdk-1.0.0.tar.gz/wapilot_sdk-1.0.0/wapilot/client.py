import requests

class WapilotSDK:
    def __init__(self, token, base_url="https://app.wapilot.io"):
        """
        Initialize the WAPILOT SDK.
        
        Args:
            token (str): Your WAPILOT API token
            base_url (str, optional): API base URL. Defaults to "https://app.wapilot.io"
        """
        if not token:
            raise ValueError("API token is required")

        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    # Contacts API
    def get_contacts(self):
        """Get all contacts."""
        response = self.session.get(f"{self.base_url}/api/contacts")
        response.raise_for_status()
        return response.json()

    def create_contact(self, contact_data):
        """Create a new contact."""
        response = self.session.post(f"{self.base_url}/api/contacts", json=contact_data)
        response.raise_for_status()
        return response.json()

    def update_contact(self, uuid, contact_data):
        """Update an existing contact."""
        response = self.session.put(f"{self.base_url}/api/contacts/{uuid}", json=contact_data)
        response.raise_for_status()
        return response.json()

    def delete_contact(self, uuid):
        """Delete a contact."""
        response = self.session.delete(f"{self.base_url}/api/contacts/{uuid}")
        response.raise_for_status()
        return response.json()

    # Contact Groups API
    def get_contact_groups(self):
        """Get all contact groups."""
        response = self.session.get(f"{self.base_url}/api/contact-groups")
        response.raise_for_status()
        return response.json()

    def create_contact_group(self, group_data):
        """Create a new contact group."""
        response = self.session.post(f"{self.base_url}/api/contact-groups", json=group_data)
        response.raise_for_status()
        return response.json()

    def update_contact_group(self, uuid, group_data):
        """Update an existing contact group."""
        response = self.session.put(f"{self.base_url}/api/contact-groups/{uuid}", json=group_data)
        response.raise_for_status()
        return response.json()

    def delete_contact_group(self, uuid):
        """Delete a contact group."""
        response = self.session.delete(f"{self.base_url}/api/contact-groups/{uuid}")
        response.raise_for_status()
        return response.json()

    # Automated Replies API
    def get_canned_replies(self):
        """Get all automated replies."""
        response = self.session.get(f"{self.base_url}/api/canned-replies")
        response.raise_for_status()
        return response.json()

    def create_canned_reply(self, reply_data):
        """Create a new automated reply."""
        response = self.session.post(f"{self.base_url}/api/canned-replies", json=reply_data)
        response.raise_for_status()
        return response.json()

    def update_canned_reply(self, uuid, reply_data):
        """Update an existing automated reply."""
        response = self.session.put(f"{self.base_url}/api/canned-replies/{uuid}", json=reply_data)
        response.raise_for_status()
        return response.json()

    def delete_canned_reply(self, uuid):
        """Delete an automated reply."""
        response = self.session.delete(f"{self.base_url}/api/canned-replies/{uuid}")
        response.raise_for_status()
        return response.json()

    # Messages API
    def send_message(self, message_data):
        """Send a text message."""
        response = self.session.post(f"{self.base_url}/api/send", json=message_data)
        response.raise_for_status()
        return response.json()

    def send_media_message(self, media_data):
        """Send a media message."""
        response = self.session.post(f"{self.base_url}/api/send/media", json=media_data)
        response.raise_for_status()
        return response.json()

    def send_template_message(self, template_data):
        """Send a template message."""
        response = self.session.post(f"{self.base_url}/api/send/template", json=template_data)
        response.raise_for_status()
        return response.json()

    # Templates API
    def get_templates(self):
        """Get all templates."""
        response = self.session.get(f"{self.base_url}/api/templates")
        response.raise_for_status()
        return response.json()
