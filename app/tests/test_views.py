import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home(client):
    url = reverse('home')
    response = client.get(url)
    assert "The Wanderverse Project" in response.content.decode()


@pytest.mark.django_db
def test_contribute(client):
    url = reverse('contribute_random')
    response = client.get(url)
    assert "<form method=\"post\"" in response.content.decode()
