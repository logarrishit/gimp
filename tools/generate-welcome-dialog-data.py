#!/usr/bin/env python3

"""
generate-welcome-dialog-data.py -- Generate app/dialogs/welcome-dialog-data.h
Copyright (C) 2022 Jehan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


Usage: generate-welcome-dialog-data.py
"""

import argparse
import os.path
import re
import sys
import xml.etree.ElementTree as ET

tools_dir   = os.path.dirname(os.path.realpath(__file__))
desktop_dir = os.path.join(tools_dir, '../desktop')
outdir      = os.path.join(tools_dir, '../app/dialogs')

infile      = os.path.join(desktop_dir, 'org.gimp.GIMP.appdata.xml.in.in')
outfile     = os.path.join(outdir, 'welcome-dialog-data.h')

def parse_appdata(infile, version):
  introduction  = []
  release_texts = []
  release_demos = []

  spaces = re.compile(r'\s+')
  tree = ET.parse(infile)
  root = tree.getroot()
  releases_node = root.find('releases')
  releases = releases_node.findall('release')
  for release in releases:
    if 'version' in release.attrib and release.attrib['version'] == version:
      intro = release.findall('./description/p')
      for p in intro:
        # Naive conversion for C strings, but it will probably fit for
        # most cases.
        p = p.text.strip()
        p = p.replace('\\', '\\\\')
        p = p.replace('"', '\\"')
        # All redundant spaces unwanted as XML merges them anyway.
        introduction += [spaces.sub(' ', p)]

      items = release.findall('./description/ul/li')
      for item in items:
        text = item.text.strip()
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        demo = None
        if 'demo' in item.attrib:
          demo = item.attrib['demo']
          # All spaces unneeded in demo string.
          demo = demo.replace(' ', '')
        release_texts += [spaces.sub(' ', text)]
        release_demos += [demo]
      break

  return introduction, release_texts, release_demos

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('version')
  parser.add_argument('--header', action='store_true')
  args = parser.parse_args(sys.argv[1:])

  top_comment = '''/* GIMP - The GNU Image Manipulation Program
 * Copyright (C) 1995 Spencer Kimball and Peter Mattis
 *
 * welcome-dialog-data.h
 * Copyright (C) 2022 Jehan
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 ***********************************************************************
 * This file is autogenerated by tools/generate-welcome-dialog-data.py *
 ***********************************************************************
 *
 * Modify the python script or desktop/org.gimp.GIMP.appdata.xml.in.in
 * instead of this one
 * Then run tools/generate-welcome-dialog-data.py again.
 */

'''
  print(top_comment)

  intro_p, items, demos = parse_appdata(infile, args.version)

  if args.header:
    print('#ifndef __WELCOME_DIALOG_DATA_H__')
    print('#define __WELCOME_DIALOG_DATA_H__\n\n')

    print('extern gint          gimp_welcome_dialog_n_items;')
    print('extern const gchar * gimp_welcome_dialog_items[];')
    print('extern const gchar * gimp_welcome_dialog_demos[];')
    print()
    print('extern gint          gimp_welcome_dialog_intro_n_paragraphs;')
    print('extern const gchar * gimp_welcome_dialog_intro[];')

    print('\n\n#endif /* __WELCOME_DIALOG_DATA_H__ */')
  else:
    print('#include "config.h"')
    print('#include <glib.h>')
    print()

    print('const gint   gimp_welcome_dialog_n_items = {};'.format(len(demos)))
    print()
    print('const gchar *gimp_welcome_dialog_items[] =')
    print('{')
    for item in items:
      print('  "{}",'.format(item))
    print('  NULL,\n};')
    print()
    print('const gchar *gimp_welcome_dialog_demos[] =')
    print('{')
    for demo in demos:
      if demo is None:
        print('  NULL,')
      else:
        print('  "{}",'.format(demo))
    print('  NULL,\n};')
    print()
    print('const gint   gimp_welcome_dialog_intro_n_paragraphs = {};'.format(len(intro_p)))
    print()
    print('const gchar *gimp_welcome_dialog_intro[] =')
    print('{')
    for p in intro_p:
      print('  "{}",'.format(p))
    print('  NULL,\n};')