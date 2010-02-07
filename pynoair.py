#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pynoair - a modular script displaying what's on Nolife TV channel
#
# Copyright (C) 2009 by Damien Leone <damien.leone@fensalir.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA.

import os
import re
import sys
import time
import string
import urllib
import datetime
import xml.parsers.expat

VERSION="0.9.4"
COLOURS= { 'yellow': "\033[1;33m",
           'pink'  : "\033[1;35m",
           'blue'  : "\033[0;34m",
           'red'   : "\033[0;31m",
           'purple': "\033[0;35m",
           'green' : "\033[0;32m",
           'white' : "\033[0m" }

class PyNoAir(object):
    def __init__(self, base_config = "~/.pynoair/"):
        # Attributes and their default values
        self.__xml_url         = "http://www.nolife-tv.com/noair/noair.xml"
        self.__xml_file        = os.path.expanduser(base_config + "noair.xml")
        self.__output_format   = "[%y] %D : %d"
        self.__date_format     = "%H:%M"
        self.__extra_format    = "\n\tElapsed %e/%d [%p%]"
        self.__outdated_format = "<XML file is outdated>"
        self.__display_extra   = True
        self.__nb_past_display = 1
        self.__nb_next_display = 2
        self.__verbose         = False
        self.__updated         = False
        self.__colours         = False
        self.__download_delay  = 15
        self.__leveltypes      = "80, 90, 100"
        self.__data            = []
        self.__date_pattern    = re.compile("(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})")
        self.__now             = None
        self.__on_air          = None

        # Default values for missing fields in XML file
        self.__default_url = ""
        self.__default_screenshot = ""

        base = os.path.dirname(self.__xml_file)
        if not os.path.exists(base):
            self.verbose("Creating directory %s" % base)
            try:
                os.makedirs(base)
            except OSError, e:
                error(e)

        self.load_config_file(os.path.expanduser(base_config + "config"))
        self.set_current_time()

    def load_config_file(self, path):
        """
        Read configuration file and extract options
        """
        try:
            fd = open(path, 'r')
        except IOError:
            self.verbose("Configuration file not found: %s" % path)
            return

        conf = {}
        lines = fd.readlines()
        pattern = re.compile("(\S+)\s+=\s+(.+)")
        for l in lines:
            if l[0] == '#':
                continue

            r = re.match(pattern, l)

            try:
                conf[r.group(1)] = r.group(2)
            except AttributeError:
                continue
            except IndexError:
                continue

        fd.close()
        self.set_config(conf)

    def set_config(self, conf):
        """
        Override default options from a dictionary
        """
        for k in conf.keys():
            val = conf[k]
            if val == None:
                continue
            elif k == "xml_url":
                self.__xml_url = val
            elif k == "output_format":
                self.__output_format = val
            elif k == "date_format":
                self.__date_format = val
            elif k == "extra_format":
                self.__extra_format = val
            elif k == "outdated_format":
                self.__outdated_format = val
            elif k == "display_extra":
                if val == "True":
                    self.__display_extra = True
                else:
                    self.__display_extra = False
            elif k == "nb_past_display":
                self.__nb_past_display = int(val)
            elif k == "nb_next_display":
                self.__nb_next_display = int(val)
            elif k == "colours":
                if val == "True":
                    self.__colours = True
                else:
                    self.__colours = False
            elif k == "verbose":
                if val == "True":
                    self.__verbose = True
                else:
                    self.__verbose = False
            elif k == "download_delay":
                self.__download_delay = int(val)
            elif k == "leveltypes":
                self.__leveltypes = val
            elif k == "default_url":
                self.__default_url = val
            elif k == "default_screenshot":
                self.__default_screenshot = val

    def prepare(self):
        """
        Make sure everything is fine before displaying anything
        """
        try:
            mtime = int(os.path.getmtime(self.__xml_file))
            if self.__now - mtime >= self.__download_delay*60:
                self.verbose("XML file too old.")
                self.download_xml()
        except OSError:
            self.verbose("XML file not found.")
            self.download_xml()

        self.parse_xml()

    def verbose(self, str):
        """
        Print a message if verbose option is enabled
        """
        if (self.__verbose):
            print str

    def set_current_time(self):
        """
        Find current time and store it as a timestamp
        """
        self.__now = int(time.time())

    def download_xml(self, update_only = False):
        """
        Download the XML file from the given url
        """
        if self.__updated:
            error("[ERROR] The XML file has been re-downloaded and errors remain, " \
                      "maybe check the url: %s" % self.__xml_url)

        try:
            self.verbose("Downloading %s" % self.__xml_url)
            urllib.urlretrieve(self.__xml_url, self.__xml_file)
            self.verbose("File saved to %s" % self.__xml_file)
        except IOError, e:
            error(e)

        self.__updated = True

        if update_only:
            sys.exit(0)

    def parse_xml(self):
        """
        Parse the XML file and store data in dictionaries
        """
        try:
            fd = open(self.__xml_file, 'r')
        except IOError, e:
            error(e)

        try:
            p = xml.parsers.expat.ParserCreate()
            p.StartElementHandler = self.add_entry
            p.ParseFile(fd)
        except xml.parsers.expat.ExpatError:
            self.verbose("[WARNING] The downloaded XML file seems to be invalid, " \
                             "trying to fix it...")
            self.download_xml()
            self.prepare()
            return

        fd.close()

        l = len(self.__data)
        if l == 0:
            error("[ERROR] The parsed XML file should not give 0 result.")
        else:
            self.verbose("Parsed %i entries." % l)

        if not self.__on_air:
            error("[ERROR] Could not determine timestamps.")

        # Adjust nb_past_display and nb_next_display index so they
        # don't go out boundaries
        if self.__on_air - self.__nb_past_display < 0:
            self.__nb_past_display = self.__on_air
        if self.__on_air + self.__nb_next_display >= l:
            self.__nb_next_display = l - self.__on_air - 1

    def add_entry(self, name, dict):
        """
        Add entry to data table, also convert all dates in
        timestamp. Also figure out here what show is currently on air,
        thus avoiding an extra parsing later.
        """
        if dict.get("date") != None:
            m = self.__date_pattern.match(dict["date"])
            d = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), \
                                      int(m.group(4)),  int(m.group(5)), int(m.group(6)), 0)
            t = int(time.mktime(d.timetuple()))

            if t < self.__now:
                self.__on_air = len(self.__data)

            dict["timestamp"] = t
            self.__data.append(dict)

    def display_extra(self):
        """
        Compute and display extra informations on current show
        """
        if self.__on_air < len(self.__data) - 1:
            begin = self.__data[self.__on_air]['timestamp']
            end   = self.__data[self.__on_air + 1]['timestamp']

            delta1   = self.__now - begin
            mod1     = delta1 % 60
            elapsed  = str(delta1 / 60) + ':' + (mod1 > 10 and str(mod1) or '0' + str(mod1))
            delta2   = end - begin
            mod2     = delta2 % 60
            duration = str(delta2 / 60) + ':' + (mod2 > 10 and str(mod2) or '0' + str(mod2))
            percent  = str(int(float(delta1)/delta2*100))
        else:
            elapsed  = "n/a"
            duration = "n/a"
            percent  = "n/a"

        o = self.__extra_format

        o = o.replace("%e", elapsed)
        o = o.replace("%d", duration)
        o = o.replace("%p", percent)

        return o

    def display(self):
        """
        Display current show
        """
        self.prepare()
        i = self.__on_air

        if i == len(self.__data) - 1:
            output(self.__outdated_format)
            return

        # The shows we found
        past = []
        next = []

        # We are not going to display every result
        # So if we want to display self.__nb_????_display results we might
        # have to search for more
        # That's why we are going to search in the whole file
        l = len(self.__data)
        for n in range(0, l):
            d = self.__data[n]
            o = self.__output_format

            o = o.replace("%D", time.strftime(self.__date_format, \
                                                  time.localtime(d['timestamp'])))
            o = o.replace("%d", d['description'])
            o = o.replace("%t", d['title'])
            o = o.replace("%s", d['sub-title'])
            o = o.replace("%a", d['detail'])
            o = o.replace("%l", d['leveltype'])
            o = o.replace("%r", d['color'])
            o = o.replace("%c", d['csa'])
            # provide default url and screenshot if fields are missing
            if d['url'] != "":
                o = o.replace("%u", d['url'])
            else:
                o = o.replace("%u", self.__default_url)
            if d['screenshot'] != "":
                o = o.replace("%o", d['screenshot'])
            else:
                o = o.replace("%o", self.__default_screenshot)

            if self.__colours:
                o = COLOURS[d['color']] + o + COLOURS['white']

            # Let's clean that later ;)
            if n < i:
                o = o.replace("%y", "past")
                # We don't display the show if its leveltype wasn't selected
                if d['leveltype'] in self.__leveltypes:
                    past.append(o)
            elif n == i:
                o = o.replace("%y", "now ")
                if self.__display_extra:
                    o = o + self.display_extra()
                    # We always display the curent show
                    now = o
            else:
                o = o.replace("%y", "next")
                # We don't display the show if its leveltype wasn't selected
                if d['leveltype'] in self.__leveltypes:
                    next.append(o)

        # Now we display what is inside the lists
        l = len(past)
        for n in range(min(l, self.__nb_past_display), 0, -1):
            output(past[l-n])

        output(now)

        for n in range(0, min(len(next), self.__nb_next_display)):
            output(next[n])

    def show_version(self):
        """
        Print software version
        """
        output("pynoair version: %s" % VERSION)

    def show_help(self):
        """
        Print help
        """
        output("Usage: pynoair <options>")
        output("Options list:")
        output("-h|--help                      : This helpful message")
        output("-v|--version                   : Print version and exit")
        output("-u|--update                    : Force XML file download")
        output("-U|--update-only               : Download XML file and exit")
        output("-o|--output-format \"<format>\"  : Output format to display")
        output("-d|--date-format \"<format>\"    : Date format to display")
        output("-x|--extra-format \"<format>\"   : Extra informations format to display")
        output("-t|--outdated-format \"<format>\": Format when the XML file is outdated")
        output("-V|--verbose                   : Enable verbose mode")
        output("-c|--with-colours              : Enable colours")
        output("-C|--without-colours           : Disable colours")
        output("-e|--no-display-extra          : Do not display extra informations")
        output("-E|--display-extra             : Display extra informations")
        output("-p|--nb-past-display <num>     : Number of past shows to display")
        output("-n|--nb-next-display <num>     : Number of upcoming shows to display")
        output("-D|--download-delay <num>      : Delay in minutes before the XML gets updated")
        output("-l|--leveltypes \"<leveltypes>\" : Leveltypes to display, separated by commas")
        output("                                 Levels are: 80 (Indies), 90 (J-Music), 100 (others)")

