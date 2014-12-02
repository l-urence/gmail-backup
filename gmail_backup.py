#!/usr/bin/env python

from gmail_func import GetMessage, GetGoogleService, ListMessagesWithLabels
from email.generator import Generator
from slugify import slugify
import os
import progressbar

def getFilename(filename, apendix=0):
    if apendix > 0:
        tmp_filename = ('%s_%i.eml' % (filename, apendix))
    else:
        tmp_filename = ('%s.eml' % filename)

    if os.path.isfile(tmp_filename):
        return getFilename(filename, apendix=apendix+1)

    return tmp_filename

def saveToFile(filename, msg):
    directory = './emails'
    filename = getFilename('%s/%s' % (directory, filename))

    with open(filename, 'w') as outfile:
        generator = Generator(outfile)
        generator.flatten(msg)

def doBackup():
    gmail_service = GetGoogleService()
    mail_list = ListMessagesWithLabels(gmail_service, 'me', ['Label_4'])
    bar = progressbar.ProgressBar(maxval=len(mail_list),
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

    print 'Start import %i mails' % len(mail_list)

    for i, m in enumerate(mail_list):
        msg = GetMessage(gmail_service, 'me', m['id'])
        filename = slugify(msg['Subject'])
        saveToFile(filename, msg)
        bar.update(i)

    bar.finish()

if __name__ == '__main__':
    doBackup()
