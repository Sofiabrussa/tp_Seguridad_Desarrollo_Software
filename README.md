--- Laboratorio CSRF — Vulnerable vs Parcheado ---

---- Demostrar parte vulnerable ----
Crear/activar el virtualenv e instalar Flask
1) .\venv\Scripts\Activate.ps1
2) pip install flask
3) Levantar la versión vulnerable: python app_legit_vuln.py
4) Iniciar sesion, ver que tiene cierto mail
5) Abrir en otra pestaña: http://localhost:5000/change-email, se va a enviar automaticamente el hack para cambiar de mail e informa: Email cambiado 
6) Volver a http://localhost:5000/profile y recargar pagina, se ve que el mail se cambio por evil 

---- Para demostrar la app no vulnerable ----
7) Detener la app vulnerable (Ctrl+C) y lanzar la parcheada: python app_legit_csrf.py
8) En el navegador limpiar cookies del dominio localhost (importante) o abrir ventana privada/incógnito para que sesión sea limpia.
9) Acceder a http://localhost:5000/login y loguear alice/password.
10) Ir a http://localhost:5000/profile y hay un campo oculto csrf_token (inspeccionar elemento).
11) Abrir http://localhost:5000/change-email en otra pestaña (mismo navegador). El evil.html intentará enviar el POST sin token.
12) Volver a http://localhost:5000/profile → el email NO cambio.
13) En la terminal del servidor parcheado aparece un log de bloqueo similar a: [CSRF BLOCK] token invalid. got= expected=<some token>


Para repetir la demo desde cero, borrar users.db y reiniciar la aplicación para que init_db() regenere la base de datos con los valores por defecto.

