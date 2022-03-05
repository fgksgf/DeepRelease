def has_related_pull_request(commit):
    """
    Checks if the pull request has a related pull request.
    """
    return len(commit.get('associatedPullRequests').get('nodes')) > 0
