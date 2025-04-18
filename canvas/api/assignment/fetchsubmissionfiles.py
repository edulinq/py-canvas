import concurrent.futures
import logging
import os

import requests

import canvas.api.assignment.fetchscores
import canvas.util.file

KEYS = [
    'id',
    'body',
    'submission_type',
    'attachments',
]

SUBMISSION_TYPES = [
    'online_text_entry',
    'online_upload',
]

TEXT_ENTRY_FILENAME = 'contents.html'
MIN_WORKERS = 4

def request(server = None, token = None, course = None, assignment = None, **kwargs):
    submission_infos = canvas.api.assignment.fetchscores.request(server = server, token = token, course = course,
            assignment = assignment, keys = KEYS)

    # {email: [(filename, url), ...], ...}
    file_targets = {}
    # {email: <utf-8 content>}
    file_contents = {}

    for submission_info in submission_infos:
        email = submission_info.get('user', {}).get('email', None)
        if (email is None):
            logging.debug("Skipping submission (%s) from unknown user '%s'." % (str(submission_info.get('id', '???')), submission_info.get('user', {}).get('id')))
            continue

        submission_type = submission_info['submission_type']
        if (submission_type is None):
            # No submission.
            continue

        if (submission_type not in SUBMISSION_TYPES):
            logging.warning("Unknown submission type ('%s') for student '%s'." % (str(submission_type), email))
            continue

        if (submission_type == 'online_text_entry'):
            content = submission_info['body']
            if (content is None):
                content = ''

            file_contents[email] = content
        elif (submission_type == 'online_upload'):
            attachments = submission_info['attachments']
            if (attachments is None):
                continue

            for i in range(len(attachments)):
                attachment = attachments[i]

                filename = attachment.get('display_name', '')
                if ((filename is None) or (filename.strip() == '')):
                    mime = attachment.get('mime_class', '')
                    if (mime is None):
                        mime = ''

                    filename = "%03d.%s" % (i, mime)
                    logging.warning("Could not get filename for attachment at index %d for user %s, using '%s'." % (i, email, filename))

                url = attachment.get('url', '')
                if ((url is None) or (url.strip() == '')):
                    logging.warning("Attachment at index %d for user %s has no URL." % (i, email))
                    continue

                if (email not in file_targets):
                    file_targets[email] = []

                file_targets[email].append((filename, url))
        else:
            raise ValueError("Unknown submission type: '%s'." % (submission_type))

    temp_dir = canvas.util.file.get_temp_path(prefix = 'canvas-submission-files-')

    count = _download_files(temp_dir, file_targets)
    count += _write_files(temp_dir, file_contents)

    return temp_dir, count

def _write_files(temp_dir, file_contents):
    for (email, contents) in file_contents.items():
        try:
            user_dir = os.path.join(temp_dir, email)
            os.makedirs(user_dir, exist_ok = True)

            path = os.path.join(user_dir, TEXT_ENTRY_FILENAME)
            canvas.util.file.write_avoid_collisions(path, contents)
        except Exception as ex:
            logging.error("Failed to write file for student '%s'." % (email), exc_info = ex)

    return len(file_contents)

def _download_files(temp_dir, file_targets):
    num_files = sum([len(targets) for targets in file_targets.values()])
    if (num_files == 0):
        return 0

    count = 0
    max_workers = min(MIN_WORKERS , num_files)
    tasks = []

    for email, targets in file_targets.items():
        user_dir = os.path.join(temp_dir, email)
        os.makedirs(user_dir, exist_ok = True)

        for filename, url in targets:
            tasks.append((email, filename, url, user_dir))

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers = max_workers) as executor:
            results = executor.map(lambda t: download_file(t[0], t[1], t[2], t[3]), tasks)
            count = sum(results)
    except Exception as ex:
        logging.error("Error while downloading files.", exc_info = ex)

    return count

def download_file(email, filename, url, user_dir):
    path = os.path.join(user_dir, filename)

    try:
        logging.debug("Downloading file for student '%s': '%s'." % (email, filename))
        response = requests.get(url, timeout = 10)
        response.raise_for_status()

        with open(path, 'wb') as file:
            file.write(response.content)
        return 1
    except requests.exceptions.HTTPError as ex:
        logging.error("HTTP error while downloading '%s' for student '%s': %s" % (filename, email, str(ex)))
        return 0
