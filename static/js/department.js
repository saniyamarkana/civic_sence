/* ==========================================================================
   CivicSense — Department Portal Logic (Dual Card/Table Views, Filter Pills)
   ========================================================================== */

let deptComplaints = [];
let currentViewMode = 'cards';
let currentQuickFilter = 'All';

const DEPT_CATEGORY_ICONS = {
  'Garbage': '🗑️',
  'Streetlight': '💡',
  'Water Leakage': '💧',
  'Pothole': '🕳️',
  'Drainage': '🌊',
  'Illegal Parking': '🚗',
  'Public Cleanliness': '🧹',
  'Damaged Road': '🚧'
};

document.addEventListener('DOMContentLoaded', () => {
  initLiveHeroClock();
  loadDeptData();
});

function initLiveHeroClock() {
  function updateClock() {
    const clockEl = document.getElementById('deptLiveClock');
    const dateEl = document.getElementById('deptLiveDate');
    if (!clockEl) return;

    const now = new Date();
    clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (dateEl) {
      dateEl.textContent = now.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
    }
  }

  updateClock();
  setInterval(updateClock, 1000);
}

function switchDeptTab(tabId) {
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const activeLink = document.querySelector(`.nav-link[data-tab="${tabId}"]`);
  if (activeLink) activeLink.classList.add('active');

  const tabs = ['dashboard', 'assigned', 'updater'];
  tabs.forEach(t => {
    const el = document.getElementById(`deptTab_${t}`);
    if (el) el.style.display = (t === tabId) ? 'block' : 'none';
  });

  if (tabId === 'dashboard' || tabId === 'assigned') loadDeptData();
  if (tabId === 'updater') populateDeptSelect();
}

async function loadDeptData() {
  try {
    const statsRes = await fetch('/api/stats');
    const stats = await statsRes.json();

    const total = stats.total || 0;
    const pending = stats.pending || 0;
    const inProgress = stats.in_progress || 0;
    const resolved = stats.resolved || 0;

    // Stat cards in Dashboard
    document.getElementById('deptStatTotal').textContent = total;
    document.getElementById('deptStatPending').textContent = pending;
    document.getElementById('deptStatProgress').textContent = inProgress;
    document.getElementById('deptStatResolved').textContent = resolved;

    // Update Resolution Efficiency Progress Bar
    updateResolutionProgress(total, resolved, inProgress);

    const compRes = await fetch('/api/complaints');
    deptComplaints = await compRes.json();

    // Update filter pill counts
    updateFilterPillCounts();

    renderUrgentTasks(deptComplaints);
    filterDeptTasks();
    populateDeptSelect();
  } catch (err) {
    showToast('Failed to load department data', 'error');
  }
}

function updateResolutionProgress(total, resolved, inProgress) {
  const percentEl = document.getElementById('deptProgressPercent');
  const fillEl = document.getElementById('deptProgressFill');
  const subEl = document.getElementById('deptProgressSubtitle');

  if (!percentEl || !fillEl) return;

  if (total === 0) {
    percentEl.textContent = '100%';
    fillEl.style.width = '100%';
    if (subEl) subEl.textContent = 'No active tasks assigned — all clear!';
    return;
  }

  const pct = Math.round((resolved / total) * 100);
  percentEl.textContent = `${pct}%`;
  fillEl.style.width = `${pct}%`;

  if (subEl) {
    subEl.textContent = `${resolved} of ${total} tasks resolved · ${inProgress} currently underway in field`;
  }
}

function updateFilterPillCounts() {
  const pillAll = document.getElementById('pillAll');
  const pillPending = document.getElementById('pillPending');
  const pillProgress = document.getElementById('pillProgress');
  const pillResolved = document.getElementById('pillResolved');
  const pillHigh = document.getElementById('pillHigh');

  if (pillAll) pillAll.textContent = deptComplaints.length;
  if (pillPending) pillPending.textContent = deptComplaints.filter(c => c.status === 'Pending').length;
  if (pillProgress) pillProgress.textContent = deptComplaints.filter(c => c.status === 'In Progress').length;
  if (pillResolved) pillResolved.textContent = deptComplaints.filter(c => c.status === 'Resolved').length;
  if (pillHigh) pillHigh.textContent = deptComplaints.filter(c => c.priority === 'High' && c.status !== 'Resolved').length;
}

function setQuickFilter(filterKey) {
  currentQuickFilter = filterKey;
  document.querySelectorAll('.filter-pill').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-filter') === filterKey);
  });
  filterDeptTasks();
}

