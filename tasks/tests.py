from django.test import TestCase
from tasks.models import Task

# Create your tests here.

class IndexViewTests(TestCase):
    def test_homepage_returns_200(self):
        Task.objects.create(title="Test task", complete=False)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

class TaskCreateTests(TestCase):
    def test_create_task_redirects_and_creates(self):
        response = self.client.post("/", data={"title": "New task", "complete": False})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title="New task").exists())

class TaskUpdateTests(TestCase):
    def test_update_task_changes_title(self):
        task = Task.objects.create(title="Old title", complete=False)

        response = self.client.post(f"/update_task/{task.id}/", data={"title": "New title", "complete": False})

        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, "New title")

class TaskDeleteTests(TestCase):
    def test_delete_task_removes_task(self):
        task = Task.objects.create(title="To delete", complete=False)

        response = self.client.post(f"/delete_task/{task.id}/")

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())