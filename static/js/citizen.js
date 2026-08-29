/* ==========================================================================
   CivicSense — Citizen Portal Logic (Wizard, Cards, Timeline, Rating)
   ========================================================================== */

let citizenComplaints = [];
let selectedCategory = 'Garbage';
let selectedPriority = 'Medium';
let currentRating = 5;

document.addEventListener('DOMContentLoaded', () => {
  loadCitizenComplaints();
});

// ─────────────────────────── Tab Navigation ───────────────────────────
function switchTab(tabId) {
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const activeLink = document.querySelector(`.nav-link[data-tab="${tabId}"]`);
  if (activeLink) activeLink.classList.add('active');

  const tabs = ['complaints', 'report', 'feedback', 'profile'];
  tabs.forEach(t => {
    const el = document.getElementById(`tabContent_${t}`);
    if (el) el.style.display = (t === tabId) ? 'block' : 'none';
  });

  const titles = {
    complaints: '<i class="fa-solid fa-list-check" style="color: var(--accent-cyan);"></i> My Complaints & Status',
    report: '<i class="fa-solid fa-circle-plus" style="color: var(--accent-cyan);"></i> Report a New Civic Issue',
    feedback: '<i class="fa-solid fa-star" style="color: #fbbf24;"></i> Municipal Service Feedback',
    profile: '<i class="fa-solid fa-user-gear" style="color: var(--accent-cyan);"></i> Account Profile Settings'
  };
  document.getElementById('pageHeaderTitle').innerHTML = titles[tabId] || 'Citizen Portal';

  if (tabId === 'complaints') loadCitizenComplaints();
  if (tabId === 'feedback') loadFeedbackTab();
}

// ─────────────────────────── Fetch & Render Complaints ───────────────────────────
async function loadCitizenComplaints() {
  try {
    const res = await fetch('/api/complaints');
    citizenComplaints = await res.json();
    renderComplaints(citizenComplaints);
    updateStats(citizenComplaints);
  } catch (e) {
    showToast('Failed to load complaints', 'error');
  }
}

function updateStats(data) {
  document.getElementById('statTotal').textContent = data.length;
  document.getElementById('statPending').textContent = data.filter(c => c.status === 'Pending').length;
  document.getElementById('statProgress').textContent = data.filter(c => c.status === 'In Progress').length;
  document.getElementById('statResolved').textContent = data.filter(c => c.status === 'Resolved').length;
}

