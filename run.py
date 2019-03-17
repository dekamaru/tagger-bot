#!/usr/bin/env python
from argparse import ArgumentParser
import sys
import os

from rtmbot import RtmBot

sys.path.append(os.getcwd())

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '--debug',
        help='Debug mode',
        action='store_true',
        default=False
    )
    parser.add_argument(
        '--slack_token',
        help='Bot User OAuth Access Token'
    )
    parser.add_argument(
        '--log_path',
        help='Store logs path',
        metavar='path'
    )

    return parser.parse_args()


def main(args=None):
    # load args with config path if not specified
    if not args:
        args = parse_args()

    if os.environ.get('DEBUG'):
        DEBUG_MODE = str2bool(os.environ.get('DEBUG'))
    else:
        DEBUG_MODE = args.debug

    config = {
        'DEBUG': DEBUG_MODE,
        'SLACK_TOKEN': os.environ.get('SLACK_TOKEN') or args.slack_token,
        'LOGFILE': os.environ.get('LOG_PATH') or args.log_path,
        'ACTIVE_PLUGINS': [
            'plugins.tagger.Tagger'
        ]
    }

    if config['SLACK_TOKEN'] is None:
        print('SLACK_TOKEN is not set! Define it in environment variable or provide as run argument --slack_token=YOUR_SLACK_TOKEN')
        sys.exit(1)

    bot = RtmBot(config)
    try:
        bot.start()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()