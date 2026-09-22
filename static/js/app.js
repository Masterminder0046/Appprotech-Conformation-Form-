/**
 * Approtech Internship Confirmation Letter Request System - Client Script
 * Company: Approtech R&D Solutions Pvt. Ltd. (ISO 9001 : 2015 Certified)
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('confirmationForm');
  if (!form) return;

  // Form Inputs
  const fullNameInput = document.getElementById('full_name');
  const regNoInput = document.getElementById('registration_number');
  const emailInput = document.getElementById('email');
  const phoneInput = document.getElementById('phone');
  const degreeInput = document.getElementById('degree_department');
  const instNameInput = document.getElementById('institution_name');
  const instLocInput = document.getElementById('institution_location');
  const domainInput = document.getElementById('internship_domain');
  const startDateInput = document.getElementById('start_date');
  const endDateInput = document.getElementById('end_date');
  const formatInput = document.getElementById('format_type');
  const durationText = document.getElementById('durationText');

  // Domain search & chips
  const domainSearchInput = document.getElementById('domainSearch');
  const domainChips = document.querySelectorAll('.domain-chip');
  const formatCards = document.querySelectorAll('.format-card');

  // Modals & Buttons
  const reviewModal = document.getElementById('reviewModal');
  const reviewBtn = document.getElementById('reviewBtn');
  const closeReviewModal = document.getElementById('closeReviewModal');
  const cancelReviewBtn = document.getElementById('cancelReviewBtn');
  const confirmSubmitBtn = document.getElementById('confirmSubmitBtn');

  // Review Summary Fields
  const revName = document.getElementById('revName');
  const revRegNo = document.getElementById('revRegNo');
  const revEmail = document.getElementById('revEmail');
  const revPhone = document.getElementById('revPhone');
  const revDegree = document.getElementById('revDegree');
  const revCollege = document.getElementById('revCollege');
  const revLocation = document.getElementById('revLocation');
  const revDomain = document.getElementById('revDomain');
  const revFormat = document.getElementById('revFormat');
  const revDates = document.getElementById('revDates');
  const revDuration = document.getElementById('revDuration');

  // Format Date (YYYY-MM-DD -> DD-MM-YYYY)
  function formatDate(str) {
    if (!str) return '';
    const parts = str.split('-');
    if (parts.length === 3) {
      return `${parts[2]}-${parts[1]}-${parts[0]}`;
    }
    return str;
  }

  // Calculate Duration
  function calculateDuration() {
    const sStr = startDateInput.value;
    const eStr = endDateInput.value;
    if (!sStr || !eStr) {
      if (durationText) durationText.textContent = 'Select start and end dates';
      return 0;
    }

    const s = new Date(sStr);
    const e = new Date(eStr);
    if (e < s) {
      if (durationText) durationText.textContent = 'End date cannot be earlier than start date';
      return 0;
    }

    const diffMs = e.getTime() - s.getTime();
    const days = Math.ceil(diffMs / (1000 * 60 * 60 * 24)) + 1;
    if (durationText) {
      durationText.textContent = `${days} Days Duration`;
    }
    return days;
  }

  // Input Listeners for Validation
  [fullNameInput, regNoInput, degreeInput, instNameInput, instLocInput, emailInput, phoneInput].forEach(el => {
    if (el) el.addEventListener('input', () => {
      validateField(el);
    });
  });

  [startDateInput, endDateInput].forEach(el => {
    if (el) el.addEventListener('change', () => {
      calculateDuration();
      validateField(el);
    });
  });

  // Domain Chip Selection
  domainChips.forEach(chip => {
    chip.addEventListener('click', () => {
      domainChips.forEach(c => c.classList.remove('selected'));
      chip.classList.add('selected');
      const val = chip.getAttribute('data-domain');
      domainInput.value = val;
      const dErr = document.getElementById('domainError');
      if (dErr) dErr.style.display = 'none';
    });
  });

  // Domain Search Filter
  if (domainSearchInput) {
    domainSearchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      domainChips.forEach(chip => {
        const dText = chip.getAttribute('data-domain').toLowerCase();
        if (dText.includes(q)) {
          chip.style.display = 'inline-flex';
        } else {
          chip.style.display = 'none';
        }
      });
    });
  }

  // Format Type Toggle Cards
  formatCards.forEach(card => {
    card.addEventListener('click', () => {
      formatCards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      const fVal = card.getAttribute('data-format');
      formatInput.value = fVal;
    });
  });

  // Toast notification helper
  function showToast(msg, type = 'error') {
    let toast = document.getElementById('portalToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'portalToast';
      toast.className = 'portal-toast';
      document.body.appendChild(toast);
    }
    toast.className = `portal-toast ${type} show`;
    toast.innerHTML = `
      <i data-lucide="${type === 'error' ? 'alert-circle' : 'check-circle-2'}" style="width: 20px; height: 20px; flex-shrink: 0;"></i>
      <span>${msg}</span>
    `;
    if (window.lucide) lucide.createIcons();

    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
      toast.classList.remove('show');
    }, 4500);
  }

  // Validation Logic
  function validateField(field) {
    if (!field) return true;
    const parent = field.closest('.form-group');
    if (!parent) return true;
    let isValid = true;
    const val = field.value.trim();

    if (field.hasAttribute('required') && !val) {
      isValid = false;
    } else if (field.type === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      isValid = emailRegex.test(val);
    } else if (field.id === 'phone') {
      const cleanPhone = val.replace(/\D/g, '');
      isValid = cleanPhone.length >= 10;
    } else if (field.id === 'end_date') {
      const sVal = startDateInput.value;
      if (sVal && val && val < sVal) {
        isValid = false;
      }
    }

    if (!isValid) {
      parent.classList.add('has-error');
      field.classList.add('is-invalid');
    } else {
      parent.classList.remove('has-error');
      field.classList.remove('is-invalid');
    }
    return isValid;
  }

  function validateAll() {
    let allValid = true;
    let firstInvalid = null;
    const requiredInputs = [
      fullNameInput, regNoInput, emailInput, phoneInput,
      degreeInput, instNameInput, instLocInput,
      startDateInput, endDateInput
    ];

    requiredInputs.forEach(input => {
      if (input) {
        const valid = validateField(input);
        if (!valid) {
          allValid = false;
          if (!firstInvalid) firstInvalid = input;
        }
      }
    });

    const domainParent = domainInput ? domainInput.closest('.form-group') : null;
    if (!domainInput || !domainInput.value.trim()) {
      allValid = false;
      if (domainParent) domainParent.classList.add('has-error');
      const dErr = document.getElementById('domainError');
      if (dErr) dErr.style.display = 'block';
      if (!firstInvalid) firstInvalid = domainSearchInput || domainChips[0];
    } else {
      if (domainParent) domainParent.classList.remove('has-error');
      const dErr = document.getElementById('domainError');
      if (dErr) dErr.style.display = 'none';
    }

    return { allValid, firstInvalid };
  }

  // Intercept form submit event to use review modal
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (reviewBtn) reviewBtn.click();
  });

  // Review Modal Handling
  if (reviewBtn) {
    reviewBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const { allValid, firstInvalid } = validateAll();
      if (!allValid) {
        showToast('Please fill in all required fields marked with *', 'error');
        if (firstInvalid) {
          firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
          if (typeof firstInvalid.focus === 'function') {
            firstInvalid.focus();
          }
        }
        return;
      }

      // Populate review modal fields
      if (revName) revName.textContent = fullNameInput.value.trim();
      if (revRegNo) revRegNo.textContent = regNoInput.value.trim();
      if (revEmail) revEmail.textContent = emailInput.value.trim();
      if (revPhone) revPhone.textContent = phoneInput.value.trim();
      if (revDegree) revDegree.textContent = degreeInput.value.trim();
      if (revCollege) revCollege.textContent = instNameInput.value.trim();
      if (revLocation) revLocation.textContent = instLocInput.value.trim();
      if (revDomain) revDomain.textContent = domainInput.value.trim();
      if (revFormat) revFormat.textContent = formatInput.value.trim();
      if (revDates) revDates.textContent = `${formatDate(startDateInput.value)} to ${formatDate(endDateInput.value)}`;
      if (revDuration) revDuration.textContent = `${calculateDuration()} Days`;

      // Open Modal (support both active and open classes)
      if (reviewModal) {
        reviewModal.classList.add('active', 'open');
        document.body.style.overflow = 'hidden';
      }
      if (window.lucide) lucide.createIcons();
    });
  }

  function closeReview() {
    if (reviewModal) {
      reviewModal.classList.remove('active', 'open');
      document.body.style.overflow = '';
    }
  }

  if (closeReviewModal) closeReviewModal.addEventListener('click', closeReview);
  if (cancelReviewBtn) cancelReviewBtn.addEventListener('click', closeReview);
  
  if (reviewModal) {
    reviewModal.addEventListener('click', (e) => {
      if (e.target === reviewModal) {
        closeReview();
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && reviewModal && (reviewModal.classList.contains('active') || reviewModal.classList.contains('open'))) {
      closeReview();
    }
  });

  // Blast Modal & Confetti Elements
  const successBlastModal = document.getElementById('successBlastModal');
  const blastAppId = document.getElementById('blastAppId');
  const blastDoneBtn = document.getElementById('blastDoneBtn');

  // Confetti Blast Engine
  function triggerConfettiBlast() {
    const canvas = document.getElementById('confettiCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colors = ['#0088FF', '#0052D4', '#00D2FF', '#10B981', '#F59E0B', '#6366F1', '#EC4899', '#38BDF8'];
    const particles = [];
    const count = 130;
    const originX = canvas.width / 2;
    const originY = canvas.height * 0.42;

    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 14 + 7;
      particles.push({
        x: originX,
        y: originY,
        vx: Math.cos(angle) * speed * (Math.random() * 0.8 + 0.5),
        vy: Math.sin(angle) * speed * (Math.random() * 0.8 + 0.5) - 5,
        size: Math.random() * 9 + 6,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        rotSpeed: (Math.random() - 0.5) * 12,
        opacity: 1,
        shape: Math.random() > 0.35 ? 'rect' : 'circle',
        drag: 0.955,
        gravity: 0.26
      });
    }

    let animationFrame;
    function render() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let activeCount = 0;

      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.vx *= p.drag;
        p.vy = p.vy * p.drag + p.gravity;
        p.rotation += p.rotSpeed;
        p.opacity -= 0.006;

        if (p.opacity > 0 && p.y < canvas.height + 30) {
          activeCount++;
          ctx.save();
          ctx.globalAlpha = Math.max(0, p.opacity);
          ctx.translate(p.x, p.y);
          ctx.rotate((p.rotation * Math.PI) / 180);
          ctx.fillStyle = p.color;

          if (p.shape === 'rect') {
            ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
          } else {
            ctx.beginPath();
            ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
            ctx.fill();
          }
          ctx.restore();
        }
      });

      if (activeCount > 0) {
        animationFrame = requestAnimationFrame(render);
      } else {
        cancelAnimationFrame(animationFrame);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }

    render();
  }

  // Submit via AJAX with Celebration Blast Modal
  if (confirmSubmitBtn) {
    confirmSubmitBtn.addEventListener('click', async () => {
      const originalHtml = confirmSubmitBtn.innerHTML;
      confirmSubmitBtn.disabled = true;
      confirmSubmitBtn.innerHTML = `
        <span class="btn-spinner" style="display:inline-block; width: 15px; height: 15px; border: 2px solid #ffffff; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; vertical-align: middle; margin-right: 6px;"></span>
        <span>Submitting...</span>
      `;

      const formData = new FormData(form);

      try {
        const resp = await fetch('/submit', {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: formData
        });

        const res = await resp.json();
        if (res.success) {
          // Close review modal
          closeReview();

          // Set application ID in celebration blast modal
          if (blastAppId) {
            blastAppId.textContent = res.application_id || 'APP-2026-CONFIRMED';
          }

          // Open animated celebration blast modal
          if (successBlastModal) {
            successBlastModal.classList.add('active', 'open');
            document.body.style.overflow = 'hidden';
            if (window.lucide) lucide.createIcons();
            triggerConfettiBlast();
          }

          // Reset button state
          confirmSubmitBtn.disabled = false;
          confirmSubmitBtn.innerHTML = originalHtml;
        } else {
          showToast(res.errors ? res.errors.join(', ') : (res.message || 'Submission failed. Please check your inputs.'), 'error');
          confirmSubmitBtn.disabled = false;
          confirmSubmitBtn.innerHTML = originalHtml;
          if (window.lucide) lucide.createIcons();
        }
      } catch (err) {
        console.error('AJAX submit exception, falling back to standard submit:', err);
        form.submit();
      }
    });
  }

  // Done button in blast modal
  if (blastDoneBtn) {
    blastDoneBtn.addEventListener('click', () => {
      if (successBlastModal) successBlastModal.classList.remove('active', 'open');
      document.body.style.overflow = '';
      window.location.href = '/';
    });
  }

  if (successBlastModal) {
    successBlastModal.addEventListener('click', (e) => {
      if (e.target === successBlastModal) {
        successBlastModal.classList.remove('active', 'open');
        document.body.style.overflow = '';
        window.location.href = '/';
      }
    });
  }

  // Initialize values
  calculateDuration();
  if (window.lucide) lucide.createIcons();
});
