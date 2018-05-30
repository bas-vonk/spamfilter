import re
import logging


def extract_email_features(email):
    """
    Extract features from an email and return them in a dictionary. These
    features can be extended, and are ultimately used to train ML models.
    """

    features = {}

    # Extract both the body and the metadata
    # ASSUMPTION: metadata and body are separated by a blank line
    try:
        metadata, body = re.split(r"\n\s*\n",
                                  email,
                                  1
                                  )
    except ValueError:
        logging.warning("Could not split email: %s", email)
        return False

    # Extract the subject
    # ASSUMPTION: the subject is identified by Subject: * or subject: *
    regex_result = re.search('[S|s]ubject: (.*)', metadata)
    if regex_result is not None:
        subject = regex_result.group(1)
    else:
        subject = ''

    # Extract the wordcount
    # Split the body on spaces and count the amount of resulting items
    # TODO: strip html tags to get a more accurate value
    wordcount = len(body.split())

    # Return the features in a dictionary
    return {
        "metadata": metadata,
        "subject": subject,
        "body": body,
        "wordcount": wordcount
    }
