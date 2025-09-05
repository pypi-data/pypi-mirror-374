import os
import sys
import json
import shutil
import importlib.util
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from django.test import TestCase
from django.conf import settings
from nodes.models import Node, NodeRole
from django.contrib.sites.models import Site
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
import socket


class SeedDataEntityTests(TestCase):
    def test_preserve_seed_data_on_create(self):
        role = NodeRole.objects.create(name="Tester", is_seed_data=True)
        self.assertTrue(NodeRole.all_objects.get(pk=role.pk).is_seed_data)


class EnvRefreshFixtureTests(TestCase):
    def setUp(self):
        call_command("flush", verbosity=0, interactive=False)

    def test_env_refresh_marks_seed_data(self):
        base_dir = Path(settings.BASE_DIR)
        tmp_dir = base_dir / "temp_fixture"
        fixture_dir = tmp_dir / "fixtures"
        fixture_dir.mkdir(parents=True, exist_ok=True)
        fixture_path = fixture_dir / "sample.json"
        fixture_path.write_text(
            json.dumps(
                [
                    {
                        "model": "nodes.noderole",
                        "pk": 999,
                        "fields": {"name": "Fixture Role"},
                    }
                ]
            )
        )
        rel_path = str(fixture_path.relative_to(base_dir))
        spec = importlib.util.spec_from_file_location("env_refresh", base_dir / "env-refresh.py")
        env_refresh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(env_refresh)
        env_refresh._fixture_files = lambda: [rel_path]
        from django.core.management import call_command as django_call

        def fake_call_command(name, *args, **kwargs):
            if name == "loaddata":
                django_call(name, *args, **kwargs)
            # ignore other commands

        env_refresh.call_command = fake_call_command
        env_refresh.run_database_tasks()
        role = NodeRole.all_objects.get(pk=999)
        self.assertTrue(role.is_seed_data)
        shutil.rmtree(tmp_dir)


class EnvRefreshNodeTests(TestCase):
    def setUp(self):
        base_dir = Path(settings.BASE_DIR)
        spec = importlib.util.spec_from_file_location("env_refresh", base_dir / "env-refresh.py")
        self.env_refresh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.env_refresh)
        self.env_refresh.call_command = lambda *args, **kwargs: None
        self.env_refresh._fixture_files = lambda: []

    def test_env_refresh_registers_node(self):
        Node.objects.all().delete()
        self.env_refresh.run_database_tasks()
        self.assertIsNotNone(Node.get_local())

    def test_env_refresh_updates_existing_node(self):
        mac = Node.get_current_mac()
        Node.objects.create(hostname="old", address="0.0.0.0", port=1, mac_address=mac)
        self.env_refresh.run_database_tasks()
        node = Node.objects.get(mac_address=mac)
        self.assertEqual(node.hostname, socket.gethostname())

    def test_env_refresh_creates_control_site(self):
        Node.objects.all().delete()
        Site.objects.all().delete()
        lock_dir = Path(settings.BASE_DIR) / "locks"
        lock_dir.mkdir(exist_ok=True)
        control_lock = lock_dir / "control.lck"
        try:
            control_lock.touch()
            self.env_refresh.run_database_tasks()
            node = Node.get_local()
            self.assertIsNotNone(node)
            self.assertTrue(
                Site.objects.filter(domain=node.public_endpoint, name="Control").exists()
            )
        finally:
            control_lock.unlink(missing_ok=True)


class SeedDataViewTests(TestCase):
    def setUp(self):
        call_command("loaddata", "nodes/fixtures/node_roles.json")
        NodeRole.objects.filter(pk=1).update(is_seed_data=True)
        User = get_user_model()
        self.user = User.objects.create_superuser("sdadmin", password="pw")
        self.client.login(username="sdadmin", password="pw")

    def test_seed_data_view_shows_fixture(self):
        response = self.client.get(reverse("admin:seed_data"))
        self.assertContains(response, "node_roles.json")
