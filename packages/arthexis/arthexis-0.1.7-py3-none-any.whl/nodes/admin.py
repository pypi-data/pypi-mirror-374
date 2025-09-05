from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from app.widgets import CopyColorWidget, CodeEditorWidget
from django.db import models
from django.conf import settings
from pathlib import Path
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.core.management import call_command
import base64
import pyperclip
from pyperclip import PyperclipException
import uuid
import subprocess
import io
import threading
import re
from .utils import capture_screenshot, save_screenshot
from .actions import NodeAction

from .models import (
    Node,
    EmailOutbox as NodeEmailOutbox,
    NodeRole,
    ContentSample,
    NodeTask,
    NetMessage,
    Operation,
    Interrupt,
    Logbook,
    User,
)
from core.admin import UserAdmin as CoreUserAdmin


RUN_CONTEXTS: dict[int, dict] = {}
SIGIL_RE = re.compile(r"\[[A-Za-z0-9_]+\.[A-Za-z0-9_]+\]")


class NodeAdminForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = "__all__"
        widgets = {"badge_color": CopyColorWidget()}


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = (
        "hostname",
        "mac_address",
        "address",
        "port",
        "role",
        "last_seen",
    )
    search_fields = ("hostname", "address", "mac_address")
    change_list_template = "admin/nodes/node/change_list.html"
    change_form_template = "admin/nodes/node/change_form.html"
    form = NodeAdminForm
    actions = ["run_task", "take_screenshots"]


    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "register-current/",
                self.admin_site.admin_view(self.register_current),
                name="nodes_node_register_current",
            ),
            path(
                "<int:node_id>/action/<str:action>/",
                self.admin_site.admin_view(self.action_view),
                name="nodes_node_action",
            ),
            path(
                "<int:node_id>/public-key/",
                self.admin_site.admin_view(self.public_key),
                name="nodes_node_public_key",
            ),
        ]
        return custom + urls

    def register_current(self, request):
        """Create or update this host and offer browser node registration."""
        node, created = Node.register_current()
        if created:
            self.message_user(
                request, f"Current host registered as {node}", messages.SUCCESS
            )
        token = uuid.uuid4().hex
        context = {
            "token": token,
            "register_url": reverse("register-node"),
        }
        return render(request, "admin/nodes/node/register_remote.html", context)

    def public_key(self, request, node_id):
        node = self.get_object(request, node_id)
        if not node:
            self.message_user(request, "Unknown node", messages.ERROR)
            return redirect("..")
        security_dir = Path(settings.BASE_DIR) / "security"
        pub_path = security_dir / f"{node.public_endpoint}.pub"
        if pub_path.exists():
            response = HttpResponse(pub_path.read_bytes(), content_type="text/plain")
            response["Content-Disposition"] = f'attachment; filename="{pub_path.name}"'
            return response
        self.message_user(request, "Public key not found", messages.ERROR)
        return redirect("..")

    def run_task(self, request, queryset):
        if "apply" in request.POST:
            recipe_text = request.POST.get("recipe", "")
            task_obj, _ = NodeTask.objects.get_or_create(recipe=recipe_text)
            results = []
            for node in queryset:
                try:
                    output = task_obj.run(node)
                except Exception as exc:
                    output = str(exc)
                results.append((node, output))
            context = {"recipe": recipe_text, "results": results}
            return render(request, "admin/nodes/task_result.html", context)
        context = {"nodes": queryset}
        return render(request, "admin/nodes/node/run_task.html", context)

    run_task.short_description = "Run task"

    @admin.action(description="Take Screenshots")
    def take_screenshots(self, request, queryset):
        tx = uuid.uuid4()
        sources = getattr(settings, "SCREENSHOT_SOURCES", ["/"])
        count = 0
        for node in queryset:
            for source in sources:
                try:
                    url = source.format(node=node, address=node.address, port=node.port)
                except Exception:
                    url = source
                if not url.startswith("http"):
                    url = f"http://{node.address}:{node.port}{url}"
                try:
                    path = capture_screenshot(url)
                except Exception as exc:  # pragma: no cover - selenium issues
                    self.message_user(request, f"{node}: {exc}", messages.ERROR)
                    continue
                sample = save_screenshot(
                    path, node=node, method="ADMIN", transaction_uuid=tx
                )
                if sample:
                    count += 1
        self.message_user(request, f"{count} screenshots captured", messages.SUCCESS)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["node_actions"] = NodeAction.get_actions()
        if object_id:
            extra_context["public_key_url"] = reverse(
                "admin:nodes_node_public_key", args=[object_id]
            )
        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def action_view(self, request, node_id, action):
        node = self.get_object(request, node_id)
        action_cls = NodeAction.registry.get(action)
        if not node or not action_cls:
            self.message_user(request, "Unknown node action", messages.ERROR)
            return redirect("..")
        try:
            result = action_cls.run(node)
            if hasattr(result, "status_code"):
                return result
            self.message_user(
                request,
                f"{action_cls.display_name} executed successfully",
                messages.SUCCESS,
            )
        except NotImplementedError:
            self.message_user(
                request,
                "Remote node actions are not yet implemented",
                messages.WARNING,
            )
        except Exception as exc:  # pragma: no cover - unexpected errors
            self.message_user(request, str(exc), messages.ERROR)
        return redirect(reverse("admin:nodes_node_change", args=[node_id]))


