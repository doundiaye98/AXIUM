# -*- coding: utf-8 -*-
"""Catalogue des fiches services (URLs, images, clés i18n)."""

from __future__ import annotations

from typing import Any

# Ordre d’affichage page /services/
# Visuels servis depuis static/img/services/ (jpg) ; sources dans img_service/ — voir SERVICE_IMAGE_SYNC_RULES.
SERVICES: tuple[dict[str, Any], ...] = (
    {
        "slug": "ui",
        "anchor_id": "service-ui",
        "step": "01",
        "image": "img/services/ui.jpg",
        "meta_title_key": "svc_meta_ui",
        "title_key": "sp_ui_h",
        "intro_key": "sp_ui_p",
        "detail_keys": ("sp_ui_d1", "sp_ui_d2", "sp_ui_d3"),
        "prefill_key": "contact_prefill_ui",
    },
    {
        "slug": "mobile",
        "anchor_id": "service-mobile",
        "step": "02",
        "image": "img/services/mobile.jpg",
        "meta_title_key": "svc_meta_mobile",
        "title_key": "sp_mobile_h",
        "intro_key": "sp_mobile_p",
        "detail_keys": ("sp_mobile_d1", "sp_mobile_d2", "sp_mobile_d3"),
        "prefill_key": "contact_prefill_mobile",
    },
    {
        "slug": "web",
        "anchor_id": "service-web",
        "step": "03",
        "image": "img/services/web.jpg",
        "meta_title_key": "svc_meta_web",
        "title_key": "sp_web_h",
        "intro_key": "sp_web_p",
        "detail_keys": ("sp_web_d1", "sp_web_d2", "sp_web_d3"),
        "prefill_key": "contact_prefill_web",
    },
    {
        "slug": "erp",
        "anchor_id": "service-erp",
        "step": "04",
        "image": "img/services/erp.jpg",
        "meta_title_key": "svc_meta_erp",
        "title_key": "sp_erp_h",
        "intro_key": "sp_erp_p",
        "detail_keys": ("sp_erp_d1", "sp_erp_d2", "sp_erp_d3"),
        "prefill_key": "contact_prefill_erp",
    },
    {
        "slug": "conseil",
        "anchor_id": "service-conseil",
        "step": "05",
        "image": "img/services/conseil.jpg",
        "meta_title_key": "svc_meta_conseil",
        "title_key": "sp_consult_h",
        "intro_key": "sp_consult_p",
        "detail_keys": ("sp_consult_d1", "sp_consult_d2", "sp_consult_d3"),
        "prefill_key": "contact_prefill_conseil",
    },
)

BY_SLUG: dict[str, dict[str, Any]] = {s["slug"]: s for s in SERVICES}

# img_service/ → static/img/services/<premier champ> ; noms sources essayés dans l’ordre (nouveaux noms en premier).
SERVICE_IMAGE_SYNC_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ui.jpg", ("ui_ux.jpg", "SITE.png", "SITE.jpg", "ui.png")),
    ("mobile.jpg", ("app_mobile.jpg", "Développement mobile.png", "mobile.png")),
    ("web.jpg", ("developpement_web.jpg", "DÉVELOPPEMENT WEB.png", "web.png")),
    ("erp.jpg", ("ERP_Systeme.jpg", "ERP & CRM.jpg", "erp.jpg")),
    ("conseil.jpg", ("conseil_assistant informatique.jpg", "Assistant informatique.png", "conseil.png")),
)
