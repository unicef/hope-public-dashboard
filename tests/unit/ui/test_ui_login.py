from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables") -> "DjangoTestApp":
    return django_app_factory(csrf_checks=False)


def test_login_page_is_sso_only(app: "DjangoTestApp") -> None:
    response = app.get(reverse("ui:login"))

    assert response.status_code == 200
    assert "Login with Azure" in response.text
    assert 'name="password"' not in response.text
    assert 'id="login-form"' not in response.text
    assert "Forgotten your password" not in response.text
