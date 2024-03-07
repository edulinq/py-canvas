import logging
import re

import canvas.api.assignment.common
import canvas.api.assignment.list

def fetch_and_resolve_assignments(server, token, course, assignment_queries,
        keys = canvas.api.assignment.common.DEFAULT_KEYS):
    course_assignments = canvas.api.assignment.list.request(server = server, token = token,
            course = course, keys = None)

    assignments = resolve_assignments(assignment_queries, course_assignments)

    if (keys is None):
        return assignments

    return [{key: assignment[key] for key in keys} for assignment in assignments]

def resolve_assignments(assignment_queries, course_assignments, id_field = 'id'):
    """
    Try to match each assignment query to an acutal assignment.
    """

    assignments = []

    for query in assignment_queries:
        id = None
        name = None

        # Clean whitespace.
        query = re.sub(r'\s+', ' ', str(query)).strip()
        if (query == ''):
            continue

        match = re.search(r'^(\S.*)\((\d+)\)$', query)
        if (match is not None):
            name = match.group(1).strip()
            id = match.group(2)
        elif (re.search(r'^\d+$', query) is not None):
            # Query must be an ID.
            id = query
        else:
            # Otherwise, query must be a name.
            name = query

        found_assignments = {}
        for assignment in course_assignments:
            if (id_field not in assignment):
                raise ValueError("Could not find id field '%s' in assignment ('%s')." % (id_field, str(assignment.keys())))
            assignment_id = assignment[id_field]

            if ((id is not None) and (assignment.get('id', '') == id)):
                found_assignments[assignment_id] = assignment

            if (name is not None):
                names = [
                    assignment.get('name', ''),
                ]

                if (name in names):
                    found_assignments[assignment_id] = assignment

        if (len(found_assignments) == 0):
            logging.warning("No assignment found that matches assignment query: '%s'." % (query))
        elif (len(found_assignments) > 1):
            labels = ["%s (%s)" % (str(assignment.get('name', '')), str(assignment.get('id', ''))) for assignment in found_assignments.values()]
            logging.warning("Assignment query ('%s') matches multiple assignments: '%s'." % (query, labels))
        else:
            assignments.append(list(found_assignments.values())[0])

    return assignments

def requires_resolution(assignments):
    """
    Does this list of assignments require resolution?
    I.E., does the list only contain assignment IDs?
    """

    for assignment in assignments:
        if (re.search(r'^\s*\d+\s*$', str(assignment)) is None):
            return True

    return False
