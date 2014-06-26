# Pipeline Authenticator
Two step client authentication class for OAuth login with the GitHub API
against an application API.

Makes use of the excellent libraries:

- [requests](https://github.com/kennethreitz/requests) by Kenneth Reitz
- [github3](https://github.com/sigmavirus24/github3.py) by Ian Cordasco

Installation:
```bash
$ virtualenv/bin/pip install "git+ssh://git@github.com/allclasses/pipeline_auth.git@master#egg=pipeline_auth"
```

### Example Use

```python
>>> from pipeline_auth import PipelineAuthenticator
>>> pa = PipelineAuthenticator(
...     token_dir="/tmp/tokens/",
...     host="http://localhost:5000"
... )
>>> token = pa.get_token()
Github username: gthole
Password:
>>> requests.get("http://localhost:5000", headers={"authorization": token})
```


### Example Application API

The application API that is being queried against is expected to have an
endpoint that accepts a valid Github application token, and returns an
application token for itself.  Using flask and itsdangerous:

```python
from flask import Flask, request, abort
from itsdangerous import Signer
import github3

app = Flask(__name__)
signer = Signer('secret-key')

@app.route('/api/auth', methods=["POST"])
def auth_token():
    try:
        gh_token = request.args.get("authorization")
        assert gh_token, "Authorization heading required"

        # Login to Github with token
        gh = github3.login(token=data["github_token"])
        assert gh is not None, "Token login unsuccessful"

        # Validate the github identity however you please, using
        user = gh.user().login

    except AssertionError as e:
        return jsonify({"error": str(e)}), 401

    return json.dumps({"token": signer.sign(user), "user": user}), 202


if __name__ == '__main__':
    app.run()
```
