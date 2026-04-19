/**
 * Chat conversationnel — POST /api/chat, statut /api/chat/status à l’ouverture.
 */
(function () {
  'use strict';

  var i18n = window.AXIUM_CHAT_I18N || {};
  var root = document.getElementById('ax-chat');
  if (!root) return;

  var toggle = document.getElementById('ax-chat-toggle');
  var panel = document.getElementById('ax-chat-panel');
  var closeBtn = document.getElementById('ax-chat-close');
  var bodyEl = document.getElementById('ax-chat-body');
  var inputEl = document.getElementById('ax-chat-input');
  var sendBtn = document.getElementById('ax-chat-send');
  var newBtn = document.getElementById('ax-chat-new');
  var openFormBtn = document.getElementById('ax-chat-open-form');
  var unconfiguredEl = document.getElementById('ax-chat-unconfigured');
  var composeEl = document.getElementById('ax-chat-compose');

  if (!toggle || !panel || !bodyEl) return;

  var apiChat = root.getAttribute('data-api-chat') || '';
  var apiReset = root.getAttribute('data-api-reset') || '';
  var apiStatus = root.getAttribute('data-api-status') || '';
  /** Saisie activée (clé OpenAI et/ou mode local serveur). */
  var chatEnabled = root.getAttribute('data-llm') === '1';

  var sending = false;

  function t(key) {
    return i18n[key] || key;
  }

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function applyChatVisibility(enabled) {
    chatEnabled = !!enabled;
    if (unconfiguredEl) unconfiguredEl.hidden = chatEnabled;
    if (composeEl) composeEl.hidden = !chatEnabled;
  }

  function refreshChatStatus(done) {
    if (!apiStatus) {
      applyChatVisibility(chatEnabled);
      if (done) done();
      return;
    }
    fetch(apiStatus, { credentials: 'same-origin', headers: { Accept: 'application/json' } })
      .then(function (r) {
        return r.json().catch(function () {
          return {};
        });
      })
      .then(function (data) {
        if (typeof data.chat_enabled === 'boolean') {
          applyChatVisibility(data.chat_enabled);
        }
      })
      .catch(function () {})
      .finally(function () {
        if (done) done();
      });
  }

  function addBubble(text, fromUser) {
    var div = document.createElement('div');
    div.className = 'ax-chat-msg' + (fromUser ? ' ax-chat-msg--user' : ' ax-chat-msg--bot');
    div.innerHTML = '<div class="ax-chat-msg-inner">' + esc(text) + '</div>';
    bodyEl.appendChild(div);
    bodyEl.scrollTop = bodyEl.scrollHeight;
    return div;
  }

  function addTyping() {
    var div = document.createElement('div');
    div.className = 'ax-chat-msg ax-chat-msg--bot ax-chat-msg--typing';
    div.innerHTML = '<div class="ax-chat-msg-inner"><span class="ax-chat-typing-dots">' + esc(t('typing')) + '</span></div>';
    bodyEl.appendChild(div);
    bodyEl.scrollTop = bodyEl.scrollHeight;
    return div;
  }

  function removeTyping(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function setOpen(open) {
    root.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    panel.hidden = !open;
    if (open && chatEnabled && inputEl) {
      try {
        inputEl.focus();
      } catch (e) {}
    }
  }

  function normalizePath(pathname) {
    if (!pathname || pathname === '/') return '/';
    var p = pathname.replace(/\/+$/, '');
    return p || '/';
  }

  function applyChatPrefillFromSession() {
    var raw;
    try {
      raw = sessionStorage.getItem('axium_chat_prefill');
      if (raw) sessionStorage.removeItem('axium_chat_prefill');
    } catch (e) {
      return;
    }
    if (!raw) return;
    var data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      return;
    }
    if (!data || !data.message) return;
    var ta = document.querySelector('.cta-contact-form textarea[name="message"]');
    if (!ta) return;
    if (ta.value && ta.value.trim().length) return;
    ta.value = data.message;
    var ctaPanel = document.getElementById('cta-project-panel');
    var ctaToggle = document.getElementById('cta-launch-toggle');
    if (ctaPanel && ctaToggle) {
      ctaPanel.hidden = false;
      ctaToggle.setAttribute('aria-expanded', 'true');
      ctaToggle.classList.add('is-open');
    }
    try {
      ta.focus();
    } catch (err) {}
  }

  window.AXIUM_applyChatPrefillFromSession = applyChatPrefillFromSession;

  function collectTranscript() {
    var lines = [t('prefill_intro'), ''];
    bodyEl.querySelectorAll('.ax-chat-msg').forEach(function (row) {
      if (row.classList.contains('ax-chat-msg--typing')) return;
      var inner = row.querySelector('.ax-chat-msg-inner');
      if (!inner) return;
      var text = inner.textContent.trim();
      if (!text) return;
      var who = row.classList.contains('ax-chat-msg--user') ? t('transcript_you') : t('transcript_assistant');
      lines.push(who + ': ' + text);
    });
    return lines.join('\n');
  }

  function openContactForm() {
    var text = collectTranscript();
    try {
      sessionStorage.setItem('axium_chat_prefill', JSON.stringify({ message: text, ts: Date.now() }));
    } catch (e) {}
    var dest = root.getAttribute('data-contact-href') || '/nous-ecrire#contact-form';
    try {
      var url = new URL(dest, window.location.href);
      if (normalizePath(url.pathname) === normalizePath(window.location.pathname)) {
        if (url.hash) window.location.hash = url.hash;
        else window.location.hash = '#contact-form';
        applyChatPrefillFromSession();
        setOpen(false);
        var anchor = document.getElementById('contact-form') || document.getElementById('contact-cta');
        if (anchor) anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
    } catch (e) {}
    window.location.href = dest;
  }

  function showError(msg) {
    addBubble(msg || t('error_generic'), false);
  }

  function sendMessage() {
    if (!chatEnabled || sending || !inputEl) return;
    var v = (inputEl.value || '').trim();
    if (!v.length) return;
    sending = true;
    inputEl.value = '';
    if (sendBtn) sendBtn.disabled = true;
    addBubble(v, true);
    var typingEl = addTyping();

    fetch(apiChat, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ message: v }),
    })
      .then(function (r) {
        return r.text().then(function (txt) {
          var data = {};
          try {
            data = txt ? JSON.parse(txt) : {};
          } catch (e) {}
          if (!r.ok) {
            throw new Error(data.error || t('error_generic'));
          }
          return data;
        });
      })
      .then(function (data) {
        removeTyping(typingEl);
        if (data.reply) addBubble(data.reply, false);
        else showError(t('error_generic'));
      })
      .catch(function (err) {
        removeTyping(typingEl);
        showError(err && err.message ? err.message : t('error_network'));
      })
      .finally(function () {
        sending = false;
        if (sendBtn) sendBtn.disabled = false;
        try {
          inputEl.focus();
        } catch (e) {}
      });
  }

  function resetChat() {
    if (!apiReset) return;
    fetch(apiReset, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    }).finally(function () {
      bodyEl.innerHTML = '';
      addBubble(t('welcome'), false);
      if (inputEl) inputEl.value = '';
      try {
        inputEl.focus();
      } catch (e) {}
    });
  }

  function initWelcome() {
    bodyEl.innerHTML = '';
    addBubble(t('welcome'), false);
  }

  toggle.addEventListener('click', function () {
    var opening = !root.classList.contains('is-open');
    if (!opening) {
      setOpen(false);
      return;
    }
    refreshChatStatus(function () {
      setOpen(true);
    });
  });
  if (closeBtn) closeBtn.addEventListener('click', function () { setOpen(false); });

  if (sendBtn) sendBtn.addEventListener('click', sendMessage);
  if (inputEl) {
    inputEl.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' || e.shiftKey) return;
      e.preventDefault();
      sendMessage();
    });
  }
  if (newBtn) newBtn.addEventListener('click', resetChat);
  if (openFormBtn) openFormBtn.addEventListener('click', openContactForm);

  initWelcome();
  applyChatVisibility(chatEnabled);
  refreshChatStatus(null);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && root.classList.contains('is-open')) setOpen(false);
  });
})();
