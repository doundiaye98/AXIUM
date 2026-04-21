"""
AXIUM — site vitrine servi par Flask.

La structure et le parti graphique initial reprennent un gabarit issu d’un
site de référence protégé ; les droits sur ce modèle restent ceux de leurs
titulaires (voir ATTRIBUTION.txt à la racine du dossier toftal_python).

Lancer : double-clic sur run.bat (port 5001 par défaut), ou  python app.py
depuis le dossier toftal_python. Si le navigateur affiche ERR_CONNECTION_REFUSED,
le serveur n’est pas démarré ou le port ne correspond pas — relancez run.bat et
gardez la fenêtre ouverte.

Chat : OPENAI_API_KEY dans .env pour OpenAI. Sans clé, le mode assistant local est actif par défaut
(sauf AXIUM_CHAT_LOCAL=0). Cookie de session renommé (axium_session) ; l’ancien « session » est
effacé automatiquement. Si le site plante encore : ouvrir /_axium/nettoyer-cookies puis l’accueil.

Admin local (sans formulaire de connexion) : /_axium/admin — localhost par défaut,
ou définir AXIUM_ADMIN=1 pour y accéder depuis le réseau (déconseillé en public).
Option AXIUM_ADMIN_TOKEN : ajouter ?token=VOTRE_CLE à l’URL.
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import secrets
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
except ImportError:
    logging.getLogger("axium").warning(
        "python-dotenv absent : pip install python-dotenv — le fichier .env ne sera pas chargé."
    )
else:
    try:
        # D’abord .env à la racine du projet (AXIUM), puis toftal_python/.env (prioritaire).
        _parent_env = _ROOT.parent / ".env"
        if _parent_env.is_file():
            load_dotenv(_parent_env, override=False)
        load_dotenv(_ROOT / ".env", override=True)
    except Exception as exc:
        logging.getLogger("axium").warning(
            "Impossible de lire un fichier .env (encodage ou contenu) : %s — poursuite sans .env.",
            exc,
        )

from flask import (
    Flask,
    abort,
    flash,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from i18n import CHAT_SYSTEM_PROMPTS, CHAT_UI, CONTACT_EMAIL, mailto_href, translate
from services_catalog import BY_SLUG, SERVICES
from sync_service_images import sync_service_thumbnails_to_static
from llm_chat import complete_chat

# import_name fixe : avec "python app.py", __name__ vaut __main__ et sans root_path
# explicite Flask pouvait chercher les templates au mauvais endroit → erreur 500.
app = Flask(
    "axium_app",
    root_path=str(_ROOT),
    template_folder="templates",
    static_folder="static",
)
# Vignettes services : incrémenter après mise à jour des fichiers dans static/img/services/ (cache navigateur).
_SERVICE_ASSETS_VER = "20260422e"
_SERVICE_IMAGES_DIR = _ROOT / "static" / "img" / "services"
log = logging.getLogger("axium")
_STORAGE = Path(__file__).resolve().parent / "storage"
_CONTACT_LOG = _STORAGE / "contact_messages.log"
_ADMIN_CACHE_BUMP = _STORAGE / "admin_cache_bump.txt"


def _service_thumb_version() -> str:
    """Version affichée pour ?v= sur CSS et vignettes ; suffixe optionnel via panneau admin."""
    base = _SERVICE_ASSETS_VER
    try:
        if _ADMIN_CACHE_BUMP.is_file():
            extra = _ADMIN_CACHE_BUMP.read_text(encoding="utf-8").strip()
            if extra and re.fullmatch(r"[A-Za-z0-9._-]{1,48}", extra):
                return f"{base}-{extra}"
    except OSError:
        pass
    return base


def _admin_request_allowed() -> bool:
    """Accès /_axium/admin : localhost, ou AXIUM_ADMIN=1, ou jeton d’URL si AXIUM_ADMIN_TOKEN est défini."""
    env_open = (os.environ.get("AXIUM_ADMIN") or "").strip().lower() in ("1", "true", "yes")
    token_cfg = (os.environ.get("AXIUM_ADMIN_TOKEN") or "").strip()
    q_token = (request.args.get("token") or "").strip()
    if token_cfg:
        return secrets.compare_digest(q_token, token_cfg)
    if env_open:
        return True
    ra = (request.remote_addr or "").strip()
    if ra in ("127.0.0.1", "127.0.0.0", "::1"):
        return True
    if ra.startswith("127."):
        return True
    if ra.endswith("127.0.0.1") or "::ffff:127.0.0.1" in ra:
        return True
    return False


def _admin_service_image_rows():
    rows: list[dict] = []
    for meta in SERVICES:
        rel = str(meta.get("image") or "").replace("\\", "/")
        basename = Path(rel).name if rel else ""
        path = _SERVICE_IMAGES_DIR / basename if basename else None
        ok = bool(path and path.is_file() and path.stat().st_size > 64)
        size = int(path.stat().st_size) if path and path.is_file() else 0
        rows.append(
            {
                "slug": meta["slug"],
                "catalog": rel,
                "basename": basename,
                "ok": ok,
                "bytes": size,
                "url_static": url_for("static", filename=rel) if rel else "",
                "url_direct": url_for("axium_service_image", service_slug=meta["slug"]),
            }
        )
    return rows


def _ensure_service_thumbnails() -> None:
    """Au démarrage : copie img_service/ (ou img/) → static/img/services/ si absent ou source plus récente."""
    try:
        updated = sync_service_thumbnails_to_static(verbose=False)
    except OSError as exc:
        log.warning("Synchronisation visuels services impossible : %s", exc)
        return
    if updated:
        log.info("Visuels services : %s fichier(s) synchronisé(s) vers static/img/services/.", updated)


_ensure_service_thumbnails()

# Logo en-tête : JPEG si présent dans img/ (ex. logo_Axuim.jpeg), sinon SVG embarqué (évite 404).
_LOGO_JPEG_DEST = _ROOT / "static" / "img" / "logo-axium.jpeg"
_LOGO_JPEG_SOURCES: tuple[tuple[Path, str], ...] = (
    (_ROOT / "img", "logo-axium.jpeg"),
    (_ROOT / "img", "logo_Axuim.jpeg"),
    (_ROOT / "img", "logo_axium.jpeg"),
)


def _ensure_logo_jpeg() -> None:
    _LOGO_JPEG_DEST.parent.mkdir(parents=True, exist_ok=True)
    for folder, name in _LOGO_JPEG_SOURCES:
        src = folder / name
        if not src.is_file():
            continue
        if _LOGO_JPEG_DEST.is_file() and _LOGO_JPEG_DEST.stat().st_mtime >= src.stat().st_mtime:
            return
        try:
            shutil.copy2(src, _LOGO_JPEG_DEST)
            log.info("Logo : copié vers static/img/logo-axium.jpeg (%s)", src.name)
        except OSError as exc:
            log.warning("Logo : copie impossible depuis %s : %s", src, exc)
        return


_ensure_logo_jpeg()


def _logo_image_static_path() -> str:
    if _LOGO_JPEG_DEST.is_file() and _LOGO_JPEG_DEST.stat().st_size > 32:
        return "img/logo-axium.jpeg"
    return "img/logo-axium.svg"


app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-production")
# Ne plus utiliser le cookie par défaut « session » (confusion avec d’anciennes versions qui y
# stockaient tout le chat → cookie énorme → en-têtes HTTP refusés ou pages cassées).
app.config["SESSION_COOKIE_NAME"] = "axium_session"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Render (HTTPS + proxy) : en-têtes X-Forwarded-* et cookies sécurisés.
if (os.environ.get("RENDER") or "").strip().lower() in ("true", "1", "yes"):
    app.config["PREFERRED_URL_SCHEME"] = "https"
    app.config["SESSION_COOKIE_SECURE"] = True
    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # type: ignore[method-assign]

# Ancien nom du cookie Flask / Werkzeug (à effacer côté navigateur à chaque réponse).
_LEGACY_FLASK_SESSION_COOKIE = "session"

# Chat : historique en mémoire serveur ; identifiant dans un PETIT cookie dédié (pas dans session Flask).
CHAT_SESSION_KEY = "ax_chat_messages"
CHAT_COOKIE_NAME = "axium_chat_id"
_CHAT_SID_OK = re.compile(r"^[A-Za-z0-9_.=-]{12,128}$")
CHAT_MAX_USER_CHARS = 4000
CHAT_MAX_STORED_MSGS = 24
_MAX_CHAT_SESSIONS = 500
_CHAT_STORE: OrderedDict[str, list] = OrderedDict()


def _chat_read_sid() -> str | None:
    raw = request.cookies.get(CHAT_COOKIE_NAME)
    if raw and isinstance(raw, str) and _CHAT_SID_OK.match(raw):
        return raw
    return None


def _chat_new_sid() -> str:
    return secrets.token_urlsafe(24)


def _set_chat_cookie(resp, sid: str) -> None:
    resp.set_cookie(
        CHAT_COOKIE_NAME,
        sid,
        max_age=60 * 60 * 24 * 180,
        path="/",
        httponly=True,
        samesite="Lax",
    )


def _clear_chat_cookie(resp) -> None:
    resp.set_cookie(CHAT_COOKIE_NAME, "", max_age=0, path="/", httponly=True, samesite="Lax")


def _chat_get_messages(sid: str) -> list:
    if sid in _CHAT_STORE:
        _CHAT_STORE.move_to_end(sid)
        return _CHAT_STORE[sid]
    return []


def _chat_set_messages(sid: str, messages: list) -> None:
    _CHAT_STORE[sid] = messages
    _CHAT_STORE.move_to_end(sid)
    while len(_CHAT_STORE) > _MAX_CHAT_SESSIONS:
        _CHAT_STORE.popitem(last=False)


def _chat_clear_messages(sid: str) -> None:
    _CHAT_STORE.pop(sid, None)


def _openai_api_key() -> str:
    """Clé depuis l’environnement ou .env ; enlève espaces, guillemets et BOM."""
    raw = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if raw.startswith("\ufeff"):
        raw = raw[1:].strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        raw = raw[1:-1].strip()
    return raw


def _chat_local_mode() -> bool:
    """
    Assistant sans appel OpenAI. Par défaut : ON si aucune clé API (site utilisable tout de suite).
    Désactiver explicitement : AXIUM_CHAT_LOCAL=0 dans .env.
    Forcer ON : AXIUM_CHAT_LOCAL=1.
    """
    v = (os.environ.get("AXIUM_CHAT_LOCAL") or "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return not bool(_openai_api_key())


def _chat_ui_enabled() -> bool:
    """Barre de saisie visible si clé OpenAI ou mode local."""
    return bool(_openai_api_key()) or _chat_local_mode()


def _local_chat_reply(user_text: str, lang: str) -> str:
    """Réponse sans API (résumé + orientation contact)."""
    snippet = (user_text or "").strip()
    if len(snippet) > 280:
        snippet = snippet[:277] + "…"
    if lang == "en":
        return (
            "Thanks for your message. This assistant runs in local mode (no live AI model on the server). "
            "The AXIUM team can answer in detail: use the Contact form button below or write to contact@axium.sn.\n\n"
            f"You wrote: «{snippet}»"
        )
    return (
        "Merci pour votre message. L’assistant est en mode local (pas de modèle IA connecté sur ce serveur). "
        "Pour une réponse détaillée, l’équipe AXIUM est joignable via le bouton « Formulaire » ci-dessous ou à contact@axium.sn.\n\n"
        f"Vous avez écrit : «{snippet}»"
    )


def _chat_ui_merged(lang: str) -> dict:
    """Toutes les clés du chat (évite les clés manquantes en EN)."""
    lang = lang if lang in CHAT_UI else "fr"
    merged = dict(CHAT_UI["fr"])
    merged.update(CHAT_UI[lang])
    return merged


def _safe_internal_redirect(target: Optional[str]) -> str:
    """Autorise uniquement une redirection vers un chemin relatif du même site."""
    if not target:
        return url_for("index")
    if not target.startswith("/") or target.startswith("//"):
        return url_for("index")
    path_only = target.split("?", 1)[0]
    if path_only.startswith("/set-language/"):
        return url_for("index")
    return target


def _language_redirect_destination() -> str:
    """Conserve la page courante (chemin + query) pour le changement de langue."""
    q = (request.query_string or b"").decode("utf-8", "replace")
    path = request.path or "/"
    if path.startswith("/set-language/"):
        return url_for("index")
    if q:
        return f"{path}?{q}"
    return path


# Paramètre d’URL de secours si le navigateur n’enregistre pas le cookie `lang` sur la 302 initiale.
_LANG_Q = "_axium_lang"


def _with_lang_hint(target: str, code: str) -> str:
    """Ajoute ou remplace ?_axium_lang= sur une URL relative interne."""
    parts = urlsplit(target)
    path = parts.path or "/"
    pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != _LANG_Q]
    pairs.append((_LANG_Q, code))
    return urlunsplit(("", "", path, urlencode(pairs), ""))


def _url_without_lang_hint() -> str:
    """Chemin + query courants sans _axium_lang."""
    path = request.path or "/"
    raw_q = (request.query_string or b"").decode("utf-8", "replace")
    if not raw_q:
        return path
    pairs = [(k, v) for k, v in parse_qsl(raw_q, keep_blank_values=True) if k != _LANG_Q]
    if not pairs:
        return path
    return f"{path}?{urlencode(pairs)}"


@app.before_request
def _before_request() -> None:
    hint = request.args.get(_LANG_Q)
    g._axium_strip_lang_query = bool(hint in ("fr", "en") and request.method == "GET")
    try:
        if hint in ("fr", "en"):
            g.lang = hint
            session["lang"] = hint
            session.modified = True
        else:
            raw = session.get("lang")
            if raw not in ("fr", "en"):
                raw = request.cookies.get("lang", "fr")
            if raw not in ("fr", "en"):
                raw = "fr"
            g.lang = raw
        for _legacy in (CHAT_SESSION_KEY, "ax_chat_sid"):
            if _legacy in session:
                session.pop(_legacy, None)
                session.modified = True
    except Exception as exc:
        log.warning("Session Flask illisible (cookie corrompu ou trop volumineux) : %s", exc)
        if hint in ("fr", "en"):
            g.lang = hint
        else:
            raw = request.cookies.get("lang", "fr")
            g.lang = raw if raw in ("fr", "en") else "fr"


@app.after_request
def _axium_response_headers(response):
    """En-têtes diagnostic + suppression de l’ancien cookie « session » gonflé."""
    if getattr(g, "_axium_strip_lang_query", False):
        ct = (response.headers.get("Content-Type") or "").lower()
        if response.status_code == 200 and "text/html" in ct:
            dest = _url_without_lang_hint()
            lang = getattr(g, "lang", "fr")
            r = redirect(dest, code=302)
            r.headers.setdefault("X-AXIUM-App", "axium-flask")
            r.set_cookie(
                "lang",
                lang,
                max_age=60 * 60 * 24 * 365,
                samesite="Lax",
                path="/",
                httponly=False,
            )
            r.set_cookie(
                _LEGACY_FLASK_SESSION_COOKIE,
                "",
                max_age=0,
                path="/",
                samesite="Lax",
                httponly=True,
            )
            return r

    response.headers.setdefault("X-AXIUM-App", "axium-flask")
    response.set_cookie(
        _LEGACY_FLASK_SESSION_COOKIE,
        "",
        max_age=0,
        path="/",
        samesite="Lax",
        httponly=True,
    )
    return response


def _axium_admin_url(**extra) -> str:
    """URL du panneau admin en conservant ?token= si configuré."""
    tok = (request.args.get("token") or "").strip()
    if tok and (os.environ.get("AXIUM_ADMIN_TOKEN") or "").strip():
        extra = {**extra, "token": tok}
    return url_for("axium_admin", **extra)


@app.route("/_axium/admin", methods=["GET", "POST"])
def axium_admin():
    """Panneau maintenance : synchro vignettes, bump cache, liens de test (sans page de login)."""
    if not _admin_request_allowed():
        abort(404)
    if request.method == "POST":
        action = (request.form.get("action") or "").strip()
        if action == "sync_images":
            try:
                n = int(sync_service_thumbnails_to_static(verbose=False))
                _ensure_logo_jpeg()
                flash(
                    f"Synchro terminée : {n} fichier(s) services mis à jour vers static/img/services/. "
                    "Rechargez l’accueil (Ctrl+F5) si les images ne changent pas.",
                    "success",
                )
            except OSError as exc:
                flash(f"Synchro impossible : {exc}", "error")
        elif action == "bump_cache":
            try:
                _STORAGE.mkdir(parents=True, exist_ok=True)
                bump = datetime.now(timezone.utc).strftime("%m%d%H%M%S")
                _ADMIN_CACHE_BUMP.write_text(bump, encoding="utf-8")
                flash(
                    f"Suffixe cache navigateur : « {bump} » (ajouté à service_thumb_ver). "
                    "Rechargez avec Ctrl+F5.",
                    "success",
                )
            except OSError as exc:
                flash(f"Écriture cache bump impossible : {exc}", "error")
        return redirect(_axium_admin_url())

    rows = _admin_service_image_rows()
    _admin_env_open = (os.environ.get("AXIUM_ADMIN") or "").strip().lower() in ("1", "true", "yes")
    return render_template(
        "admin_dev.html",
        admin_service_rows=rows,
        admin_thumb_ver=_service_thumb_version(),
        admin_base_ver=_SERVICE_ASSETS_VER,
        admin_env_open=_admin_env_open,
        admin_token_mode=bool((os.environ.get("AXIUM_ADMIN_TOKEN") or "").strip()),
        admin_form_action=_axium_admin_url(),
    )


@app.get("/_axium/nettoyer-cookies")
def axium_nettoyer_cookies():
    """Page de secours : supprime tous les cookies de session AXIUM pour ce domaine."""
    body = """<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>AXIUM — cookies</title></head>
