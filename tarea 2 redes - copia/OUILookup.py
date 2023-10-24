#imports necesarios para el funcionamiento del codigo
import getopt
import sys
from getmac import get_mac_address
import subprocess

# Nombre del archivo de base de datos OUI (Organizationally Unique Identifier)
OUI_DATABASE_FILE = 'manuf.txt'

# Función para obtener los datos de fabricación de una tarjeta de red por IP
def obtener_datos_por_ip(ip, database):
    try:
        mac = get_mac_address(ip=ip)
        if mac:
            return mac, solicitudDB(mac)
        else:
            return None, "Error: No se pudo obtener la dirección MAC para la IP: " + ip
    except Exception as e:
        return None, str(e)

# Función para obtener los datos de fabricación de una tarjeta de red por MAC
def obtener_datos_por_mac(mac, database):
    return mac, solicitudDB(mac)

# Función para mostrar la tabla ARP
def mostrar_tabla_arp():
    try:
        arp_table = subprocess.check_output(["arp", "-a"], universal_newlines=True)
        print(arp_table)
    except subprocess.CalledProcessError:
        print("No se pudo obtener la tabla ARP.")
    except FileNotFoundError:
        print("El comando 'arp' no está disponible en tu sistema.")

# Función para buscar información en la base de datos OUI
def solicitudDB(mac):
    mac = mac[:8]
    with open(OUI_DATABASE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(mac):
                parts = line.strip().split()
                if len(parts) > 1:
                    mac = parts[0]
                    vendor = ' '.join(parts[1:])
                    return vendor
    return "No se encontró información en la base de datos."

def main(argv):
    ip = None
    mac = None
    show_arp = False

    try:
        opts, args = getopt.getopt(argv, "hi:m:", ["ip=", "mac=", "arp", "help"])

    except getopt.GetoptError:
        print("Uso: python OUILookup.py --ip <IP> --mac <MAC> --arp [--help]")
        sys.exit(2)

    for opt, arg in opts: #ciclo for que muestra las opciones help
        if opt in ("-h", "--help"):
            print("Uso: python OUILookup.py --ip <IP> --mac <MAC> --arp [--help]")
            print("--ip: IP del host a consultar.")
            print("--mac: MAC address a consultar.")
            print("--arp: Muestra la tabla ARP.")
            sys.exit()

        if opt in ("-i", "--ip"):
            ip = arg

        if opt in ("-m", "--mac"):
            mac = arg

        if opt == "--arp":
            show_arp = True

    if show_arp: 
        mostrar_tabla_arp()
    elif ip:
        mac, vendor = obtener_datos_por_ip(ip, OUI_DATABASE_FILE)
        if mac:
            print(f"IP address: {ip}")
            print(f"MAC address: {mac}")
            print(f"Fabricante: {vendor}")
        else:
            print(f"Error: {vendor}")
    elif mac:
        mac, vendor = obtener_datos_por_mac(mac, OUI_DATABASE_FILE)
        print(f"MAC address: {mac}")
        print(f"Fabricante: {vendor}")
    else:
        print("Debe proporcionar una opción válida (--ip, --mac, --arp, o --help.")

if __name__ == "__main__":
    main(sys.argv[1:])