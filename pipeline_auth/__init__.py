import os
import getpass

import requests
import github3


class PipelineAuthenticator(object):
    """
    Multi-step authentication mechanism via GitHub and an external API:
        1. Client performs user/pass authentication with GitHub API,
           receives application token and stores for later use.
        2. Client posts GitHub token to <host>/api/auth and receives
           token from <host>, stores for all subsequent queries to <host>.

    This allows <host> to validate OAuth login with GitHub and confirm public
    organizations, repos, or user emails to establish identity without having
    to store usernames or passwords itself.  After one-time validation, a
    signed token key is all that is needed for future <host> authentication.
    """

    def __init__(self, host, token_dir, auth_uri=None, note=None, scopes=None):
        self.host = host

        # Make sure token folder exists
        if not os.path.isdir(token_dir):
            os.makedirs(token_dir)

        self.gh_token = os.path.join(token_dir, "gh_token")
        self.app_token = os.path.join(token_dir, "app_token")

        # Defaults
        self.note = note or "pipeline authenticator app"
        self.auth_uri = auth_uri or "/api/auth"
        self.gh_scopes = scopes or ['user']

    def get_github_token(self):
        """
        Log in to the GitHub API, store the auth token for later use
        """
        # Read in existing auth token if exists
        if os.path.isfile(self.gh_token):
            with open(self.gh_token, 'r') as f:
                return f.readline().strip()

        # Get authentication
        username = raw_input("Github username: ")
        password = getpass.getpass("Password: ")

        # Request authorization token from Github
        auth = github3.authorize(
            username,
            password,
            self.scopes,
            self.note,
            self.host
        )

        assert auth is not None, "Github login failed.  " \
            "Please check your credentials."

        # Store auth token for later
        succ("Successfully logged into Github.  Stored auth token in\n"
             "%s for later use." % self.gh_token)
        with open(self.gh_token, 'w') as f:
            f.write("%s\n%s" % (auth.token, auth.id))
        return auth.token

    def reset_tokens(self):
        """
        Deletes stored tokens
        """
        if os.path.isfile(self.gh_token):
            os.remove(self.gh_token)
        if os.path.isfile(self.app_token):
            os.remove(self.app_token)
        warn("Make sure to delete the pipeline token in Github at:\n"
             "https://github.com/settings/emails")
        succ("Tokens removed")

    def get_token(self):
        """
        Send Github auth token to the Pipeline API to get an AC token
        """
        if os.path.isfile(self.app_token):
            with open(self.app_token, 'r') as f:
                return f.readline().strip()

        # Get Github auth token
        token = self.get_github_token()

        # Request authorization token from host application
        resp = requests.post(
            "%s/api/auth" % self.host,
            headers={
                "authorization": token,
                "accept": "application/json"
            },
        )
        if resp.status_code not in [200, 202]:
            return fail(resp.text)
        token = resp.json()["token"]

        # Store auth token for later
        succ("Successfully logged into %s.  Stored auth token in\n"
             "%s\n for later use." % (self.host, self.app_token))
        with open(self.app_token, 'w') as f:
            f.write("%s\n" % token)
        return token


# Color terminal printing
def fail(msg):
    print "\033[91m%s\033[0m" % msg


def warn(msg):
    print "\033[93m%s\033[0m" % msg


def succ(msg):
    print "\033[92m%s\033[0m" % msg
