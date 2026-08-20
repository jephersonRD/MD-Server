<div align="center">

![MD Server](https://img.shields.io/badge/MD%20Server-v1.1.4--beta-cyan?style=for-the-badge)
[![Termux](https://img.shields.io/badge/Platform-Termux%20%28Android%29-3b9e46?style=for-the-badge)](https://termux.dev)
[![Java](https://img.shields.io/badge/Java-21%20%2F%2017-e76f00?style=for-the-badge)](https://adoptium.net)
[![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)](LICENSE)

<br/>

```
 ███╗   ███╗██████╗   ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗
 ████╗ ████║██╔══██╗  ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
 ██╔████╔██║██║  ██║  ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
 ██║╚██╔╝██║██║  ██║  ╚════██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██╔══██╗
 ██║ ╚═╝ ██║██████╔╝  ███████║███████╗██║  ██║╚██████╔╝███████╗██║  ██║
 ╚═╝     ╚═╝╚═════╝   ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
```

**Convierte tu teléfono Android en un servidor de Minecraft Java.**
**Turn your Android phone into a Minecraft Java server.**

</div>

---

## 📥 Zona de descarga | Download zone

Copia **una** de estas líneas en Termux y pulsa Enter (**este es el código que pegarás en Termux** / **this is the code you paste in Termux**):

**Método 1 — un solo comando (recomendado / recommended):**

```bash
curl -fsSL https://raw.githubusercontent.com/jephersonRD/MD-Server/main/install.sh | bash
```

**Método 2 — desde GitHub:**

```bash
pkg update -y && pkg install -y git python && cd ~ && if [ -d MD-Server/.git ]; then cd MD-Server && git pull --ff-only; else git clone --depth 1 https://github.com/jephersonRD/MD-Server.git && cd MD-Server; fi && bash install.sh
```

> ⚠️ El instalador es **reutilizable y seguro**: puedes ejecutarlo todas las veces que quieras. Detecta si es la primera instalación, si ya tienes una versión antigua o nueva, si faltan dependencias o si una instalación quedó a medias, y lo resuelve automáticamente **sin borrar nunca tus servidores, mundos, mods ni ajustes** (esos viven en `~/mdserver/`, no en la carpeta del código).

> ℹ️ La primera vez te preguntará el idioma y guía todo el proceso. Al abrir MD Server verás el menú principal: **[1] Crear servidor**, **[2] Mis servidores**, **[3] Configuración**, **[4] Salir**.
> ℹ️ On first use it asks for your language and guides you through the entire process. When you open MD Server you'll see the main menu: **[1] Create Server**, **[2] My Servers**, **[3] Settings**, **[4] Exit**.
>
> 🆕 **v1.1.4-beta**: la consola ya no se rompe con texto raro de Minecraft (se imprime siempre como texto literal, sin errores de markup) y el lector de consola nunca se detiene por una línea problemática. Detecta automáticamente la **entrada y salida de jugadores** y muestra paneles azules **🔵 JUGADOR CONECTADO / 🔵 JUGADOR DESCONECTADO** (compatible con formatos antiguos tipo 1.7.10 `<Steve>[/127.0.0.1:port] logged in` y modernos `<Steve> joined the game`), una sola vez por evento y sin inventar direcciones. En **Crear servidor**, Fabric y Forge aparecen como **PRÓXIMAMENTE** (solo Vanilla está disponible por ahora) y el menú del servidor se adapta al tipo: Vanilla sin opciones de Mods/Plugins, Fabric/Forge con ellas, renumeradas automáticamente (detección de tipo también para servidores antiguos).
> 🆕 **v1.1.3**: cuando el servidor Minecraft termina de iniciar (`Done ...!`), MD Server muestra automáticamente un panel **✓ SERVIDOR ONLINE** con las direcciones de conexión (`127.0.0.1:PUERTO` y la IP de la red local detectada) justo antes del prompt de la consola. **v1.1.2**: gestión completa de servidores — menú principal con **Mis servidores** (ver, iniciar, detener, consola, información, configuración, renombrar y eliminar con doble confirmación). Detecta automáticamente los servidores creados en versiones anteriores. **v1.1.1**: selector de versiones corregido (escribe 1.7.10, 1.12.2, 1.16.5 sin volver al menú), mensajes claros cuando Mojang no responde (lista local de respaldo) y aviso si la versión requiere Java 8 (no disponible en Termux). **v1.1.0**: instalador y actualizador automático. **v1.0.1**: menús 100% numéricos y RAM por número.

---

## 📋 Requisitos | Requirements

- 📱 Dispositivo **Android** (recomendado 4 GB+ de RAM) o cualquier sistema Linux/POSIX.
- 🧪 **Termux** (desde F-Droid o GitHub) y permisos de almacenamiento.
- 🌐 Conexión a Internet (al menos al crear el servidor).

*MD Server instala automáticamente lo que falte (Python, paquetes y Java).*

---

## ▶️ Abrir MD Server | Open MD Server

**`mdserver` es el comando global** que abre MD Server desde **cualquier directorio** de Termux.

```bash
mdserver
```

Ejemplos:

```bash
cd ~
mdserver
```

```bash
cd ~/storage/downloads
mdserver
```

> No necesitas entrar manualmente a la carpeta `MD-Server` ni recordar rutas: escribe `mdserver` y listo.

### 🤖 Instalación automática
- Si la carpeta `MD-Server` **no existe**, se clona desde GitHub.
- Si ya existe un repo Git, se **actualiza** automáticamente.
- Si la carpeta está dañada o no es MD Server, se **respalda** (`MD-Server.old-FECHA`) y se instala de nuevo — nunca borra datos sin avisar.
- Si **faltan dependencias** (git, Python, rich, requests), las instala.
- Si una **instalación quedó a medias**, se repara en la siguiente ejecución.
- Las descargas se comprueban y el proceso se puede volver a ejecutar aunque hubo un error de red.

---

## 🖥️ Mis servidores | My Servers

Al abrir MD Server verás el menú principal:

```
[1] Crear servidor
[2] Mis servidores
[3] Configuración
[4] Salir
```

Con **[2] Mis servidores** puedes gestionar todos tus servidores desde una sola pantalla:

- Ver **todos los servidores** creados con su versión, tipo y estado (● ONLINE / ○ OFFLINE).
- **Iniciar / Detener / Reiniciar** cada servidor.
- **Consola** en vivo con comandos de Minecraft.
- **Información**: nombre, versión, tipo, estado, puerto, carpeta y (si está ONLINE) las direcciones local, LAN e Internet.
- **Configuración** del servidor (MOTD, jugadores, gamemode, dificultad, PvP, modo online).
- **Renombrar** el servidor sin tocar sus archivos internos.
- **Eliminar** con doble confirmación: se muestra exactamente qué se borrará y hay que escribir `ELIMINAR` para confirmar. Nunca borra otros servidores. Si el servidor está ONLINE, primero pide detenerlo.

Los servidores creados con versiones anteriores de MD Server se **detectan automáticamente** — no tienes que volver a crearlos. Todo vive en `~/mdserver/servers/`.


## 🗑️ Desinstalación | Uninstall

El código y el comando viven en rutas separadas de tus datos.

```bash
# Quitar el comando global y el código (Termux)
rm -f "$PREFIX/bin/mdserver"
rm -rf ~/MD-Server

# Quitar TODOS tus datos de servidores (mundos, mods, backups, ajustes)
rm -rf ~/mdserver
```
---

## 📶 Conexión | Connection

- **LAN:** jugadores en la misma red Wi-Fi se conectan a `IP_local:25565`.
- **Pública:** MD Server detecta tu IP pública, pero **si tu router usa CGNAT o el puerto no está abierto, no permitirá conexiones externas**.
- **Externa sin puertos:** desde la sección *Conexión externa* puedes instalar **Playit.gg** o **Tailscale** y compartir un enlace público con tus amigos.

---


## 🔒 Seguridad | Security

- Todas las descargas provienen de **fuentes oficiales** (Mojang `piston-meta`, `meta.fabricmc.net`, Maven de MinecraftForge) sobre **HTTPS**.
- Los servidores de Vanilla se verifican contra su **SHA-1** oficial.
- No se ejecutan scripts de Internet sin validación.
- Se pide **confirmación** antes de borrar o sobrescribir mundos, mods o servidores.

---

## ⚠️ Limitaciones reales | Real limitations

- **Los plugins** (Bukkit/Spigot/Paper) **no son compatibles** con Vanilla/Fabric/Forge; MD Server lo informa y no crea carpetas falsas.
- La conexión pública depende de tu red (CGNAT/puertos); MD Server lo explica sin prometer imposibles.
- El rendimiento depende del hardware del teléfono (la RAM y CPU determinan cuántos jugadores soportas).

---

## 🧪 Cómo está construido | Built with

- **Python 3** — portabilidad total en Termux.
- **Rich** — interfaz TUI profesional (paneles, tablas, barras de progreso, spinners).
- **Requests / urllib** — descargas robustas con reintentos.
- **OpenJDK** (Termux) — Java 21/17 según la versión de Minecraft.

---

<div align="center">

**Hecho para la comunidad · Made for the community** 🌍

⭐ Si te sirve, dale una estrella. | If this helped you, please star the repo.

</div>
