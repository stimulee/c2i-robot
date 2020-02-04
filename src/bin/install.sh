#!/usr/bin/env bash

if [ $(id -u) -ne 0 ]; then
  echo "You must be logged as root user!"
  exit 1
fi

echo 'INSTALL ; installation des packages python requis'
pip install log4p

echo 'INSTALL : creation du lien symbolique de la version "/opt/c2i/robot"'
if [ -h /opt/c2i/robot ]; then
  rm /opt/c2i/robot
fi
ln -s $(cd `dirname $0`/..; pwd) /opt/c2i/robot
RC=$?
if [ $RC -ne 0 ]; then
  echo "Error on symlink creation \"/opt/c2i/robot\"! [$RC]"
  exit 20
fi

if [ ! -h /lib/systemd/system/c2irobot.service ]; then
  echo 'INSTALL : Creation de lien symbolique du service'
  ln -s /opt/c2i/robot/service/c2irobot.service /lib/systemd/system
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "Error on symlink creation! [$RC]"
    exit 30
  fi
fi

echo 'INSTALL : reload du demon systemd'
systemctl daemon-reload
RC=$?
if [ $RC -ne 0 ]; then
  echo "Error on service daemon-reload! [$RC]"
  exit 40
fi

echo 'INSTALL : activation du service'
systemctl enable c2irobot.service
RC=$?
if [ $RC -ne 0 ]; then
  echo "Error on service c2irobot enable! [$RC]"
  exit 50
fi

# Confiugration pour bouton d'arrêt
if [ $(grep -c "/opt/c2i/robot/bin/off_button.py" /etc/rc.local) -eq 0 ]; then
  echo 'INSTALL : rc.local update'
  sed -i "s|exit 0|if [ -f /opt/c2i/robot/bin/off_button.py ]; then \n\
  python /opt/c2i/robot/bin/off_button.py \n\
fi \n\
\n\
exit 0|" /etc/rc.local
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "Error on rc.local update for shutdown button configuration! [$RC]"
    exit 70
  fi
fi

echo 'INSTALL : installation terminée, vous pouvez démarrer le service manuellement ou redémarrer.'
