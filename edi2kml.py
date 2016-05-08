#!/usr/bin/python3

import re
from pyhamtools.locator import locator_to_latlong
import sys

def get_contacts(log):
    f = open(log)
    qso_records = False
    contacts = dict()
    start = re.compile("\\[QSORecords;[0-9]+\\]")
    end = re.compile("\\[END;")
    for line in f.readlines():
        if qso_records:
            if end.match(line):
                qso_records = False
            else:
                sp = line.split(';')
                callsign = sp[2]
                locator = sp[9]
                contacts.update([(callsign, locator)])
        elif start.match(line):
            qso_records = True
    return contacts

def contacts_latlong(contacts_per_band):
    contacts = dict()
    for band in contacts_per_band:
        for callsign, locator in band.items():
            if callsign not in contacts:
                contacts.update([(callsign, locator_to_latlong(locator))])
    return contacts

def kml(vhf, uhf, mycall, mylatlong):
    contacts = contacts_latlong([vhf, uhf])
    kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
	xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <Style id="vhf_icon">
      <IconStyle>
        <Icon>
          <href>http://destevez.net/wp-content/plugins/osm/icons/mic_blue_pinother_02.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="uhf_icon">
      <IconStyle>
        <Icon>
          <href>http://destevez.net/wp-content/plugins/osm/icons/mic_green_pinother_02.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="me_icon">
      <IconStyle>
        <Icon>
          <href>http://destevez.net/wp-content/plugins/osm/icons/mic_red_pinother_02.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <StyleMap id="vhf">
      <Pair>
        <key>normal</key>
        <styleUrl>#vhf_icon</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#vhf_icon</styleUrl>
      </Pair>
    </StyleMap>
    <StyleMap id="uhf">
      <Pair>
        <key>normal</key>
        <styleUrl>#uhf_icon</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#uhf_icon</styleUrl>
      </Pair>
    </StyleMap>
    <StyleMap id="me">
      <Pair>
        <key>normal</key>
        <styleUrl>#me_icon</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#me_icon</styleUrl>
      </Pair>
    </StyleMap>
    <Folder>
      <name>Waypoints</name>
"""
    kml += """      <Placemark>
        <name>{0}</name>
        <styleUrl>#me</styleUrl>
        <Point>
          <coordinates>{1[1]},{1[0]}</coordinates>
        </Point>
      </Placemark>
""".format(mycall, mylatlong)

    for callsign, latlong in contacts.items():
        kml += """      <Placemark>
        <name>{0}</name>
        <styleUrl>{1}</styleUrl>
        <Point>
          <coordinates>{2[1]},{2[0]}</coordinates>
        </Point>
      </Placemark>
""".format(callsign, "#uhf" if callsign in uhf else "#vhf", latlong)

    kml += """    </Folder>
  </Document>
</kml>"""

    return kml

def main():
    if len(sys.argv) != 6:
        print("Usage: {} <vhf.edi> <uhf.edi> <callsign> <lat> <long>".format(sys.argv[0]))
        return

    vhf = get_contacts(sys.argv[1])
    uhf = get_contacts(sys.argv[2])
    print(kml(vhf, uhf, sys.argv[3], (sys.argv[4], sys.argv[5])))

    return

if __name__ == "__main__":
    main()

