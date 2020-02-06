# c2i-robot

Il s'agit du projet de bras robotisé de l'association C-2i. Le code disponible ici permet d'automatiser une routine de déplacement du bras robotisé, afin que ce dernier prenne un objet en un point A et le déplace en un point B et boucle sur cette opération.

Pour plus de détail sur le projet, consultez la page [documentation](docs/documentation.md).

## Installation

Câblage ;
- Brancher un bouton poussoir sur les pins 37 (GPIO 26)  et 39 (Ground).
- Brancher l'écran LCD sur les pins 2 (5V), 3 (GPIO2 -> SDA), 5 (GPIO3 -> SCL) et 6 (Ground).

      mkdir /opt/c2i/

Placer les sources sous /opt/c2i/vx.y.z

      cd /opt/c2i/vx.y.z/bin
      ./install.sh

Le service n'est pas démarré à la fin de l'installation.

## Exploitation

Au démarrage du Raspberry PI, le service est démarré. Il convient de respecter les conditions suivantes avant d'allumer le Raspberry PI :
- brancher la batterie sur l'Arduino
- connecter l'Arduino sur le port USB
- placer le bras en position verticale, coude plié et pince fermée

### Démarrage

     systemctl start c2irobot

### Arrêt

      systemctl stop c2irobot

### Status

      systemctl status c2irobot
