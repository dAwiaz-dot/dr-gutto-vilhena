// Mobile nav toggle
const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".site-nav");
if (toggle && nav) {
  const closeMenu = () => {
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Abrir menu");
  };
  toggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
    toggle.setAttribute("aria-label", isOpen ? "Fechar menu" : "Abrir menu");
  });
  nav.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link) return;
    closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
  document.addEventListener("click", (event) => {
    if (!nav.classList.contains("is-open")) return;
    if (nav.contains(event.target) || toggle.contains(event.target)) return;
    closeMenu();
  });
}

// Header glass state on scroll
const header = document.querySelector("[data-header]");
if (header) {
  const updateHeader = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 12);
  };
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });
}

// Reveal-on-scroll
const revealTargets = document.querySelectorAll("[data-reveal]");
if (revealTargets.length && "IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.14, rootMargin: "0px 0px -40px 0px" }
  );
  revealTargets.forEach((el) => revealObserver.observe(el));
} else {
  revealTargets.forEach((el) => el.classList.add("is-visible"));
}

// Timeline connecting line
const timeline = document.querySelector("[data-timeline]");
if (timeline && "IntersectionObserver" in window) {
  const timelineObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.3 }
  );
  timelineObserver.observe(timeline);
} else if (timeline) {
  timeline.classList.add("is-visible");
}

// Treatment modals
const modalOverlay = document.querySelector("[data-modal-overlay]");
if (modalOverlay) {
  const modalPanels = Array.from(modalOverlay.querySelectorAll("[data-modal-panel]"));
  const openButtons = Array.from(document.querySelectorAll("[data-open-modal]"));
  let lastTrigger = null;

  const getFocusable = (panel) =>
    Array.from(
      panel.querySelectorAll(
        'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    );

  const closeModal = () => {
    const activePanel = modalOverlay.querySelector("[data-active]");
    modalOverlay.classList.remove("is-open");
    if (activePanel) {
      activePanel.removeAttribute("data-active");
    }
    window.setTimeout(() => {
      modalPanels.forEach((panel) => panel.setAttribute("hidden", ""));
      modalOverlay.setAttribute("hidden", "");
    }, 220);
    if (lastTrigger) lastTrigger.focus();
  };

  const openModal = (name, trigger) => {
    const panel = modalPanels.find((p) => p.dataset.modalPanel === name);
    if (!panel) return;
    lastTrigger = trigger || null;
    modalOverlay.removeAttribute("hidden");
    modalPanels.forEach((p) => p.setAttribute("hidden", ""));
    panel.removeAttribute("hidden");
    requestAnimationFrame(() => {
      modalOverlay.classList.add("is-open");
      panel.setAttribute("data-active", "");
      const focusable = getFocusable(panel);
      (focusable[0] || panel).focus();
    });
  };

  openButtons.forEach((btn) => {
    btn.addEventListener("click", () => openModal(btn.dataset.openModal, btn));
  });

  modalOverlay.querySelectorAll("[data-modal-close]").forEach((btn) => {
    btn.addEventListener("click", closeModal);
  });

  modalOverlay.addEventListener("click", (event) => {
    if (event.target === modalOverlay) closeModal();
  });

  document.addEventListener("keydown", (event) => {
    if (!modalOverlay.classList.contains("is-open")) return;
    if (event.key === "Escape") {
      closeModal();
      return;
    }
    if (event.key === "Tab") {
      const activePanel = modalOverlay.querySelector("[data-active]");
      if (!activePanel) return;
      const focusable = getFocusable(activePanel);
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });
}

// Smart form: phone mask, validation, WhatsApp submit
const smartForm = document.querySelector("[data-smart-form]");
if (smartForm) {
  const phoneInput = smartForm.querySelector("[data-phone-mask]");
  const feedback = smartForm.querySelector("[data-form-feedback]");

  if (phoneInput) {
    phoneInput.addEventListener("input", () => {
      const digits = phoneInput.value.replace(/\D/g, "").slice(0, 11);
      let formatted = digits;
      if (digits.length > 2) {
        formatted = `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
      }
      if (digits.length > 7) {
        formatted = `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
      }
      phoneInput.value = formatted;
    });
  }

  const setFieldError = (field, message) => {
    const wrapper = field.closest(".form-field");
    const errorEl = smartForm.querySelector(`[data-error-for="${field.name}"]`);
    if (message) {
      wrapper.classList.add("has-error");
      if (errorEl) errorEl.textContent = message;
      field.setAttribute("aria-invalid", "true");
    } else {
      wrapper.classList.remove("has-error");
      if (errorEl) errorEl.textContent = "";
      field.removeAttribute("aria-invalid");
    }
  };

  const validateForm = () => {
    let valid = true;
    const nome = smartForm.elements.nome;
    const telefone = smartForm.elements.telefone;
    const motivo = smartForm.elements.motivo;

    if (!nome.value.trim()) {
      setFieldError(nome, "Informe seu nome.");
      valid = false;
    } else {
      setFieldError(nome, "");
    }

    const phoneDigits = telefone.value.replace(/\D/g, "");
    if (phoneDigits.length < 10) {
      setFieldError(telefone, "Informe um telefone com DDD.");
      valid = false;
    } else {
      setFieldError(telefone, "");
    }

    if (!motivo.value) {
      setFieldError(motivo, "Selecione uma opção.");
      valid = false;
    } else {
      setFieldError(motivo, "");
    }

    return valid;
  };

  smartForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!validateForm()) {
      if (feedback) feedback.textContent = "Revise os campos destacados antes de enviar.";
      return;
    }

    const nome = smartForm.elements.nome.value.trim();
    const telefone = smartForm.elements.telefone.value.trim();
    const motivo = smartForm.elements.motivo.value;

    const message =
      `Olá, Dr. Gutto! Meu nome é ${nome}. ` +
      `Tenho interesse em: ${motivo}. ` +
      `Meu WhatsApp para contato: ${telefone}.`;

    const url = `https://wa.me/5535991338862?text=${encodeURIComponent(message)}`;
    window.open(url, "_blank", "noreferrer");

    if (feedback) {
      feedback.textContent = "Abrindo o WhatsApp com sua mensagem preenchida...";
    }
  });
}
