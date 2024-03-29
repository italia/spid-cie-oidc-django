#!/bin/sh
### BEGIN INIT INFO
# Provides:          gain-poc
# Required-Start:    nginx
# Required-Stop:
# Should-Start:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Create dynamic part of /etc/motd
# Description:       /etc/motd is user-editable and static.  This script
#                    creates the initial dynamic part, by default the
#                    output of uname, and stores it in /var/run/motd.dynamic.
#                    Both parts are output by pam_motd.
### END INIT INFO

# and then
# update-rc.d uniticket defaults
# update-rc.d uniticket enable

PATH=/sbin:/usr/sbin:/bin:/usr/bin
BASEDIR="/opt/spid-cie-oidc-django"
ENVDIR="$BASEDIR/env"
APPNAME="examples-docker/federation_authority"
APPDIR="$BASEDIR/$APPNAME"
#DEBUG=""
PID_PATH="/var/log/uwsgi"
USER=wert
COMMAND="uwsgi --ini $APPDIR/../uwsgi.ini &"
STOP_CMD="source $ENVDIR/bin/activate && uwsgi --stop /var/log/uwsgi/spid-cie-oidc-django.pid"
RELOAD_CMD="source $ENVDIR/bin/activate && uwsgi --reload /var/log/uwsgi/spid-cie-oidc-django.pid"


mkdir -p $PID_PATH
chown -R $USER $PID_PATH

case "$1" in
  start)
    su -l $USER -c "source $ENVDIR/bin/activate && $COMMAND"
    ;;
  stop)
    #kill -KILL  $(ps ax | grep $APPNAME | awk -F' ' {'print $1'} | xargs echo)
    su -l $USER -c "$STOP_CMD"
    ;;
  restart)
    su -l $USER -c "$RELOAD_CMD"
    ;;
  *)
    echo "Usage: motd [start|stop|restart]" >&2
    exit 1
    ;;
esac

exit 0