<body style="font-family:system-ui,sans-serif;padding:2rem;line-height:1.5;max-width:40rem">
<h1>Cookies AXIUM supprimés</h1>
<p>Les cookies de session pour ce site ont été effacés. Revenez à l’accueil et rechargez la page (F5).</p>
<p><a href="/">Accueil</a> · <a href="/services/">Services</a></p>
</body></html>"""
    resp = make_response(body, 200)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    for name in (_LEGACY_FLASK_SESSION_COOKIE, app.config["SESSION_COOKIE_NAME"], CHAT_COOKIE_NAME, "lang"):
        resp.set_cookie(name, "", max_age=0, path="/", samesite="Lax", httponly=True)
    return resp


@app.context_processor
def _inject_i18n():
    lang = getattr(g, "lang", "fr")
    try:
        ax_prefix = (request.script_root or "").rstrip("/")
    except RuntimeError:
        ax_prefix = ""

    return {
        "lang": lang,
        "t": lambda key: translate(lang, key),
        "mailto_href": mailto_href(lang),
        "chat_i18n": _chat_ui_merged(lang),
        "chat_llm_configured": _chat_ui_enabled(),
        "service_thumb_ver": _service_thumb_version(),
        "ax_svc_prefix": ax_prefix,
        # Visuels services : URL en dur dans les gabarits /i/service/<slug>?v=… (évite UndefinedError / BuildError).
        # Filet si une vue oublie de passer services_catalog (évite une grille vide).
        "services_catalog_default": SERVICES,
        "offers_default": SERVICES,
        # Alias explicite (évite tout conflit avec un nom générique « offers » dans le contexte).
        "services_catalog_items": SERVICES,
        "logo_static": _logo_image_static_path(),
    }


@app.route("/set-language/<string:code>")
def set_language(code: str):
    code = (code or "fr").lower()[:2]
    if code not in ("fr", "en"):
        code = "fr"
    dest = _safe_internal_redirect(request.args.get("next") or _language_redirect_destination())
    dest = _with_lang_hint(dest, code)
    session["lang"] = code
    session.modified = True
    resp = redirect(dest)
    resp.set_cookie(
        "lang",
        code,
        max_age=60 * 60 * 24 * 365,
        samesite="Lax",
        path="/",
        httponly=False,
    )
    return resp


@app.route("/health")
def health():
    """Diagnostic rapide : doit répondre « ok » si l’app tourne."""
    return "ok", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.get("/api/chat/status")
def api_chat_status():
    """Permet au script du widget de resynchroniser l’UI sans recharger la page (clé .env ajoutée, etc.)."""
    return jsonify(
        llm=bool(_openai_api_key()),
        local=_chat_local_mode(),
        chat_enabled=_chat_ui_enabled(),
    )


@app.post("/api/chat")
def api_chat():
    """Chat : historique en mémoire ; cookie dédié axium_chat_id (pas la session Flask)."""
    lang = getattr(g, "lang", "fr")
    ui = _chat_ui_merged(lang)
    api_key = _openai_api_key()
    payload = request.get_json(silent=True) or {}
    user_text = (payload.get("message") or "").strip()
    sid = _chat_read_sid() or _chat_new_sid()

    if not user_text:
        return jsonify(error=ui["error_empty"], code="empty"), 400
    if len(user_text) > CHAT_MAX_USER_CHARS:
        user_text = user_text[:CHAT_MAX_USER_CHARS]

    history: list = list(_chat_get_messages(sid))
    trial = history + [{"role": "user", "content": user_text}]
    while len(trial) > CHAT_MAX_STORED_MSGS:
        trial = trial[2:]

    if not api_key:
        if _chat_local_mode():
            reply = _local_chat_reply(user_text, lang)
            _chat_set_messages(sid, trial + [{"role": "assistant", "content": reply}])
            resp = jsonify(reply=reply)
            _set_chat_cookie(resp, sid)
            return resp
        resp = jsonify(error=ui["error_unconfigured"], code="unconfigured")
        _set_chat_cookie(resp, sid)
        return resp, 503

    system = CHAT_SYSTEM_PROMPTS.get(lang if lang in CHAT_SYSTEM_PROMPTS else "fr", CHAT_SYSTEM_PROMPTS["fr"])
    model = (os.environ.get("OPENAI_MODEL") or "gpt-4o-mini").strip() or "gpt-4o-mini"
    base = (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").strip()

    try:
        reply = complete_chat(
            base_url=base,
            api_key=api_key,
            model=model,
            system=system,
            messages=trial,
        )
    except RuntimeError as exc:
        err_s = str(exc).lower()
        if str(exc) == "network":
            msg = ui["error_network"]
        elif (
            "401" in err_s
            or "invalid api key" in err_s
            or "incorrect api key" in err_s
            or "invalid_api_key" in err_s
        ):
            msg = ui["error_api_key"]
        else:
            msg = ui["error_upstream"]
        log.warning("Chat LLM error: %s", exc)
        resp = jsonify(error=msg, code="upstream")
        _set_chat_cookie(resp, sid)
        return resp, 502

    _chat_set_messages(sid, trial + [{"role": "assistant", "content": reply}])
    resp = jsonify(reply=reply)
    _set_chat_cookie(resp, sid)
    return resp


@app.post("/api/chat/reset")
def api_chat_reset():
    sid = _chat_read_sid()
    if sid:
        _chat_clear_messages(sid)
    session.pop(CHAT_SESSION_KEY, None)
    resp = jsonify(ok=True)
    _clear_chat_cookie(resp)
    return resp


@app.route("/i/service/<string:service_slug>", methods=["GET"])
def axium_service_image(service_slug: str):
    """Sert le visuel d’une offre depuis static/img/services/."""
    key = (service_slug or "").strip().lower().rstrip("/")
    meta = BY_SLUG.get(key)
    if not meta:
        abort(404)
    try:
        rel = str(meta["image"]).replace("\\", "/").strip()
    except (TypeError, ValueError):
        abort(404)
    if ".." in rel or not rel.startswith("img/services/"):
        abort(404)
    basename = Path(rel).name
    if not basename or "/" in basename:
        abort(404)
    path = _SERVICE_IMAGES_DIR / basename
    if not path.is_file():
        log.warning("Visuel service manquant : %s (slug=%s)", path, key)
        abort(404)
    return send_from_directory(str(_SERVICE_IMAGES_DIR), basename, max_age=3600)


@app.route("/")
def index():
    return render_template(
        "index.html",
        contact_email=CONTACT_EMAIL,
        services_page_offers=list(SERVICES),
    )


@app.route("/a-propos")
@app.route("/a-propos/")
def a_propos():
    return render_template("a_propos.html")


@app.route("/services")
@app.route("/services/")
def services():
    items = list(SERVICES)
    if not items:
        log.error("services_catalog.SERVICES est vide : la page /services/ n'affichera aucune offre.")
    return render_template("services.html", services_page_offers=items)


@app.route("/services/<slug>/")
def service_detail(slug: str):
    key = (slug or "").strip().lower()
    meta = BY_SLUG.get(key)
    if not meta:
        abort(404)
    return render_template("service_detail.html", service=meta)


@app.route("/realisations")
@app.route("/realisations/")
def realisations():
    return render_template("realisations.html")


def _contact_form_redirect() -> str:
    """Après envoi du formulaire : page « Nous écrire » + ancre pour afficher les messages flash."""
    return url_for("nous_ecrire") + "#contact-form"


def _handle_contact_post():
    """Enregistre le message dans storage/contact_messages.log (pas d’SMTP requis)."""
    lang = getattr(g, "lang", "fr")
    dest = _contact_form_redirect()
    if request.form.get("website"):
        flash(translate(lang, "flash_honeypot"), "success")
        return redirect(dest)

    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    message = (request.form.get("message") or "").strip()

    if len(name) < 2:
        flash(translate(lang, "flash_name"), "error")
        return redirect(dest)
    if "@" not in email or len(email) < 5:
        flash(translate(lang, "flash_email"), "error")
        return redirect(dest)
    if len(message) < 10:
        flash(translate(lang, "flash_message_short"), "error")
        return redirect(dest)
    if len(message) > 8000:
        flash(translate(lang, "flash_message_long"), "error")
        return redirect(dest)

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "email": email,
        "phone": phone,
        "message": message,
    }
    try:
        _STORAGE.mkdir(parents=True, exist_ok=True)
        with _CONTACT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        log.exception("Impossible d'écrire dans storage/contact_messages.log : %s", exc)
        flash(translate(lang, "flash_contact_log_error"), "error")
        return redirect(dest)

    flash(translate(lang, "flash_contact_success"), "success")
    return redirect(dest)


@app.route("/nous-ecrire", methods=["GET", "POST"])
@app.route("/nous-ecrire/", methods=["GET", "POST"])
def nous_ecrire():
    """Page « Nous écrire » : formulaire et alternatives (e-mail, modèle)."""
    if request.method == "POST":
        return _handle_contact_post()
    lang = getattr(g, "lang", "fr")
    prefill_slug = (request.args.get("service") or "").strip().lower()
    prefill_msg = ""
    if prefill_slug in BY_SLUG:
        pkey = BY_SLUG[prefill_slug]["prefill_key"]
        prefill_msg = translate(lang, pkey)
    return render_template(
        "nous_ecrire.html",
        contact_email=CONTACT_EMAIL,
        contact_prefill_message=prefill_msg,
    )


@app.route("/contact", methods=["POST"])
def contact():
    """Compatibilité : anciennes intégrations qui postent encore vers /contact."""
    return _handle_contact_post()


def _assert_axium_routes_complete() -> None:
    """Évite un site « à moitié chargé » si `python app.py` est lancé depuis un mauvais dossier."""
    required = ("index", "services", "nous_ecrire", "a_propos", "realisations", "axium_admin")
    missing = [ep for ep in required if ep not in app.view_functions]
    if missing:
        raise RuntimeError(
            f"AXIUM : routes manquantes {missing}. Fichier chargé : {Path(__file__).resolve()}. "
            "Cause fréquente : commande « python app.py » sans être dans toftal_python, ou autre app.py. "
            "Utilisez DEMARRER-ICI.cmd / run.bat, ou : "
            f'"{sys.executable}" "{Path(__file__).resolve()}"'
        )


_assert_axium_routes_complete()


if __name__ == "__main__":
    import socket

    print(f"[AXIUM] Chargement depuis : {Path(__file__).resolve()}", flush=True)

    port = int(os.environ.get("PORT", "5001"))
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    # Détection « port déjà pris » (désactivable si faux positif : AXIUM_SKIP_PORT_CHECK=1).
    _skip = (os.environ.get("AXIUM_SKIP_PORT_CHECK") or "").strip().lower() in ("1", "true", "yes")
    if not _skip:
        _probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            _probe.settimeout(0.4)
            if _probe.connect_ex(("127.0.0.1", port)) == 0:
                print(
                    "\n[AXIUM] Le port {p} est déjà utilisé — Flask ne peut pas démarrer.\n"
                    "          Ce qui écoute sur ce port n’est en général PAS AXIUM (ex. Apache/WAMP, autre appli).\n"
                    "          Si vous ouvrez http://127.0.0.1:{p}/_axium/admin sans Flask, vous obtiendrez une 404 « introuvable ».\n"
                    "          • Libérez le port ou utilisez un autre port, puis relancez :\n"
                    "            cmd :  set PORT=5002 && python app.py\n"
                    "            PowerShell :  $env:PORT=\"5002\"; python app.py\n"
                    "          • Vérifier quel programme utilise le port (invite admin) :\n"
                    "            netstat -ano | findstr :{p}\n".format(p=port),
                    file=sys.stderr,
                )
                sys.exit(1)
        finally:
            _probe.close()

    # Par défaut : pas de reloader (2 processus, conflits sous Windows ; rechargement sur fichier
    # mal enregistré → SyntaxError côté enfant). Activer : FLASK_USE_RELOADER=1
    use_reloader = os.environ.get("FLASK_USE_RELOADER", "").strip().lower() in ("1", "true", "yes")
    print(f"\n[AXIUM] http://{host}:{port}/  —  Ctrl+C pour arrêter\n")
    app.run(
        host=host,
        port=port,
        debug=True,
        use_reloader=use_reloader,
        use_debugger=True,
        # threaded=True (défaut Flask) : évite de bloquer tout le site si une requête reste
        # pendante (ex. débogueur interactif, appel réseau lent vers l’API chat).
        threaded=True,
    )
