#!/usr/bin/env bash

# Installer script for pynoair

PREFIX="/usr/local/bin"
EXEC="pynoair"

CP="/bin/cp"
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
	$CP $EXEC $PREFIX/
	$CHMOD 755 $PREFIX/$EXEC
}

uninstall()
{
	check_root
	echo "Removing $PREFIX/$EXEC"
	$RM $PREFIX/$EXEC
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