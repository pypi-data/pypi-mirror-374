"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "KeystackUI.wsgi:application"

# The granularity of Error log outputs
loglevel = "debug"

# The number of worker processes for handling requests
workers = 2

# The socket to bind
bind = "0.0.0.0:28028"

# Restart workers when code changes (development only!)
reload = True

# Write access and error info to /var/log
#accesslog = errorlog = "/var/log/gunicorn/keystackWsgi.log"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"

# Redirect stdout/stderr to log file
capture_output = True

# PID file so you can easily fetch process ID
#pidfile = "/var/run/gunicorn/keystackWsgi.pid"
pidfile = "/var/run/keystackWsgi_gunicorn.pid"

# Daemonize the Gunicorn process (detach & enter background)
daemon = False
