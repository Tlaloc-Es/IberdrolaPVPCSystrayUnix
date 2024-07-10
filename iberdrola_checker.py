import sys
import requests
import json
import fcntl
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, QTime
from PIL import Image, ImageDraw, ImageFont
import io
import os

# Ruta del archivo de bloqueo
LOCK_FILE = '/tmp/IberdrolaPVPCSystray.lock'

def create_text_icon(text, size, color):
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    
    try:
        font_size = size
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    text_bbox = d.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2)
    
    d.text(position, text, font=font, fill=color)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qimage = QPixmap()
    qimage.loadFromData(buffer.getvalue(), "PNG")
    return QIcon(qimage)

def fetch_and_parse_data():
    url = "https://www.iberdrola.es/o/PreciosLuzController/getDatosPreciosLuzHoy"
    
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading the data: {e}")
        return []
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        return []
    
    return data.get('entidad', {}).get('values', [])

def main():
    # Crear archivo de bloqueo
    with open(LOCK_FILE, 'w') as lockfile:
        try:
            fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            print("La aplicación ya está en ejecución.")
            sys.exit(1)

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        # Fetch and parse the data
        data = fetch_and_parse_data()
        
        if not data:
            print("No data available.")
            sys.exit(1)
        
        # Sort data by value
        sorted_data = sorted(data, key=lambda x: x['value'])
        
        # Determine price ranges
        top_8_cheapest = {item['value'] for item in sorted_data[:8]}
        next_8_cheapest = {item['value'] for item in sorted_data[8:16]}

        # Create the tray icon
        tray_icon = QSystemTrayIcon()
        
        def update_icon():
            current_hour = QTime.currentTime().hour()
            price_info = data[current_hour]
            price = price_info['value'] * 100  # Convert to cents for display
            
            if price_info['value'] in top_8_cheapest:
                color = (0, 255, 0, 255)  # Green
            elif price_info['value'] in next_8_cheapest:
                color = (255, 165, 0, 255)  # Orange
            else:
                color = (255, 0, 0, 255)  # Red

            text_icon = create_text_icon(f"{int(price)}", 128, color)  # Tamaño ajustado
            tray_icon.setIcon(text_icon)
        
        timer = QTimer()
        timer.timeout.connect(update_icon)
        timer.start(60000)  # Update every minute

        # Create the menu
        menu = QMenu()
        
        # Add actions to the menu
        quit_action = QAction("Exit")
        quit_action.triggered.connect(app.quit)

        menu.addAction(quit_action)

        # Assign the menu to the tray icon
        tray_icon.setContextMenu(menu)

        # Show the tray icon
        tray_icon.show()

        update_icon()  # Call initially to set up the first icon

        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
