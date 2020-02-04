# c2i-robot

Il s'agit du projet de bras robotisé de l'association C-2i. Le code disponible ici permet d'automatiser une routine de déplacement du bras robotisé, afin que ce dernier prenne un objet en un point A et le déplace en un point B.

Le projet utilise un Raspberry PI pour piloter l'ensemble en envoyant les instructions à un Arduino. L'Arduino fait tourner grbl, un interpréteur de g-code, qui pilote les moteurs pas à pas du bras et le servomoteur de la pince. Afin de piloter la pince, il faut utiliser une version spécifique de grbl : grbl-servo (https://github.com/stimulee/grbl-servo).

Pour l'écriture sur l'écran lcd, nous utilisons cette librairie : https://github.com/stimulee/i2c_lcd.
Pour logger les messages dans les fichiers de log, on utilise log4p : https://pypi.org/project/log4p/


## Structure du projet

    ├── LICENSE
    ├── README.md
    └── src
        ├── bin
        │   ├── c2irobotctl
        │   ├── c2irobot.py
        │   ├── i2c_lcd.py
        │   ├── install.sh
        │   └── simple_stream.py
        ├── conf
        │   ├── c2irobot.conf
        │   ├── end.gcode
        │   ├── loop.gcode
        │   └── start.gcode
        ├── log
        │   └── c2irobot.out
        └── service
            └── c2irobot.service


## Installation

Cablage ;
- Brancher un bouton poussoir sur les pins 37 (GPIO 26)  et 39 (Ground).
- Brancher l'écran LCD sur les pins 2 (5V), 3 (GPIO2 -> SDA), 5 (GPIO3 -> SCL) et 6 (Ground).

      mkdir /opt/c2i/

Placer les sources sous /opt/c2i/vx.y.z

      cd /opt/c2i/vx.y.z/bin
      ./install.sh

## Exploitation

Une fois installé, le service est démarré automatiquement au démarrage du Raspberry PI. Il convient de respecter les conditions suivantes avant d'allumer le Raspberry PI :
- connecter l'Arduino sur le port USB
- brancher la batterie sur l'Arduino
- placer le bras en position verticale, coude plié et pince fermée


### Démarrage

     systemctl start c2irobot

### Arrêt

      systemctl stop c2irobot

### Status

      systemctl status c2irobot

# Test

Pour tester, il faut :
- disposer d'un simulateur grbl
- créer un device factice qui sera utilisé pour parler au simulateur

## Création du simulateur grbl

     git clone git@github.com:stimulee/grbl.git
     cd grbl/grbl
     git clone git@github.com:stimulee/grbl-sim.git
     cd grbl-sim
     make new

## Création du device factice de type port série

      apt install socat
      sudo socat PTY,raw,link=/dev/ttyFAKE,echo=0 "EXEC:'/path/to/grbl/grbl/grbl-sim/grbl_sim.exe -n -s step.out -b block.out',pty,raw,echo=0"

## Exécution d'un test

      git clone git@github.com:stimulee/c2i-robot.git
      cd c2i-robot/src/bin
      sudo ./c2irobotctl start
      sudo ./c2irobotctl status
      sudo ./c2irobotctl stop

      cat ../log/c2irobot.out
