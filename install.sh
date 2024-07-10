#!/bin/bash

# Ruta del repositorio
REPO_URL="https://github.com/Tlaloc-Es/IberdrolaPVPCSystrayUnix"

# Directorio donde se clonará el repositorio
INSTALL_DIR="$HOME/.IberdrolaPVPCSystrayUnix"

# Clonar el repositorio
echo "Clonando el repositorio..."
if [ -d "$INSTALL_DIR" ]; then
    echo "El directorio ya existe. Actualizando el repositorio..."
    cd "$INSTALL_DIR" && git pull origin master
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r "$INSTALL_DIR/requirements.txt"

# Crear un archivo .desktop en el directorio de autostart
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

DESKTOP_ENTRY="[Desktop Entry]
Type=Application
Exec=python $INSTALL_DIR/iberdrola_checker.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=IberdrolaPVPCSystray
Comment=Aplicación para mostrar los precios de la electricidad de Iberdrola en la bandeja del sistema"

echo "$DESKTOP_ENTRY" > "$AUTOSTART_DIR/IberdrolaPVPCSystray.desktop"

echo "Instalación completada. La aplicación se ejecutará automáticamente al iniciar sesión."
