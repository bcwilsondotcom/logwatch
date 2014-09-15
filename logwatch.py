#!/usr/bin/env python

# The location of our logwatch config files.
confdir = '/etc/logwatch.d/*.conf'

# Imports
from threading import Thread
import glob
import subprocess
import csv
import time
import logging
import sys
from collections import defaultdict
from logging.handlers import SysLogHandler


# Syslog Settings
logger = logging.getLogger()
logger.setLevel(logging.WARN)
syslog = SysLogHandler(address=('zenoss', 514))
formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
syslog.setFormatter(formatter)
logger.addHandler(syslog)
logger.setLevel(logging.DEBUG)


# Read logwatch.conf and set up strings into list.
def readDict(file):
    data = defaultdict(list)
    files = glob.glob(confdir)
    for name in files:
        with open(name, 'r') as handle:
            reader = csv.DictReader(handle, ['logfile', 'string', 'level'])

            for line in reader:
                thelist = [line['string'], line['level']]
                data[line['logfile']].append(thelist)

    return data


# Start following the logs
def follow(stream):
    "Follow the live contents of a text file."
    line = ''
    for block in iter(lambda:stream.read(1024), None):
        if '\n' in block:
            # Only enter this block if we have at least one line to yield.
            # The +[''] part is to catch the corner case of when a block
            # ends in a newline, in which case it would repeat a line.
            for line in (line+block).splitlines(True)+['']:
                if line.endswith('\n'):
                    yield line
            # When exiting the for loop, 'line' has any remaninig text.
        elif not block:
            # Wait for data.
            time.sleep(1.0)


#Sets up the log follow, looks for strings, and reports when found
def watch(logfile, list):
        print "watch launched for %s" % logfile
        with open(logfile, 'rt') as following:
                print "opened %s" % logfile
                following.seek(-64, 2)
                for line in follow(following):
                        for value in list:
                                if value[0] in line:
                                        sys.stdout.write(line)
                                        getattr(logger, value[1])('[logwatch] %s' % value[0])


# main
def main():
    watchlist = readDict(confdir)

    for logfile, list in watchlist.iteritems():
        try:
                print "trying to launch new thread"
                thread = Thread(target=watch, args=(logfile, list))
                thread.start()

        except KeyboardInterrupt:
            pass

        except:
                print "Error: unable to start thread"

if __name__ == '__main__':
    main()
