Proyecto: MD Server — Minecraft Java Server Manager para Termux

Quiero que desarrolles MD Server, una herramienta completa para crear, configurar, administrar y ejecutar servidores de Minecraft Java directamente desde Android usando Termux.

⚠️ IMPORTANTE

Esto NO es una aplicación Android/APK.

NO quiero una aplicación gráfica Android.

Quiero que desarrolles código ejecutable directamente desde Termux, pensado específicamente para Android.

La herramienta debe funcionar mediante una interfaz CLI/TUI moderna, visualmente atractiva, intuitiva y profesional, aprovechando colores, paneles, iconos Unicode/ASCII, animaciones, barras de progreso y demás elementos que sean compatibles con Termux.

El objetivo es que una persona pueda instalar el proyecto en Termux y, sin necesidad de conocimientos técnicos avanzados, crear un servidor de Minecraft Java completo.

---

1. Nombre del proyecto

El nombre será:

MD Server

La interfaz debe mostrar este nombre de forma prominente.

Quiero un encabezado/banner profesional en la terminal.

Ejemplo conceptual:

╔══════════════════════════════════════════════════════╗
║                                                      ║
║                  ███╗   ███╗██████╗                 ║
║                  ████╗ ████║██╔══██╗                ║
║                  ██╔████╔██║██║  ██║                ║
║                  ██║╚██╔╝██║██║  ██║                ║
║                  ██║ ╚═╝ ██║██████╔╝                ║
║                                                      ║
║                  M D   S E R V E R                  ║
║                                                      ║
║           Minecraft Java Server Manager             ║
╚══════════════════════════════════════════════════════╝

No copies exactamente este diseño si puedes crear algo mucho mejor.

Quiero que el banner tenga una apariencia 3D/profesional, utilizando ASCII art, sombras, degradados de terminal, colores y otros recursos compatibles con Termux.

Debe parecer una herramienta moderna de 2026, no un script básico.

---

2. Selección de idioma

Al iniciar MD Server, la primera pantalla debe permitir seleccionar el idioma:

Select language / Selecciona el idioma

[1] 🇪🇸 Español
[2] 🇺🇸 English

Todo el programa debe funcionar completamente en:

- Español
- Inglés

No debe haber textos mezclados accidentalmente entre ambos idiomas.

La selección debe guardarse para que el usuario no tenga que elegir el idioma cada vez que inicia el programa.

También debe existir una opción posteriormente para cambiar el idioma.

---

3. Analizar automáticamente el dispositivo

Antes de crear el servidor, MD Server debe analizar automáticamente el teléfono.

Debe detectar como mínimo:

- RAM total
- RAM disponible
- Arquitectura CPU
- número de núcleos/hilos cuando sea posible
- versión de Android
- versión de Termux
- almacenamiento disponible
- espacio utilizado
- espacio libre
- arquitectura ARM/ARM64/etc.
- versión de Java instalada
- versión de Python si es necesaria
- conexión a Internet

Mostrar la información de forma profesional.

Ejemplo:

╭──────────── DEVICE INFORMATION ────────────╮
│ RAM:          8 GB                          │
│ Available:    5.7 GB                        │
│ CPU:          8 cores                       │
│ Architecture: ARM64                         │
│ Android:      13                            │
│ Storage:      128 GB                        │
│ Free:         62 GB                         │
│ Java:         21                            │
│ Internet:     Connected ✓                   │
╰─────────────────────────────────────────────╯

---

4. Recomendación automática de RAM

El programa debe calcular cuánto RAM debería utilizar el servidor.

Por ejemplo:

- dispositivos con poca RAM → asignación conservadora
- dispositivos con RAM media → asignación moderada
- dispositivos con mucha RAM → mayor asignación

Nunca debe asignar prácticamente toda la RAM del teléfono.

Debe dejar memoria suficiente para Android y Termux.

El usuario también debe poder modificar manualmente la cantidad.

Ejemplo:

Recommended server RAM: 3072 MB

[1] Use recommended amount
[2] Choose manually

Si el usuario selecciona manualmente una cantidad peligrosa, mostrar una advertencia.

---

5. Crear servidor Minecraft Java

El usuario debe poder elegir:

Create Minecraft Server

[1] Vanilla
[2] Fabric
[3] Forge

Opcionalmente, si técnicamente es viable:

[4] NeoForge

Pero no implementes opciones que realmente no puedan funcionar correctamente.

---

6. Selección de versión de Minecraft

Debe permitir seleccionar la versión de Minecraft Java.

Por ejemplo:

Minecraft Version

[1] 1.21.x
[2] 1.20.6
[3] 1.20.4
[4] 1.20.1
[5] 1.19.4
...

