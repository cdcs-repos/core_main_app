"""Mailing task
"""
from __future__ import absolute_import
from logging import getLogger
from core_main_app.utils.tasks_managers.celery import app
import os
from django.utils.importlib import import_module
from django.template import loader, Context
from django.core.mail import send_mail as django_send_mail, mail_admins, mail_managers, BadHeaderError


logger = getLogger(__name__)
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
SERVER_EMAIL = settings.SERVER_EMAIL
EMAIL_SUBJECT_PREFIX = settings.EMAIL_SUBJECT_PREFIX


@app.task
def send_mail(recipient_list, subject, path_to_template, context={}, fail_silently=True, sender=SERVER_EMAIL):
    """Send email.

    Args:
        recipient_list:
        subject:
        path_to_template:
        context:
        fail_silently:
        sender:

    Returns:

    """
    try:
        # Render the given template with context information
        template = loader.get_template(path_to_template)
        context = Context(context)
        message = template.render(context)
        # Send mail
        django_send_mail(subject=EMAIL_SUBJECT_PREFIX+subject, message='', from_email=sender, recipient_list=recipient_list,
                         html_message=message, fail_silently=fail_silently)
    except BadHeaderError, e:
        raise e
    except Exception, e:
        raise e


@app.task
def send_mail_to_administrators(subject, path_to_template, context={}, fail_silently=True):
    """Send email to administrators.

    Args:
        subject:
        path_to_template:
        context:
        fail_silently:

    Returns:

    """
    try:
        # Render the given template with context information
        template = loader.get_template(path_to_template)
        context = Context(context)
        message = template.render(context)
        # Send mail
        mail_admins(subject=subject, message='', html_message=message, fail_silently=fail_silently)
    except BadHeaderError:
        pass
    except Exception:
        pass


@app.task
def send_mail_to_managers(subject, path_to_template, context={}, fail_silently=True):
    """Send email to managers.

    Args:
        subject:
        path_to_template:
        context:
        fail_silently:

    Returns:

    """
    try:
        # Render the given template with context information
        template = loader.get_template(path_to_template)
        context = Context(context)
        message = template.render(context)
        # Send mail
        mail_managers(subject=subject, message='', html_message=message, fail_silently=fail_silently)
    except BadHeaderError:
        pass
    except Exception:
        pass

