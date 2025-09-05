import pytest


@pytest.fixture()
def answers():
    return {
        "site_id": "site",
        "title": "Site",
        "description": "Site created with A CMS solution for public websites. Created by kitconcept.",  # noQA: E501
        "default_language": "en",
        "portal_timezone": "Europe/Berlin",
        "setup_content": True,
        "authentication": {
            "provider": "authomatic-google",
            "authomatic-google-consumer_key": "google-12345",
            "authomatic-google-consumer_secret": "12345678",
            "authomatic-google-scope": ["profile", "email"],
        },
    }
