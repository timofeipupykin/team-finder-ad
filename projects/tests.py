from django.test import TestCase

from users.models import User

from .models import Project


class ProjectFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123",
            name="Owner",
            surname="User",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="StrongPass123",
            name="Member",
            surname="User",
        )

    def test_create_project_adds_owner_to_participants(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            "/projects/create-project",
            {
                "name": "Test Project",
                "description": "desc",
                "github_url": "https://github.com/example/repo",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="Test Project")
        self.assertTrue(project.participants.filter(pk=self.owner.pk).exists())

    def test_toggle_favorite(self):
        project = Project.objects.create(name="P1", owner=self.owner, status="open")
        self.client.force_login(self.member)
        response = self.client.post(f"/projects/{project.id}/toggle-favorite/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.member.favorites.filter(pk=project.pk).exists())

    def test_toggle_participation(self):
        project = Project.objects.create(name="P1", owner=self.owner, status="open")
        self.client.force_login(self.member)
        response = self.client.post(f"/projects/{project.id}/toggle-participate/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(project.participants.filter(pk=self.member.pk).exists())
