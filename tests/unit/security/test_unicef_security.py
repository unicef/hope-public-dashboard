import pytest
from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_string

pytestmark = [pytest.mark.django_db]


def test_social_auth_pipeline_is_importable():
    assert settings.SOCIAL_AUTH_PIPELINE
    for path in settings.SOCIAL_AUTH_PIPELINE:
        assert import_string(path)
    assert "social_core.backends.azuread_tenant.AzureADTenantOAuth2" in settings.AUTHENTICATION_BACKENDS


def test_admin_login_exposes_local_and_unicef_azure_login(client):
    response = client.get(reverse("admin:login"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Login with Azure" in content
    assert reverse("social:begin", args=["azuread-tenant-oauth2"]) in content
    assert 'name="username"' in content
    assert 'name="password"' in content
    assert 'id="login-form"' in content


def test_admin_is_not_available_at_default_path(client):
    assert client.get("/admin/").status_code == 404


def test_unicef_security_urls_are_registered(client):
    response = client.get(reverse("unicef_security:unauthorized"))
    assert response.status_code == 200
