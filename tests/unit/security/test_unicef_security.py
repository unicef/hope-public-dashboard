import pytest
from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_string

pytestmark = [pytest.mark.django_db]


def test_social_auth_pipeline_is_importable():
    assert settings.SOCIAL_AUTH_PIPELINE
    for path in settings.SOCIAL_AUTH_PIPELINE:
        assert import_string(path)


def test_admin_login_exposes_unicef_azure_login(client):
    response = client.get("/admin/login/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Login with Azure" in content
    assert reverse("social:begin", args=["azuread-tenant-oauth2"]) in content


def test_unicef_security_urls_are_registered(client):
    response = client.get(reverse("unicef_security:unauthorized"))
    assert response.status_code == 200
