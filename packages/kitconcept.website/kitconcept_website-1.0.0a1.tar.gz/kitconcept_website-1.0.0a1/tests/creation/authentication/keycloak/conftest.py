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
            "provider": "keycloak",
            "oidc-server_url": "http://localhost:8180",
            "oidc-realm_name": "site",
            "oidc-client_id": "plone",
            "oidc-client_secret": "12345678",
            "oidc-site-url": "http://localhost:3000",
            "oidc-scope": ["openid", "profile", "email"],
        },
    }
