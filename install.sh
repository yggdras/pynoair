#!/usr/bin/env bash

# Installer script for pynoair
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

PREFIX="/usr/local/bin"
EXEC="pynoair.py"
SIMLINK="pynoair"

CP="/bin/cp"
LN="/bin/ln"
RM="/bin/rm -f"
CHMOD="/bin/chmod"

check_root()
{
	if [ `whoami` != 'root' ]; then
		echo "*** You must be root."
		exit 1
	fi
}

install()
{
	check_root
	echo "Copying $EXEC to $PREFIX/$EXEC"
	echo "Linking $PREFIX/$EXEC to $PREFIX/$SIMLINK"
	$CP $EXEC $PREFIX/
	$CHMOD 755 $PREFIX/$EXEC
	$LN -sf $PREFIX/$EXEC $PREFIX/$SIMLINK
}

uninstall()
{
	check_root
	echo "Removing $PREFIX/$EXEC, $PREFIX/$SIMLINK"
	$RM $PREFIX/$EXEC $PREFIX/$SIMLINK
}

case "$1" in
	install)
		install
		;;
	uninstall)
		uninstall
		;;
	*)
		echo "Usage: $0 {install|uninstall|help}"
esac

exit 0
