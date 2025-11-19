# Laboratorio CSRF — Vulnerable vs Parcheado

### Activar virtualenv (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

### Instalar todas las dependencias del proyecto
pip install -r requirements.txt


Pasos para demostrar vulnerabilidad:

- Levantar la versión vulnerable: python app_legit_vuln.py
- Abrir http://localhost:5000/login, Loguear con alice / password
- Ir al menú “Perfil” → “Ver oferta exclusiva”
- Hacer clic en “Obtener Beneficio”
➡ Cuando se presiona ese botón, la página ejecuta un POST oculto
- El email habrá sido cambiado sin consentimiento.


Pasos para demostrar NO vulnerabilidad:

- Detener la app vulnerable (Ctrl+C) y lanzar: python app_legit_csrf.py
- Acceder a http://localhost:5000/login y loguear alice / password.
- Intentar el ataque: Ir al menú “Perfil” → “Ver oferta exclusiva”
- Presionar “Obtener beneficio”: La página maliciosa envía un POST pero SIN token CSRF, entonces es rechazado.
- Comprobar que NO se modificó el email