function renderComplaints(data) {
  const container = document.getElementById('complaintsListContainer');
  if (!container) return;

  if (data.length === 0) {
    container.innerHTML = `
      <div class="glass-card" style="text-align: center; padding: 50px 20px;">
        <div style="font-size: 48px; margin-bottom: 15px;">📭</div>
        <h3 style="font-size: 18px; font-weight: 700;">No Complaints Found</h3>
        <p style="color: var(--text-secondary); font-size: 13px; margin-top: 6px;">You have not reported any civic issues yet or matching filter criteria.</p>
        <button class="btn btn-primary btn-sm" style="margin-top: 20px;" onclick="switchTab('report')">
          <i class="fa-solid fa-plus"></i> Submit Your First Issue
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = data.map(c => `
    <div class="glass-card complaint-card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 15px; margin-bottom: 12px; flex-wrap: wrap;">
        <div>
          <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--accent-cyan); background: var(--bg-input); padding: 2px 8px; border-radius: 6px;">#${c.id}</span>
            <h4 style="font-size: 16px; font-weight: 700; color: var(--text-primary);">${escapeHtml(c.title)}</h4>
          </div>
          <div style="font-size: 12px; color: var(--text-secondary); display: flex; gap: 15px; flex-wrap: wrap;">
            <span><i class="fa-solid fa-folder"></i> ${c.category}</span>
            <span><i class="fa-solid fa-location-dot"></i> ${c.location || 'Area A'}</span>
            <span><i class="fa-regular fa-clock"></i> ${c.created_at}</span>
            ${c.department ? `<span><i class="fa-solid fa-building"></i> ${c.department}</span>` : ''}
            ${c.assigned_officer_name ? `<span style="color: var(--accent-cyan); font-weight: 600;"><i class="fa-solid fa-user-tie"></i> Officer: ${c.assigned_officer_name}</span>` : ''}
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="badge ${c.priority === 'High' ? 'badge-rejected' : (c.priority === 'Medium' ? 'badge-pending' : 'badge-resolved')}">
            ${c.priority} Priority
          </span>
          <span class="badge badge-${c.status.toLowerCase().replace(' ', '_')}">
            ● ${c.status}
          </span>
        </div>
      </div>

      ${c.description ? `<p style="font-size: 13px; color: var(--text-primary); margin-bottom: 14px; line-height: 1.5;">${escapeHtml(c.description)}</p>` : ''}

      ${c.admin_remarks ? `
        <div style="background: var(--bg-input); padding: 10px 14px; border-radius: 8px; font-size: 12px; color: var(--accent-cyan); margin-bottom: 14px; border-left: 3px solid var(--accent-cyan);">
          <strong><i class="fa-solid fa-comment-dots"></i> Municipal Remarks:</strong> ${escapeHtml(c.admin_remarks)}
        </div>
      ` : ''}

      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 12px; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-sm btn-primary" onclick="openComplaintDetails(${c.id})">
            <i class="fa-solid fa-eye"></i> View Full Details
          </button>
          <button class="btn btn-sm btn-secondary" onclick="openTimeline(${c.id})">
            <i class="fa-solid fa-timeline"></i> Timeline
          </button>
        </div>
        <span style="font-size: 11px; color: var(--text-muted);">Last Updated: ${c.updated_at || c.created_at}</span>
      </div>
    </div>
  `).join('');
}

function filterComplaints() {
  const query = document.getElementById('complaintSearch').value.toLowerCase().trim();
  const status = document.getElementById('statusFilter').value;

  const filtered = citizenComplaints.filter(c => {
    const matchStatus = (status === 'All' || c.status === status);
    const txt = `${c.id} ${c.title} ${c.category} ${c.location} ${c.description}`.toLowerCase();
    const matchQuery = !query || txt.includes(query);
    return matchStatus && matchQuery;
  });

  renderComplaints(filtered);
}

// ─────────────────────────── Complaint Wizard Submissions ───────────────────────────
function selectCategory(cat, el) {
  selectedCategory = cat;
  document.querySelectorAll('.category-card').forEach(c => c.classList.remove('selected'));
  if (el) el.classList.add('selected');
}

function selectPriority(prio, el) {
  selectedPriority = prio;
  document.querySelectorAll('.priority-chip').forEach(p => p.classList.remove('selected'));
  if (el) el.classList.add('selected');
}

async function submitNewComplaint(e) {
  e.preventDefault();
  const title = document.getElementById('reportTitle').value.trim();
  const location = document.getElementById('reportLocation').value.trim();
  const description = document.getElementById('reportDesc').value.trim();

  if (!title || !location) {
    showToast('Please fill in title and location.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/complaints', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        category: selectedCategory,
        location,
        priority: selectedPriority,
        description
      })
    });
    const data = await res.json();

    if (data.success) {
      showToast(data.message || 'Complaint submitted successfully!', 'success');
      document.getElementById('newComplaintForm').reset();
      switchTab('complaints');
    } else {
      showToast(data.message || 'Failed to submit complaint', 'error');
    }
  } catch (err) {
    showToast('Server communication error', 'error');
  }
}

// ─────────────────────────── Timeline Modal ───────────────────────────
async function openComplaintDetails(cid) {
  const modal = document.getElementById('complaintDetailModal');
  const content = document.getElementById('complaintDetailContent');
  modal.style.display = 'flex';
  content.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><div style="margin-top: 10px;">Loading full details...</div></div>';

  try {
    const res = await fetch(`/api/complaints/${cid}`);
    const data = await res.json();
    const c = data.complaint;
    const history = data.history || [];

    // Compute progress step index
    // Steps: 1: Pending (Submitted), 2: Approved / Officer Assigned, 3: In Progress, 4: Resolved
    let stepIdx = 1;
    if (c.status === 'Approved' || c.assigned_officer_name) stepIdx = 2;
    if (c.status === 'In Progress') stepIdx = 3;
    if (c.status === 'Resolved') stepIdx = 4;

    content.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 15px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-family: var(--font-mono); font-size: 16px; font-weight: 700; color: var(--accent-cyan); background: var(--bg-input); padding: 4px 12px; border-radius: 8px;">#${c.id}</span>
          <h3 style="font-size: 20px; font-weight: 800; color: var(--text-primary);">${escapeHtml(c.title)}</h3>
        </div>
        <button class="btn btn-sm btn-secondary" onclick="closeDetailsModal()"><i class="fa-solid fa-xmark"></i></button>
      </div>

      <!-- Live Status Stepper -->
      <div style="margin-bottom: 25px; background: var(--bg-input); padding: 18px 20px; border-radius: 14px; border: 1px solid var(--border-color);">
        <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 12px; text-transform: uppercase;">Resolution Journey</div>
        <div style="display: flex; justify-content: space-between; position: relative;">
          <!-- Step 1 -->
          <div style="text-align: center; flex: 1; position: relative; z-index: 1;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: ${stepIdx >= 1 ? 'var(--accent-cyan)' : 'var(--bg-surface)'}; color: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px; font-weight: 700; font-size: 12px; box-shadow: ${stepIdx >= 1 ? '0 0 12px var(--accent-cyan-glow)' : 'none'};">✓</div>
            <div style="font-size: 11px; font-weight: 700; color: ${stepIdx >= 1 ? 'var(--text-primary)' : 'var(--text-muted)'};">1. Submitted</div>
          </div>
          <!-- Step 2 -->
          <div style="text-align: center; flex: 1; position: relative; z-index: 1;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: ${stepIdx >= 2 ? 'var(--accent-blue)' : 'var(--bg-surface)'}; color: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px; font-weight: 700; font-size: 12px; box-shadow: ${stepIdx >= 2 ? '0 0 12px rgba(59,130,246,0.5)' : 'none'};">${stepIdx > 2 ? '✓' : '2'}</div>
            <div style="font-size: 11px; font-weight: 700; color: ${stepIdx >= 2 ? 'var(--text-primary)' : 'var(--text-muted)'};">2. Officer Assigned</div>
          </div>
          <!-- Step 3 -->
          <div style="text-align: center; flex: 1; position: relative; z-index: 1;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: ${stepIdx >= 3 ? 'var(--status-pending)' : 'var(--bg-surface)'}; color: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px; font-weight: 700; font-size: 12px; box-shadow: ${stepIdx >= 3 ? '0 0 12px rgba(245,158,11,0.5)' : 'none'};">${stepIdx > 3 ? '✓' : '3'}</div>
            <div style="font-size: 11px; font-weight: 700; color: ${stepIdx >= 3 ? 'var(--text-primary)' : 'var(--text-muted)'};">3. In Progress</div>
          </div>
          <!-- Step 4 -->
          <div style="text-align: center; flex: 1; position: relative; z-index: 1;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: ${stepIdx >= 4 ? 'var(--status-resolved)' : 'var(--bg-surface)'}; color: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px; font-weight: 700; font-size: 12px; box-shadow: ${stepIdx >= 4 ? '0 0 12px rgba(16,185,129,0.5)' : 'none'};">${stepIdx >= 4 ? '✓' : '4'}</div>
            <div style="font-size: 11px; font-weight: 700; color: ${stepIdx >= 4 ? 'var(--text-primary)' : 'var(--text-muted)'};">4. Resolved</div>
          </div>
        </div>
      </div>

      <!-- Details Grid -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
        <div style="background: var(--bg-input); padding: 14px; border-radius: 10px;">
          <div style="font-size: 11px; color: var(--text-muted); font-weight: 700;">CATEGORY & LOCATION</div>
          <div style="font-size: 13px; font-weight: 700; color: var(--text-primary); margin-top: 4px;">${c.category}</div>
          <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">📍 ${c.location || 'Area A'}</div>
        </div>

        <div style="background: var(--bg-input); padding: 14px; border-radius: 10px;">
          <div style="font-size: 11px; color: var(--text-muted); font-weight: 700;">ASSIGNED OFFICER & DEPT</div>
          <div style="font-size: 13px; font-weight: 700; color: var(--accent-cyan); margin-top: 4px;">
            ${c.assigned_officer_name ? `👷 ${c.assigned_officer_name}` : '<span style="color: var(--text-muted);">Awaiting Assignment</span>'}
          </div>
          <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">🏢 ${c.department || 'Municipal Dept'}</div>
        </div>
      </div>

      ${c.description ? `
        <div style="margin-bottom: 20px;">
          <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 6px;">COMPLAINT DESCRIPTION</div>
          <div style="background: var(--bg-input); padding: 14px; border-radius: 10px; font-size: 13px; line-height: 1.5; color: var(--text-primary);">${escapeHtml(c.description)}</div>
        </div>
      ` : ''}

      ${c.admin_remarks ? `
        <div style="margin-bottom: 20px; background: rgba(6, 182, 212, 0.1); border-left: 4px solid var(--accent-cyan); padding: 14px; border-radius: 8px;">
          <div style="font-size: 12px; font-weight: 700; color: var(--accent-cyan);"><i class="fa-solid fa-clipboard-check"></i> Field Action & Remarks:</div>
          <div style="font-size: 13px; color: var(--text-primary); margin-top: 4px;">${escapeHtml(c.admin_remarks)}</div>
        </div>
      ` : ''}

      <!-- Bottom Action Row -->
      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 16px;">
        <button class="btn btn-sm btn-secondary" onclick="openTimeline(${c.id})"><i class="fa-solid fa-timeline"></i> View Full Timeline</button>
        ${c.status === 'Resolved' ? `<button class="btn btn-sm btn-primary" onclick="closeDetailsModal(); switchTab('feedback');"><i class="fa-solid fa-star"></i> Rate Resolution Quality</button>` : ''}
      </div>
    `;
  } catch (e) {
    content.innerHTML = '<div style="color: var(--status-rejected);">Failed to load complaint details.</div>';
  }
}

