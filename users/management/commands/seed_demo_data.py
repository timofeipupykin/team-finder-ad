from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import User


class Command(BaseCommand):
    help = "Create demo users and projects for review."

    def handle(self, *args, **options):
        demo_users = [
            {
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Ivanova",
                "phone": "+79990000001",
                "about": "Backend developer",
            },
            {
                "email": "bob@example.com",
                "name": "Bob",
                "surname": "Petrov",
                "phone": "+79990000002",
                "about": "Frontend developer",
            },
            {
                "email": "carol@example.com",
                "name": "Carol",
                "surname": "Sidorova",
                "phone": "+79990000003",
                "about": "Designer",
            },
        ]

        created_users = []
        for payload in demo_users:
            email = payload["email"]
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": payload["name"],
                    "surname": payload["surname"],
                    "phone": payload["phone"],
                    "about": payload["about"],
                },
            )
            if created:
                user.set_password("StrongPass123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {email}"))
            else:
                self.stdout.write(f"User already exists: {email}")
            created_users.append(user)

        for idx, user in enumerate(created_users, start=1):
            project_name = f"Demo Project {idx}"
            project, created = Project.objects.get_or_create(
                name=project_name,
                owner=user,
                defaults={
                    "description": f"Demo description for {project_name}",
                    "status": Project.STATUS_OPEN,
                    "github_url": f"https://github.com/example/demo-project-{idx}",
                },
            )
            project.participants.add(user)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created project: {project_name}"))
            else:
                self.stdout.write(f"Project already exists: {project_name}")

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
