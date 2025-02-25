#!/bin/bash

# Mostrar los mensajes del kernel relacionados con tty
sudo dmesg | grep tty

# Conectar a la placa M5Stack usando screen
sudo screen /dev/ttyACM0 115200