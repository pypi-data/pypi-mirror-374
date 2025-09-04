"""
API resources for Evolution API.
"""

from .chat import ChatResource
from .group import GroupResource
from .instance import InstanceResource
from .message import MessageResource
from .profile import ProfileResource
from .webhook import WebhookResource

__all__ = [
    "InstanceResource",
    "MessageResource",
    "ChatResource",
    "GroupResource",
    "ProfileResource",
    "WebhookResource",
]
