#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys;
import time;
import os;
import json;
import logging;
import getopt;

MAXHOUR = 2087;


def processTask(day, stdindir):
    flowcount = [];
    for index in xrange(0, 24):
        if day * 24 + index > MAXHOUR:
            break;
        count = 0;
        with open(os.path.join(stdindir, '%d-%d') % (index, day * 24 + index), 'r') as dinput:
            records = dinput.read().split("\n");
            for record_index in xrange(len(records) - 1):
                columns = records[record_index].split(",");
                count += int(columns[3]);
        flowcount.append(count);
    if day <= 26:
        date = '2016-07-%02d' % (day + 5);
    elif day <= 57:
        date = '2016-08-%02d' % (day - 26);
    elif day <= 87:
        date = '2016-09-%02d' % (day - 57);
    else:
        date = 'None valid date';
    flowdict = {'data': date, 'flowCount': flowcount};
    return flowdict;


def main(argv):
    try:
        argsArray = ["day=", "stdindir=", "stdoutdir="];
        opts, args = getopt.getopt(argv, "d:i:o:", argsArray);
    except getopt.GetoptError as err:
        print
        str(err);
        sys.exit(2);
    stdindir = "/datahouse/tripflow/Anomaly/bj-byhour-statics";
    stdoutdir = "/datahouse/tripflow/Anomaly/bj-flowcount";
    day = 87;
    start_time = time.time();
    for opt, arg in opts:
        if opt in ("-d", "--day"):
            day = int(arg);
        elif opt in ("-i", "--stdindir"):
            stdindir = arg;
        elif opt in ("-o", "--stdoutdir"):
            stdoutdir = arg;
    result = [];
    for index in xrange(day):
        result.append(processTask(index, stdindir));
    with open(os.path.join(stdoutdir, "totalcount.json"), 'wb') as output:
        output.write(json.dumps(result));
    print
    "Complete time: " + str(time.time() - start_time);


if __name__ == '__main__':
    logging.basicConfig(filename='flowcount.log', level=logging.DEBUG)
    main(sys.argv[1:]);
	