function closeDetailsModal() {
  document.getElementById('complaintDetailModal').style.display = 'none';
}

async function openTimeline(cid) {
  const modal = document.getElementById('timelineModal');
  const body = document.getElementById('timelineBody');
  const title = document.getElementById('modalTitle');
  title.textContent = `Tracking Timeline for Complaint #${cid}`;
  body.innerHTML = '<div style="text-align: center; color: var(--text-secondary);"><i class="fa-solid fa-spinner fa-spin"></i> Loading...</div>';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/api/complaints/${cid}/history`);
    const data = await res.json();
    const history = data.history || [];

    if (history.length === 0) {
      body.innerHTML = '<div style="text-align: center; color: var(--text-muted);">No history events logged yet.</div>';
      return;
    }

    body.innerHTML = history.map(h => `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span class="badge badge-${h.new_status.toLowerCase().replace(' ', '_')}">● ${h.new_status}</span>
            <span style="font-size: 11px; color: var(--text-muted);">${h.changed_at}</span>
          </div>
          <div style="font-size: 12px; color: var(--text-primary); margin-top: 6px;">${escapeHtml(h.remarks || 'Status updated')}</div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    body.innerHTML = '<div style="color: var(--status-rejected);">Failed to load timeline.</div>';
  }
}

function closeTimelineModal() {
  document.getElementById('timelineModal').style.display = 'none';
}

