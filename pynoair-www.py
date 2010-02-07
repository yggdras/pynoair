#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import sys

import pynoair


def main():
    noair = pynoair.PyNoAir(base_config = '~/.pynoair/')
    conf = {}

    conf["output_format"]  = u'<tr>'
    conf["output_format"] += u'<td><a href="%u"><img class="emission" src="%o"></a></td>'
    conf["output_format"] += u'<td>%D</td>'
    conf["output_format"] += u'<td>%d</td>'
    conf["output_format"] += u'<td>%a</td>'
    conf["output_format"] += u'</tr>'

    conf["extra_format"]  = u'<tr>'
    conf["extra_format"] += u'<td><div class="progress"><div class="progress_current" style="width: %ppx;"></div></div></td>'
    conf["extra_format"] += u'<td colspan=2 class="écoulé">Temps écoulé: %e/%d [%p%]</td>'
    conf["extra_format"] += u'</tr>'

    conf['default_url'] = 'http://nolife-tv.com'
    conf['default_screenshot'] = 'nolife-tv.png'

    print 'Content-Type: text/html; charset=utf-8'
    print ''   # add additionnal new line to finish headers
    print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
    print '<html>'
    print '<head>'
    print '  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" >'
    print '  <link rel="stylesheet" type="text/css" href="style.css">'
    print '  <title>Programme de Nolife TV</title>'
    print '</head>'

    print '<body>'
    print '  <table>'
    print '    <tr>'
    print '      <th>Image</th>'
    print '      <th>Début</th>'
    print '      <th>Émission</th>'
    print '      <th>Description</th>'
    print '    </tr>'

    
    conf["nb_past_display"] = 5
    conf["display_now"] = "False"
    conf["nb_next_display"] = 0
    noair.set_config(conf)
    noair.display()

    # TODO: this should be displayed in another color
    conf["nb_past_display"] = 0
    conf["display_now"] = "True"
    conf["nb_next_display"] = 0
    noair.set_config(conf)
    noair.display()

    conf["nb_past_display"] = 0
    conf["display_now"] = "False"
    conf["nb_next_display"] = 20
    noair.set_config(conf)
    noair.display()

    print '  </table>'
    print '</body>'
    print '</html>'

    sys.exit(0)

if __name__ == "__main__":

    # print debug messages on failures
    import cgitb
    cgitb.enable(display=1)

    main()