class EmailOutbox(NodeEmailOutbox):
    class Meta:
        proxy = True
        app_label = "post_office"
        verbose_name = NodeEmailOutbox._meta.verbose_name
        verbose_name_plural = NodeEmailOutbox._meta.verbose_name_plural


@admin.register(EmailOutbox)
class EmailOutboxAdmin(admin.ModelAdmin):
    list_display = ("node", "host", "port", "username", "use_tls", "use_ssl")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.__class__ = EmailOutbox


class NodeRoleAdminForm(forms.ModelForm):
    nodes = forms.ModelMultipleChoiceField(
        queryset=Node.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Nodes", False),
    )

    class Meta:
        model = NodeRole
        fields = ("name", "description", "nodes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["nodes"].initial = self.instance.node_set.all()


@admin.register(NodeRole)
class NodeRoleAdmin(admin.ModelAdmin):
    form = NodeRoleAdminForm
    list_display = ("name", "description")

    def save_model(self, request, obj, form, change):
        obj.node_set.set(form.cleaned_data.get("nodes", []))


@admin.register(ContentSample)
class ContentSampleAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "node", "user", "created_at")
    readonly_fields = ("created_at", "name", "user", "image_preview")

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "from-clipboard/",
                self.admin_site.admin_view(self.add_from_clipboard),
                name="nodes_contentsample_from_clipboard",
            ),
            path(
                "capture/",
                self.admin_site.admin_view(self.capture_now),
                name="nodes_contentsample_capture",
            ),
        ]
        return custom + urls

    def add_from_clipboard(self, request):
        try:
            content = pyperclip.paste()
        except PyperclipException as exc:  # pragma: no cover - depends on OS clipboard
            self.message_user(request, f"Clipboard error: {exc}", level=messages.ERROR)
            return redirect("..")
        if not content:
            self.message_user(request, "Clipboard is empty.", level=messages.INFO)
            return redirect("..")
        if ContentSample.objects.filter(content=content, kind=ContentSample.TEXT).exists():
            self.message_user(
                request, "Duplicate sample not created.", level=messages.INFO
            )
            return redirect("..")
        user = request.user if request.user.is_authenticated else None
        ContentSample.objects.create(content=content, user=user, kind=ContentSample.TEXT)
        self.message_user(
            request, "Text sample added from clipboard.", level=messages.SUCCESS
        )
        return redirect("..")

    def capture_now(self, request):
        node = Node.get_local()
        url = request.build_absolute_uri("/")
        try:
            path = capture_screenshot(url)
        except Exception as exc:  # pragma: no cover - depends on selenium setup
            self.message_user(request, str(exc), level=messages.ERROR)
            return redirect("..")
        sample = save_screenshot(path, node=node, method="ADMIN")
        if sample:
            self.message_user(request, f"Screenshot saved to {path}", messages.SUCCESS)
        else:
            self.message_user(
                request, "Duplicate screenshot; not saved", messages.INFO
            )
        return redirect("..")

    @admin.display(description="Screenshot")
    def image_preview(self, obj):
        if not obj or obj.kind != ContentSample.IMAGE or not obj.path:
            return ""
        file_path = Path(obj.path)
        if not file_path.is_absolute():
            file_path = settings.LOG_DIR / file_path
        if not file_path.exists():
            return "File not found"
        with file_path.open("rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        return format_html(
            '<img src="data:image/png;base64,{}" style="max-width:100%;" />',
            encoded,
        )


