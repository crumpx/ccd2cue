#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
https://github.com/crumpx/ccd2cue.git
'''

import ConfigParser
import os

def ConfigSectionMap(Config, section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def CCD2CUE(ccdsheet):
    filename = os.path.splitext(ccdsheet)
    cuesheet = os.path.join(filename[0]+'.cue')
    imagetype=('.img','.bin','.iso')
    imgfile = ''
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if os.path.splitext(f)[1] in imagetype:
            imgfile = f

    Config = ConfigParser.ConfigParser()
    Config.read(ccdsheet)
    cuefile = open(cuesheet, 'wb')

    track_counter = 0
    BEGIN = False

    cuefile.write("FILE \"%s\" BINARY\r\n" % (imgfile))
    for item in Config.sections():
        if 'Entry' not in item:
            continue

        trackinfo = {}
        tracktype = ConfigSectionMap(Config,item)['control']
        trackinfo['minute'] = int(ConfigSectionMap(Config, item)['pmin'])
        trackinfo['second'] = int(ConfigSectionMap(Config,item)['psec'])
        trackinfo['frame'] = int(ConfigSectionMap(Config,item)['pframe'])

        if int(ConfigSectionMap(Config,item)['plba']) == 0:
            BEGIN = True

        if BEGIN is True:
            track_counter += 1
            if trackinfo['second'] == 0:
                if trackinfo['minute'] >= 1:
                    trackinfo['minute'] -= 1
                    trackinfo['second'] = 60
                else:
                    trackinfo['minute'] = 0
                    trackinfo['second'] = 0
            trackinfo['second'] -= 2
            cuefile.write("  TRACK %02d %s\r\n" \
                  "    INDEX 01 %02d:%02d:%02d\r\n" % (track_counter,
                                               "MODE1/2352" if tracktype == '0x04' else 'AUDIO',
                                               trackinfo['minute'],
                                               trackinfo['second'],
                                               trackinfo['frame'],))

    cuefile.close()
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='Description of commands:', dest='command')
    rename_parser = subparsers.add_parser('convert', help='To rename a file to and move it to the \"Renamed\" folder.')
    rename_parser.add_argument('--ccd', dest='ccdsheet', required=True, help='ccd file name')

    args = parser.parse_args()
    CCD2CUE(args.ccdsheet)