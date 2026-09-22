/**
 * Approtech Internship Admin Portal - Client Script
 * Company: Approtech R&D Solutions Pvt. Ltd.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Filter Inputs
  const searchInput = document.getElementById('filterSearch');
  const startDateInput = document.getElementById('filterStartDate');
  const endDateInput = document.getElementById('filterEndDate');
  const domainSelect = document.getElementById('filterDomain');
  const statusSelect = document.getElementById('filterStatus');
  const formatSelect = document.getElementById('filterFormat');
  const btnApplyFilters = document.getElementById('btnApplyFilters');
  const btnClearFilters = document.getElementById('btnClearFilters');
  const visibleCountBadge = document.getElementById('visibleCountBadge');
  const rows = document.querySelectorAll('.submission-row');

  // Stats Counters
  const statTotal = document.getElementById('statTotal');
  const statPending = document.getElementById('statPending');
  const statAccepted = document.getElementById('statAccepted');
  const statRejected = document.getElementById('statRejected');

  // Toast Container
  const toastContainer = document.getElementById('adminToastContainer');

  function showToast(message, type = 'success') {
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `admin-toast ${type === 'danger' ? 'admin-toast-danger' : 'admin-toast-success'}`;
    const iconName = type === 'danger' ? 'x-circle' : 'check-circle-2';
    toast.innerHTML = `
      <i data-lucide="${iconName}" style="width: 18px; height: 18px; flex-shrink: 0; color: ${type === 'danger' ? '#ef4444' : '#10b981'};"></i>
      <span>${message}</span>
    `;
    toastContainer.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    // Trigger animation
    setTimeout(() => {
      toast.classList.add('show');
    }, 10);

    // Auto dismiss after 3.2 seconds
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 3200);
  }

  // Letter Preview Modal Elements
  const letterPreviewModal = document.getElementById('letterPreviewModal');
  const letterPreviewIframe = document.getElementById('letterPreviewIframe');
  const previewModalStudentName = document.getElementById('previewModalStudentName');
  const previewModalAppId = document.getElementById('previewModalAppId');
  const previewModalOpenTab = document.getElementById('previewModalOpenTab');
  const previewModalPrint = document.getElementById('previewModalPrint');
  const previewModalPdf = document.getElementById('previewModalPdf');
  const previewModalWord = document.getElementById('previewModalWord');
  const closeLetterPreviewModal = document.getElementById('closeLetterPreviewModal');

  function openLetterPreview(subId, appId, studentName) {
    if (!letterPreviewModal || !letterPreviewIframe) return;

    if (previewModalStudentName) {
      previewModalStudentName.textContent = `${studentName} - Confirmation Letter`;
    }
    if (previewModalAppId) {
      previewModalAppId.textContent = `Application ID: ${appId}`;
    }
    if (previewModalOpenTab) {
      previewModalOpenTab.href = `/letter/${appId}`;
    }
    if (previewModalPdf) {
      previewModalPdf.href = `/admin/generate-pdf/${subId}`;
    }
    if (previewModalWord) {
      previewModalWord.href = `/admin/generate-word/${subId}`;
    }

    // Set iframe URL to load the exact letter
    letterPreviewIframe.src = `/letter/${appId}`;
    letterPreviewModal.classList.add('open');
    if (window.lucide) lucide.createIcons();
  }

  function closeLetterPreview() {
    if (!letterPreviewModal) return;
    letterPreviewModal.classList.remove('open');
    if (letterPreviewIframe) {
      letterPreviewIframe.src = 'about:blank';
    }
  }

  if (closeLetterPreviewModal) {
    closeLetterPreviewModal.addEventListener('click', closeLetterPreview);
  }

  if (previewModalPrint && letterPreviewIframe) {
    previewModalPrint.addEventListener('click', () => {
      try {
        letterPreviewIframe.contentWindow.focus();
        letterPreviewIframe.contentWindow.print();
      } catch (err) {
        window.open(previewModalOpenTab.href, '_blank');
      }
    });
  }

  // Dossier Modal Elements
  const dossierModal = document.getElementById('dossierModal');
  const closeDossierModal = document.getElementById('closeDossierModal');
  const closeDossierBtn = document.getElementById('closeDossierBtn');
  const dosName = document.getElementById('dosName');
  const dosAppId = document.getElementById('dosAppId');
  const dosStatusBadge = document.getElementById('dosStatusBadge');
  const dosReg = document.getElementById('dosReg');
  const dosEmail = document.getElementById('dosEmail');
  const dosPhone = document.getElementById('dosPhone');
  const dosDegree = document.getElementById('dosDegree');
  const dosCollege = document.getElementById('dosCollege');
  const dosLocation = document.getElementById('dosLocation');
  const dosDomain = document.getElementById('dosDomain');
  const dosMode = document.getElementById('dosMode');
  const dosPeriod = document.getElementById('dosPeriod');
  const dosDuration = document.getElementById('dosDuration');
  const dosPdfLink = document.getElementById('dosPdfLink');
  const dosWordLink = document.getElementById('dosWordLink');
  const dosLetterLink = document.getElementById('dosLetterLink');

  function closeDossier() {
    if (dossierModal) dossierModal.classList.remove('open');
  }
  if (closeDossierModal) closeDossierModal.addEventListener('click', closeDossier);
  if (closeDossierBtn) closeDossierBtn.addEventListener('click', closeDossier);

  // Delete Modal Elements
  const deleteModal = document.getElementById('deleteModal');
  const closeDeleteModal = document.getElementById('closeDeleteModal');
  const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  const deleteTargetName = document.getElementById('deleteTargetName');
  let pendingDeleteId = null;

  function closeDelete() {
    if (deleteModal) deleteModal.classList.remove('open');
    pendingDeleteId = null;
  }
  if (closeDeleteModal) closeDeleteModal.addEventListener('click', closeDelete);
  if (cancelDeleteBtn) cancelDeleteBtn.addEventListener('click', closeDelete);

  // Close modals on clicking backdrop
  window.addEventListener('click', (e) => {
    if (e.target === letterPreviewModal) closeLetterPreview();
    if (e.target === dossierModal) closeDossier();
    if (e.target === deleteModal) closeDelete();
  });

  // Filter Function
  function filterSubmissions() {
    const q = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const sDate = startDateInput ? startDateInput.value : '';
    const eDate = endDateInput ? endDateInput.value : '';
    const dom = domainSelect ? domainSelect.value : '';
    const stat = statusSelect ? statusSelect.value : '';
    const fmt = formatSelect ? formatSelect.value : '';

    let visibleCount = 0;

    rows.forEach(row => {
      const name = (row.getAttribute('data-name') || '').toLowerCase();
      const reg = (row.getAttribute('data-reg') || '').toLowerCase();
      const email = (row.getAttribute('data-email') || '').toLowerCase();
      const phone = (row.getAttribute('data-phone') || '').toLowerCase();
      const college = (row.getAttribute('data-college') || '').toLowerCase();
      const domain = (row.getAttribute('data-domain') || '');
      const mode = (row.getAttribute('data-mode') || '');
      const status = (row.getAttribute('data-status') || '');
      const start = (row.getAttribute('data-start') || '');
      const end = (row.getAttribute('data-end') || '');

      // Search match across all fields
      const matchesSearch = !q || 
        name.includes(q) || 
        reg.includes(q) || 
        email.includes(q) || 
        phone.includes(q) || 
        college.includes(q) || 
        domain.toLowerCase().includes(q);

      const matchesDomain = !dom || domain === dom;
      const matchesStatus = !stat || status === stat;
      const matchesFormat = !fmt || mode === fmt;

      let matchesDate = true;
      if (sDate && start < sDate) matchesDate = false;
      if (eDate && end > eDate) matchesDate = false;

      if (matchesSearch && matchesDomain && matchesStatus && matchesFormat && matchesDate) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    if (visibleCountBadge) {
      visibleCountBadge.textContent = `${visibleCount} Records`;
    }
  }

  // Filter Listeners
  if (searchInput) searchInput.addEventListener('input', filterSubmissions);
  if (startDateInput) startDateInput.addEventListener('change', filterSubmissions);
  if (endDateInput) endDateInput.addEventListener('change', filterSubmissions);
  if (domainSelect) domainSelect.addEventListener('change', filterSubmissions);
  if (statusSelect) statusSelect.addEventListener('change', filterSubmissions);
  if (formatSelect) formatSelect.addEventListener('change', filterSubmissions);
  if (btnApplyFilters) btnApplyFilters.addEventListener('click', filterSubmissions);

  if (btnClearFilters) {
    btnClearFilters.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (startDateInput) startDateInput.value = '';
      if (endDateInput) endDateInput.value = '';
      if (domainSelect) domainSelect.value = '';
      if (statusSelect) statusSelect.value = '';
      if (formatSelect) formatSelect.value = '';
      filterSubmissions();
      showToast('Filters cleared', 'success');
    });
  }

  // GLOBAL EVENT DELEGATION FOR ALL TABLE ACTIONS
  document.addEventListener('click', async (e) => {
    
    // 1. PREVIEW LETTER BUTTON
    const previewBtn = e.target.closest('.btn-preview-letter');
    if (previewBtn) {
      e.preventDefault();
      const subId = previewBtn.getAttribute('data-id');
      const appId = previewBtn.getAttribute('data-app-id');
      const studentName = previewBtn.getAttribute('data-name') || 'Student';
      openLetterPreview(subId, appId, studentName);
      return;
    }

    // 2. ACCEPT / REJECT STATUS BUTTON
    const statusBtn = e.target.closest('.btn-action-status');
    if (statusBtn) {
      e.preventDefault();
      const id = statusBtn.getAttribute('data-id');
      const targetStatus = statusBtn.getAttribute('data-status');
      const studentName = statusBtn.getAttribute('data-name') || 'Student';

      // Visual click response immediately
      statusBtn.style.opacity = '0.5';
      statusBtn.style.transform = 'scale(0.9)';

      try {
        const formData = new FormData();
        formData.append('status', targetStatus);

        const resp = await fetch(`/admin/update-status/${id}`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: formData
        });

        const res = await resp.json();
        statusBtn.style.opacity = '1';
        statusBtn.style.transform = 'scale(1)';

        if (res.success) {
          const row = document.getElementById(`row-${id}`);
          if (row) {
            row.setAttribute('data-status', targetStatus);
            row.classList.remove('row-updated');
            void row.offsetWidth; // retrigger css animation
            row.classList.add('row-updated');

            const cell = document.getElementById(`status-cell-${id}`);
            if (cell) {
              cell.innerHTML = `
                <span class="status-pill status-${targetStatus.toLowerCase()}">
                  <span style="font-size: 8px;">●</span>
                  <span>${targetStatus}</span>
                </span>
              `;
            }
          }

          // Update statistics
          if (res.stats) {
            if (statTotal) statTotal.textContent = res.stats.total;
            if (statPending) statPending.textContent = res.stats.pending;
            if (statAccepted) statAccepted.textContent = res.stats.accepted;
            if (statRejected) statRejected.textContent = res.stats.rejected;
          }

          // Show floating toast notification
          showToast(`Status updated to "${targetStatus}" for ${res.student_name || studentName}`, targetStatus === 'Rejected' ? 'danger' : 'success');
        } else {
          showToast(res.error || 'Failed to update status', 'danger');
        }
      } catch (err) {
        console.error('Status update error:', err);
        statusBtn.style.opacity = '1';
        statusBtn.style.transform = 'scale(1)';
        showToast('Network error updating status', 'danger');
      }
      return;
    }

    // 3. VIEW DOSSIER BUTTON
    const viewBtn = e.target.closest('.btn-view-dossier');
    if (viewBtn) {
      e.preventDefault();
      const id = viewBtn.getAttribute('data-id');
      try {
        const resp = await fetch(`/admin/view/${id}`);
        const res = await resp.json();
        if (res.success && res.data) {
          const d = res.data;
          if (dosName) dosName.textContent = d.full_name;
          if (dosAppId) dosAppId.textContent = d.application_id;
          if (dosReg) dosReg.textContent = d.registration_number;
          if (dosEmail) dosEmail.textContent = d.email;
          if (dosPhone) dosPhone.textContent = d.phone;
          if (dosDegree) dosDegree.textContent = d.degree_department;
          if (dosCollege) dosCollege.textContent = d.institution_name;
          if (dosLocation) dosLocation.textContent = d.institution_location;
          if (dosDomain) dosDomain.textContent = d.internship_domain;
          if (dosMode) dosMode.textContent = d.format_type;
          if (dosPeriod) dosPeriod.textContent = `${d.start_date_fmt} to ${d.end_date_fmt}`;
          if (dosDuration) dosDuration.textContent = `${d.duration_days} Days`;

          if (dosStatusBadge) {
            dosStatusBadge.innerHTML = `
              <span class="status-pill status-${d.status.toLowerCase()}">
                <span style="font-size: 8px;">●</span>
                <span>${d.status}</span>
              </span>
            `;
          }

          if (dosPdfLink) dosPdfLink.href = `/admin/generate-pdf/${d.id}`;
          if (dosWordLink) dosWordLink.href = `/admin/generate-word/${d.id}`;
          if (dosLetterLink) dosLetterLink.href = `/letter/${d.application_id}`;

          if (dossierModal) {
            dossierModal.classList.add('open');
            if (window.lucide) lucide.createIcons();
          }
        }
      } catch (err) {
        console.error('Error viewing dossier:', err);
      }
      return;
    }

    // 4. DELETE BUTTON
    const deleteBtn = e.target.closest('.btn-delete-submission');
    if (deleteBtn) {
      e.preventDefault();
      pendingDeleteId = deleteBtn.getAttribute('data-id');
      const name = deleteBtn.getAttribute('data-name');
      if (deleteTargetName) deleteTargetName.textContent = name;
      if (deleteModal) deleteModal.classList.add('open');
      return;
    }
  });

  // Confirm Delete Action
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', async () => {
      if (!pendingDeleteId) return;

      confirmDeleteBtn.disabled = true;
      confirmDeleteBtn.textContent = 'Deleting...';

      try {
        const resp = await fetch(`/admin/delete/${pendingDeleteId}`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        const res = await resp.json();
        if (res.success) {
          const row = document.getElementById(`row-${pendingDeleteId}`);
          if (row) row.remove();

          if (res.stats) {
            if (statTotal) statTotal.textContent = res.stats.total;
            if (statPending) statPending.textContent = res.stats.pending;
            if (statAccepted) statAccepted.textContent = res.stats.accepted;
            if (statRejected) statRejected.textContent = res.stats.rejected;
          }

          showToast('Record deleted successfully', 'danger');
          closeDelete();
          filterSubmissions();
        } else {
          showToast('Delete operation failed', 'danger');
        }
      } catch (err) {
        console.error('Delete error:', err);
        showToast('Network error deleting record', 'danger');
      } finally {
        confirmDeleteBtn.disabled = false;
        confirmDeleteBtn.textContent = 'Delete Record';
      }
    });
  }

  if (window.lucide) lucide.createIcons();
});
