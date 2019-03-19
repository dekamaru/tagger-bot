from __future__ import print_function
from rtmbot.core import Plugin
import json
import os.path
import sys

class Tagger(Plugin):

    def __init__(self, name=None, slack_client=None, plugin_config=None):
        super().__init__(name, slack_client, plugin_config)
        self.BOT_NAME = plugin_config['BOT_DEFAULT_USERNAME']
        self.bot_id = self.resolveBotId()
        if self.bot_id is None:
            print('Cant find bot id with bot default username "'+ self.BOT_NAME +'"')
            sys.exit(3)
        self.groups = {}
        self.loadState()

    def process_message(self, data):
        if self.isBotInvitedToChannel(data):
            self.sendWelcomeMessage(data)
            return

        if self.isBotMentioned(self.getMessageText(data)):
            self.handleBotCommands(data)
            return

        knownTags = self.getMentionedKnownTags(self.getMessageText(data))
        if len(knownTags) > 0:
            self.sendTagNotifyMessage(knownTags, data)

    def sendTagNotifyMessage(self, tags, data):
        participants = []
        for tag in tags:
             if self.isTagExistsInChannel(tag, data['channel']):
                 participants += self.getParticipantsByTagAndChannel(tag, data['channel'])

        participants = list(set(participants))
        message = '^^^\n' + ', '.join(participants)
        if self.isMessageInThread(data):
            self.slack_client.api_call("chat.postMessage", channel=data['channel'], text=message, thread_ts=data['thread_ts'])
        else:
            self.outputs.append([data['channel'], message])

    def handleBotCommands(self, data):
        parts = self.removeEmptyParts(self.getMessageText(data).split(' '))
        if len(parts) < 1:
            return

        command = parts[1]
        if command == 'register' and len(parts) > 4:
            tag = parts[2]
            participants = parts[4:]
            self.outputs.append([data['channel'], self.register(tag, participants, data['channel'])])

        if command == 'unregister' and len(parts) == 3:
            tag = parts[2]
            self.outputs.append([data['channel'], self.unregister(tag, data['channel'])])

        if (command == 'add' or command == 'remove') and len(parts) > 3:
            tag = parts[2]
            participants = parts[3:]
            if command == 'add':
                self.outputs.append([data['channel'], self.addParticipantsToTag(data['channel'], tag, participants)])
            else:
                self.outputs.append([data['channel'], self.removeParticipantsFromTag(data['channel'], tag, participants)])

        if command == 'list':
            self.outputs.append([data['channel'], self.listTagsInChannel(data['channel'])])

        if command == 'help':
            self.sendHelpMessage(data)

    def addParticipantsToTag(self, channel, tag, participants):
        if not self.isTagExistsInChannel(tag, channel):
            return 'Tag ' + tag +  ' not found in this channel.'

        correctParticipants = []
        for participant in participants:
            if self.isUserMention(participant):
                correctParticipants.append(participant)

        if len(correctParticipants) == 0:
            return 'Participants list length is 0. You must mention user with @'

        self.addTagToChannel(tag, correctParticipants, channel)
        return 'Tag ' + tag + ' members updated.'

    def removeParticipantsFromTag(self, channel, tag, participants):
        if not self.isTagExistsInChannel(tag, channel):
            return 'Tag ' + tag +  ' not found in this channel.'

        newParticipants = []
        currentParticipants = self.getParticipantsByTagAndChannel(tag, channel)
        for participant in currentParticipants:
            if participant not in participants:
                newParticipants.append(participant)
        
        if len(newParticipants) == 0:
            return self.unregister(tag, channel)

        self.groups[tag][channel] = list(set(newParticipants))
        self.saveState()
        return 'Tag ' + tag + ' members updated.'

    def unregister(self, tag, channel):
        if not self.isTagExistsInChannel(tag, channel):
            return 'Tag ' + tag + ' not found'

        self.removeTagFromChannel(tag, channel)
        return 'Tag ' + tag + ' unregistered'


    def register(self, tag, participants, channel):
        if self.isTagExistsInChannel(tag, channel):
            return 'Tag ' + tag +  ' already registered.'

        if not self.isTagValid(tag):
            return 'Tag ' + tag + ' has a invalid name. Allowed non-empty, started with @ tags (not mentions!)'

        correctParticipants = []
        for participant in participants:
            if self.isUserMention(participant):
                correctParticipants.append(participant)

        if len(correctParticipants) == 0:
            return 'Participants list length is 0. You must mention user with @'

        self.addTagToChannel(tag, correctParticipants, channel)
        return 'Tag ' + tag + ' registered.'

    def listTagsInChannel(self, channelId):
        members = self.slack_client.api_call("users.list")['members']
        message = 'List of tags in this channel:\n'
        count = 0
        for tag, _ in self.groups.items():
            for groupChannelId, participants in self.groups[tag].items():
                if groupChannelId == channelId:
                    message += ':black_small_square:*' + tag + ':* ' + ', '.join(self.transformIdsToUsernames(members, participants)) + '\n'
                    count += 1

        if count == 0:
            return 'No registered tags found in this channel'

        return message

    def transformIdsToUsernames(self, members, participants):
        usernames = []
        for participant in participants:
            for member in members:
                if member['id'] == participant.lstrip("<@").rstrip(">"):
                    if member['profile']['display_name'] != '':
                        memberName = member['profile']['display_name']
                    else:
                        memberName = member['real_name']
                    usernames.append('@'+memberName)
        return usernames

    def getMentionedKnownTags(self, text):
        tags = []
        for key, _ in self.groups.items():
            if key in text:
                tags.append(key)
        return tags

    def getParticipantsByTagAndChannel(self, tag, channel):
        return self.groups[tag][channel]

    def addTagToChannel(self, tag, participants, channel):
        if not self.isTagExists(tag):
            self.groups[tag] = {}

        if not self.isTagExistsInChannel(tag, channel):
            self.groups[tag][channel] = []

        for participant in participants:
            self.groups[tag][channel].append(participant)

        self.groups[tag][channel] = list(set(self.groups[tag][channel]))
        self.saveState()

    def removeTagFromChannel(self, tag, channel):
        del self.groups[tag][channel]
        self.saveState()

    def isTagExistsInChannel(self, tag, channel):
        return self.isTagExists(tag) and channel in self.groups[tag]

    def isTagExists(self, tag):
        return tag in self.groups

    def isTagValid(self, tag):
        return tag.startswith('@') and tag.strip() != '' and len(tag) > 1

    def isUserMention(self, str):
        return str.startswith('<@U') and str.endswith('>')

    def isBotMentioned(self, text):
        return text.startswith('<@'+ self.bot_id +'>')

    def isBotInvitedToChannel(self, data):
        return 'subtype' in data and (data['subtype'] == 'channel_join' or data['subtype'] == 'group_join') and data['user'] == self.bot_id
    

    def isMessageInThread(self, data):
        return 'thread_ts' in data and 'bot_id' not in data

    def removeEmptyParts(self, parts):
        newParts = []
        for part in parts:
            if part.strip() != '':
                newParts.append(part)
        return newParts

    def resolveBotId(self):
        for member in self.slack_client.api_call("users.list")['members']:
            if member['name'] == self.BOT_NAME:
                return member['id']
        return None

    def getMessageText(self, data):
        if 'text' in data:
            return data['text']
        
        return ''

    def sendWelcomeMessage(self, data):
        message = 'Howdy ho! I am a bot that emulates Slack user groups\n'
        message += self.getHelpText()
        message += '\n\nWritten with :heart: by @dbezmelnitsyn for 4xxi team'
        self.outputs.append([data['channel'], message])

    def sendHelpMessage(self, data):
        self.outputs.append([data['channel'], self.getHelpText()])
    
    def getHelpText(self):
        commands = [
            ['Register a new tag', 'register @TAG_NAME with @user1 @user2 @userN'],
            ['Unregister existing tag', 'unregister @TAG_NAME'],
            ['Add members to existing tag', 'add @TAG_NAME @user1 @user2 @userN'],
            ['Remove members from existing tag', 'remove @TAG_NAME @user1 @user2 @userN'],
            ['List tags of current channel', 'list'],
            ['Show commands list', 'help']
        ]

        message = 'That\'s what i can do:\n'
        commandIndex = 1
        for command in commands:
            message += str(commandIndex) + '. ' + command[0] + '\n'
            message += '    `@' + self.BOT_NAME + ' ' + command[1] + '`\n'
            commandIndex += 1
        return message

    def loadState(self):
        if os.path.isfile('data/data.db'):
            with open('data/data.db', 'r') as db:
                self.groups = json.loads(db.read())
        
    def saveState(self):
        with open('data/data.db', 'w') as db:
            db.write(json.dumps(self.groups))
    