// ─────────────────────────── Feedback & Rating ───────────────────────────
async function loadFeedbackTab() {
  const select = document.getElementById('feedbackComplaintSelect');
  select.innerHTML = '<option value="">-- Choose a Complaint --</option>';

  citizenComplaints.forEach(c => {
    select.innerHTML += `<option value="${c.id}">#${c.id} - ${c.title} (${c.status})</option>`;
  });

  loadFeedbackHistory();
}

function setRating(val) {
  currentRating = val;
  const labels = {
    1: '1 / 5 - Poor',
    2: '2 / 5 - Fair',
    3: '3 / 5 - Average',
    4: '4 / 5 - Good',
    5: '5 / 5 - Excellent'
  };
  document.getElementById('ratingLabel').textContent = labels[val] || `${val} / 5`;

  const stars = document.querySelectorAll('#starContainer i');
  stars.forEach((s, idx) => {
    s.style.color = (idx < val) ? '#fbbf24' : '#475569';
  });
}

async function submitFeedback(e) {
  e.preventDefault();
  const cid = document.getElementById('feedbackComplaintSelect').value;
  const comments = document.getElementById('feedbackComment').value.trim();

  if (!cid) {
    showToast('Please select a complaint to rate.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ complaint_id: cid, rating: currentRating, comments })
    });
    const data = await res.json();
    if (data.success) {
      showToast('Thank you! Feedback recorded.', 'success');
      document.getElementById('feedbackComment').value = '';
      loadFeedbackHistory();
    }
  } catch (err) {
    showToast('Error recording feedback', 'error');
  }
}

async function loadFeedbackHistory() {
  const container = document.getElementById('feedbackHistoryList');
  if (!container) return;

  try {
    const res = await fetch('/api/feedback');
    const data = await res.json();

    if (data.length === 0) {
      container.innerHTML = '<div style="color: var(--text-muted); font-size: 13px;">No feedback submitted yet.</div>';
      return;
    }

    container.innerHTML = data.map(f => `
      <div style="background: var(--bg-input); padding: 14px 18px; border-radius: 12px; margin-bottom: 10px; border: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <div style="color: #fbbf24; font-size: 14px;">${'★'.repeat(f.rating)}${'☆'.repeat(5 - f.rating)}</div>
          <span style="font-size: 11px; color: var(--text-muted);">${f.created_at}</span>
        </div>
        <div style="font-weight: 700; font-size: 13px; color: var(--text-primary);">Regarding: #${f.complaint_id} ${f.complaint_title}</div>
        ${f.comments ? `<div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px; font-style: italic;">"${escapeHtml(f.comments)}"</div>` : ''}
      </div>
    `).join('');
  } catch (e) {}
}

// ─────────────────────────── Profile Updater ───────────────────────────
async function saveProfile(e) {
  e.preventDefault();
  const name = document.getElementById('profName').value.trim();
  const phone = document.getElementById('profPhone').value.trim();
  const address = document.getElementById('profAddress').value.trim();
  const password = document.getElementById('profPassword').value.trim();

  try {
    const res = await fetch('/api/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone, address, password })
    });
    const data = await res.json();
    if (data.success) {
      showToast('Profile updated successfully!', 'success');
      document.getElementById('sideUserName').textContent = name;
      document.getElementById('profPassword').value = '';
    }
  } catch (err) {
    showToast('Failed to update profile', 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[m]));
}
