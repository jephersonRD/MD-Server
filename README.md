<div align="center">

![MD Server](https://img.shields.io/badge/MD%20Server-v1.0.0-cyan?style=for-the-badge)
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

Copia este código en Termux y pulsa Enter (**este es el código que pegarás en Termux** / **this is the code you paste in Termux**):

```bash
pkg update -y && pkg install -y git python && git clone --depth 1 https://github.com/jephersonRD/MD-Server.git && cd MD-Server && bash install.sh && mdserver
```

> ℹ️ La primera vez te preguntará el idioma y guía todo el proceso.
> La primera vez que uses el código, te preguntará si **es tu primera vez** o si **ya tienes un servidor** creado (para encenderlo directamente sin crear uno nuevo).
> ℹ️ On first use it asks for your language and guides you through the entire process.
>
> 🆕 **v1.0.1**: menús 100% numéricos (elige con 1, 2, 3...), RAM por número y soporte de **versiones antiguas** (1.7.10, 1.8.9, etc.) con lista paginada o escritura manual.

---

## ✨ Características | Features

- 🖥️ **Interfaz TUI profesional** con banner 3D, colores, iconos, paneles, barras de progreso en tiempo real y animaciones.
- 🌍 **Bilingüe** (Español / English), se recuerda tu elección.
- 📱 **Análisis automático del dispositivo**: RAM, CPU, arquitectura, Android, Termux, almacenamiento, Java, Python e Internet.
- 🧠 **Recomendación automática de RAM** con advertencias de seguridad (deja siempre memoria libre para Android).
- 🚀 Creación asistida de servidores **Vanilla, Fabric y Forge** (NeoForge cuando es viable).
- 📦 **Descargas automáticas** desde fuentes oficiales (Mojang, FabricMC, MinecraftForge) con validación **SHA-1**.
- 🌍 **Gestión de mundos**: crear, importar, eliminar, copiar, restaurar y cambiar de mundo activo.
- 🧩 **Gestión de mods** (Fabric/Forge) con validación de compatibilidad de versión.
- 💾 **Copias de seguridad** (manuales y automáticas) con compresión gzip.
- 📊 **Monitor del servidor** (RAM/CPU reales del proceso Java, uptime, almacenamiento).
- ⏯️ **Consola en vivo** para enviar comandos de Minecraft y ver logs coloreados.
- 📶 **Sistema de conexión LAN** con detección de IP local y explicación de límites NAT/CGNAT.
- 🔗 **Conexión externa sin abrir puertos** con Playit.gg / Tailscale (opcional).
- 🛡️ **Seguridad**: descargas solo de fuentes confiables, verificación de hashes, confirmaciones antes de borrar y errores en lenguaje claro.

---

## 📋 Requisitos | Requirements

- 📱 Dispositivo **Android** (recomendado 4 GB+ de RAM) o cualquier sistema Linux/POSIX.
- 🧪 **Termux** (desde F-Droid o GitHub) y permisos de almacenamiento.
- 🌐 Conexión a Internet (al menos al crear el servidor).

*MD Server instala automáticamente lo que falte (Python, paquetes y Java).*

---

## 🚀 Instalación | Installation

```bash
pkg update -y
pkg install -y git python
git clone https://github.com/jephersonRD/MD-Server.git
cd MD-Server
bash install.sh
```

Después ejecuta:

```bash
mdserver
```

o directamente:

```bash
./main.py
```

`install.sh` crea el comando global `mdserver` en tu `$PREFIX/bin`.

---

## 👣 Primer uso | First run

1. Selecciona idioma (🇪🇸 Español / 🇺🇸 English).
2. MD Server analiza tu dispositivo (RAM, CPU, almacenamiento, Java, red...).
3. Elige el tipo de servidor: **Vanilla**, **Fabric** o **Forge**.
4. Selecciona la **versión de Minecraft** (se obtiene en vivo de fuentes oficiales).
5. Acepta el tamaño de RAM recomendado (o elígelo tú mismo).
6. MD Server descarga e instala todo automáticamente (con barra de progreso y ETA).
7. ¡Listo! Puedes iniciar el servidor y ver la **consola en vivo**.

> 🔁 Si ya tienes un servidor creado, al abrir MD Server te preguntará si es tu **primera vez** o si prefieres **continuar con tu servidor existente** y encenderlo directamente.

---

## 🖥️ Uso | Usage

Una vez creado el servidor, verás el **panel principal**:

| Opción | Descripción |
| --- | --- |
| `1. ▶ Iniciar / ■ Detener` | Arranca o apaga el servidor |
| `2. ↻ Reiniciar` | Reinicia el servidor |
| `3. ⌥ Consola` | Consola en vivo con comandos de Minecraft |
| `4. 🌍 Mundos` | Crear, importar, borrar, copiar y cambiar de mundo |
| `5. 🧩 Mods` | Instalar, listar, importar y eliminar mods (Fabric/Forge) |
| `6. 🔌 Plugins` | Disponible solo si el software del servidor los soporta |
| `7. ⚙ Ajustes` | MOTD, jugadores máximos, gamemode, dificultad, PvP, online-mode |
| `8. 💾 Copias de seguridad` | Crear, restaurar, eliminar y copias automáticas |
| `9. 📊 Monitor` | RAM/CPU reales del proceso Java, uptime y almacenamiento |
| `10. 🌐 Conexión` | IP local, dirección LAN, IP pública y límites NAT/CGNAT |
| `11. 📁 Archivos` | Ubicaciones de carpetas del servidor |

En la consola escribe comandos de Minecraft (ej. `list`, `say hola`, `op jugador`) o `stop` para apagar el servidor.

---

## 🧩 Mods

- Con **Fabric** o **Forge**, usa `Gestión de mods` para importar archivos `.jar` (se copia todo desde `~/mdserver/import/mods`) o colócalos directamente en la carpeta `mods/` del servidor.
- MD Server avisa si el nombre del mod sugiere una versión de Minecraft distinta a la del servidor.

## 🌍 Mundos

- Crea mundos nuevos desde el menú o **importa** un mundo existente colocándolo en `~/mdserver/import/worlds/`.
- Puedes cambiar el mundo activo (`level-name`) sin tocar archivos.

---

## 📶 Conexión | Connection

- **LAN:** jugadores en la misma red Wi-Fi se conectan a `IP_local:25565`.
- **Pública:** MD Server detecta tu IP pública, pero **si tu router usa CGNAT o el puerto no está abierto, no permitirá conexiones externas**.
- **Externa sin puertos:** desde la sección *Conexión externa* puedes instalar **Playit.gg** o **Tailscale** y compartir un enlace público con tus amigos.

---

## 🛠️ Solución de problemas | Troubleshooting

| Problema | Solución |
| --- | --- |
| `Java no instalado` | MD Server lo instala automáticamente con `pkg install openjdk-21` (o `openjdk-17` para versiones viejas). |
| Error `No internet` | Conecta el dispositivo a una red con datos/Wi-Fi antes de crear el servidor. |
| `No hay espacio` | Libera almacenamiento; MD Server comprueba espacio antes de cada descarga. |
| El servidor no inicia | Revisa en la consola el mensaje de error; suele ser RAM demasiado baja o Java incorrecto. |
| Android mata el proceso | Usa la consola de MD Server (no salgas de la app) y evita el modo de ahorro de batería para Termux. |
| Puerto ocupado | Cambia `server-port` en Ajustes del servidor. |

---

## 🏗️ Arquitectura | Architecture

```
MD-Server/
├── main.py              # Punto de entrada (idioma, primera vez, selector de servidores)
├── wizard.py            # Asistente guiado de creación
├── install.sh           # Instalador (crea el comando global `mdserver`)
├── requirements.txt
├── locales/
│   ├── es.json          # Traducciones español
│   └── en.json          # Traducciones inglés
├── core/
│   ├── config.py        # Rutas, estado, metadatos
│   ├── i18n.py          # Carga de idiomas
│   ├── device_info.py   # Análisis del dispositivo
│   ├── memory_manager.py# Recomendación/validación de RAM
│   ├── version_manager.py # Versiones de Mojang/Fabric/Forge
│   ├── downloader.py    # Descargas con progreso y verificación SHA-1
│   ├── server_manager.py# Crear/iniciar/detener/reiniciar servidores
│   ├── java_manager.py  # Detección e instalación de Java
│   └── network_manager.py # IP local/pública y herramientas externas
├── managers/
│   ├── world_manager.py # Gestión de mundos
│   ├── mod_manager.py   # Gestión de mods
│   ├── plugin_manager.py# Gestión de plugins
│   └── backup_manager.py# Copias de seguridad
└── ui/
    ├── banner.py        # Banner 3D animado
    ├── menus.py         # Menús, prompts y paneles
    ├── progress.py      # Barras de progreso profesionales
    ├── dashboard.py     # Panel principal por servidor
    ├── console_view.py  # Consola en vivo
    └── manager_menus.py # Menús de mundos/mods/backups/ajustes/monitor/conexión
```

Los datos se guardan en `~/mdserver/`:

```
~/mdserver/
├── servers/<nombre>/    # Cada servidor aislado en su carpeta
│   ├── server.jar
│   ├── server.properties
│   ├── eula.txt
│   ├── world/  mods/  plugins/  config/  logs/  backups/
├── import/worlds/      # Coloca aquí mundos para importar
├── import/mods/        # Coloca aquí mods para importar
├── backups/<servidor>/ # Copias de seguridad
└── config/config.json  # Preferencias (idioma, etc.)
```

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