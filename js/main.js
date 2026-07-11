/* ============================================================
   NIGAMA FOUNDATION — Main JS
   ============================================================ */

// ── bfcache restore: re-show fade-up elements ──
window.addEventListener('pageshow', (e) => {
  if (e.persisted) {
    document.body.style.opacity = '1';
    document.body.style.animation = 'none';
    document.querySelectorAll('.fade-up').forEach(el => el.classList.add('visible'));
  }
});

// ── Nav: always frosted on inner pages, scroll-aware on home ─
const nav = document.querySelector('.nav');
const isHomePage = document.querySelector('.hero') !== null;

function updateNav() {
  nav?.classList.add('scrolled');
}
updateNav();
window.addEventListener('scroll', updateNav, { passive: true });

// ── Sticky donate CTA (homepage only) ───────────────────────
const stickyDonate = document.querySelector('.sticky-donate');
if (stickyDonate && isHomePage) {
  window.addEventListener('scroll', () => {
    const heroBottom = document.querySelector('.hero')?.getBoundingClientRect().bottom ?? 0;
    stickyDonate.classList.toggle('visible', heroBottom < 0);
  }, { passive: true });
}

// ── Mobile nav ───────────────────────────────────────────────
const hamburger = document.querySelector('.nav-hamburger');
const mobileMenu = document.querySelector('.nav-mobile');

hamburger?.addEventListener('click', () => {
  const isOpen = mobileMenu?.classList.toggle('open');
  hamburger.setAttribute('aria-expanded', String(isOpen));
});

document.querySelectorAll('.nav-mobile a').forEach(link => {
  link.addEventListener('click', () => mobileMenu?.classList.remove('open'));
});

// ── Scroll-triggered fade-up ─────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ── Counter animation ────────────────────────────────────────
function animateCounter(el) {
  const target   = parseInt(el.dataset.target, 10);
  const suffix   = el.dataset.suffix ?? '';
  const prefix   = el.dataset.prefix ?? '';
  const duration = 1600;
  const start    = performance.now();

  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased    = 1 - Math.pow(1 - progress, 3);
    el.textContent = prefix + Math.round(eased * target).toLocaleString() + suffix;
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      animateCounter(e.target);
      counterObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.4 });

document.querySelectorAll('[data-target]').forEach(el => counterObserver.observe(el));

// ── Donation amount selector ──────────────────────────────────
const amountBtns  = document.querySelectorAll('.amount-btn');
const customInput = document.querySelector('#donate-amount, .donate-custom input');

amountBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    amountBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    if (customInput && btn.dataset.amount) customInput.value = btn.dataset.amount;
  });
});

customInput?.addEventListener('input', () => {
  amountBtns.forEach(b => b.classList.remove('active'));
});

// ── Video: inline player + fullscreen modal ──────────────────
const videoModal        = document.getElementById('video-modal');
const videoModalIframe  = document.getElementById('video-modal-iframe');
const videoInlineIframe = document.getElementById('video-inline-iframe');
const videoPlayerInline = document.getElementById('video-player-inline');
const videoPosterWrap   = document.getElementById('video-poster-wrap');
const videoClose        = videoModal?.querySelector('.video-modal-close');
const videoBackdrop     = videoModal?.querySelector('.video-modal-backdrop');
const videoExpandBtn    = document.getElementById('video-expand-btn');
const videoInlineClose  = document.getElementById('video-inline-close');

// Play button → swap poster for inline iframe
document.querySelectorAll('[data-video]').forEach(btn => {
  btn.addEventListener('click', () => {
    const id = btn.dataset.video;
    videoInlineIframe.src = `https://www.youtube.com/embed/${id}?autoplay=1&rel=0`;
    videoPosterWrap.hidden = true;
    videoPlayerInline.hidden = false;
  });
});

// Close button → stop inline, restore poster
videoInlineClose?.addEventListener('click', () => {
  videoInlineIframe.src = '';
  videoPlayerInline.hidden = true;
  videoPosterWrap.hidden = false;
});

// Expand button → stop inline, open fullscreen modal
videoExpandBtn?.addEventListener('click', () => {
  const src = videoInlineIframe.src;
  videoInlineIframe.src = '';
  videoPosterWrap.hidden = false;
  videoPlayerInline.hidden = true;
  videoModalIframe.src = src;
  videoModal.classList.add('is-open');
  document.body.style.overflow = 'hidden';
});

function closeVideoModal() {
  videoModal.classList.remove('is-open');
  videoModalIframe.src = '';
  document.body.style.overflow = '';
}

videoClose?.addEventListener('click', closeVideoModal);
videoBackdrop?.addEventListener('click', closeVideoModal);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && videoModal?.classList.contains('is-open')) closeVideoModal();
});

// ── Certificate lightbox ─────────────────────────────────────
const certModal    = document.getElementById('cert-modal');
const certModalImg = document.getElementById('cert-modal-img');
const certClose    = certModal?.querySelector('.cert-modal-close');
const certBackdrop = certModal?.querySelector('.cert-modal-backdrop');

document.querySelectorAll('[data-cert]').forEach(btn => {
  btn.addEventListener('click', () => {
    certModalImg.src = btn.dataset.cert;
    certModal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  });
});

function closeCertModal() {
  certModal?.classList.remove('is-open');
  if (certModalImg) certModalImg.src = '';
  document.body.style.overflow = '';
}

certClose?.addEventListener('click', closeCertModal);
certBackdrop?.addEventListener('click', closeCertModal);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && certModal?.classList.contains('is-open')) closeCertModal();
});

// ── Contact form ─────────────────────────────────────────────
const contactForm   = document.querySelector('#contact-form');
const contactThanks = document.querySelector('#contact-thanks');

contactForm?.addEventListener('submit', (e) => {
  e.preventDefault();
  contactForm.style.display = 'none';
  if (contactThanks) contactThanks.style.display = 'block';
});

// ── Prefetch same-origin pages on hover/focus for instant transitions ──
(() => {
  const prefetched = new Set();
  const supportsPrefetch = (() => {
    const l = document.createElement('link');
    return l.relList && l.relList.supports && l.relList.supports('prefetch');
  })();

  function prefetch(url) {
    if (!url || prefetched.has(url)) return;
    prefetched.add(url);
    if (supportsPrefetch) {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = url;
      link.as = 'document';
      document.head.appendChild(link);
    } else {
      // Fallback: warm the HTTP cache with a low-priority fetch
      fetch(url, { credentials: 'same-origin', priority: 'low' }).catch(() => {});
    }
  }

  function candidate(a) {
    if (!a || !a.href) return null;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin) return null;         // same-origin only
    if (url.pathname === location.pathname) return null;       // not the current page
    if (url.hash && url.pathname === location.pathname) return null;
    if (a.hasAttribute('download') || a.target === '_blank') return null;
    return url.href;
  }

  function onIntent(e) {
    const a = e.target.closest && e.target.closest('a[href]');
    if (a) prefetch(candidate(a));
  }

  document.addEventListener('mouseover', onIntent, { passive: true });
  document.addEventListener('focusin', onIntent, { passive: true });
  document.addEventListener('touchstart', onIntent, { passive: true });

  // Idle-prefetch the primary nav destinations so first click is instant too
  const idle = window.requestIdleCallback || ((fn) => setTimeout(fn, 1500));
  idle(() => {
    document.querySelectorAll('.nav-links a[href]').forEach((a) => prefetch(candidate(a)));
  });
})();