function filterDeptTasks() {
  const query = (document.getElementById('deptSearchInput')?.value || '').toLowerCase().trim();

  const filtered = deptComplaints.filter(c => {
    let matchFilter = true;
    if (currentQuickFilter === 'Pending') matchFilter = (c.status === 'Pending');
    else if (currentQuickFilter === 'In Progress') matchFilter = (c.status === 'In Progress');
    else if (currentQuickFilter === 'Resolved') matchFilter = (c.status === 'Resolved');
    else if (currentQuickFilter === 'High') matchFilter = (c.priority === 'High' && c.status !== 'Resolved');

    const searchTarget = `${c.id} ${c.title} ${c.category} ${c.location} ${c.citizen_name || ''} ${c.description || ''}`.toLowerCase();
    const matchQuery = !query || searchTarget.includes(query);

    return matchFilter && matchQuery;
  });

  const countBadge = document.getElementById('deptTaskCountBadge');
  if (countBadge) {
    countBadge.textContent = `${filtered.length} Task${filtered.length === 1 ? '' : 's'} Assigned`;
  }

  renderTableView(filtered);
}

const DEPT_CATEGORY_META = {
  'Garbage':            { icon: '🗑️', bg: 'rgba(16, 185, 129, 0.14)', color: '#10b981', border: 'rgba(16, 185, 129, 0.4)' },
  'Streetlight':        { icon: '💡', bg: 'rgba(245, 158, 11, 0.14)', color: '#f59e0b', border: 'rgba(245, 158, 11, 0.4)' },
  'Water Leakage':      { icon: '💧', bg: 'rgba(6, 182, 212, 0.14)', color: '#06b6d4', border: 'rgba(6, 182, 212, 0.4)' },
  'Pothole':            { icon: '🕳️', bg: 'rgba(236, 72, 153, 0.14)', color: '#ec4899', border: 'rgba(236, 72, 153, 0.4)' },
  'Drainage':           { icon: '🌊', bg: 'rgba(59, 130, 246, 0.14)', color: '#3b82f6', border: 'rgba(59, 130, 246, 0.4)' },
  'Illegal Parking':    { icon: '🚗', bg: 'rgba(139, 92, 246, 0.14)', color: '#8b5cf6', border: 'rgba(139, 92, 246, 0.4)' },
  'Public Cleanliness': { icon: '🧹', bg: 'rgba(20, 184, 166, 0.14)', color: '#14b8a6', border: 'rgba(20, 184, 166, 0.4)' },
  'Damaged Road':       { icon: '🚧', bg: 'rgba(249, 115, 22, 0.14)', color: '#f97316', border: 'rgba(249, 115, 22, 0.4)' }
};

