# Tagger bot

This bot emulates slack user groups (@backend, @frontend, @own_name) in public or private channels.

It can be used in workspaces that are at a free plan (free plan not include user groups)

![Image build status](https://img.shields.io/docker/cloud/build/heavyrainx/tagger-bot.svg)

## Requirements

1. Python 3.6+
2. python-rtmbot (version 0.4.0)
3. Slack workspace

## Installation guide

### Slack part
1. Create application in slack. https://api.slack.com/apps?new_app=1
2. Go to `Bot Users` and add a new bot.
3. Go to `OAuth & Permissions` and click on `Install App to Workspace`
4. Authorize installation
5. Copy token from `Bot User OAuth Access Token` (starts with `xoxb`)

### Docker installation
1. Pull image `docker pull heavyrainx/tagger-bot`
2. Run `docker run -e "SLACK_TOKEN=TOKEN_HERE" -e "BOT_DEFAULT_USERNAME=USERNAME_HERE" -v /var/tagger-bot/:/usr/src/app/data heavyrainx/tagger-bot` (`/var/tagger-bot` can be changed to another host path)

### Manual installation
1. Clone this repository
2. Install requirements (`pip install -r requirements.txt`)
3. Run `python run.py --slack_token SLACK_TOKEN_HERE --bot_default_username=BOT_USERNAME_HERE`

## After installation
1. Invite bot in any channel or group (`/invite @BOT_USERNAME`) where BOT_USERNAME is `bot_default_username` variable
2. Enjoy!