# Laboratorio CSRF — Vulnerable vs Parcheado

### Activar virtualenv (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

### Instalar todas las dependencias del proyecto
pip install -r requirements.txt


Pasos para demostrar vulnerabilidad:

- Levantar la versión vulnerable: python app_legit_vuln.py
- Abrir http://localhost:5000/login, Loguear con alice / password
- Ir a http://localhost:5000/profile y confirmar el email actual
- Abrir en otra pestaña (mismo navegador): http://localhost:5000/change-email → se enviará automáticamente el hack para cambiar el email e informará Email cambiado.
- Volver a http://localhost:5000/profile y recargar la página — se verá que el email se cambió por evil@attacker.com.


Pasos para demostrar NO vulnerabilidad:

- Detener la app vulnerable (Ctrl+C) y lanzar la parcheada: python app_legit_csrf.py
- En el navegador limpiar cookies del dominio localhost (importante) o abrir ventana privada/incógnito para que la sesión sea limpia.
- Acceder a http://localhost:5000/login y loguear alice / password.
- Ir a http://localhost:5000/profile y comprobar que el formulario contiene un campo oculto csrf_token (inspeccionar elemento).
- Abrir http://localhost:5000/change-email en otra pestaña (mismo navegador). El evil.html intentará enviar el POST sin token.
- Volver a http://localhost:5000/profile → el email NO cambió.
- En la terminal del servidor parcheado aparecerá un log de bloqueo similar a: [CSRF BLOCK] token invalid. got= expected=<some token>


> Para repetir la demo desde cero, borrar users.db y reiniciar la aplicación para que init_db() regenere la base de datos con los valores por defecto.




