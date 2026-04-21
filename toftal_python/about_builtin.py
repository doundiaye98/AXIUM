# -*- coding: utf-8 -*-
"""Contenu page À propos — secours intégré (sans dépendre des fichiers locale/)."""

from __future__ import annotations

ABOUT_PAGES: dict[str, dict[str, str]] = {
    "fr": {
        "about_page_h1_full": "AXIUM GROUP",
        "about_positioning_l1": "Le cœur digital de la nouvelle Afrique.",
        "about_positioning_l2": "Groupe technologique et financier construisant les infrastructures numériques de demain.",
        "about_page_tagline": (
            "Digital, systèmes d’information et finance : une trajectoire de bout en bout, pilotée depuis Dakar."
        ),
        "about_manifest_html": (
            """
<div class="about-block about-lead-block">
  <p class="about-lead">AXIUM GROUP relie <strong>produit digital</strong>, <strong>systèmes d’information</strong> et <strong>services financiers</strong> sous une même gouvernance — pour des organisations qui investissent sur plusieurs années, pas sur un seul livrable ponctuel.</p>
</div>
<p class="about-rule-text" aria-hidden="true">⸻</p>
<span class="about-section-eyebrow">Horizon</span>
<h2 class="about-section-title about-section-title--major">Où nous voulons aller</h2>
<div class="about-vision-panel">
  <p>À moyen et long terme, nous visons à être le partenaire de référence pour les structures qui refusent l’addition de prestataires déconnectés : une équipe capable d’aligner expérience utilisateur, applications, données, ERP/CRM et usages financiers, avec une responsabilité qui s’étend <strong>jusqu’à l’exploitation</strong>, pas seulement jusqu’à la recette.</p>
  <p>Notre pari est simple : des décisions et des équipes <strong>ancrées à Dakar</strong>, des projets menés avec exigence pour le Sénégal et, lorsque le besoin l’impose, pour d’autres pays africains — en gardant la même cohérence d’ensemble sur la durée.</p>
</div>
<p class="about-rule-text" aria-hidden="true">⸻</p>
<span class="about-section-eyebrow">Différenciation</span>
<h2 class="about-section-title about-section-title--major">Ce qui nous distingue</h2>
<div class="about-block">
<ul class="about-list about-list--diff">
<li><strong>Bout-en-bout, pas en silos</strong> Nous ne nous arrêtons pas aux maquettes ou aux rapports : conception, développement, intégration, mise en service et stabilisation — avec une présence après le go-live lorsque vous en avez besoin.</li>
<li><strong>Tech et finance dans le même groupe</strong> Axium Digital, Axium Bank et BiPay permettent de réduire l’écart entre ce qui se passe à l’écran et ce qui se passe en trésorerie, paiement ou épargne, sans multiplier les interlocuteurs.</li>
<li><strong>Ancrage local, ambition régionale</strong> Pilotage et équipes à Dakar ; nous montons des dispositifs pour des organisations basées au Sénégal et, sur projet, ailleurs en Afrique — avec des engagements de calendrier et de qualité explicites.</li>
<li><strong>Patrimoine maintenable</strong> Nous privilégions des choix techniques et fonctionnels que vous ou nous pourrons faire évoluer : documentation, transfert de compétences et dette technique maîtrisée.</li>
</ul>
</div>
<p class="about-rule-text" aria-hidden="true">⸻</p>
<span class="about-section-eyebrow">Méthode</span>
<h2 class="about-section-title about-section-title--major">Comment nous avançons avec vous</h2>
<div class="about-block">
<ol class="about-steps">
<li><strong>Cadrage &amp; priorisation</strong> Besoin métier, utilisateurs, contraintes, risques : nous tranchons ce qui est critique en premier et ce qui peut attendre.</li>
<li><strong>Conception &amp; architecture</strong> Parcours, données, intégrations (y compris ERP/CRM) : nous figeons une trajectoire réaliste avant d’industrialiser.</li>
<li><strong>Réalisation &amp; intégration</strong> Développement, tests, recette avec vos équipes ; ajustements tant que le système n’est pas stable pour les usages réels.</li>
<li><strong>Mise en service &amp; durabilité</strong> Go-live, surveillance des premières semaines, puis accompagnement ou transfert pour que le système reste pertinent dans le temps.</li>
</ol>
</div>
<p class="about-rule-text" aria-hidden="true">⸻</p>
<span class="about-section-eyebrow">Organisation</span>
<h2 class="about-section-title about-section-title--major">Le groupe en appui</h2>
<div class="about-block">
<ul class="about-list">
<li><strong>Axium Digital</strong> — UX/UI, applications web et mobiles, intégration et structuration des systèmes d’information.</li>
<li><strong>Axium Bank</strong> — services financiers adaptés aux usages actuels.</li>
<li><strong>BiPay</strong> — paiement, épargne et investissement accessibles en ligne.</li>
</ul>
<p>Ces entités ne sont pas une vitrine : elles servent la vision d’ensemble — <strong>moins de ruptures</strong> entre le digital, la donnée et la finance pour vos projets structurants.</p>
</div>
<p class="about-rule-text" aria-hidden="true">⸻</p>
<div class="about-block about-closing">
<p class="about-closing-lead">Parlons de votre prochain jalon</p>
<p>Contactez-nous : nous préférons cadrer une trajectoire réaliste qu’empiler des promesses génériques.</p>
</div>
            """
        ).strip(),
        "about_title": "À propos | AXIUM GROUP",
        "about_btn_contact": "Contactez-nous",
        "about_btn_services": "Découvrir nos services",
        "about_back": "Section « À propos » sur l'accueil",
    },
    "en": {
        "about_page_h1_full": "AXIUM GROUP",
        "about_positioning_l1": "The digital heart of the new Africa.",
        "about_positioning_l2": "A technology and finance group building tomorrow’s digital infrastructure.",
        "about_page_tagline": "Digital, information systems and finance — an end-to-end path, led from Dakar.",
        "about_manifest_html": (
            """
<div class="about-block about-lead-block">
  <p class="about-lead">AXIUM GROUP connects <strong>digital product</strong>, <strong>information systems</strong> and <strong>financial services</strong> under one governance — for organisations investing over years, not a one-off deliverable.</p>
</div>
<hr class="about-rule" aria-hidden="true">
<span class="about-section-eyebrow">Horizon</span>
<h2 class="about-section-title about-section-title--major">Where we are headed</h2>
<div class="about-vision-panel">
  <p>Over the medium and long term, we aim to be the reference partner for teams that refuse a patchwork of disconnected vendors: one group able to align user experience, applications, data, ERP/CRM and financial workflows, with accountability that runs <strong>through operations</strong> — not only through UAT.</p>
  <p>Our bet is straightforward: <strong>Dakar-based</strong> leadership and delivery, rigorous execution for Senegal and, when required, for other African markets — with the same end-to-end coherence over time.</p>
</div>
<hr class="about-rule" aria-hidden="true">
<span class="about-section-eyebrow">Differentiation</span>
<h2 class="about-section-title about-section-title--major">What sets us apart</h2>
<div class="about-block">
<ul class="about-list about-list--diff">
<li><strong>End-to-end, not hand-offs</strong> We do not stop at wireframes or slide decks: design, build, integrate, go-live and stabilisation — with post-launch presence when you need it.</li>
<li><strong>Technology and finance in one group</strong> Axium Digital, Axium Bank and BiPay narrow the gap between what happens on screen and what happens in treasury, payments or savings — without a crowd of middlemen.</li>
<li><strong>Local roots, regional project reach</strong> Leadership and teams in Dakar; we run engagements for Senegal-based organisations and, project by project, elsewhere in Africa — with explicit quality and timeline commitments.</li>
<li><strong>Maintainable assets</strong> We favour technical and functional choices that you or we can evolve: documentation, skills transfer and controlled technical debt.</li>
</ul>
</div>
<hr class="about-rule" aria-hidden="true">
<span class="about-section-eyebrow">How we work</span>
<h2 class="about-section-title about-section-title--major">How we move forward with you</h2>
<div class="about-block">
<ol class="about-steps">
<li><strong>Framing &amp; prioritisation</strong> Business need, users, constraints, risks: we decide what must work first and what can wait.</li>
<li><strong>Design &amp; architecture</strong> Journeys, data, integrations (including ERP/CRM): we lock a realistic path before scaling delivery.</li>
<li><strong>Build &amp; integration</strong> Development, testing, acceptance with your teams; adjustments until the system is stable for real use.</li>
<li><strong>Go-live &amp; durability</strong> Launch, watch the first weeks, then handover or ongoing support so the system stays relevant.</li>
</ol>
</div>
<hr class="about-rule" aria-hidden="true">
<span class="about-section-eyebrow">Organisation</span>
<h2 class="about-section-title about-section-title--major">The group behind the work</h2>
<div class="about-block">
<ul class="about-list">
<li><strong>Axium Digital</strong> — UX/UI, web and mobile applications, integration and structuring of information systems.</li>
<li><strong>Axium Bank</strong> — financial services aligned with how people and businesses operate today.</li>
<li><strong>BiPay</strong> — payment, savings and investment online.</li>
</ul>
<p>These entities are not decorative: they support the overall vision — <strong>fewer fractures</strong> between digital, data and finance on structural programmes.</p>
</div>
<hr class="about-rule" aria-hidden="true">
<div class="about-block about-closing">
<p class="about-closing-lead">Let’s talk about your next milestone</p>
<p>Get in touch — we would rather frame a credible path than stack generic promises.</p>
</div>
            """
        ).strip(),
        "about_title": "About | AXIUM GROUP",
        "about_btn_contact": "Contact us",
        "about_btn_services": "Discover our services",
        "about_back": "“About” section on the home page",
    },
}


def about_fallback(lang: str, key: str) -> str | None:
    block = ABOUT_PAGES.get(lang) or ABOUT_PAGES.get("fr") or {}
    v = block.get(key)
    if isinstance(v, tuple):
        v = "".join(str(x) for x in v)
    return v if isinstance(v, str) and v.strip() else None
