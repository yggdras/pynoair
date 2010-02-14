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

from distutils.core import setup

setup(name = "pynoair",
      version = "0.9.4",
      description = "pynoair - a modular script displaying what's on Nolife TV channel",
      author = "Damien Leone",
      author_email = "damien.leone@fensalir.fr",
      url = "",
      packages = [""],
      scripts = ["pynoair"],
      data_files = [('share/doc/pynoair', ['README', 'COPYING', 'AUTHORS']) ],
      long_description = """
pynoair  est un  script modulaire  et  léger écrit  en Python  (2.5.4)
permettant d'exploiter  le fichier XML mis à  disposition contenant la
programmation précise de la chaîne de TV française Nolife.

http://www.nolife-tv.com/

Son but est  de fournir une interface simple en  mode texte en offrant
la  possibilité  de le  personnaliser  au  maximum,  il devient  ainsi
facilement intégrable  dans des greffons, scripts,  logiciels tels que
Conky etc.
"""          
      )    

