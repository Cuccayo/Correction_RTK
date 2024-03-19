from pygnssutils import GNSSNTRIPClient
from gnssapp_silent import GNSSSkeletonApp
from time import sleep
from queue import Queue
from threading import Event
from datetime import datetime

# Paramètres de configuration pour la communication GNSS et NTRIP
NTRIP_HOST = '92.245.148.38'
NTRIP_PORT = 2101
NTRIP_MOUNTPOINT = 'B612_RTK_CORR'

SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 38400
TIMEOUT = 10

# Identifiant du récepteur GNSS
ROVER_ID = 1

# File d'attente pour envoyer des données au récepteur
send_queue = Queue()

# Événement pour arrêter le programme de manière propre
stop_event = Event()

# Fonction principale du programme
def main():
    try:
        # Initialisation de la communication avec le récepteur GNSS
        print(f"Starting GNSS reader/writer on {SERIAL_PORT} @ {BAUDRATE}...\n")
        with GNSSSkeletonApp(
            SERIAL_PORT,
            BAUDRATE,
            TIMEOUT,
            stopevent=stop_event,
            recvqueue=None,
            sendqueue=send_queue,
            enableubx=True,
            showhacc=True,
        ) as gna:
            gna.run()
            sleep(2)  # Attente pour que le récepteur GNSS produise au moins une solution de navigation

            print(f"Starting NTRIP client on {NTRIP_HOST}:{NTRIP_PORT}...\n")

            # Connexion au serveur NTRIP et transmission des données GNSS
            with GNSSNTRIPClient(gna, logtofile=1, logpath='logs', verbosity=1) as gnc:
                streaming = gnc.run(
                    ipprot="IPv4",
                    server=NTRIP_HOST,
                    port=NTRIP_PORT,
                    mountpoint=NTRIP_MOUNTPOINT,
                    output=send_queue,  # Envoi des données NTRIP au récepteur
                )
                # Boucle principale du programme, exécute jusqu'à ce que l'utilisateur appuie sur CTRL-C
                while streaming and not stop_event.is_set():
                    # Récupération des coordonnées GNSS actuelles
                    connected, lat, lon, alt, sep = gna.get_coordinates()
                    print(f"lat: {lat}, lon: {lon}, alt: {alt}")

                    sleep(1)  # Pause d'une seconde avant la prochaine itération

                sleep(1)  # Attente supplémentaire avant de terminer
    except KeyboardInterrupt:
        # Arrêt propre du récepteur GNSS et du client NTRIP en cas d'interruption par l'utilisateur
        gna.stop()
        gnc.stop()
        stop_event.set()
        print("Terminated by user")

# Point d'entrée du programme
if __name__ == "__main__":
    main()
