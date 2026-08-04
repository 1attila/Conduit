from mconduit.perms.resolver import HierarchicalPermissionResolver
from mconduit.perms.perm import Permission
from mconduit.perms.item import perm_item

from mconduit.text import text


guest = perm_item("guest", text.gray("guest"))


class Builtin(Permission):
    """
    Permission system used for builtin plugin.

    Priviledge schema:

    • `GUEST`: help and infos

    • `HELPER`: plugin manipulation

    • `ADMIN`: permission manipulation
    """

    GUEST  = guest
    USER   = perm_item("user", text.yellow("user"))
    HELPER = perm_item("helper", text.aqua("helper"))
    ADMIN  = perm_item("admin", text.dark_aqua("admin"))
    OWNER  = perm_item("owner", text.blue("owner"))

    RESOLVER = HierarchicalPermissionResolver
    DEFAULT = guest