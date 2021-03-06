# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016: Alignak team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak.
#
# Alignak is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alignak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Alignak.  If not, see <http://www.gnu.org/licenses/>.
#
#
# This file incorporates work covered by the following copyright and
# permission notice:
#
#  Copyright (C) 2009-2014:
#     Thibault Cohen, titilambert@gmail.com
#     Grégory Starck, g.starck@gmail.com
#     aviau, alexandre.viau@savoirfairelinux.com
#     Sebastien Coavoux, s.coavoux@free.fr

#  This file is part of Shinken.
#
#  Shinken is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Shinken is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Shinken.  If not, see <http://www.gnu.org/licenses/>.
"""
This module lists provide facilities to parse log type Broks.
The supported event are listed in the event_type variable
"""

import re

# pylint: disable=bad-continuation
EVENT_TYPE_PATTERN = re.compile(
    r'^\[[0-9]{10}] (TIMEPERIOD TRANSITION|EXTERNAL COMMAND|'
    r'RETENTION SAVE|RETENTION LOAD|'
    r'CURRENT HOST STATE|CURRENT SERVICE STATE|'
    r'HOST COMMENT|SERVICE COMMENT|'
    r'HOST NOTIFICATION|SERVICE NOTIFICATION|'
    r'HOST ALERT|SERVICE ALERT|'
    r'HOST EVENT HANDLER|SERVICE EVENT HANDLER|'
    r'ACTIVE HOST CHECK|ACTIVE SERVICE CHECK|'
    r'PASSIVE HOST CHECK|PASSIVE SERVICE CHECK|'
    r'HOST ACKNOWLEDGE ALERT|SERVICE ACKNOWLEDGE ALERT|'
    r'HOST DOWNTIME ALERT|SERVICE DOWNTIME ALERT|'
    r'HOST FLAPPING ALERT|SERVICE FLAPPING ALERT)($|: .*)'
)
EVENT_TYPES = {
    'TIMEPERIOD': {
        # [1490998324] RETENTION SAVE
        'pattern': r'^\[([0-9]{10})] (TIMEPERIOD) (TRANSITION): (.*)',
        'properties': [
            'time',
            'event_type',  # 'TIMEPERIOD'
            'state_type',  # 'TRANSITION'
            'output',  # 'WARNING - load average: 5.04, 4.67, 5.04'
        ]
    },
    'RETENTION': {
        # [1490998324] RETENTION SAVE
        'pattern': r'^\[([0-9]{10})] (RETENTION) (LOAD|SAVE): (.*)',
        'properties': [
            'time',
            'event_type',  # 'RETENTION'
            'state_type',  # 'LOAD' or 'SAVE'
            'output',  # 'scheduler name
        ]
    },
    'EXTERNAL': {
        # [1490997636] EXTERNAL COMMAND: [1490997512]
        # PROCESS_HOST_CHECK_RESULT;ek3022sg-0001;0;EK3022SG-0001 is alive,
        # uptime is 43639 seconds (0 days 12 hours 7 minutes 19 seconds 229 ms)|'Uptime'=43639
        'pattern': r'^\[([0-9]{10})] (EXTERNAL COMMAND): '
                   r'([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'event_type',  # 'EXTERNAL COMMAND'
            'command',  # 'PROCESS_SERVICE_CHECK_RESULT'
            'parameters',  # ;ek3022sg-0001;svc_Screensaver;0;Ok|'ScreensaverOff'=61c
        ]
    },
    'CURRENT': {
        # ex: "[1498108167] CURRENT HOST STATE: localhost;UP;HARD;1;Host assumed to be UP"
        # ex: "[1498108167] CURRENT SERVICE STATE: localhost;Maintenance;UNKNOWN;HARD;0;"
        'pattern': r'^\[([0-9]{10})] CURRENT (HOST|SERVICE) (STATE): '
                   r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^\;]*);([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'item_type',  # 'SERVICE' (or could be 'HOST')
            'event_type',  # 'STATE'
            'hostname',  # 'localhost'
            'service_desc',  # 'Maintenance' (or could be None)
            'state',  # 'UP'
            'state_type',  # 'HARD'
            'attempts',  # '0'
            'output',  # 'WARNING - load average: 5.04, 4.67, 5.04'
        ]
    },
    'ACTIVE': {
        # ex: "[1402515279] ACTIVE SERVICE CHECK: localhost;Nrpe-status;OK;HARD;1;NRPE v2.15"
        'pattern': r'^\[([0-9]{10})] ACTIVE (HOST|SERVICE) (CHECK): '
                   r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^\;]*);([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'item_type',  # 'SERVICE' (or could be 'HOST')
            'event_type',  # 'CHECK'
            'hostname',  # 'localhost'
            'service_desc',  # 'cpu load maui' (or could be None)
            'state',  # 'WARNING'
            'state_type',  # 'HARD'
            'attempts',  # '0'
            'output',  # 'NRPE v2.15'
        ]
    },
    'PASSIVE': {
        # ex: "[1402515279] PASSIVE SERVICE CHECK: localhost;nsca_uptime;0;OK: uptime: 02:38h,
        # boot: 2017-08-31 06:18:03 (UTC)|'uptime'=9508s;2100;90000"
        'pattern': r'^\[([0-9]{10})] PASSIVE (HOST|SERVICE) (CHECK): '
                   r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^$]*)',
        'properties': [
            'time',
            'item_type',  # 'SERVICE' (or could be 'HOST')
            'event_type',  # 'CHECK'
            'hostname',  # 'localhost'
            'service_desc',  # 'cpu load maui' (or could be None)
            'state_id',  # '0'
            'output',  # 'K: uptime: 02:38h, boot: 2017-08-31 06:18:03 (UTC)
            # |'uptime'=9508s;2100;90000'
        ]
    },
    'NOTIFICATION': {
        # ex: "[1402515279] SERVICE NOTIFICATION:
        # admin;localhost;check-ssh;CRITICAL;notify-service-by-email;Connection refused"
        'pattern': r'\[([0-9]{10})\] (HOST|SERVICE) (NOTIFICATION): '
        r'([^\;]*);([^\;]*);(?:([^\;]*);)?([^\;]*);([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'notification_type',  # 'SERVICE' (or could be 'HOST')
            'event_type',  # 'NOTIFICATION'
            'contact',  # 'admin'
            'hostname',  # 'localhost'
            'service_desc',  # 'check-ssh' (or could be None)
            'state',  # 'CRITICAL'
            'notification_method',  # 'notify-service-by-email'
            'output',  # 'Connection refused'
        ]
    },
    'ALERT': {
        # ex: "[1329144231] SERVICE ALERT:
        #  dfw01-is02-006;cpu load maui;WARNING;HARD;4;WARNING - load average: 5.04, 4.67, 5.04"
        'pattern': r'^\[([0-9]{10})] (HOST|SERVICE) (ALERT): '
                   r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^\;]*);([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'alert_type',  # 'SERVICE' (or could be 'HOST')
            'event_type',  # 'ALERT'
            'hostname',  # 'localhost'
            'service_desc',  # 'cpu load maui' (or could be None)
            'state',  # 'WARNING'
            'state_type',  # 'HARD'
            'attempts',  # '4'
            'output',  # 'WARNING - load average: 5.04, 4.67, 5.04'
        ]
    },
    'EVENT': {
        # ex: "[1329144231] HOST EVENT HANDLER: host-03;DOWN;HARD;0;g_host_event_handler"
        'pattern': r'^\[([0-9]{10})] (HOST|SERVICE) (EVENT HANDLER): '
                   r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^\;]*);([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'item_type',  # 'SERVICE' (or could be 'HOST')
            'event_type',  # 'EVENT HANDLER'
            'hostname',  # 'localhost'
            'service_desc',  # 'cpu load maui' (or could be None)
            'state',  # 'WARNING'
            'state_type',  # 'HARD'
            'attempts',  # '4'
            'output',  # 'g_host_event_handler'
        ]
    },
    'COMMENT': {
        # ex: "[1329144231] SERVICE COMMENT:
        #  dfw01-is02-006;cpu load maui;author;Comment text"
        'pattern': r'^\[([0-9]{10})] (HOST|SERVICE) (COMMENT): '
                   r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^$]*)',
        'properties': [
            'time',
            'comment_type',  # 'SERVICE' (or could be 'HOST')
            'event_type',  # 'COMMENT'
            'hostname',  # 'localhost'
            'service_desc',  # 'cpu load maui' (or could be None)
            'author',
            'comment',  # 'WARNING - load average: 5.04, 4.67, 5.04'
        ]
    },
    'ACKNOWLEDGE': {
        # ex: "[1279250211] HOST ACKNOWLEDGE STARTED:
        # maast64;Host has been acknowledged"
        'pattern': r'^\[([0-9]{10})] (HOST|SERVICE) (ACKNOWLEDGE) ALERT: '
                   r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'ack_type',  # 'SERVICE' or 'HOST'
            'event_type',  # 'ACKNOWLEDGE'
            'hostname',  # The hostname
            'service_desc',  # The service description or None
            'state',  # 'STARTED' or 'EXPIRED'
            'output',  # 'Host has been acknowledged'
        ]
    },
    'DOWNTIME': {
        # ex: "[1279250211] HOST DOWNTIME ALERT:
        # maast64;STARTED; Host has entered a period of scheduled downtime"
        'pattern': r'^\[([0-9]{10})] (HOST|SERVICE) (DOWNTIME) ALERT: '
                   r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'downtime_type',  # 'SERVICE' or 'HOST'
            'event_type',  # 'DOWNTIME'
            'hostname',  # The hostname
            'service_desc',  # The service description or None
            'state',  # 'STOPPED' or 'STARTED'
            'output',  # 'Service appears to have started flapping (24% change >= 20.0% threshold)'
        ]
    },
    'FLAPPING': {
        # service flapping ex: "[1375301662] SERVICE FLAPPING ALERT:
        # testhost;check_ssh;STARTED;
        # Service appears to have started flapping (24.2% change >= 20.0% threshold)"

        # host flapping ex: "[1375301662] HOST FLAPPING ALERT:
        # hostbw;STARTED; Host appears to have started flapping (20.1% change > 20.0% threshold)"
        'pattern': r'^\[([0-9]{10})] (HOST|SERVICE) (FLAPPING) ALERT: '
        r'([^\;]*);(?:([^\;]*);)?([^\;]*);([^\;]*)',
        'properties': [
            'time',
            'alert_type',  # 'SERVICE' or 'HOST'
            'event_type',  # 'FLAPPING'
            'hostname',  # The hostname
            'service_desc',  # The service description or None
            'state',  # 'STOPPED' or 'STARTED'
            'output',  # 'Service appears to have started flapping (24% change >= 20.0% threshold)'
        ]
    }
}