La lista debe obtenerse dinámicamente de fuentes oficiales o confiables cuando sea posible.

NO quiero una lista falsa o escrita manualmente que quede obsoleta.

Si hay conexión a Internet, MD Server debe consultar las versiones disponibles.

---

7. Descargar automáticamente todo lo necesario

Una de las funciones principales de MD Server es que el usuario no tenga que descargar manualmente los componentes.

Dependiendo de la configuración seleccionada, debe descargar automáticamente:

- Minecraft server
- Fabric
- Forge
- NeoForge si está implementado
- Java compatible
- libraries necesarias
- archivos necesarios del servidor

Debe comprobar:

- conexión
- espacio disponible
- compatibilidad
- arquitectura
- versión de Java

Antes de comenzar una descarga importante.

---

8. Sistema profesional de descargas

NO quiero una barra de progreso básica como:

Downloading... 50%
██████████

Quiero una interfaz mucho más profesional.

Debe mostrar:

╭────────────── DOWNLOAD ──────────────╮
│ Minecraft Server                     │
│                                      │
│ ███████████████████░░░░░  78%       │
│                                      │
│ 142.5 MB / 182.3 MB                  │
│ 8.4 MB/s                             │
│ ETA: 00:05                           │
│                                      │
│ Status: Downloading                  │
╰──────────────────────────────────────╯

La barra debe actualizarse en tiempo real.

Cuando haya varios archivos:

Downloading components

✓ Minecraft Server
✓ Libraries
◉ Fabric Loader
○ Dependencies
○ Configuration

También debe mostrar:

- tamaño
- progreso
- velocidad
- ETA
- archivo actual
- porcentaje
- estado

Si una descarga falla, debe intentar recuperarla de forma segura.

---

9. Estructura automática del servidor

Al crear el servidor debe generar automáticamente una estructura organizada.

Ejemplo:

MDServer/
└── servers/
    └── MyServer/
        ├── server.jar
        ├── server.properties
        ├── eula.txt
        ├── world/
        ├── mods/
        ├── plugins/
        ├── config/
        ├── logs/
        ├── backups/
        └── libraries/

La estructura debe adaptarse dependiendo de si el servidor es Vanilla, Fabric o Forge.

No crear carpetas innecesarias cuando no correspondan.

---

10. Gestión de mundos

Debe existir un menú:

World Management

[1] Create new world
[2] Import world
[3] Delete world
[4] Backup world
[5] Restore backup
[6] Set active world

El usuario debe poder colocar/importar un mundo existente.

Por ejemplo, MD Server puede crear una carpeta de importación:

MDServer/import/worlds/

El usuario coloca ahí su mundo y después selecciona:

Import World

El programa debe detectar automáticamente el mundo y configurarlo correctamente.

---

11. Gestión de mods

Para Fabric/Forge/NeoForge debe existir:

Mod Manager

[1] Install mod
[2] Remove mod
[3] List installed mods
[4] Open mods folder
[5] Import mod

Debe crear automáticamente:

mods/

El usuario debe poder colocar archivos ".jar" manualmente.

El programa debe detectar los mods instalados.

Cuando sea posible, debe validar:

- versión de Minecraft
- loader
- dependencias
- arquitectura/compatibilidad cuando aplique

Si un mod no corresponde a la versión seleccionada, mostrar una advertencia.

---

12. Gestión de plugins

Para servidores compatibles con plugins debe existir:

Plugin Manager

[1] Install plugin
[2] Remove plugin
[3] List plugins
[4] Open plugins folder
[5] Import plugin

Debe crear automáticamente:

plugins/

Solo debe permitir plugins cuando el software del servidor seleccionado los soporte.

NO quiero que el programa simplemente cree la carpeta y diga que funciona si realmente el servidor seleccionado no soporta plugins.

---

13. Menú principal

Después de crear el servidor, mostrar un dashboard.

Ejemplo:

╭──────────────────── MD SERVER ────────────────────╮
│ Server: My Survival Server                         │
│ Minecraft: 1.20.1                                  │
│ Type: Fabric                                        │
│ RAM: 3072 MB                                       │
│ Players: 0/10                                      │
│ Status: STOPPED                                    │
╰────────────────────────────────────────────────────╯

[1] ▶ Start Server
[2] ■ Stop Server
[3] ↻ Restart Server
[4] 🌍 World Manager
[5] 🧩 Mod Manager
[6] 🔌 Plugin Manager
[7] ⚙ Server Settings
[8] 💾 Backups
[9] 📊 Server Monitor
[10] 🌐 Connection
[11] 📁 File Manager
[12] ⚙ Advanced
[13] ← Back

Haz la interfaz más moderna que este ejemplo.