function renderTableView(data) {
  const tbody = document.getElementById('deptAssignedTableBody');
  if (!tbody) return;

  if (data.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; padding: 50px 20px; color: var(--text-muted);">
          <div style="font-size: 32px; margin-bottom: 8px;">📋</div>
          <div style="font-size: 15px; font-weight: 700; color: var(--text-primary);">No Complaints Found</div>
          <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">No tasks match your selected filter or search query.</div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = data.map(c => {
    const meta = DEPT_CATEGORY_META[c.category] || { icon: '📋', bg: 'rgba(6,182,212,0.12)', color: '#06b6d4', border: 'rgba(6,182,212,0.3)' };

    // Crisp, modern Priority Badge
    let prioHtml = '';
    if (c.priority === 'High') {
      prioHtml = `<span class="prio-badge prio-badge-high"><span class="prio-dot prio-dot-high"></span> HIGH</span>`;
    } else if (c.priority === 'Low') {
      prioHtml = `<span class="prio-badge prio-badge-low"><span class="prio-dot prio-dot-low"></span> LOW</span>`;
    } else {
      prioHtml = `<span class="prio-badge prio-badge-medium"><span class="prio-dot prio-dot-medium"></span> MEDIUM</span>`;
    }

    // Crisp, modern Status Badge
    let statusHtml = '';
    if (c.status === 'Resolved') {
      statusHtml = `<span class="status-badge status-badge-resolved"><i class="fa-solid fa-circle-check" style="font-size: 11px;"></i> RESOLVED</span>`;
    } else if (c.status === 'In Progress') {
      statusHtml = `<span class="status-badge status-badge-in_progress"><i class="fa-solid fa-arrows-rotate fa-spin" style="font-size: 10px;"></i> IN PROGRESS</span>`;
    } else {
      statusHtml = `<span class="status-badge status-badge-pending"><i class="fa-solid fa-clock" style="font-size: 10px;"></i> PENDING</span>`;
    }

    return `
      <tr class="dept-table-row" style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background 0.18s ease;">
        <!-- ID -->
        <td style="padding: 16px 18px; font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 800; font-size: 14px;">
          #${c.id}
        </td>

        <!-- Issue & Category -->
        <td style="padding: 16px 18px;">
          <div style="display: flex; flex-direction: column; gap: 5px;">
            <div style="display: flex; align-items: center; gap: 7px; flex-wrap: wrap;">
              <span style="background: ${meta.bg}; color: ${meta.color}; border: 1px solid ${meta.border}; font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 20px; display: inline-flex; align-items: center; gap: 5px;">
                ${meta.icon} ${c.category}
              </span>
              ${c.complaint_image ? `
                <button type="button" class="task-thumb-btn" onclick="openLightbox('/static/uploads/complaint_images/${escapeHtml(c.complaint_image)}')" title="Click to inspect citizen photo">
                  <i class="fa-solid fa-camera"></i> Photo
                </button>
              ` : ''}
            </div>

            <div style="font-weight: 700; font-size: 14px; color: var(--text-primary); line-height: 1.35;">
              ${escapeHtml(c.title)}
            </div>

            <div style="font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 6px;">
              <i class="fa-solid fa-user" style="font-size: 10px; color: var(--accent-cyan);"></i> Filed by <strong>${escapeHtml(c.citizen_name || 'Citizen')}</strong>
            </div>
          </div>
        </td>

        <!-- Location & Date -->
        <td style="padding: 16px 18px;">
          <div style="color: var(--text-primary); font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px;">
            <span style="color: #f43f5e;">📍</span> ${escapeHtml(c.location || '-')}
          </div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px; display: flex; align-items: center; gap: 6px;">
            <span style="color: var(--accent-cyan);">📅</span> ${formatDateTime(c.created_at)}
          </div>
        </td>

        <!-- Priority -->
        <td style="padding: 16px 18px;">
          ${prioHtml}
        </td>

        <!-- Status -->
        <td style="padding: 16px 18px;">
          ${statusHtml}
        </td>

        <!-- Actions -->
        <td style="padding: 16px 18px; text-align: right;">
          <div style="display: flex; gap: 8px; align-items: center; justify-content: flex-end; flex-wrap: nowrap;">
            ${c.status === 'Pending' ? `
              <button class="btn btn-sm btn-primary" onclick="quickDeptUpdate(${c.id}, 'In Progress')" title="Start field assignment">
                <i class="fa-solid fa-play"></i> Start
              </button>
              <button class="btn btn-sm btn-success" onclick="promptDeptSolve(${c.id})" title="Solve complaint">
                <i class="fa-solid fa-check"></i> Solve
              </button>
              <button class="btn btn-sm btn-secondary" onclick="viewDeptComplaintDetail(${c.id})" title="View Details">
                <i class="fa-solid fa-eye"></i> Details
              </button>
            ` : ''}

            ${c.status === 'In Progress' ? `
              <button class="btn btn-sm btn-success" onclick="promptDeptSolve(${c.id})" title="Mark complete and attach proof photo">
                <i class="fa-solid fa-circle-check"></i> Complete
              </button>
              <button class="btn btn-sm btn-secondary" onclick="viewDeptComplaintDetail(${c.id})" title="View Details">
                <i class="fa-solid fa-eye"></i> Details
              </button>
            ` : ''}

            ${c.status === 'Resolved' ? `
              <button class="btn btn-sm btn-secondary" onclick="viewDeptComplaintDetail(${c.id})" style="border-color: rgba(16,185,129,0.4); color: var(--status-resolved); background: rgba(16,185,129,0.08); font-weight: 700;" title="View resolution notes &amp; proof of work">
                <i class="fa-solid fa-file-shield"></i> Details
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function renderUrgentTasks(data) {
  const container = document.getElementById('deptUrgentList');
  const badge = document.getElementById('deptUrgentCountBadge');
  if (!container) return;

  const urgent = data.filter(c => c.priority === 'High' && c.status !== 'Resolved');

  if (badge) {
    badge.textContent = `${urgent.length} Urgent`;
  }

  if (urgent.length === 0) {
    container.innerHTML = `
      <div style="background: rgba(16,185,129,0.06); border: 1px dashed rgba(16,185,129,0.3); border-radius: 12px; padding: 20px; text-align: center; color: var(--status-resolved); font-size: 13px; font-weight: 600;">
        <i class="fa-solid fa-circle-check" style="font-size: 20px; margin-bottom: 6px; display: block;"></i>
        All urgent high-priority assignments are currently resolved and clear!
      </div>
    `;
    return;
  }

  container.innerHTML = urgent.map(c => `
    <div style="background: var(--bg-input); border-left: 4px solid var(--status-rejected); padding: 14px 18px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;">
      <div>
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span style="font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 700; font-size: 13px;">#${c.id}</span>
          <span style="font-weight: 700; font-size: 14px; color: var(--text-primary);">${escapeHtml(c.title)}</span>
          <span class="badge badge-rejected" style="font-size: 9px;">CRITICAL</span>
        </div>
        <div style="font-size: 12px; color: var(--text-secondary); display: flex; gap: 14px; flex-wrap: wrap;">
          <span>📍 ${escapeHtml(c.location || 'Area A')}</span>
          <span>📅 ${formatDateTime(c.created_at)}</span>
          <span>👤 ${escapeHtml(c.citizen_name || 'Citizen')}</span>
        </div>
      </div>
      <div class="btn-action-group">
        <button class="btn btn-sm btn-secondary" onclick="viewDeptComplaintDetail(${c.id})"><i class="fa-solid fa-eye"></i> Details</button>
        ${c.status !== 'In Progress' ? `<button class="btn btn-sm btn-primary" onclick="quickDeptUpdate(${c.id}, 'In Progress')"><i class="fa-solid fa-play"></i> Start Work</button>` : ''}
        <button class="btn btn-sm btn-success" onclick="promptDeptSolve(${c.id})"><i class="fa-solid fa-circle-check"></i> Solve</button>
      </div>
    </div>
  `).join('');
}

// ─────────────────────────── Task Detail Modal ───────────────────────────
async function viewDeptComplaintDetail(cid) {
  const modal = document.getElementById('deptDetailModal');
  const titleEl = document.getElementById('deptDetailTitle');
  const contentEl = document.getElementById('deptDetailContent');
  if (!modal || !contentEl) return;

  titleEl.textContent = `📋 Loading Task Details #${cid}...`;
  contentEl.innerHTML = '<div style="padding: 30px; text-align: center; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin fa-2x"></i></div>';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/api/complaints/${cid}`);
    const data = await res.json();
    const c = data.complaint;
    const history = data.history || [];

    const icon = DEPT_CATEGORY_ICONS[c.category] || '📋';
    titleEl.innerHTML = `📋 Task #${c.id} — ${escapeHtml(c.title)}`;

    contentEl.innerHTML = `
      <!-- Info Header Banner -->
      <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px 18px; margin-bottom: 18px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 13px;">
          <div><span style="color: var(--text-muted);">Category:</span> <strong>${icon} ${c.category}</strong></div>
          <div><span style="color: var(--text-muted);">Priority:</span> <span class="badge ${c.priority === 'High' ? 'badge-rejected' : 'badge-pending'}">${c.priority}</span></div>
          <div><span style="color: var(--text-muted);">Current Status:</span> <span class="badge badge-${c.status.toLowerCase().replace(' ', '_')}">${c.status}</span></div>
          <div><span style="color: var(--text-muted);">Citizen:</span> <strong>${escapeHtml(c.citizen_name || 'Anonymous')}</strong> ${c.citizen_phone ? `(${c.citizen_phone})` : ''}</div>
          <div style="grid-column: 1 / -1;"><span style="color: var(--text-muted);">Location:</span> <strong>📍 ${escapeHtml(c.location || 'N/A')}</strong></div>
        </div>
      </div>

      <!-- Description -->
      <div style="margin-bottom: 20px;">
        <h5 style="font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px;">Issue Description</h5>
        <div style="background: var(--bg-input); padding: 14px 16px; border-radius: 10px; border: 1px solid var(--border-color); font-size: 13px; line-height: 1.6; color: var(--text-primary);">
          ${escapeHtml(c.description || 'No detailed description provided.')}
        </div>
      </div>

      <!-- Photos (Before & After) -->
      ${(c.complaint_image || c.solution_image) ? `
        <div style="margin-bottom: 20px;">
          <h5 style="font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 10px;">
            <i class="fa-solid fa-images" style="color: var(--accent-cyan);"></i> Inspection &amp; Resolution Photos
          </h5>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;">
            ${c.complaint_image ? `
              <div class="complaint-img-box" style="margin: 0; background: rgba(14,21,38,0.7); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px;">
                <div class="complaint-img-label" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 11px; font-weight: 700; color: var(--text-secondary);">
                  <span><i class="fa-solid fa-camera" style="color: var(--accent-cyan);"></i> Before: Citizen Photo</span>
                  <span style="font-size: 10px; color: var(--text-muted);"><i class="fa-solid fa-magnifying-glass-plus"></i> Click to expand</span>
                </div>
                <img src="/static/uploads/complaint_images/${escapeHtml(c.complaint_image)}" alt="Before Photo"
                     onclick="openLightbox('/static/uploads/complaint_images/${escapeHtml(c.complaint_image)}')"
                     style="width: 100%; height: 180px; object-fit: cover; border-radius: 8px; cursor: pointer; border: 1px solid rgba(255,255,255,0.08); transition: transform 0.2s;"
                     onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
              </div>
            ` : ''}

            ${c.solution_image ? `
              <div class="solution-img-box" style="margin: 0; background: rgba(14,21,38,0.7); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px;">
                <div class="solution-img-label" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 11px; font-weight: 700; color: var(--status-resolved);">
                  <span><i class="fa-solid fa-circle-check"></i> After: Proof of Resolution</span>
                  <span style="font-size: 10px; color: var(--text-muted);"><i class="fa-solid fa-magnifying-glass-plus"></i> Click to expand</span>
                </div>
                <img src="/static/uploads/solution_images/${escapeHtml(c.solution_image)}" alt="After Photo"
                     onclick="openLightbox('/static/uploads/solution_images/${escapeHtml(c.solution_image)}')"
                     style="width: 100%; height: 180px; object-fit: cover; border-radius: 8px; cursor: pointer; border: 1px solid rgba(255,255,255,0.08); transition: transform 0.2s;"
                     onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
              </div>
            ` : ''}
          </div>
        </div>
      ` : ''}

      <!-- Admin Instructions / Field Remarks -->
      ${c.admin_remarks ? `
        <div style="margin-bottom: 20px;">
          <h5 style="font-size: 12px; font-weight: 700; color: var(--accent-cyan); text-transform: uppercase; margin-bottom: 6px;">Field Notes &amp; Resolution Remarks</h5>
          <div style="background: rgba(6,182,212,0.06); padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(6,182,212,0.3); font-size: 13px; color: var(--text-primary);">
            ${escapeHtml(c.admin_remarks)}
          </div>
        </div>
      ` : ''}

      <!-- Action Buttons inside modal (Mark Solved removed per request) -->
      <div style="display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid var(--border-color); padding-top: 16px; margin-top: 20px;">
        <button class="btn btn-secondary" onclick="closeDeptDetailModal()">
          <i class="fa-solid fa-xmark"></i> Close
        </button>
      </div>
    `;
  } catch (err) {
    contentEl.innerHTML = '<div style="color: var(--status-rejected); padding: 20px; text-align: center;">Failed to load task details.</div>';
  }
}

function closeDeptDetailModal() {
  const modal = document.getElementById('deptDetailModal');
  if (modal) modal.style.display = 'none';
}

function onDeptSelectComplaint(cid) {
  const summaryBox = document.getElementById('deptSelectedTaskSummary');
  if (!summaryBox) return;

  if (!cid) {
    summaryBox.style.display = 'none';
    return;
  }

  const c = deptComplaints.find(item => String(item.id) === String(cid));
  if (!c) {
    summaryBox.style.display = 'none';
    return;
  }

  const icon = DEPT_CATEGORY_ICONS[c.category] || '📋';
  summaryBox.style.display = 'block';
  summaryBox.innerHTML = `
    <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">
      ${icon} #${c.id} — ${escapeHtml(c.title)}
    </div>
    <div style="font-size: 12px; color: var(--text-secondary);">
      Current Status: <strong style="color: var(--accent-cyan);">${c.status}</strong> &nbsp;|&nbsp;
      Priority: <strong>${c.priority}</strong> &nbsp;|&nbsp;
      Location: <strong>📍 ${escapeHtml(c.location || 'Area')}</strong>
    </div>
  `;

  // Pre-fill target status if already in progress
  const targetSelect = document.getElementById('deptTargetStatus');
  if (targetSelect) {
    targetSelect.value = c.status === 'In Progress' ? 'Resolved' : (c.status === 'Pending' ? 'In Progress' : c.status);
  }
}

function populateDeptSelect() {
  const select = document.getElementById('deptComplaintSelect');
  if (!select) return;

  select.innerHTML = '<option value="">-- Choose an Assigned Complaint --</option>';
  deptComplaints.forEach(c => {
    const icon = DEPT_CATEGORY_ICONS[c.category] || '📋';
    select.innerHTML += `<option value="${c.id}">${icon} #${c.id} — ${escapeHtml(c.title)} (${c.status})</option>`;
  });
}

let activeSolvingId = null;

function promptDeptSolve(cid) {
  activeSolvingId = cid;
  const c = deptComplaints.find(item => item.id === cid);
  const title = c ? c.title : `Complaint #${cid}`;

  document.getElementById('deptSolveModalTitle').innerHTML = `<i class="fa-solid fa-circle-check"></i> Solve Task #${cid}`;
  document.getElementById('deptSolveNotes').value = '';
  removeSolveImg();
  document.getElementById('deptSolveModal').style.display = 'flex';
}

function closeDeptSolveModal() {
  document.getElementById('deptSolveModal').style.display = 'none';
  removeSolveImg();
}

async function confirmDeptSolve() {
  const notes = document.getElementById('deptSolveNotes').value.trim();
  if (!notes) {
    showToast('Please provide resolution details.', 'error');
    return;
  }

  try {
    // 1. Upload the solution proof image if provided
    const solveImgInput = document.getElementById('solveImgInput');
    if (solveImgInput && solveImgInput.files && solveImgInput.files[0]) {
      const imgFormData = new FormData();
      imgFormData.append('solution_image', solveImgInput.files[0]);
      await fetch(`/api/complaints/${activeSolvingId}/solve-image`, {
        method: 'POST',
        body: imgFormData
      });
    }

    // 2. Mark as Resolved with remarks
    const res = await fetch(`/api/complaints/${activeSolvingId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: 'Resolved',
        admin_remarks: notes,
        remarks: `Work Completed & Solved: ${notes}`
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Complaint #${activeSolvingId} marked as Solved!`, 'success');
      closeDeptSolveModal();
      loadDeptData();
    }
  } catch (e) {
    showToast('Failed to solve complaint', 'error');
  }
}