class LogEvent(object):  # pylint: disable=too-few-public-methods, useless-object-inheritance
    """Class for parsing event logs
    Populates self.data with the log type's properties
    """

    def __init__(self, log):
        self.data = {}
        self.valid = False
        self.time = None
        self.event_type = 'unknown'
        self.pattern = 'unknown'

        # Find the type of event
        event_type_match = EVENT_TYPE_PATTERN.match(log)
        if event_type_match:
            matched = event_type_match.group(1)
            matched = matched.split()
            self.pattern = matched[0]
            if self.pattern in ['HOST', 'SERVICE']:
                self.pattern = matched[1]

            # parse it with it's pattern
            if self.pattern in EVENT_TYPES:
                event_type = EVENT_TYPES[self.pattern]
                properties_match = re.match(event_type['pattern'], log)
                if properties_match:
                    self.valid = True

                    # Populate self.data with the event's properties
                    for i, prop in enumerate(event_type['properties']):
                        # print("Property: %s / %s" % (prop, properties_match.group(i + 1)))
                        self.data[prop] = properties_match.group(i + 1)

                    # Convert the time to int
                    self.data['time'] = int(self.data['time'])

                    # Convert event_type to int
                    if 'event_type' in self.data:
                        self.event_type = self.data['event_type']

                    # Convert attempts to int
                    if 'attempts' in self.data:
                        self.data['attempts'] = int(self.data['attempts'])

    def __iter__(self):
        return self.data.iteritems()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def __str__(self):
        return str(self.data)
