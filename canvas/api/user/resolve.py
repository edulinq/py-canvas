import canvas.api.user.common
import canvas.api.user.list
import canvas.api.resolve

def fetch_and_resolve_users(server, token, course, user_queries,
        keys = canvas.api.user.common.DEFAULT_KEYS, include_role = False,
        fill_missing = False):
    return canvas.api.resolve.fetch_and_resolve(server, token, course, user_queries,
            canvas.api.user.list.request, {'include_role': include_role},
            keys = keys, resolve_kwargs = {'fill_missing': fill_missing})

def requires_resolution(users):
    return canvas.api.resolve.requires_resolution(users)