@admin.register(NetMessage)
class NetMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "body", "reach", "created", "complete")
    search_fields = ("subject", "body")
    list_filter = ("complete", "reach")
    ordering = ("-created",)
    readonly_fields = ("complete",)
    actions = ["send_messages"]

    def send_messages(self, request, queryset):
        for msg in queryset:
            msg.propagate()
        self.message_user(request, f"{queryset.count()} messages sent")

    send_messages.short_description = "Send selected messages"


class NodeTaskForm(forms.ModelForm):
    class Meta:
        model = NodeTask
        fields = "__all__"
        widgets = {"recipe": CodeEditorWidget()}


@admin.register(NodeTask)
class NodeTaskAdmin(admin.ModelAdmin):
    form = NodeTaskForm
    list_display = ("recipe", "role", "created")
    actions = ["execute"]

    def execute(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request, "Please select exactly one task", messages.ERROR
            )
            return
        task_obj = queryset.first()
        if "apply" in request.POST:
            node_ids = request.POST.getlist("nodes")
            nodes_qs = Node.objects.filter(pk__in=node_ids)
            results = []
            for node in nodes_qs:
                try:
                    output = task_obj.run(node)
                except Exception as exc:
                    output = str(exc)
                results.append((node, output))
            context = {"recipe": task_obj.recipe, "results": results}
            return render(request, "admin/nodes/task_result.html", context)
        nodes = Node.objects.all()
        context = {"nodes": nodes, "task_obj": task_obj}
        return render(request, "admin/nodes/nodetask/run.html", context)

    execute.short_description = "Run task on nodes"


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    formfield_overrides = {models.TextField: {"widget": CodeEditorWidget}}
    change_form_template = "admin/nodes/operation/change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<path:object_id>/run/",
                self.admin_site.admin_view(self.run_view),
                name="nodes_operation_run",
            )
        ]
        return custom + urls

    def run_view(self, request, object_id):
        operation = self.get_object(request, object_id)
        if not operation:
            self.message_user(request, "Unknown operation", messages.ERROR)
            return redirect("..")
        context = RUN_CONTEXTS.setdefault(operation.pk, {"inputs": {}})
        template_text = operation.resolve_sigils("template")

        # Interrupt handling
        interrupt_id = request.GET.get("interrupt")
        if interrupt_id:
            try:
                interrupt = operation.outgoing_interrupts.get(pk=interrupt_id)
            except Interrupt.DoesNotExist:
                self.message_user(request, "Unknown interrupt", messages.ERROR)
                return redirect(request.path)
            proc = context.get("process")
            if proc and proc.poll() is None:
                proc.terminate()
                out, err = proc.communicate()
                log = context.get("log")
                if log:
                    log.output = out
                    log.error = err
                    log.interrupted = True
                    log.interrupt = interrupt
                    log.save()
            RUN_CONTEXTS.pop(operation.pk, None)
            return redirect(
                reverse("admin:nodes_operation_run", args=[interrupt.to_operation.pk])
            )

        # Check running processes
        proc = context.get("process")
        thread = context.get("thread")
        if proc and proc.poll() is not None:
            out, err = proc.communicate()
            log = context.pop("log")
            log.output = out
            log.error = err
            log.save()
            RUN_CONTEXTS.pop(operation.pk, None)
            self.message_user(request, "Operation executed", messages.SUCCESS)
            return redirect("..")
        if thread and not thread.is_alive():
            out = context.pop("out")
            err = context.pop("err")
            log = context.pop("log")
            log.output = out.getvalue()
            log.error = err.getvalue()
            log.save()
            RUN_CONTEXTS.pop(operation.pk, None)
            self.message_user(request, "Operation executed", messages.SUCCESS)
            return redirect("..")

        interrupts = [
            (i, i.resolve_sigils("preview"))
            for i in operation.outgoing_interrupts.all().order_by("-priority")
        ]
        logs = Logbook.objects.filter(operation=operation).order_by("created")

        # Waiting for user-provided sigils
        waiting = context.get("waiting_inputs")
        if waiting:
            if request.method == "POST":
                for token in waiting:
                    name = token[1:-1].replace(".", "__")
                    context["inputs"][token] = request.POST.get(name, "")
                command = context.pop("pending_command")
                for token, value in context["inputs"].items():
                    command = command.replace(token, value)
                context["waiting_inputs"] = None
                self._start_operation(context, operation, command, request.user)
                return redirect(request.path)
            form_fields = [(t, t[1:-1].replace(".", "__")) for t in waiting]
            tpl_context = {
                **self.admin_site.each_context(request),
                "operation": operation,
                "interrupts": interrupts,
                "logs": logs,
                "waiting_inputs": form_fields,
                "template": template_text,
            }
            return TemplateResponse(
                request, "admin/nodes/operation/run.html", tpl_context
            )

        # Waiting for user continuation
        if context.get("waiting_continue"):
            if request.method == "POST":
                context["waiting_continue"] = False
                RUN_CONTEXTS.pop(operation.pk, None)
                self.message_user(request, "Operation executed", messages.SUCCESS)
                return redirect("..")
            tpl_context = {
                **self.admin_site.each_context(request),
                "operation": operation,
                "interrupts": interrupts,
                "logs": logs,
                "waiting_continue": True,
                "template": template_text,
            }
            return TemplateResponse(
                request, "admin/nodes/operation/run.html", tpl_context
            )

        # If a process or thread is running, show running state
        if context.get("process") or context.get("thread"):
            tpl_context = {
                **self.admin_site.each_context(request),
                "operation": operation,
                "interrupts": interrupts,
                "logs": logs,
                "running": True,
                "template": template_text,
            }
            return TemplateResponse(
                request, "admin/nodes/operation/run.html", tpl_context
            )

        if request.method == "POST":
            command = operation.resolve_sigils("command")
            for token, value in context["inputs"].items():
                command = command.replace(token, value)
            unresolved = SIGIL_RE.findall(command)
            if unresolved:
                context["waiting_inputs"] = unresolved
                context["pending_command"] = command
                return redirect(request.path)
            if command.strip() == "...":
                log = Logbook.objects.create(
                    operation=operation,
                    user=request.user,
                    input_text=command,
                    output="Waiting for user continuation",
                )
                context["log"] = log
                context["waiting_continue"] = True
                return redirect(request.path)
            self._start_operation(context, operation, command, request.user)
            return redirect(request.path)

        tpl_context = {
            **self.admin_site.each_context(request),
            "operation": operation,
            "interrupts": interrupts,
            "logs": logs,
            "template": template_text,
        }
        return TemplateResponse(request, "admin/nodes/operation/run.html", tpl_context)

    def _start_operation(self, ctx, operation, command, user):
        log = Logbook.objects.create(operation=operation, user=user, input_text=command)
        if operation.is_django:
            out = io.StringIO()
            err = io.StringIO()

            def target():
                try:
                    call_command(*command.split(), stdout=out, stderr=err)
                except Exception as exc:  # pragma: no cover - unexpected errors
                    err.write(str(exc))

            thread = threading.Thread(target=target)
            thread.start()
            ctx.update({"thread": thread, "out": out, "err": err, "log": log})
        else:
            proc = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            ctx.update({"process": proc, "log": log})

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            extra_context["run_url"] = reverse(
                "admin:nodes_operation_run", args=[object_id]
            )
        return super().changeform_view(request, object_id, form_url, extra_context)


admin.site.register(User, CoreUserAdmin)