---

14. Consola del servidor

Cuando el servidor esté ejecutándose debe mostrar una consola en tiempo real.

Debe mostrar:

- logs
- jugadores conectados
- errores
- warnings
- comandos

Por ejemplo:

╭──────────────────── SERVER CONSOLE ────────────────────╮
│ [10:42:01] [Server thread/INFO]: Starting Minecraft... │
│ [10:42:03] [Server thread/INFO]: Done!                  │
│ [10:43:12] [Server thread/INFO]: Steve joined           │
│                                                         │
│ Command > _                                             │
╰─────────────────────────────────────────────────────────╯

El usuario debe poder escribir comandos de Minecraft directamente.

---

15. Monitor del servidor

Crear una sección para monitorear:

- RAM utilizada
- CPU
- TPS cuando sea posible
- jugadores
- uptime
- almacenamiento
- temperatura si Android/Termux permite obtenerla de manera fiable

Ejemplo:

SERVER MONITOR

CPU       ███████░░░  68%
RAM       ██████░░░░  58%
TPS       19.8
PLAYERS   3/10
UPTIME    02:14:32

---

16. Sistema de IP/conexión

Después de iniciar el servidor, MD Server debe detectar automáticamente la información necesaria para que otros jugadores puedan conectarse.

Debe mostrar:

CONNECTION

Local IP:
192.168.1.25

Port:
25565

LAN Address:
192.168.1.25:25565

También debe explicar claramente:

«Players must be connected to the same Wi-Fi network.»

En español:

«Los jugadores deben estar conectados a la misma red Wi-Fi.»

Si técnicamente es posible, detectar también la IP pública.

Pero NO debes afirmar que la IP pública permite conectarse directamente si el router tiene CGNAT o no tiene el puerto abierto.

Debe explicar las limitaciones de NAT/CGNAT.

---

17. Sistema de conexión sin abrir puertos

Si es técnicamente viable, quiero una sección para conexiones externas mediante soluciones como:

- Tailscale
- Playit.gg
- otras alternativas compatibles

Pero debe ser opcional.

La herramienta debe detectar si están instaladas y explicar cómo utilizarlas.

No debe requerir que el usuario tenga conocimientos de redes.

---

18. Crear múltiples servidores

El usuario debe poder tener varios servidores.

Ejemplo:

My Servers

[1] Survival Fabric
    Minecraft 1.20.1
    ● Running

[2] Modded Adventure
    Minecraft 1.21.x
    ● Stopped

[3] Vanilla
    Minecraft 1.16.5
    ● Stopped

[4] + Create New Server

Cada servidor debe estar aislado en su propia carpeta.

---

19. Backups

Debe existir un sistema de backups.

Opciones:

[1] Create backup
[2] Restore backup
[3] Delete backup
[4] Automatic backups

Los backups deben poder incluir:

- mundo
- configuración
- mods
- plugins

No hacer backups innecesariamente gigantes si solamente cambió una configuración.

---

20. Compatibilidad con Termux

El código debe estar diseñado específicamente para Termux.

Debe evitar depender de componentes que normalmente no existen en Android.

Antes de comenzar debe comprobar dependencias.

Si falta algo:

Missing dependency: Java

Installing Java...
████████████████████░░ 92%

Debe instalar automáticamente las dependencias necesarias siempre que sea seguro y posible.

También debe explicar claramente qué está instalando.

---

21. Instalación inicial

Quiero que el proyecto pueda instalarse fácilmente.

Idealmente:

git clone <repository>
cd MDServer
bash install.sh

Después:

mdserver

O:

./mdserver

Si es posible, crear un comando global:

mdserver

---

22. Calidad del código

El proyecto debe estar organizado profesionalmente.

No quiero un único archivo gigante con miles de líneas.

Utiliza una arquitectura modular.

Por ejemplo:

MDServer/
├── main.py
├── core/
│   ├── server_manager.py
│   ├── downloader.py
│   ├── java_manager.py
│   ├── memory_manager.py
│   ├── version_manager.py
│   └── network_manager.py
├── ui/
│   ├── dashboard.py
│   ├── menus.py
│   ├── progress.py
│   └── banner.py
├── managers/
│   ├── world_manager.py
│   ├── mod_manager.py
│   ├── plugin_manager.py
│   └── backup_manager.py
├── locales/
│   ├── es.json
│   └── en.json
├── config/
├── scripts/
├── install.sh
├── requirements.txt
└── README.md

Puedes cambiar esta estructura si existe una arquitectura mejor.

---

23. Interfaz visual

La interfaz es MUY importante.

Quiero una experiencia similar a una herramienta profesional moderna de terminal.

Utiliza, si son apropiadas:

