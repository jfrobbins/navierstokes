"""
RSSTools.py
Author: Stephen J. Sekula
Created: Aug. 18, 2014

* RSSHandler:
Inherits from: SocialHandler
Purpose: to gather messages from an RSS Feed for writing to other places.
The write() function does nothing.)
"""

from SocialHandler import *
from requests.exceptions import ConnectionError

from MessageObj import Message

import sys
import os
import inspect
import unicodedata
import datetime
import calendar
import codecs
import feedparser
from bs4 import BeautifulSoup


class RSSHandler(SocialHandler):
    
    def __init__(self,feed_url=""):
        SocialHandler.__init__(self)

        # the feed URL
        self.feed_url = feed_url
        self.prepend  = ""
        
            
        pass


    def gather(self):
        """ Gather messages from the RSS feed """

        self.messages = []

        self.msg(0, self.texthandler("Gathering messages.") )

        rss_content = feedparser.parse(self.texthandler(self.feed_url))
        
        for entry in rss_content.entries:
            msg = Message()

            msg.source = self.texthandler("RSS")

            msg.public = True
            msg.reply  = False
            msg.direct = False

            try:
                msg.id     = self.generate_id(entry.link)
            except AttributeError:
                continue

            try:
                msg.date = calendar.timegm(entry.updated_parsed)
            except TypeError:
                continue

            #msg.content = self.texthandler("<p>Shared from RSS:</p>\n")
            msg.content = self.texthandler(self.prepend)
            try:

                msg.content += self.texthandler("<p><b>\"%s\"</b></p>\n" % entry.title)
                msg.title   =  self.texthandler(entry.title)
            except AttributeError:
                pass
            
            try:
                msg.content += self.texthandler("<p>%s</p>\n" % entry.summary )
            except AttributeError:
                try:
                    msg.content += self.texthandler("<p>%s ... </p>\n" % entry.content[:500])
                except AttributeError:
                    pass
            
            try:
                msg.content += self.texthandler("<p><a href=\"%s\">%s</a></p>\n" % (entry.link,entry.link))
            except AttributeError:
                pass
            
            try:
                msg.content += self.texthandler("( Feed URL: <a href=\"%s\">%s</a> )" % (self.feed_url,self.feed_url))
            except AttributeError:
                pass


            # Cleanup HTML from content.
            msg_text = BeautifulSoup(msg.content, "html.parser").get_text()
            #msg_text = msg_text.replace('\n','\n\n')
            msg.content = msg_text

            
            msg.link = entry.link
            try:
                msg.author = self.texthandler(entry.author)
            except AttributeError:
                msg.author = self.texthandler("Unknown Author")

            try:
                msg.title = self.texthandler(entry.title)
            except AttributeError:
                msg.title = self.texthandler(msg.content[:60])+self.texthandler("...")
                pass

            # make an effort to get the featured image, if there is one
            try:
                content = entry.content[0]['value']
                soup = BeautifulSoup(content, "lxml")
                for img in soup.findAll('img', limit=1):
                    filename = img['src'].split('/')[-1]
                    os.system('curl --connect-timeout 60 -m 120 -s -o /tmp/%s %s' % ( filename, img['src'] ))
                    msg.attachments.append( '/tmp/%s' % (filename) )
            except:
                pass

            self.messages.append(msg)
            


        self.messages = sorted(self.messages, key=lambda msg: msg.date, reverse=False)

        if self.debug:
            print self.texthandler("********************** RSS Handler **********************\n")
            print self.texthandler("Here are the messages I gathered from the RSS feed:\n")
            for message in self.messages:
                print message.Printable()
                pass
            
        return self.messages


    def write(self, messages = []):
        self.msg(0, "RSS cannot be written to - this is normal.")
        return []
