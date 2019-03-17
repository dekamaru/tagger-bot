# Tagger bot

This bot emulates slack user groups (@backend, @frontend, @own_name) in public or private channels.

It can be used in workspaces that are at a free plan (free plan not include user groups)

## Requirements

1. Python 3.6+
2. python-rtmbot (version 0.4.0)
3. Slack workspace

## Installation guide

### Slack part
1. Create application in slack. https://api.slack.com/apps?new_app=1
2. Go to `Bot Users` and add a new bot with default username `tagger`. (if you need another username, you should change `self.BOT_NAME` in `plugins/tagger.py`)
3. Go to `OAuth & Permissions` and click on `Install App to Workspace`
4. Authorize installation
5. Copy token from `Bot User OAuth Access Token` (starts with `xoxb`)

### Manual installation
1. Clone this repository
2. Install requirements (`pip install -r requirements.txt`)
3. Run `python run.py --slack_token SLACK_TOKEN_HERE`
4. Invite bot in any channel or group (`/invite @tagger`)
5. Enjoy!