- Rich
- Textual
- Typer
- Click
- tqdm u otra alternativa

Pero elige las librerías realmente adecuadas para Termux.

Quiero:

- paneles
- bordes modernos
- colores
- iconos
- animaciones
- spinners
- barras de progreso
- tablas
- menús
- estados
- mensajes de éxito/error
- transiciones cuando sean posibles

Debe verse bien tanto en una pantalla pequeña de teléfono como en una terminal grande.

No llenes la pantalla con información innecesaria.

---

24. Experiencia para usuarios principiantes

Un usuario que nunca haya creado un servidor debe poder hacer algo como:

Start MD Server

↓
Select language

↓
Device analysis

↓
Select Minecraft version

↓
Select Vanilla / Fabric / Forge

↓
Choose RAM

↓
Download files

↓
Create server

↓
Configure world

↓
Start server

↓
Show connection address

Todo debe estar guiado.

No obligues al usuario a editar manualmente archivos de configuración para realizar las tareas básicas.

---

25. Seguridad

No ejecutes comandos arbitrarios provenientes de Internet sin validación.

Las descargas deben proceder de fuentes confiables.

Valida archivos descargados cuando sea posible mediante:

- SHA-256
- hashes oficiales
- HTTPS

No descargues ejecutables desconocidos simplemente porque una URL lo indique.

Antes de sobrescribir/eliminar mundos, mods o servidores, pide confirmación.

---

26. Manejo de errores

El programa debe manejar correctamente:

- Internet desconectado
- descarga interrumpida
- falta de almacenamiento
- falta de RAM
- Java incompatible
- versión inexistente
- mod incompatible
- dependencia faltante
- servidor cerrado inesperadamente
- puerto ocupado
- permisos de Termux
- archivo corrupto
- error de Forge/Fabric
- mundo corrupto

Los errores deben ser entendibles para un usuario normal.

No mostrar solamente un traceback gigante.

Debe existir una opción:

[View technical details]

para usuarios avanzados.

---

27. No inventar funcionalidades

Si una función no puede implementarse realmente en Android/Termux, NO simules que funciona.

Investiga técnicamente cómo realizar cada función.

Por ejemplo:

- descarga real
- instalación real de loaders
- ejecución real de Java
- detección real de RAM
- detección real de red
- creación real de carpetas
- ejecución real del servidor
- importación real de mundos
- instalación real de mods

Todo debe ser funcional.

---

28. Documentación

Genera un README.md profesional que explique:

- qué es MD Server
- características
- instalación
- requisitos
- compatibilidad
- uso
- creación de servidores
- mods
- mundos
- plugins
- backups
- conexión LAN
- conexión externa
- solución de problemas
- arquitectura del proyecto

Incluye ejemplos reales de comandos.

---

29. Objetivo final

El resultado debe sentirse como:

"Puedo convertir mi teléfono Android en un servidor de Minecraft Java con unos pocos pasos."

El usuario no debería necesitar saber:

- Java
- Linux
- Termux
- servidores
- configuración de mods
- configuración de mundos
- administración avanzada

MD Server debe encargarse de todo lo posible automáticamente.

---

30. Antes de escribir el código

Primero analiza técnicamente todo el proyecto.

Identifica:

1. Qué partes son realmente posibles en Termux/Android.
2. Qué librerías son necesarias.
3. Qué versiones de Java necesita cada versión de Minecraft.
4. Cómo descargar correctamente Vanilla/Fabric/Forge.
5. Cómo detectar RAM y CPU en Android.
6. Cómo ejecutar y detener correctamente Java.
7. Cómo manejar procesos en segundo plano.
8. Cómo detectar IP local.
9. Qué limitaciones existen con conexiones externas.
10. Cómo implementar mods, mundos y plugins correctamente.
11. Cómo hacer la interfaz TUI.
12. Cómo evitar que Android mate el proceso del servidor.

Después de ese análisis, diseña la arquitectura.

No comiences escribiendo código inmediatamente.

Primero presenta el diseño técnico y, después de validarlo, implementa el proyecto completo.

El resultado final debe ser código funcional y ejecutable en Termux, no pseudocódigo ni una demostración.




además al final debes de subir los códigos necesarios al repo que te daré y el tokenn de github para que lo subas y para que crear un .me profesional y un título y descripción y # del proyecto profesional para este proyecto 

además debe d ver una zona de descarga para copiar un código que ese código será el que pagaremos en termux para descargar está herramienta para poder crear el servidor de mc, además si eluser usa el código por primera vez le preguntas está es la primera vez que usa este código ya que si ya había hecho un servidor anteriormente y solo quiere encender ese antiguo servidior lo hagas si tener que haceruno nuevo 