def error(err):
    """
    Display error message and exit
    """
    print >>sys.stderr, err
    sys.exit(1)

def output(str):
    """
    Display text on screen
    """
    print >>sys.stdout, unicode(str).encode("UTF-8")

def main():
    pynoair = PyNoAir()

    conf = {}
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        try:
            val = sys.argv[i + 1]
        except IndexError:
            val = None

        if arg == "-h" or arg == "--help":
            pynoair.show_help()
            sys.exit(0)
        elif arg == "-v" or arg == "--version":
            pynoair.show_version()
            sys.exit(0)
        elif arg == "-u" or arg == "--update":
            pynoair.download_xml()
        elif arg == "-U" or arg == "--update-only":
            pynoair.download_xml(True)
        elif arg == "-o" or arg == "--output-format":
            conf['output_format'] = val
            i += 1
        elif arg == "-d" or arg == "--date-format":
            conf['date_format'] = val
            i += 1
        elif arg == "-x" or arg == "--extra-format":
            conf['extra_format'] = val
            i += 1
        elif arg == "-t" or arg == "--outdated-format":
            conf['outdated_format'] = val
            i += 1
        elif arg == "-V" or arg == "--verbose":
            conf['verbose'] = "True"
        elif arg == "-c" or arg == "--with-colours":
            conf['colours'] = "True"
        elif arg == "-C" or arg == "--without-colours":
            conf['colours'] = "False"
        elif arg == "-e" or arg == "--no-display-extra":
            conf['display_extra'] = "False"
        elif arg == "-E" or arg == "--display-extra":
            conf['display_extra'] = "True"
        elif arg == "-p" or arg == "--nb-past-display":
            conf['nb_past_display'] = val
            i += 1
        elif arg == "-n" or arg == "--nb-next-display":
            conf['nb_next_display'] = val
            i += 1
        elif arg == "-D" or arg == "--download-delay":
            conf['download_delay'] = val
            i += 1
        elif arg == "-l" or arg == "--leveltypes":
            conf['leveltypes'] = val
            i += 1
        else:
            error("[ERROR] Unknown option: %s" % arg)

        i += 1

    pynoair.set_config(conf)
    pynoair.display()

    sys.exit(0)

if __name__ == '__main__':
    main()
