#!/usr/bin/env python3
"""Serveur local Go Project — reproduit les URLs propres de la production.

    python serve.py            (port 8123)
    python serve.py 3000

Sert /contact depuis contact.html, / depuis index.html, exactement comme
le fera le .htaccess en ligne. Indispensable pour tester en local, sinon
les liens sans .html renvoient une 404.
"""
import http.server
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8123

# Alias d'URL -> fichier réel
ALIASES = {
    "/accueil": "/index.html",
    "/apropos": "/a-propos.html",
}


class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        clean = path.split("?", 1)[0].split("#", 1)[0]

        if clean in ALIASES:
            path = ALIASES[clean]
        elif len(clean) > 1 and clean.endswith("/"):
            path = clean.rstrip("/")

        full = super().translate_path(path)

        if os.path.isdir(full):
            index = os.path.join(full, "index.html")
            if os.path.exists(index):
                return index

        # /contact -> contact.html
        if not os.path.exists(full) and os.path.exists(full + ".html"):
            return full + ".html"

        return full

    def end_headers(self):
        # Pas de cache en développement : on veut voir ses modifications
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stdout.write("  %s\n" % (fmt % args))


class Server(http.server.ThreadingHTTPServer):
    """Multi-thread obligatoire : le navigateur ouvre plusieurs connexions
    en parallèle pour les images. Un serveur mono-thread les sérialise et
    finit par bloquer la page."""
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Server(("", PORT), CleanURLHandler) as httpd:
        print("Go Project — serveur local")
        print("  http://localhost:%d/" % PORT)
        print("  http://localhost:%d/a-propos" % PORT)
        print("  http://localhost:%d/contact" % PORT)
        print("  Ctrl+C pour arreter\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrete.")
