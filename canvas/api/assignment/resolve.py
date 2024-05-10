import canvas.api.assignment.common
import canvas.api.assignment.list
import canvas.api.resolve

def fetch_and_resolve_assignments(server, token, course, assignment_queries,
        keys = canvas.api.assignment.common.DEFAULT_KEYS):
    return canvas.api.resolve.fetch_and_resolve(server, token, course, assignment_queries,
            canvas.api.assignment.list.request,
            keys = keys, resolve_kwargs = {'match_email': False, 'label_uses_email': False})

def requires_resolution(assignments):
    return canvas.api.resolve.requires_resolution(assignments)
