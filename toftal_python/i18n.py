"""Textes FR / EN pour le site AXIUM (Flask + Jinja) — source : locale/*.json + * _extra.json."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from urllib.parse import quote

from about_builtin import ABOUT_PAGES, about_fallback

CONTACT_EMAIL = "contact@axium.sn"

# Accueil — hero (filet si locale/*.json incomplet ou absent au déploiement)
_HOME_HERO_FALLBACK: dict[str, dict[str, str]] = {
    "fr": {
        "hero_title_heart": "Le cœur digital de la nouvelle Afrique.",
        "hero_lead": (
            "Nous concevons les infrastructures technologiques, financières et digitales "
            "qui transforment les économies africaines."
        ),
        "hero_cta_primary": "Découvrir nos solutions",
        "hero_cta_secondary": "Contacter un expert",
        "astro_hi": "Votre réussite, notre priorité",
        "svg_hero_alt": "AXIUM — innovation digitale",
    },
    "en": {
        "hero_title_heart": "The digital heart of the new Africa.",
        "hero_lead": (
            "We design the technological, financial and digital infrastructure "
            "that transforms African economies."
        ),
        "hero_cta_primary": "Discover our solutions",
        "hero_cta_secondary": "Contact an expert",
        "astro_hi": "Your success is our priority",
        "svg_hero_alt": "AXIUM — digital innovation",
    },
}

_ROOT = Path(__file__).resolve().parent
_log = logging.getLogger("axium")


def _read_json_dict(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig") as f:
        raw = json.load(f)
    return {str(k): str(v) for k, v in raw.items()}


def _read_about_embed(code: str) -> dict[str, str]:
    """Textes « À propos » de secours (locale/about_embed.json) si fr.json / en.json est incomplet."""
    path = _ROOT / "locale" / "about_embed.json"
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8-sig") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        _log.warning("i18n : about_embed.json illisible (%s)", exc)
        return {}
    block = raw.get(code) or raw.get("fr") or {}
    if not isinstance(block, dict):
        return {}
    return {str(k): str(v) for k, v in block.items()}


def _load_locale(code: str) -> dict[str, str]:
    """
    Couches (dans l'ordre) :
    1) about_embed.json — textes de secours (about_*, hero_*, etc.) si le JSON principal est incomplet ;
    2) locale/{code}.json — version principale ;
    3) locale/{code}_extra.json — complète uniquement les clés encore absentes ;
    4) about_builtin (Python) puis filet hero (_HOME_HERO_FALLBACK).
    """
    main = _ROOT / "locale" / f"{code}.json"
    extra = _ROOT / "locale" / f"{code}_extra.json"
    merged: dict[str, str] = {}
    merged.update(_read_about_embed(code))
    if main.is_file():
        try:
            for k, v in _read_json_dict(main).items():
                # Ne pas écraser un texte déjà présent (ex. about_embed) par une chaîne vide du JSON principal.
                if v:
                    merged[k] = v
                else:
                    merged.setdefault(k, v)
        except (OSError, json.JSONDecodeError) as exc:
            _log.warning("i18n : lecture impossible %s (%s)", main, exc)
    else:
        _log.warning("i18n : fichier principal absent %s", main)
    if extra.is_file():
        try:
            for k, v in _read_json_dict(extra).items():
                merged.setdefault(k, v)
        except (OSError, json.JSONDecodeError) as exc:
            _log.warning("i18n : lecture impossible %s (%s)", extra, exc)
    # Dernier filet : textes « À propos » en Python (toujours présents, même sans dossier locale/)
    def _builtin_str(val: object) -> str:
        if isinstance(val, str):
            return val
        if isinstance(val, tuple):
            return "".join(str(x) for x in val)
        return str(val)

    _builtin = ABOUT_PAGES.get(code) or ABOUT_PAGES["fr"]
    for bk, bv in _builtin.items():
        cur = merged.get(bk, "")
        if not (isinstance(cur, str) and cur.strip()):
            merged[bk] = _builtin_str(bv)
    _home = _HOME_HERO_FALLBACK.get(code) or _HOME_HERO_FALLBACK["fr"]
    for hk, hv in _home.items():
        cur = merged.get(hk, "")
        if not (isinstance(cur, str) and cur.strip()):
            merged[hk] = _builtin_str(hv)
    return merged


MESSAGES: dict[str, dict[str, str]] = {
    "fr": _load_locale("fr"),
    "en": _load_locale("en"),
}


def _locales_bundle_mtime() -> float:
    """Dernière modification parmi les JSON de locale (rechargement sans redémarrer le serveur)."""
    mt = 0.0
    for rel in (
        "fr.json",
        "en.json",
        "fr_extra.json",
        "en_extra.json",
        "about_embed.json",
    ):
        path = _ROOT / "locale" / rel
        try:
            mt = max(mt, path.stat().st_mtime)
        except OSError:
            continue
    return mt


_LAST_LOCALE_BUNDLE_MT: float = _locales_bundle_mtime()


def _maybe_reload_locales() -> None:
    """Si les fichiers locale/*.json ont changé depuis le dernier chargement, recharge MESSAGES."""
    global _LAST_LOCALE_BUNDLE_MT
    cur = _locales_bundle_mtime()
    if cur <= _LAST_LOCALE_BUNDLE_MT:
        return
    _LAST_LOCALE_BUNDLE_MT = cur
    MESSAGES["fr"] = _load_locale("fr")
    MESSAGES["en"] = _load_locale("en")


def translate(lang: str, key: str) -> str:
    """Retourne la chaîne pour la langue demandée, avec repli sur le français puis sur la clé."""
    _maybe_reload_locales()
    key_s = str(key)
    lg = lang if lang in MESSAGES else "fr"
    table = MESSAGES[lg]

    def _nonempty(d: dict[str, str], k: str) -> str | None:
        v = d.get(k)
        return v if isinstance(v, str) and v.strip() else None

    val = _nonempty(table, key_s)
    if val is not None:
        return val
    if lg != "fr":
        val = _nonempty(MESSAGES["fr"], key_s)
        if val is not None:
            return val
    # Secours disque : about_embed.json
    for code in (lg, "fr"):
        if code not in ("fr", "en"):
            continue
        patch = _read_about_embed(code)
        val = _nonempty(patch, key_s)
        if val is not None:
            return val
    val = about_fallback(lg, key_s) or (about_fallback("fr", key_s) if lg != "fr" else None)
    if val is not None:
        return val
    if key_s.startswith("about_"):
        _log.warning(
            "i18n : texte « À propos » introuvable %r (lang=%r).",
            key_s,
            lg,
        )
    return key_s


def mailto_href(lang: str) -> str:
    """Lien mailto avec objet et corps issus des clés cta_mail_*."""
    subj = translate(lang, "cta_mail_subject")
    body = translate(lang, "cta_mail_template")
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subj)}&body={quote(body)}"


CHAT_UI: dict[str, dict[str, str]] = {
    "fr": {
        "open_aria": "Ouvrir l’assistant de discussion",
        "title": "Assistant AXIUM",
        "subtitle": "Une question sur nos services ou votre projet ? Écrivez-nous ici.",
        "close_aria": "Fermer le chat",
        "error_unconfigured": "L’assistant n’est pas disponible sur ce serveur (aucune clé API configurée et mode local désactivé). Utilisez le formulaire de contact.",
        "placeholder": "Votre message…",
        "new_chat": "Nouvelle conversation",
        "send": "Envoyer",
        "open_form": "Formulaire de contact",
        "error_empty": "Saisissez un message.",
        "error_network": "Problème de connexion. Vérifiez le réseau et réessayez.",
        "error_api_key": "Configuration serveur incorrecte (clé API).",
        "error_upstream": "Le service de réponse est temporairement indisponible.",
        "typing": "…",
        "prefill_intro": "Transcription de la conversation :",
        "transcript_you": "Vous",
        "transcript_assistant": "Assistant",
        "error_generic": "Une erreur s’est produite. Réessayez ou utilisez le formulaire.",
        "welcome": "Bonjour ! Je suis l’assistant AXIUM. Comment puis-je vous aider aujourd’hui ?",
    },
    "en": {
        "open_aria": "Open chat assistant",
        "title": "AXIUM assistant",
        "subtitle": "Ask about our services or your project — we’re here to help.",
        "close_aria": "Close chat",
        "error_unconfigured": "The assistant is not available on this server (no API key and local mode off). Please use the contact form.",
        "placeholder": "Your message…",
        "new_chat": "New conversation",
        "send": "Send",
        "open_form": "Contact form",
        "error_empty": "Please enter a message.",
        "error_network": "Connection issue. Check your network and try again.",
        "error_api_key": "Server misconfiguration (API key).",
        "error_upstream": "The reply service is temporarily unavailable.",
        "typing": "…",
        "prefill_intro": "Conversation transcript:",
        "transcript_you": "You",
        "transcript_assistant": "Assistant",
        "error_generic": "Something went wrong. Try again or use the contact form.",
        "welcome": "Hello! I’m the AXIUM assistant. How can I help you today?",
    },
}


CHAT_SYSTEM_PROMPTS: dict[str, str] = {
    "fr": (
        "Tu es l’assistant du site AXIUM GROUP, basé au Sénégal et actif en Afrique. "
        "Tu t’exprimes en français, de façon professionnelle et concise. "
        "AXIUM GROUP propose : design UI/UX, développement web et mobile, intégration ERP & CRM / systèmes de gestion, "
        "conseil et accompagnement informatique. "
        "Tu ne inventes pas de tarifs ni d’engagements contractuels. "
        "Pour un devis précis ou un rendez-vous, tu orientes vers le formulaire de contact du site ou l’e-mail contact@axium.sn. "
        "Si une question sort du périmètre du groupe, tu le dis poliment et tu proposes de contacter l’équipe."
    ),
    "en": (
        "You are the assistant for the AXIUM GROUP website, based in Senegal and active across Africa. "
        "You reply in English, professionally and concisely. "
        "AXIUM GROUP offers: UI/UX design, web and mobile development, ERP & CRM / business systems integration, "
        "IT consulting and support. "
        "Do not invent prices or contractual commitments. "
        "For a precise quote or meeting, direct users to the site contact form or contact@axium.sn. "
        "If a question is outside the group’s scope, say so politely and suggest contacting the team."
    ),
}