async function quickDeptUpdate(cid, status) {
  if (status === 'Resolved') {
    promptDeptSolve(cid);
    return;
  }

  try {
    const res = await fetch(`/api/complaints/${cid}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, remarks: `Field officer started work (${status})` })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Complaint #${cid} status changed to "${status}"!`, 'success');
      loadDeptData();
    }
  } catch (e) {
    showToast('Failed to update status', 'error');
  }
}

async function submitDeptWorkUpdate(e) {
  e.preventDefault();
  const cid = document.getElementById('deptComplaintSelect').value;
  const status = document.getElementById('deptTargetStatus').value;
  const admin_remarks = document.getElementById('deptWorkRemarks').value.trim();

  if (!cid) {
    showToast('Please select an assigned complaint.', 'error');
    return;
  }

  try {
    const res = await fetch(`/api/complaints/${cid}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, admin_remarks, remarks: `Field update: ${admin_remarks || status}` })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Complaint #${cid} successfully updated to "${status}"!`, 'success');
      document.getElementById('deptWorkRemarks').value = '';
      switchDeptTab('assigned');
    }
  } catch (err) {
    showToast('Failed to update complaint', 'error');
  }
}

function formatDateTime(dtStr) {
  if (!dtStr) return 'Recently';
  try {
    const d = new Date(dtStr);
    if (isNaN(d.getTime())) return dtStr;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return dtStr;
  }
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[m]));
}

// ─────────────────────────── Solve Image Helpers ───────────────────────────
function previewSolveImg(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('solveImgPreviewImg').src = e.target.result;
    document.getElementById('solveImgPreview').style.display = 'inline-block';
  };
  reader.readAsDataURL(file);
}

function removeSolveImg() {
  const input = document.getElementById('solveImgInput');
  if (input) input.value = '';
  const preview = document.getElementById('solveImgPreview');
  if (preview) preview.style.display = 'none';
  const img = document.getElementById('solveImgPreviewImg');
  if (img) img.src = '';
}

// ─────────────────────────── Image Lightbox ───────────────────────────
function openLightbox(src) {
  const lb = document.getElementById('imgLightbox');
  const img = document.getElementById('lightboxImg');
  if (lb && img) { img.src = src; lb.classList.add('open'); }
}

function closeLightbox() {
  const lb = document.getElementById('imgLightbox');
  if (lb) lb.classList.remove('open');
}
