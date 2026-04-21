/**
 * Carrousel horizontal (une carte à la fois) — accueil #services et page /services/.
 * Racine : [data-ax-services-carousel]
 */
(function () {
  'use strict';

  function initCarousel(root) {
    var viewport = root.querySelector('.ax-services-carousel__viewport');
    var track = root.querySelector('.ax-services-carousel__track');
    var slides = track ? track.querySelectorAll('.ax-services-carousel__slide') : [];
    var btnPrev = root.querySelector('.ax-services-carousel__btn--prev');
    var btnNext = root.querySelector('.ax-services-carousel__btn--next');
    var counter = root.querySelector('.ax-services-carousel__counter');
    var n = slides.length;
    if (!viewport || !track || n === 0 || !btnPrev || !btnNext) return;

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var idx = 0;
    var layoutRetryTimer = null;
    var layoutZeroRetries = 0;

    function layout() {
      var w = Math.round(viewport.getBoundingClientRect().width);
      var sectionW = 0;
      var container = root.closest('.container');
      if (container) sectionW = Math.round(container.getBoundingClientRect().width);
      if (sectionW > 2) w = Math.max(w, sectionW);
      w = Math.max(w, Math.round(root.getBoundingClientRect().width));
      /* Première mesure parfois 0 (onglet en arrière-plan, fonts, flex) → vignettes à largeur 0 et images « cassées ». */
      if (w < 2) {
        if (layoutZeroRetries < 60) {
          layoutZeroRetries += 1;
          if (layoutRetryTimer) clearTimeout(layoutRetryTimer);
          layoutRetryTimer = setTimeout(function () {
            layoutRetryTimer = null;
            layout();
          }, 50);
          return;
        }
        var fallback = root.parentElement ? Math.round(root.parentElement.getBoundingClientRect().width) : 0;
        w = fallback > 2 ? fallback : Math.min(1200, Math.max(320, window.innerWidth || 640));
      } else {
        layoutZeroRetries = 0;
      }
      for (var i = 0; i < slides.length; i++) {
        slides[i].style.flex = '0 0 ' + w + 'px';
        slides[i].style.width = w + 'px';
        slides[i].style.maxWidth = w + 'px';
      }
      track.style.width = w * n + 'px';
      go(idx, true);
    }

    function go(i, instant) {
      idx = Math.max(0, Math.min(n - 1, i));
      var w = Math.round(viewport.getBoundingClientRect().width);
      var x = -idx * w;
      track.style.transition = instant || reduceMotion ? 'none' : 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
      track.style.transform = 'translate3d(' + x + 'px,0,0)';
      btnPrev.disabled = idx <= 0;
      btnNext.disabled = idx >= n - 1;
      if (counter) {
        counter.textContent = idx + 1 + ' / ' + n;
        var ca = root.getAttribute('data-carousel-counter-aria') || '';
        counter.setAttribute('aria-label', (ca ? ca + ' — ' : '') + (idx + 1) + ' / ' + n);
      }
    }

    btnPrev.addEventListener('click', function () {
      go(idx - 1, false);
    });
    btnNext.addEventListener('click', function () {
      go(idx + 1, false);
    });

    document.addEventListener('keydown', function (e) {
      if (!root.contains(document.activeElement)) return;
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        go(idx - 1, false);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        go(idx + 1, false);
      }
    });

    window.addEventListener(
      'resize',
      function () {
        layout();
      },
      { passive: true }
    );

    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'visible') layout();
    });

    if (typeof ResizeObserver !== 'undefined') {
      var ro = new ResizeObserver(function () {
        layout();
      });
      ro.observe(viewport);
    }

    layout();
    requestAnimationFrame(function () {
      layout();
    });
    if (counter) counter.textContent = '1 / ' + n;
  }

  function boot() {
    document.querySelectorAll('[data-ax-services-carousel]').forEach(initCarousel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
