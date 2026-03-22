# Kicktipp Predictor
- Will predict based on the odds in the bet overview
- Will adjust the bias according to the points for home, away and draw bets depending on the game mode

- After getting your cookie token using --get-login-token, add it to .env as KICKTIPP_TOKEN="<YOUR_TOKEN>" and use it with --use-login-token $KICKTIPP_TOKEN or just run `run.sh`

In newer Linux, use your VENV with the required modules in requirements.txt
or
```python
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
```
```sh
pip install robobrowser
pip install html5lib
```
