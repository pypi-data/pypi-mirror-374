import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import TestCase

from core.models import SigilRoot, OdooProfile


class SigilResolutionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SigilRoot.objects.create(prefix="ENV", context_type=SigilRoot.Context.CONFIG)
        SigilRoot.objects.create(prefix="SYS", context_type=SigilRoot.Context.CONFIG)
        cls.user = get_user_model().objects.create(username="sigiluser")

    def test_env_variable_sigil(self):
        os.environ["SIGIL_PATH"] = "demo"
        profile = OdooProfile.objects.create(
            user=self.user,
            host="path=[ENV.SIGIL_PATH]",
            database="db",
            username="odoo",
            password="secret",
        )
        tmpl = Template("{{ profile.host }}")
        rendered = tmpl.render(Context({"profile": profile}))
        self.assertEqual(rendered, "path=demo")

    def test_settings_sigil(self):
        profile = OdooProfile.objects.create(
            user=self.user,
            host="lang=[SYS.LANGUAGE_CODE]",
            database="db",
            username="odoo",
            password="secret",
        )
        tmpl = Template("{{ profile.host }}")
        rendered = tmpl.render(Context({"profile": profile}))
        expected = f"lang={settings.LANGUAGE_CODE}"
        self.assertEqual(rendered, expected)

    def test_unresolved_env_sigil_left_intact(self):
        profile = OdooProfile.objects.create(
            user=self.user,
            host="path=[ENV.MISSING_PATH]",
            database="db",
            username="odoo",
            password="secret",
        )
        tmpl = Template("{{ profile.host }}")
        with self.assertLogs("core.entity", level="WARNING") as cm:
            rendered = tmpl.render(Context({"profile": profile}))
        self.assertEqual(rendered, "path=[ENV.MISSING_PATH]")
        self.assertIn("Missing environment variable for sigil [ENV.MISSING_PATH]", cm.output[0])

    def test_unknown_root_sigil_left_intact(self):
        profile = OdooProfile.objects.create(
            user=self.user,
            host="url=[FOO.BAR]",
            database="db",
            username="odoo",
            password="secret",
        )
        tmpl = Template("{{ profile.host }}")
        with self.assertLogs("core.entity", level="WARNING") as cm:
            rendered = tmpl.render(Context({"profile": profile}))
        self.assertEqual(rendered, "url=[FOO.BAR]")
        self.assertIn("Unknown sigil root [FOO]", cm.output[0])
