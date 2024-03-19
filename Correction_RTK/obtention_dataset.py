from pygnssutils import GNSSNTRIPClient
from gnssapp_silent import GNSSSkeletonApp
from queue import Queue
from threading import Event

# Paramètres de configuration pour la communication NTRIP
NTRIP_HOST = '92.245.148.38'
NTRIP_PORT = 2101
NTRIP_MOUNTPOINT = 'B612_RTK_CORR'

# File d'attente pour recevoir les données brutes RTCM3
recv_queue = Queue()

# Événement pour arrêter le programme de manière propre
stop_event = Event()

def main():
    try:
        print(f"Starting NTRIP client on {NTRIP_HOST}:{NTRIP_PORT}...\n")
        with GNSSNTRIPClient(logtofile=1, logpath='logs', verbosity=1) as gnc:
            streaming = gnc.run(
                ipprot="IPv4",
                server=NTRIP_HOST,
                port=NTRIP_PORT,
                mountpoint=NTRIP_MOUNTPOINT,
                output=recv_queue,  # Recevoir les données NTRIP
            )
            while streaming and not stop_event.is_set():
                # Récupérer et afficher les données brutes RTCM3
                data = recv_queue.get()
                print(data.hex())  # Afficher les données brutes en hexadécimal

    except KeyboardInterrupt:
        gnc.stop()
        stop_event.set()
        print("Terminated by user")

if __name__ == "__main__":
    main()
