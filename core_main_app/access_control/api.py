""" Set of functions to define the common rules for access control across collections
"""
import logging

from core_main_app.access_control.exceptions import AccessControlError
from core_main_app.components.workspace import api as workspace_api
from core_main_app.permissions import api as permissions_api, rights as rights
from core_main_app.settings import CAN_SET_PUBLIC_DATA_TO_PRIVATE

logger = logging.getLogger(__name__)


def has_perm_publish(user, codename):
    """ Does the user have the permission to publish.

    Args:
        user
        codename

    Returns
    """
    publish_perm = permissions_api.get_by_codename(codename)
    if not user.has_perm(publish_perm.content_type.app_label + '.' + publish_perm.codename):
        raise AccessControlError("The user doesn't have enough rights to publish.")


def has_perm_administration(func, *args, **kwargs):
    """ Is the given user has administration rights.

        Args:
            func:
            *args:
            **kwargs:

        Returns:

        """
    try:
        if args[0].is_superuser:
            return func(*args, **kwargs)
    except Exception as e:
        logger.warning("has_perm_administration threw an exception: ".format(str(e)))

    raise AccessControlError("The user doesn't have enough rights.")


def check_can_write(document, user):
    """ Check that the user can write.

    Args:
        document:
        user:

    Returns:

    """
    if document.user_id != str(user.id):
        if hasattr(document, 'workspace') and document.workspace is not None:
            # get list of accessible workspaces
            accessible_workspaces = workspace_api.get_all_workspaces_with_write_access_by_user(user)
            # check that accessed document belongs to an accessible workspace
            if document.workspace not in accessible_workspaces:
                raise AccessControlError("The user doesn't have enough rights.")
        # workspace is not set
        else:
            raise AccessControlError("The user doesn't have enough rights.")


def check_can_read_list(document_list, user):
    """ Check that the user can read each document of the list.

    Args:
        document_list:
        user:

    Returns:

    """
    if len(document_list) > 0:
        # get list of accessible workspaces
        accessible_workspaces = workspace_api.get_all_workspaces_with_read_access_by_user(user)
        # check access is correct
        for document in document_list:
            # user is document owner
            if document.user_id == str(user.id):
                continue
            # user is not owner or document not in accessible workspace
            if document.workspace is None or document.workspace not in accessible_workspaces:
                raise AccessControlError("The user doesn't have enough rights.")


def can_write_document_in_workspace(func, document, workspace, user):
    """ Can user write data in workspace.

    Args:
        func:
        document:
        workspace:
        user:

    Returns:

    """
    return can_write_in_workspace(func, document, workspace, user, rights.publish_data)


def can_read_or_write_in_workspace(func, workspace, user):
    """ Can user read or write in workspace.

    Args:
        func:
        workspace:
        user:

    Returns:

    """
    if user.is_superuser:
        return func(workspace, user)

    _check_can_read_or_write_in_workspace(workspace, user)
    return func(workspace, user)


def can_write_in_workspace(func, document, workspace, user, codename):
    """ Can user write in workspace.

    Args:
        func:
        document:
        workspace:
        user:
        codename:

    Returns:

    """
    if user.is_superuser:
        return func(document, workspace, user)
    if workspace is not None:
            if workspace_api.is_workspace_public(workspace):
                has_perm_publish(user, codename)
            else:
                _check_can_write_in_workspace(workspace, user)

    check_can_write(document, user)

    # if we can not unpublish
    if CAN_SET_PUBLIC_DATA_TO_PRIVATE is False:
        # if document is in public workspace
        if document.workspace is not None and workspace_api.is_workspace_public(document.workspace):
            # if target workspace is private
            if workspace is None or workspace_api.is_workspace_public(workspace) is False:
                raise AccessControlError("The document can not be unpublished.")

    return func(document, workspace, user)


def can_read(func, user):
    """ Can a user read

    Args:
        func:
        user:

    Returns:

    """
    if user.is_superuser:
        return func(user)

    # get list of document
    document_list = func(user)
    # check that the user can access the list of document
    check_can_read_list(document_list, user)
    # return list of document
    return document_list


def can_read_id(func, document_id, user):
    """ Can read from object id.

    Args:
        func:
        document_id:
        user:

    Returns:

    """
    if user.is_superuser:
        return func(document_id, user)

    document = func(document_id, user)
    _check_can_read(document, user)
    return document


def can_write(func, document, user):
    """ Can user write

    Args:
        func:
        document:
        user:

    Returns:

    """
    if user.is_superuser:
        return func(document, user)

    check_can_write(document, user)
    return func(document, user)


def _check_can_write_in_workspace(workspace, user):
    """ Check that user can write in the workspace.

    Args:
        workspace:
        user:

    Returns:

    """
    accessible_workspaces = workspace_api.get_all_workspaces_with_write_access_by_user(user)
    if workspace not in accessible_workspaces:
        raise AccessControlError("The user does not have the permission to write into this workspace.")


def _check_can_read_or_write_in_workspace(workspace, user):
    """ Check that user can read or write in the workspace.

    Args:
        workspace:
        user:

    Returns:

    """
    accessible_write_workspaces = workspace_api.get_all_workspaces_with_write_access_by_user(user)
    accessible_read_workspaces = workspace_api.get_all_workspaces_with_read_access_by_user(user)
    if workspace not in list(accessible_write_workspaces) + list(accessible_read_workspaces):
        raise AccessControlError("The user does not have the permission to write into this workspace.")


def _check_can_read(document, user):
    """ Check that the user can read.

    Args:
        document:
        user:

    Returns:

    """
    # workspace case
    if document.user_id != str(user.id):
        # workspace is set
        if hasattr(document, 'workspace') and document.workspace is not None:
            # get list of accessible workspaces
            accessible_workspaces = workspace_api.get_all_workspaces_with_read_access_by_user(user)
            # check that accessed document belongs to an accessible workspace
            if document.workspace not in accessible_workspaces:
                raise AccessControlError("The user doesn't have enough rights to access this.")
        # workspace is not set
        else:
            raise AccessControlError("The user doesn't have enough rights to access this.")