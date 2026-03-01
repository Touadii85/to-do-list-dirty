from django.test import TestCase
from tasks.models import Task
from django.test import TestCase

class SmokeTests(TestCase):
    def test_smoke(self):
        self.assertTrue(True)

# Create your tests here.

class UrlSmokeTests(TestCase):
    def setUp(self):
        # Donnée de test réutilisée pour update/delete
        self.task = Task.objects.create(title="Task test", complete=False)

    def test_homepage_get_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_update_page_get_returns_200(self):
        response = self.client.get(f"/update_task/{self.task.id}/")
        self.assertEqual(response.status_code, 200)

    def test_delete_page_get_returns_200(self):
        response = self.client.get(f"/delete_task/{self.task.id}/")
        self.assertEqual(response.status_code, 200)


class UrlCrudBehaviorTests(TestCase):
    def setUp(self):
        self.task = Task.objects.create(title="Old title", complete=False)

    def test_update_post_redirects_and_updates(self):
        response = self.client.post(
            f"/update_task/{self.task.id}/",
            data={"title": "New title", "complete": False},
        )
        # Les vues de ce projet redirigent après POST
        self.assertEqual(response.status_code, 302)

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "New title")

    def test_delete_post_redirects_and_deletes(self):
        response = self.client.post(f"/delete_task/{self.task.id}/")
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Task.objects.filter(id=self.task.id).exists())