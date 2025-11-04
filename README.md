Crear/activar el virtualenv e instalar Flask
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install flask

Levantar la versión vulnerable:
python app_legit_vuln.py

Servir la página maliciosa (en otra terminal, desde la misma carpeta o desde una carpeta que contenga evil.html):
py -3 -m http.server 8000 --bind localhost


En navegador:

Abrí http://localhost:5000/login. Logueá con alice / password.

Ve a http://localhost:5000/profile y guardá captura de pantalla (muestra email alice@example.com).

En otra pestaña del mismo navegador abrí http://localhost:6000/evil.html.
Al cargar la página, el formulario se auto-envía.

Volvé a http://localhost:5000/profile → verás que el email cambió a evil@attacker.com. Captura de pantalla.


Comprobación con curl (alternativa)
Obtener cookie de sesión con curl es un poco más largo; ejemplo:
# login con curl y guardar cookies en cookies.txt
curl -c cookies.txt -d "username=alice&password=password" -X POST http://localhost:5000/login -L
# luego usar cookie para POST al endpoint vulnerable
curl -b cookies.txt -d "new_email=evil@attacker.com" -X POST http://localhost:5000/change-email -v

Logs en servidor: en la terminal donde corre Flask verás algo como (Guarda ese log como evidencia.) :
[VULN] change-email called for user 1 -> evil@attacker.com


Detener la app vulnerable (Ctrl+C) y lanzar la parcheada:
python app_legit_csrf.py
En el navegador limpiar cookies del dominio localhost (importante) o abrir ventana privada/incógnito para que sesión sea limpia.

Acceder a http://localhost:5000/login y loguear alice/password.

Ir a http://localhost:5000/profile y verás que el formulario incluye un campo oculto csrf_token (puedes ver código fuente de la página o inspeccionar elemento).

Abrir http://localhost:6000/evil.html en otra pestaña (mismo navegador). El evil.html intentará enviar el POST sin token.

Volver a http://localhost:5000/profile → el email NO habrá cambiado.

En la terminal del servidor parcheado verás un log de bloqueo similar a: [CSRF BLOCK] token invalid. got= expected=<some token>


