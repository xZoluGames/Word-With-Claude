#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador de Directorios - Crea estructura de directorios necesaria
"""

import os
import shutil
from datetime import datetime

def crear_estructura_directorios():
    """Crea la estructura de directorios necesaria para el proyecto"""
    print("🏗️ CONFIGURANDO ESTRUCTURA DE DIRECTORIOS\n")
    
    # Obtener directorio base del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = script_dir
    
    # Directorios a crear
    directorios = [
        "resources",
        "resources/images",
        "plantillas",
        "backups",
        "exports"
    ]
    
    created_dirs = []
    
    for directorio in directorios:
        ruta_completa = os.path.join(base_dir, directorio)
        
        if not os.path.exists(ruta_completa):
            try:
                os.makedirs(ruta_completa)
                created_dirs.append(directorio)
                print(f"✅ Creado: {directorio}/")
            except Exception as e:
                print(f"❌ Error creando {directorio}: {e}")
        else:
            print(f"📁 Ya existe: {directorio}/")
    
    # Migrar imágenes si existen en Recursos
    migrar_imagenes_recursos(base_dir)
    
    print(f"\n🎉 CONFIGURACIÓN COMPLETADA")
    if created_dirs:
        print(f"📂 Directorios creados: {len(created_dirs)}")

def migrar_imagenes_recursos(base_dir):
    """Migra imágenes del directorio Recursos al nuevo resources/images"""
    recursos_viejo = os.path.join(base_dir, "Recursos")
    recursos_nuevo = os.path.join(base_dir, "resources", "images")
    
    if os.path.exists(recursos_viejo):
        print(f"\n🔄 MIGRANDO IMÁGENES DE {recursos_viejo}")
        
        archivos_migrados = 0
        for archivo in os.listdir(recursos_viejo):
            if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                origen = os.path.join(recursos_viejo, archivo)
                destino = os.path.join(recursos_nuevo, archivo)
                
                try:
                    if not os.path.exists(destino):
                        shutil.copy2(origen, destino)
                        print(f"   📋 Migrado: {archivo}")
                        archivos_migrados += 1
                    else:
                        print(f"   ⏭️ Ya existe: {archivo}")
                except Exception as e:
                    print(f"   ❌ Error migrando {archivo}: {e}")
        
        if archivos_migrados > 0:
            print(f"✅ {archivos_migrados} archivo(s) migrado(s) exitosamente")

if __name__ == "__main__":
    crear_estructura_directorios()
