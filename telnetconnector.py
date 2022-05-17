

import os
import sys
import time
import socket
import threading
import subprocess

def clearscreen():
    os.system('clear')

def banner():
    clearscreen()
    print("""
    #############################################
    #                                           #
    #    ____  ____  ____  ____  ____  ____     #
    #   |    \|    \|    \|    \|    \|    \    #
    #   |  o  )  o  )  o  )  o  )  o  )  o  )   #
    #   |   _/|   _/|   _/|   _/|   _/|   _/    #
    #   |  |  |  |  |  |  |  |  |  |  |  |      #
    #   |  |  |  |  |  |  |  |  |  |  |  |      #
    #   |  |  |  |  |  |  |  |  |  |  |  |      #
    #   |__|  |__|  |__|  |__|  |__|  |__|      #
    #                                           #
    #                                           #
    #############################################
    """)

def menu():
    print("""
    #############################################
    #                                           #
    #   [1] Scan                                #
    #   [2] Connect                             #
    #   [3] Exit                                #
    #                                           #
    #############################################
    """)

def scan():
    ip = input("Enter IP: ")
    os.system("nmap -A " + ip)
    main_thread()

def connect():
    host = input("Enter Host: ")
    port = input("Enter Port: ")
    os.system("telnet " + host + " " + port)

def main():
    banner()
    menu()
    choice = input("Enter Choice: ")
    if choice == "1":
        scan()
    elif choice == "2":
        connect()
    elif choice == "3":
        sys.exit()
    else:
        print("Invalid Choice")
        time.sleep(2)
        main()

def main_thread():
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        time.sleep(1)
        sys.exit()

try :
    main_thread()
except Exception as e:
    print(e)
    time.sleep(1)
    sys.exit()
