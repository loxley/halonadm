#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Manage H//\\LON SP servers easily.
'''

__author__ = "Johan Svensson"
__version__ = "1.0.0"

from suds.client import Client
from suds.transport.https import HttpAuthenticated # TransportError
from suds.sudsobject import asdict
from collections import Counter
from time import time, localtime, strftime
from pkg_resources import Requirement, resource_filename
import os
import argparse
import base64
import json
import sys

try:
    import ConfigParser as configparser
except:
    import configparser

if sys.version_info < (3, 0):
     reload(sys)
     sys.setdefaultencoding('utf8')

def recursive_asdict(suds_data):
    ''' Convert Suds object into serializable format. '''

    out = {}
    for key, value in asdict(suds_data).items():
        if hasattr(value, '__keylist__'):
            out[key] = recursive_asdict(value)
        elif isinstance(value, list):
            out[key] = []
            for item in value:
                if hasattr(item, '__keylist__'):
                    out[key].append(recursive_asdict(item))
                else:
                    out[key].append(item)
        else:
            out[key] = value
    return out

def update_qshape(data1, data2):
    ''' Update qshape dict '''

    for key, value in data2.items():
        if key not in data1:
            data1[key] = {}
            data1[key].update(value)
        else:
            for item in value:
                for email in value[item]:
                    data1[key][item].append(email)
    return data1

def update_mailq(data1, data2):
    ''' Update mailq dict '''

    for key, value in data2.items():
        if key not in data1:
            data1[key] = []
        for item in value:
            data1[key].append(item)
    return data1

def json_dumps(data):
    ''' Convert to json '''

    return json.dumps(data, sort_keys=True, indent=4,
                      separators=(',', ': '))

def getdatetime(timestamp):
    ''' Get local time '''
    return strftime("%D %H:%M:%S", localtime(int(timestamp)))

def setup_client(args, smtpfilter):
    ''' Setup suds client '''

    url = 'https://' + smtpfilter + '/remote/?wsdl'
    username = args.username
    password = args.password
    transport = HttpAuthenticated(
        username=username,
        password=password,
        timeout=5)
    # todo: add exception handling
    try:
        client = Client(url, location='https://' + smtpfilter  + '/remote/',
                        transport=transport, timeout=5)
    # except urllib.error.URLError as exc:
    #     print("Error: %s" % exc.reason)
    #     exit(1)
    # except TransportError as exc:
    #     print("Error: %s '%s'" % (exc, url))
    #     exit(1)
    except Exception as exc:
        print("Error: Could not connect to '%s' as '%s'" % (url, username))
        exit(1)
    return client

def fetch_data(client, operation, filters=None, emlfile=None):
    ''' Fetch mailqQueue or mailHistory operations '''

    limit = 10000
    offset = 0
    data = None
    filterscombined = []
    if filters:
        filterscombined = ' '.join([filterval for filterval in filters])
    if operation is 'mailQueue':
        # todo: add exception handling
        try:
            data = client.service.mailQueue(filter=filterscombined,
                                            limit=limit,
                                            offset=offset)
        except Exception as exc:
            print(exc)
            exit(1)
    elif operation is 'mailHistory':
        try:
            data = client.service.mailHistory(filter=filterscombined,
                                              limit=limit,
                                              offset=offset)
        except Exception as exc:
            print(exc)
            exit(1)
    elif operation is 'fileRead':
        try:
            data = client.service.fileRead(file=emlfile,
                                           size=999999999,
                                           offset=offset)
        except Exception as exc:
            print(exc)
            exit(1)
    return data

def format_data(data):
    ''' Format data to best fit columns '''

    # Reorganize data by columns
    cols = zip(*data)

    # Compute column widths by taking maximum length of values per column
    col_widths = [max(len(value) for value in col) for col in cols]

    # Create a suitable format string
    formatted = ''
    for num, width in enumerate(col_widths, start=1):
        if num == 1:
            formatted = ('%%-%ds' % width)
        if num > 1:
            formatted += (' %%%ds' % width)
    return formatted

def process_results(data, server, sender=None):
    ''' Process results '''

    stats = {}
    mailq = {}
    if not recursive_asdict(data)['result']:
        return {'stats': stats, 'mailq': mailq}
    for res in recursive_asdict(data)['result']['item']:
        domain = None
        email = None
        age = int((time()-res['msgts0'])/60)
        if sender:
            if res['msgfrom']:
                domain = res['msgfrom'].split('@')[1]
            else:
                domain = '<MAILER-DAEMON>'
            email = res['msgfrom']
        else:
            domain = res['msgto'].split('@')[1]
            email = res['msgto']
        if domain not in stats:
            stats[domain] = {}
            stats[domain].update(
                {
                    'total': [],
                    '5': [],
                    '10': [],
                    '20': [],
                    '40': [],
                    '80': [],
                    '160': [],
                    '320': [],
                    '640': [],
                    '1280': [],
                    'older': []
                })
        stats[domain]['total'].append(email)
        if age < 5:
            stats[domain]['5'].append(email)
        elif age < 10:
            stats[domain]['10'].append(email)
        elif age < 20:
            stats[domain]['20'].append(email)
        elif age < 40:
            stats[domain]['40'].append(email)
        elif age < 80:
            stats[domain]['80'].append(email)
        elif age < 160:
            stats[domain]['160'].append(email)
        elif age < 320:
            stats[domain]['320'].append(email)
        elif age < 640:
            stats[domain]['640'].append(email)
        elif age < 1280:
            stats[domain]['1280'].append(email)
        else:
            stats[domain]['older'].append(email)

        # mailq
        msgfrom = '<MAILER-DAEMON>'
        msgsubject = ''
        msgerror = None
        msgpath = None
        msgscore = None
        if res['msgsubject'] is not None:
            msgsubject = res['msgsubject']
        if res['msgfrom'] is not None:
            msgfrom = res['msgfrom']
        if res['msgto'] is not None:
            msgto = res['msgto']
        if 'msgerror' in res and res['msgerror'] is not None:
            msgerror = res['msgerror']
        if 'msgdescription' in res and res['msgdescription'] is not None:
            msgerror = res['msgdescription']
        if res['msgts0'] not in mailq:
            mailq[res['msgts0']] = []
        if 'msgpath' in res and res['msgpath'] is not None:
            msgpath = res['msgpath']
        if 'msgscore' in res and res['msgscore'] is not None:
            msgscore = res['msgscore']
        mailq[res['msgts0']].append(
            {
                'msgid': res['msgid'],
                'msgfrom': msgfrom,
                'msgto': msgto,
                'msgsubject': msgsubject,
                'msgerror': msgerror,
                'server': server,
                'msgpath': msgpath,
                'msgscore': msgscore
            })
    return {'stats': stats, 'mailq': mailq}

def display_qshape(args, stats):
    ''' Display stats '''

    operation = ' mailQueue '
    if args.mailhistory:
        operation = 'mailHistory'
    boldtext = '\033[1m'
    normaltext = '\033[0m'
    os.system('clear')
    rows = []
    print(",.-~*´¨¯¨`*·~-.¸-( " +
          boldtext + operation + normaltext +
          " )-,.-~*´¨¯¨`*·~-.¸")
    rows.append(['', 'T', '5', '10', '20', '40', '80', '160', '320', '640',
                 '1280', '1280+'])
    total = str(sum(len(v['total']) for v in stats.values()))
    total_5 = str(sum(len(v['5']) for v in stats.values()))
    total_10 = str(sum(len(v['10']) for v in stats.values()))
    total_20 = str(sum(len(v['20']) for v in stats.values()))
    total_40 = str(sum(len(v['40']) for v in stats.values()))
    total_80 = str(sum(len(v['80']) for v in stats.values()))
    total_160 = str(sum(len(v['160']) for v in stats.values()))
    total_320 = str(sum(len(v['320']) for v in stats.values()))
    total_640 = str(sum(len(v['640']) for v in stats.values()))
    total_1280 = str(sum(len(v['1280']) for v in stats.values()))
    total_older = str(sum(len(v['older']) for v in stats.values()))
    rows.append(['domain', 'TOTAL ' + total, total_5, total_10, total_20,
                 total_40, total_80, total_160, total_320, total_640,
                 total_1280, total_older])
    #print("-" * 105)
    for num, domain in enumerate(sorted(
            stats, key=lambda k: len(stats[k]['total']), reverse=True), start=1):
        if num <= args.numdomains:
            domain_total = str(len(stats[domain]['total']))
            domain_5 = str(len(stats[domain]['5']))
            domain_10 = str(len(stats[domain]['10']))
            domain_20 = str(len(stats[domain]['20']))
            domain_40 = str(len(stats[domain]['40']))
            domain_80 = str(len(stats[domain]['80']))
            domain_160 = str(len(stats[domain]['160']))
            domain_320 = str(len(stats[domain]['320']))
            domain_640 = str(len(stats[domain]['640']))
            domain_1280 = str(len(stats[domain]['1280']))
            domain_older = str(len(stats[domain]['older']))
            rows.append([domain, domain_total, domain_5, domain_10, domain_20,
                         domain_40, domain_80, domain_160, domain_320,
                         domain_640, domain_1280, domain_older])
            if args.verbose:
                counts = Counter(stats[domain]['total']).most_common()
                length = len(counts)
                for i, recipient in enumerate(counts, start=1):
                    if i != length:
                        recp = " ├─%s (%s)" % (recipient[0], recipient[1])
                    else:
                        recp = " └─%s (%s)" % (recipient[0], recipient[1])
                    rows.append([recp, '', '', '', '', '', '', '', '', '', '',
                                 ''])
                rows.append(['', '', '', '', '', '', '', '', '', '', '', ''])
    output = format_data(rows)
    for row in rows:
        print(output % tuple(row))

def display_mailq(args, data):
    ''' Display mailq '''

    print("\033[1m%-36s %-17s %s\033[0m" % (
        'msgid', 'arrival time', 'sender/recipient'))
    num = 0
    for msgts0 in sorted(data, reverse=True):
        for res in data[msgts0]:
            num += 1
            msgerror = None
            msgsubject = base64.b64decode(res['msgsubject']).decode('utf-8')
            msgfrom = res['msgfrom']
            msgto = res['msgto']
            msgpath = res['msgpath']
            msgscore = res['msgscore']
            if 'msgerror' in res and res['msgerror'] is not None:
                msgerror = base64.b64decode(res['msgerror']).decode('utf-8')
            print("%-36s %17s %s" % (str(res['msgid']),
                                     getdatetime(msgts0),
                                     msgfrom))
            print("%54s %s" % (' ', msgto))
            if args.verbose:
                if msgscore:
                    print("%54s  ├───score: SA=%s" % (
                        ' ', res['msgscore']['item'][0]['second'].split(
                            '|')[0]))
                print("%54s  ├──server: %s" % (' ', res['server']))
                if msgerror:
                    print("%54s  ├─subject: %s" % (' ', msgsubject))
                    if msgpath:
                        print("%54s  ├─msgpath: %s" % (' ', msgpath))
                else:
                    print("%54s  └─subject: %s" % (' ', msgsubject))
            if msgerror:
                print("%54s  └───error: %s" % (' ', msgerror))
            print('')
        if num == args.numdomains:
            break
    print("-- \033[1m%d\033[0m/\033[1m%d\033[0m Requests." % (
        num, sum(len(v) for v in data.values())))

def setupconfig():
    ''' Setup config '''

    config_path = os.path.expanduser("~") + os.sep
    config_candidates = [config_path + ".halonadm.conf",
                         config_path + ".config" + os.sep + "halonadm" +
                         os.sep + "halonadm.conf",
                         os.sep + "etc" + os.sep + "halonadm.conf",
                         "halonadm.conf"]
    config_orig = resource_filename(Requirement.parse("halonadm"),
                                    "halonadm/halonadm.conf")
    config = configparser.SafeConfigParser()
    found = config.read(config_candidates)
    if not found:
        print("Found no configfiles in: " +
              " or ".join([configfile for configfile in config_candidates]))
        print("Copy skelton from " + config_orig)
        exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filter",
                        nargs='*',
                        help="search filter",
                        default=[''])
    parser.add_argument("-m", "--mailhistory",
                        help="stats from mailhistory instead of mailqueue",
                        action="store_true")
    parser.add_argument("-n", "--numdomains",
                        type=int,
                        help='report only the top "batch_top_domains" domains',
                        default=10000)
    parser.add_argument("-s", "--sender",
                        help="display the senders instead of the recipients",
                        action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity",
                        action="store_true")
    parser.add_argument('cmd',
                        help='use qshape, mailq or view',
                        choices=('qshape', 'mailq', 'view'))
    parser.add_argument("host", nargs='*',
                        help="halon server host")

    config_options = config.defaults()
    parser.set_defaults(**config_options)
    args = parser.parse_args()
    return args, config

def main():
    ''' Main '''

    (args, config) = setupconfig()
    smtpfilters = json.loads(config.get('smtpfilter', 'servers'))
    msgpath = None

    if args.host:
        if args.cmd == 'qshape' or args.cmd == 'mailq':
            smtpfilters = list(args.host)
        if args.cmd == 'view':
            if len(args.host) != 2:
                print("Error: 'view' need two options, msgpath and server.")
                exit(1)
            (msgpath, smtpfilters) = args.host

    if args.cmd == 'view':
        if not args.host:
            print("Error: 'view' need two options, msgpath and server.")
            exit(1)
        client = setup_client(args, smtpfilters)
        operation = 'fileRead'
        data = fetch_data(client, operation, emlfile=msgpath)
        data = base64.b64decode(data['data']).decode('utf-8')
        print(data)
        exit(1)

    stats = {}
    for num, smtpfilter in enumerate(smtpfilters, start=1):
        client = setup_client(args, smtpfilter)

        operation = 'mailQueue'
        if args.mailhistory:
            operation = 'mailHistory'
        data = fetch_data(client, operation, filters=args.filter)

        res = process_results(data, smtpfilter, sender=args.sender)

        if num == 1:
            if 'mailq' in args.cmd:
                stats.update(res['mailq'])
            if 'qshape' in args.cmd:
                stats.update(res['stats'])
        if num > 1:
            if 'mailq' in args.cmd:
                stats = update_mailq(stats, res['mailq'])
            if 'qshape' in args.cmd:
                stats = update_qshape(stats, res['stats'])

    if 'qshape' in args.cmd:
        display_qshape(args, stats)
    elif 'mailq' in args.cmd:
        display_mailq(args, stats)

if __name__ == '__main__':
    main()
