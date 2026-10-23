/* ==========================================================================
   CivicSense — Admin Portal & Phase 1 Interactive DSA Visual Lab
   ========================================================================== */

let adminComplaints = [];
let allUsers = [];
let categoryChartInstance = null;
let currentAdminTab = 'dashboard';
let isQueuePriorityMode = false;
let currentManagingId = null;
let iterArray = [45, 12, 85, 32, 89, 21, 67, 10, 53, 38];

document.addEventListener('DOMContentLoaded', () => {
  loadAdminDashboard();
  loadAdminNotifications();
  setInterval(loadAdminNotifications, 30000);
});

// ─────────────────────────── Navigation Switcher ───────────────────────────
function switchAdminTab(tabId) {
  currentAdminTab = tabId;
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const activeLink = document.querySelector(`.nav-link[data-tab="${tabId}"]`);
  if (activeLink) activeLink.classList.add('active');

  const tabs = ['dashboard', 'complaints', 'users', 'dsa_queue', 'dsa_stack', 'dsa_ll', 'dsa_expr', 'dsa_iter', 'dsa_rec', 'map', 'greedy'];
  tabs.forEach(t => {
    const el = document.getElementById(`adminTab_${t}`);
    if (el) el.style.display = (t === tabId) ? 'block' : 'none';
  });

  const titles = {
    dashboard: '<i class="fa-solid fa-chart-pie" style="color: var(--accent-cyan);"></i> Administrative Overview',
    complaints: '<i class="fa-solid fa-list-check" style="color: var(--accent-cyan);"></i> Manage All Civic Complaints',
    users: '<i class="fa-solid fa-users-gear" style="color: var(--accent-cyan);"></i> User Accounts Management',
    dsa_queue: '<i class="fa-solid fa-arrows-spin" style="color: var(--accent-cyan);"></i> Queue (FIFO / Emergency Heap)',
    dsa_stack: '<i class="fa-solid fa-layer-group" style="color: var(--status-pending);"></i> Stack (LIFO Undo Mechanism)',
    dsa_ll: '<i class="fa-solid fa-link" style="color: var(--accent-purple);"></i> Linked List Node Chain Visualizer',
    dsa_expr: '<i class="fa-solid fa-calculator" style="color: var(--accent-cyan);"></i> Shunting-Yard Expression Parser',
    dsa_iter: '<i class="fa-solid fa-bolt" style="color: var(--status-resolved);"></i> Iterative Sorting & Search Lab',
    dsa_rec: '<i class="fa-solid fa-sitemap" style="color: var(--accent-purple);"></i> Recursive Call Tree Visualizer',
    map: '<i class="fa-solid fa-sitemap" style="color: var(--accent-cyan);"></i> Location Graph — Binary Tree & BFS',
    greedy: '<i class="fa-solid fa-ranking-star" style="color: #10b981;"></i> Greedy Priority Processing — Phase 4'
  };
  document.getElementById('adminHeaderTitle').innerHTML = titles[tabId] || 'Admin Portal';

  // Load specific data
  if (tabId === 'dashboard') loadAdminDashboard();
  else if (tabId === 'complaints') loadAdminComplaints();
  else if (tabId === 'users') loadAdminUsers();
  else if (tabId === 'dsa_queue') renderDSAQueue();
  else if (tabId === 'dsa_stack') renderDSAStack();
  else if (tabId === 'dsa_ll') renderDSALL();
  else if (tabId === 'dsa_expr') runExpression();
  else if (tabId === 'dsa_iter') renderIterArray();
  else if (tabId === 'map') loadAreaMap();
  else if (tabId === 'greedy') runGreedyAlgorithm();
}

function refreshCurrentAdminTab() {
  switchAdminTab(currentAdminTab);
}

// ─────────────────────────── Dashboard Metrics & Charts ───────────────────────────
async function loadAdminDashboard() {
  try {
    const res = await fetch('/api/stats');
    const stats = await res.json();

    document.getElementById('admTotal').textContent = stats.total_complaints || 0;
    document.getElementById('admPending').textContent = stats.pending || 0;
    document.getElementById('admProgress').textContent = stats.in_progress || 0;
    document.getElementById('admResolved').textContent = stats.resolved || 0;

    // Render Category Distribution Chart using Chart.js
    renderCategoryChart(stats.by_category || []);

    // Department Workload List
    const deptList = document.getElementById('deptWorkloadList');
    if (deptList) {
      const depts = stats.by_department || [];
      if (depts.length === 0) {
        deptList.innerHTML = '<div style="color: var(--text-muted); font-size: 12px;">No active departments.</div>';
      } else {
        deptList.innerHTML = depts.map(d => `
          <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-input); padding: 8px 12px; border-radius: 8px;">
            <span style="font-size: 12px; font-weight: 600;">${d.department}</span>
            <span class="badge badge-approved">${d.cnt} Tasks</span>
          </div>
        `).join('');
      }
    }

    // Recent activity log
    const recentRes = await fetch('/api/complaints');
    const recent = await recentRes.json();
    const tbody = document.getElementById('recentComplaintsBody');
    if (tbody) {
      tbody.innerHTML = recent.slice(0, 6).map(c => `
        <tr style="border-bottom: 1px solid var(--border-color);">
          <td style="padding: 10px; font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 700;">#${c.id}</td>
          <td style="padding: 10px; font-weight: 600;">${escapeHtml(c.title.substring(0, 24))}</td>
          <td style="padding: 10px; color: var(--text-secondary);">${c.category}</td>
          <td style="padding: 10px; color: var(--text-secondary);">${c.location || '-'}</td>
          <td style="padding: 10px;"><span class="badge ${c.priority === 'High' ? 'badge-rejected' : 'badge-pending'}">${c.priority}</span></td>
          <td style="padding: 10px;"><span class="badge badge-${c.status.toLowerCase().replace(' ', '_')}">● ${c.status}</span></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    showToast('Failed to load admin stats', 'error');
  }
}

// Canonical categories metadata with modern vibrant theme and icons
const CANONICAL_CATEGORIES = {
  'Garbage':            { name: 'Garbage',          icon: '🗑️', color: '#10b981', border: '#059669', bgGrad: 'rgba(16, 185, 129, 0.75)' },
  'Streetlight':        { name: 'Streetlight',      icon: '💡', color: '#f59e0b', border: '#d97706', bgGrad: 'rgba(245, 158, 11, 0.75)' },
  'Water Leakage':      { name: 'Water Leak',       icon: '💧', color: '#06b6d4', border: '#0891b2', bgGrad: 'rgba(6, 182, 212, 0.75)' },
  'Pothole':            { name: 'Pothole',          icon: '🕳️', color: '#ec4899', border: '#db2777', bgGrad: 'rgba(236, 72, 153, 0.75)' },
  'Drainage':           { name: 'Drainage',         icon: '🌊', color: '#3b82f6', border: '#2563eb', bgGrad: 'rgba(59, 130, 246, 0.75)' },
  'Illegal Parking':    { name: 'Parking',          icon: '🚗', color: '#8b5cf6', border: '#7c3aed', bgGrad: 'rgba(139, 92, 246, 0.75)' },
  'Public Cleanliness': { name: 'Cleanliness',      icon: '🧹', color: '#14b8a6', border: '#0f766e', bgGrad: 'rgba(20, 184, 166, 0.75)' },
  'Damaged Road':       { name: 'Damaged Road',     icon: '🚧', color: '#f97316', border: '#c2410c', bgGrad: 'rgba(249, 115, 22, 0.75)' }
};

function normalizeCategoryName(raw) {
  if (!raw) return 'Garbage';
  const s = String(raw).trim().toLowerCase();
  if (s.includes('garbage') || s.includes('waste') || s.includes('trash') || s.includes('dump')) return 'Garbage';
  if (s.includes('streetlight') || s.includes('street light') || s.includes('light')) return 'Streetlight';
  if (s.includes('water') || s.includes('leak') || s.includes('supply') || s.includes('pipe')) return 'Water Leakage';
  if (s.includes('drain') || s.includes('sewage')) return 'Drainage';
  if (s.includes('pothole') || s.includes('hole')) return 'Pothole';
  if (s.includes('parking')) return 'Illegal Parking';
  if (s.includes('clean') || s.includes('sanitation') || s.includes('sweeping')) return 'Public Cleanliness';
  if (s.includes('road')) return 'Damaged Road';
  return raw.trim();
}

function renderCategoryChart(data) {
  const ctx = document.getElementById('categoryChart');
  if (!ctx) return;

  // Aggregate and merge counts strictly by canonical category
  const categoryMap = {};
  (data || []).forEach(d => {
    const norm = normalizeCategoryName(d.category);
    categoryMap[norm] = (categoryMap[norm] || 0) + Number(d.cnt || 0);
  });

  const activeCategories = Object.keys(categoryMap).filter(k => categoryMap[k] > 0);
  activeCategories.sort((a, b) => categoryMap[b] - categoryMap[a]);

  // Update badge count in header
  const badge = document.getElementById('chartCategoryBadge');
  if (badge) {
    const totalComplaints = Object.values(categoryMap).reduce((acc, v) => acc + v, 0);
    badge.textContent = `${activeCategories.length} Categories · ${totalComplaints} Issues`;
  }

  const labels = activeCategories.length
    ? activeCategories.map(cat => {
        const meta = CANONICAL_CATEGORIES[cat];
        return meta ? `${meta.icon} ${meta.name}` : cat;
      })
    : ['No Complaints'];

  const counts = activeCategories.length
    ? activeCategories.map(cat => categoryMap[cat])
    : [0];

  const bgColors = activeCategories.length
    ? activeCategories.map(cat => (CANONICAL_CATEGORIES[cat] ? CANONICAL_CATEGORIES[cat].bgGrad : 'rgba(6, 182, 212, 0.75)'))
    : ['rgba(6, 182, 212, 0.3)'];

  const borderColors = activeCategories.length
    ? activeCategories.map(cat => (CANONICAL_CATEGORIES[cat] ? CANONICAL_CATEGORIES[cat].color : '#06b6d4'))
    : ['rgba(6, 182, 212, 0.6)'];

  if (categoryChartInstance) categoryChartInstance.destroy();

  categoryChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Complaints',
        data: counts,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 2,
        borderRadius: { topLeft: 8, topRight: 8, bottomLeft: 2, bottomRight: 2 },
        maxBarThickness: 45,
        barPercentage: 0.6,
        categoryPercentage: 0.75
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(14, 21, 38, 0.95)',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(6, 182, 212, 0.4)',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 10,
          displayColors: true,
          callbacks: {
            label: function(context) {
              const val = context.raw || 0;
              return ` Total Complaints: ${val}`;
            },
            afterLabel: function() {
              return '💡 Click bar to view complaints';
            }
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: '#cbd5e1',
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: '600' }
          },
          grid: { display: false }
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: '#94a3b8',
            stepSize: 1,
            precision: 0,
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 }
          },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      },
      onClick: (evt, elements) => {
        if (elements && elements.length > 0) {
          const index = elements[0].index;
          const selectedCat = activeCategories[index];
          if (selectedCat) {
            switchAdminTab('complaints');
            const searchInput = document.getElementById('admCompSearch');
            if (searchInput) {
              searchInput.value = selectedCat;
              filterAdminComplaints();
            }
          }
        }
      }
    }
  });
}

// ─────────────────────────── Manage Complaints ───────────────────────────
async function loadAdminComplaints() {
  try {
    const res = await fetch('/api/complaints');
    adminComplaints = await res.json();
    renderAdminComplaints(adminComplaints);
  } catch (e) {
    showToast('Failed to load complaints list', 'error');
  }
}

function renderAdminPriorityPill(prio) {
  const p = (prio || 'Medium').trim();
  const lower = p.toLowerCase();
  if (lower === 'critical') {
    return `<span class="prio-badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.55); box-shadow: 0 0 10px rgba(239, 68, 68, 0.3); font-weight: 800;"><span class="prio-dot" style="background: #ef4444; box-shadow: 0 0 8px #ef4444;"></span>Critical</span>`;
  } else if (lower === 'high') {
    return `<span class="prio-badge prio-badge-high"><span class="prio-dot prio-dot-high"></span>High</span>`;
  } else if (lower === 'medium') {
    return `<span class="prio-badge prio-badge-medium"><span class="prio-dot prio-dot-medium"></span>Medium</span>`;
  } else {
    return `<span class="prio-badge prio-badge-low"><span class="prio-dot prio-dot-low"></span>Low</span>`;
  }
}

function renderAdminStatusPill(status) {
  const s = (status || 'Pending').trim();
  const lower = s.toLowerCase().replace(/[\s-]/g, '_');
  if (lower === 'resolved') {
    return `<span class="status-badge status-badge-resolved"><i class="fa-solid fa-circle-check" style="font-size: 9px;"></i>Resolved</span>`;
  } else if (lower === 'in_progress') {
    return `<span class="status-badge status-badge-in_progress"><i class="fa-solid fa-spinner fa-spin" style="font-size: 9px;"></i>In Progress</span>`;
  } else if (lower === 'rejected') {
    return `<span class="status-badge" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35);"><i class="fa-solid fa-circle-xmark" style="font-size: 9px;"></i>Rejected</span>`;
  } else if (lower === 'approved') {
    return `<span class="status-badge" style="background: rgba(6, 182, 212, 0.15); color: #38bdf8; border: 1px solid rgba(6, 182, 212, 0.35);"><i class="fa-solid fa-thumbs-up" style="font-size: 9px;"></i>Approved</span>`;
  } else {
    return `<span class="status-badge status-badge-pending"><i class="fa-solid fa-clock" style="font-size: 9px;"></i>Pending</span>`;
  }
}

function renderAdminComplaints(data) {
  const tbody = document.getElementById('adminComplaintsTableBody');
  if (!tbody) return;

  // Update record counters if elements exist
  const counterEl = document.getElementById('admCompCounter');
  if (counterEl) {
    counterEl.innerHTML = `<i class="fa-solid fa-list-check" style="color: #06b6d4;"></i> Showing ${data.length} of ${adminComplaints ? adminComplaints.length : data.length} Complaints`;
  }

  if (data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 36px 20px; color: var(--text-muted); font-size: 13px;"><i class="fa-solid fa-inbox" style="font-size: 28px; opacity: 0.35; display: block; margin-bottom: 8px;"></i>No complaints match the current filter.</td></tr>';
    return;
  }

  tbody.innerHTML = data.map(c => {
    const isResolved = (c.status || '').toLowerCase() === 'resolved';
    return `
    <tr id="comp-row-${c.id}" style="border-bottom: 1px solid rgba(255,255,255,0.06); transition: background 0.15s ease;" onmouseover="this.style.background='rgba(56,189,248,0.04)'" onmouseout="this.style.background='transparent'">
      <td style="padding: 14px 10px; font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 800; font-size: 13px; text-align: center; white-space: nowrap;">
        #${c.id}
      </td>
      <td style="padding: 14px 16px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
          <span style="font-weight: 700; color: #f8fafc; font-size: 13.5px; line-height: 1.3;" title="${escapeHtml(c.title || '')}">
            ${escapeHtml(c.title || 'Untitled Complaint')}
          </span>
          <span style="font-size: 10px; padding: 2px 7px; border-radius: 5px; background: rgba(6,182,212,0.12); color: #38bdf8; font-weight: 700; border: 1px solid rgba(6,182,212,0.3); display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">
            <i class="fa-solid fa-tag" style="font-size: 8px;"></i> ${escapeHtml(c.category || 'General')}
          </span>
        </div>
        <div style="font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <span><i class="fa-regular fa-calendar" style="font-size: 10px; margin-right: 3px;"></i> ${escapeHtml((c.created_at || '').substring(0, 10))}</span>
          ${c.citizen_name ? `<span>&bull; Citizen: <strong style="color: #cbd5e1;">${escapeHtml(c.citizen_name)}</strong></span>` : ''}
          ${c.department ? `<span>&bull; <span style="color: #a855f7;"><i class="fa-solid fa-building-shield" style="font-size: 9px; margin-right: 2px;"></i> ${escapeHtml(c.department)}</span></span>` : ''}
          ${isResolved && c.assigned_officer_name ? `<span>&bull; <span style="color: #10b981;"><i class="fa-solid fa-circle-check" style="font-size: 9px; margin-right: 2px;"></i> Solved: ${escapeHtml(c.assigned_officer_name)}</span></span>` : ''}
        </div>
      </td>
      <td style="padding: 14px 14px;">
        <div style="color: #cbd5e1; font-size: 12.5px; font-weight: 600; display: flex; align-items: center; gap: 6px;">
          <i class="fa-solid fa-location-dot" style="color: #06b6d4; font-size: 12px; flex-shrink: 0;"></i>
          <span title="${escapeHtml(c.location || '-')}">${escapeHtml(c.location || 'Central Ward')}</span>
        </div>
      </td>
      <td style="padding: 14px 12px; text-align: center; white-space: nowrap;">
        ${renderAdminPriorityPill(c.priority)}
      </td>
      <td style="padding: 14px 12px; text-align: center; white-space: nowrap;">
        ${renderAdminStatusPill(c.status)}
      </td>
      <td style="padding: 14px 14px; text-align: center; white-space: nowrap;">
        ${isResolved
          ? `<button class="btn btn-sm btn-secondary" onclick="openAdminModal(${c.id})" style="padding: 6px 14px; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; gap: 5px; border-radius: 7px; width: 100%; max-width: 82px; border: 1px solid rgba(16,185,129,0.35); color: #34d399; background: rgba(16,185,129,0.08);" title="View Solved Complaint #${c.id}">
              <i class="fa-solid fa-eye"></i> View
            </button>`
          : `<button class="btn btn-sm btn-primary" onclick="openAdminModal(${c.id})" style="padding: 6px 14px; font-size: 11px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; gap: 5px; box-shadow: 0 2px 8px rgba(6,182,212,0.25); border-radius: 7px; width: 100%; max-width: 82px;" title="Manage Complaint #${c.id}">
              <i class="fa-solid fa-gear"></i> Manage
            </button>`
        }
      </td>
    </tr>
  `}).join('');
}

function filterAdminComplaints() {
  const query = document.getElementById('admCompSearch').value.toLowerCase().trim();
  const status = document.getElementById('admCompStatusFilter').value;

  const filtered = adminComplaints.filter(c => {
    const matchStatus = (status === 'All' || c.status === status);
    const txt = `${c.id} ${c.title} ${c.category} ${c.location} ${c.department} ${c.assigned_officer_name || ''}`.toLowerCase();
    const matchQuery = !query || txt.includes(query);
    return matchStatus && matchQuery;
  });

  renderAdminComplaints(filtered);
}


async function loadOfficersForDept(dept, selectedOfficerId = null) {
  const select = document.getElementById('admModalOfficer');
  const statusDiv = document.getElementById('officerLoadStatus');
  if (!select) return;

  select.innerHTML = '<option value="">⏳ Loading officers...</option>';
  select.disabled = true;

  try {
    const url = dept
      ? `/api/officers?department=${encodeURIComponent(dept)}`
      : '/api/officers';
    const res = await fetch(url);

    if (!res.ok) throw new Error('Network error');
    const officers = await res.json();

    select.disabled = false;

    if (!officers || officers.length === 0) {
      select.innerHTML = '<option value="">⚠️ No officers in this department</option>';
      if (statusDiv) statusDiv.textContent = `No field officers registered under "${dept}". Add officers from User Management.`;
      return;
    }

    select.innerHTML = '<option value="">-- Select Field Officer --</option>';
    officers.forEach(o => {
      const opt = document.createElement('option');
      opt.value = o.id;
      opt.setAttribute('data-name', o.name);
      opt.textContent = `👷 ${o.name}  (${o.phone || o.email})`;
      if (selectedOfficerId && parseInt(selectedOfficerId) === o.id) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });

    if (statusDiv) statusDiv.textContent = `${officers.length} officer(s) available in ${dept}.`;
  } catch (e) {
    select.disabled = false;
    select.innerHTML = '<option value="">❌ Failed to load officers</option>';
    if (statusDiv) statusDiv.textContent = 'Error loading officers. Please try again.';
  }
}

async function openAdminModal(id) {
  currentManagingId = id;

  // Show modal immediately with loading state
  document.getElementById('admModalTitle').textContent = `🗂️ Loading Complaint #${id}...`;
  document.getElementById('admModalCitizenInfo').innerHTML =
    '<div style="color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Loading details...</div>';
  document.getElementById('adminManageModal').style.display = 'flex';

  try {
    const res = await fetch(`/api/complaints/${id}`);
    if (!res.ok) throw new Error('Failed to fetch complaint');
    const data = await res.json();
    const c = data.complaint;

    // Update title
    document.getElementById('admModalTitle').textContent = `🗂️ Manage Complaint #${id}`;

    // Set hidden form values for status and priority (Read-only for Admin)
    document.getElementById('admModalStatus').value = c.status || 'Pending';
    document.getElementById('admModalPriority').value = c.priority || 'Medium';

    // Update Read-only Status Display Badge
    const statusBadge = document.getElementById('admStatusBadge');
    if (statusBadge) {
      statusBadge.className = `badge badge-${(c.status || 'Pending').toLowerCase().replace(' ', '_')}`;
      statusBadge.textContent = c.status || 'Pending';
    }

    // Update Read-only Priority Display Badge
    const prioBadge = document.getElementById('admPriorityBadge');
    if (prioBadge) {
      prioBadge.className = `badge ${c.priority === 'High' ? 'badge-rejected' : (c.priority === 'Low' ? 'badge-resolved' : 'badge-pending')}`;
      prioBadge.textContent = c.priority || 'Medium';
    }

    // === RESOLVED STATE: hide assignment section, show resolved banner & details ===
    const isResolved = (c.status || '').toLowerCase() === 'resolved';
    const assignSection = document.getElementById('admAssignSection');
    const resolvedBanner = document.getElementById('admResolvedBanner');
    const resolvedFooter = document.getElementById('admResolvedFooter');
    if (isResolved) {
      document.getElementById('admModalTitle').textContent = `✅ Complaint #${id} · Solved & Closed`;
      if (assignSection) assignSection.style.display = 'none';
      if (resolvedBanner) {
        resolvedBanner.style.display = 'flex';
        const deptEl = document.getElementById('admResolvedDeptText');
        const offEl = document.getElementById('admResolvedOfficerText');
        const remEl = document.getElementById('admResolvedRemarksText');
        if (deptEl) deptEl.textContent = c.department || 'General Municipal Department';
        if (offEl) offEl.textContent = c.assigned_officer_name ? `👷 ${c.assigned_officer_name}` : 'Direct Municipal Resolution';
        if (remEl) remEl.textContent = c.admin_remarks || c.remarks || 'Complaint successfully verified and addressed.';

        const proofWrap = document.getElementById('admResolvedProofWrap');
        const proofContainer = document.getElementById('admResolvedProofContainer');
        if (proofWrap && proofContainer) {
          if (c.solution_image) {
            proofWrap.style.display = 'block';
            proofContainer.innerHTML = `
              <img src="/static/uploads/solution_images/${escapeHtml(c.solution_image)}" alt="Resolution Proof"
                   style="max-height: 160px; border-radius: 8px; cursor: pointer; border: 1px solid rgba(16,185,129,0.3); object-fit: cover;"
                   onclick="openLightbox('/static/uploads/solution_images/${escapeHtml(c.solution_image)}')">
            `;
          } else {
            proofWrap.style.display = 'none';
            proofContainer.innerHTML = '';
          }
        }
      }
      if (resolvedFooter) resolvedFooter.style.display = 'flex';
    } else {
      document.getElementById('admModalTitle').textContent = `🗂️ Manage Complaint #${id}`;
      if (assignSection) assignSection.style.display = 'block';
      if (resolvedBanner) resolvedBanner.style.display = 'none';
      if (resolvedFooter) resolvedFooter.style.display = 'none';
      // Editable Admin fields: Department, Officer, Remarks
      document.getElementById('admModalDept').value = c.department || 'Sanitation Department';
      document.getElementById('admModalRemarks').value = c.admin_remarks || '';
    }

    // Show citizen info banner (Read-only)
    document.getElementById('admModalCitizenInfo').innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
        <div>
          <div style="font-weight: 700; color: var(--text-primary);">👤 ${escapeHtml(c.citizen_name || 'Unknown Citizen')}</div>
          <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">
            📞 ${c.citizen_phone || 'N/A'} &nbsp;|&nbsp; 📍 ${escapeHtml(c.location || 'N/A')}
          </div>
        </div>
        <div style="margin-left: auto; text-align: right;">
          <div style="font-size: 12px; color: var(--text-secondary);">📋 Issue: <strong>${escapeHtml(c.title)}</strong></div>
          <div style="font-size: 12px; color: var(--text-secondary);">🗂️ Category: ${c.category}</div>
        </div>
      </div>
    `;

    // Show issue description (Read-only)
    const descWrap = document.getElementById('admModalDescWrap');
    const descEl = document.getElementById('admModalDesc');
    if (descWrap && descEl) {
      descEl.textContent = c.description || 'No detailed description provided.';
      descWrap.style.display = 'block';
    }

    // Show complaint image preview if available (Read-only)
    const imgContainer = document.getElementById('admModalImages');
    if (imgContainer) {
      if (c.complaint_image) {
        imgContainer.style.display = 'flex';
        imgContainer.innerHTML = `
          <div style="background: rgba(14,21,38,0.7); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 14px; width: 100%;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px;">
              <i class="fa-solid fa-camera" style="color: var(--accent-cyan);"></i> Citizen Attached Photo Evidence
            </div>
            <img src="/static/uploads/complaint_images/${escapeHtml(c.complaint_image)}" alt="Citizen Photo"
                 style="max-height: 160px; border-radius: 8px; cursor: pointer; border: 1px solid rgba(255,255,255,0.1); object-fit: cover;"
                 onclick="openLightbox('/static/uploads/complaint_images/${escapeHtml(c.complaint_image)}')">
          </div>
        `;
      } else {
        imgContainer.style.display = 'none';
        imgContainer.innerHTML = '';
      }
    }

    // Load officers for the department (only when not resolved)
    if (!isResolved) {
      await loadOfficersForDept(c.department || 'Sanitation Department', c.assigned_officer_id);
    }
  } catch (err) {
    document.getElementById('admModalCitizenInfo').innerHTML =
      '<div style="color: var(--status-rejected);">❌ Failed to load complaint details.</div>';
    showToast('Could not load complaint details', 'error');
  }
}

function closeAdminModal() {
  document.getElementById('adminManageModal').style.display = 'none';
  const statusDiv = document.getElementById('officerLoadStatus');
  if (statusDiv) statusDiv.textContent = '';
}

async function saveAdminComplaintChanges() {
  const btn = document.getElementById('admSaveBtn');
  const department = document.getElementById('admModalDept').value;
  const officerSelect = document.getElementById('admModalOfficer');
  const assigned_officer_id = officerSelect.value ? parseInt(officerSelect.value) : null;
  const selectedOpt = officerSelect.options[officerSelect.selectedIndex];
  const assigned_officer_name = (assigned_officer_id && selectedOpt)
    ? (selectedOpt.getAttribute('data-name') || selectedOpt.textContent.trim())
    : null;
  const admin_remarks = document.getElementById('admModalRemarks').value.trim();

  // Admin only assigns department, officer, and instructions (status and priority remain untouched)
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
  }

  try {
    const payload = {
      department,
      admin_remarks,
      remarks: assigned_officer_name
        ? `Assigned to Field Officer: ${assigned_officer_name} (${department})`
        : `Assigned to ${department}`
    };

    if (assigned_officer_id) {
      payload.assigned_officer_id = assigned_officer_id;
      payload.assigned_officer_name = assigned_officer_name;
    }

    const res = await fetch(`/api/complaints/${currentManagingId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.ok && data.success) {
      const msg = assigned_officer_name
        ? `✅ Complaint #${currentManagingId} assigned to ${assigned_officer_name}!`
        : `✅ Department assigned to ${department}!`;
      showToast(msg, 'success');
      closeAdminModal();
      loadAdminComplaints();
      loadAdminDashboard();
    } else {
      showToast(data.message || 'Failed to assign complaint.', 'error');
    }
  } catch (err) {
    showToast('Network error while assigning complaint.', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-user-check"></i> Assign &amp; Save';
    }
  }
}

async function resolveComplaintDirectly() {
  const resolveBtn = document.getElementById('admResolveBtn');
  if (!currentManagingId) return;

  const department = document.getElementById('admModalDept').value;
  const officerSelect = document.getElementById('admModalOfficer');
  const assigned_officer_id = officerSelect && officerSelect.value ? parseInt(officerSelect.value) : null;
  const selectedOpt = officerSelect ? officerSelect.options[officerSelect.selectedIndex] : null;
  const assigned_officer_name = (assigned_officer_id && selectedOpt)
    ? (selectedOpt.getAttribute('data-name') || selectedOpt.textContent.trim())
    : null;
  const admin_remarks = document.getElementById('admModalRemarks').value.trim();

  if (resolveBtn) {
    resolveBtn.disabled = true;
    resolveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Resolving...';
  }

  try {
    const payload = {
      status: 'Resolved',
      department,
      admin_remarks: admin_remarks || 'Complaint resolved by administrator.',
      remarks: `Complaint resolved${assigned_officer_name ? ' by ' + assigned_officer_name : ''} (${department})`
    };
    if (assigned_officer_id) {
      payload.assigned_officer_id = assigned_officer_id;
      payload.assigned_officer_name = assigned_officer_name;
    }

    const res = await fetch(`/api/complaints/${currentManagingId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast(`✅ Complaint #${currentManagingId} has been marked as Resolved!`, 'success');
      closeAdminModal();
      loadAdminComplaints();
      loadAdminDashboard();
    } else {
      showToast(data.message || 'Failed to resolve complaint.', 'error');
    }
  } catch (err) {
    showToast('Network error while resolving complaint.', 'error');
  } finally {
    if (resolveBtn) {
      resolveBtn.disabled = false;
      resolveBtn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Mark as Resolved';
    }
  }
}

// ─────────────────────────── User Management ───────────────────────────
let currentUserFilter = 'All';
let currentManagingUserId = null;

async function loadAdminUsers() {
  try {
    const res = await fetch('/api/users');
    allUsers = await res.json();
    updateUserStats(allUsers);
    filterUsers();
  } catch (e) {
    showToast('Failed to load users', 'error');
  }
}

function updateUserStats(users) {
  const total = users.length;
  const citizens = users.filter(u => u.role === 'citizen').length;
  const depts = users.filter(u => u.role === 'department').length;
  const admins = users.filter(u => u.role === 'admin').length;
  const active = users.filter(u => u.status === 'active').length;
  const blocked = users.filter(u => u.status === 'blocked').length;

  const elTotal = document.getElementById('userStatTotal');
  if (elTotal) elTotal.textContent = total;
  const elCit = document.getElementById('userStatCitizen');
  if (elCit) elCit.textContent = citizens;
  const elDept = document.getElementById('userStatDept');
  if (elDept) elDept.textContent = depts;
  const elAdm = document.getElementById('userStatAdmin');
  if (elAdm) elAdm.textContent = admins;

  const pAll = document.getElementById('userPillAll');
  if (pAll) pAll.textContent = total;
  const pCit = document.getElementById('userPillCitizen');
  if (pCit) pCit.textContent = citizens;
  const pDept = document.getElementById('userPillDept');
  if (pDept) pDept.textContent = depts;
  const pAdm = document.getElementById('userPillAdmin');
  if (pAdm) pAdm.textContent = admins;
  const pAct = document.getElementById('userPillActive');
  if (pAct) pAct.textContent = active;
  const pBlk = document.getElementById('userPillBlocked');
  if (pBlk) pBlk.textContent = blocked;
}

function setUserFilter(filter) {
  currentUserFilter = filter;
  document.querySelectorAll('#adminTab_users .filter-pill').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-filter') === filter);
  });
  filterUsers();
}

function filterUsers() {
  const q = (document.getElementById('userSearch') ? document.getElementById('userSearch').value : '').toLowerCase().trim();
  let filtered = allUsers;

  if (currentUserFilter === 'citizen') {
    filtered = filtered.filter(u => u.role === 'citizen');
  } else if (currentUserFilter === 'department') {
    filtered = filtered.filter(u => u.role === 'department');
  } else if (currentUserFilter === 'admin') {
    filtered = filtered.filter(u => u.role === 'admin');
  } else if (currentUserFilter === 'active') {
    filtered = filtered.filter(u => u.status === 'active');
  } else if (currentUserFilter === 'blocked') {
    filtered = filtered.filter(u => u.status === 'blocked');
  }

  if (q) {
    filtered = filtered.filter(u =>
      `${u.id} ${u.name} ${u.email} ${u.role} ${u.department || ''}`.toLowerCase().includes(q)
    );
  }

  renderUsers(filtered);
}

function renderUsers(users) {
  const tbody = document.getElementById('usersTableBody');
  if (!tbody) return;

  if (!users || users.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 40px; color: var(--text-muted);">
          <div style="font-size: 28px; margin-bottom: 8px;">🔍</div>
          <div>No user accounts match your search or filter criteria.</div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = users.map(u => {
    const isSelf = (window.CURRENT_ADMIN_ID && u.id === window.CURRENT_ADMIN_ID);
    const initial = (u.name || 'U').charAt(0).toUpperCase();

    // Role badge & avatar styling
    let roleBadge = '';
    let avatarBg = '';
    if (u.role === 'admin') {
      roleBadge = `<span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4);"><i class="fa-solid fa-crown"></i> ADMIN</span>`;
      avatarBg = 'linear-gradient(135deg, #f59e0b, #ef4444)';
    } else if (u.role === 'department') {
      roleBadge = `<span class="badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4);"><i class="fa-solid fa-building"></i> OFFICER</span>`;
      avatarBg = 'linear-gradient(135deg, #38bdf8, #2563eb)';
    } else {
      roleBadge = `<span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4);"><i class="fa-solid fa-user"></i> CITIZEN</span>`;
      avatarBg = 'linear-gradient(135deg, #10b981, #059669)';
    }

    return `
      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.03)'" onmouseout="this.style.background='transparent'">
        <td style="padding: 14px 18px; font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 700;">#${u.id}</td>
        <td style="padding: 14px 18px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 36px; height: 36px; border-radius: 50%; background: ${avatarBg}; color: #fff; font-weight: 800; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
              ${initial}
            </div>
            <div>
              <div style="font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 6px;">
                ${escapeHtml(u.name)}
                ${isSelf ? '<span class="badge" style="font-size: 9px; padding: 2px 6px; background: rgba(245,158,11,0.2); color: #f59e0b;">YOU</span>' : ''}
              </div>
              <div style="font-size: 11px; color: var(--text-muted);">${u.phone ? `📞 ${u.phone}` : 'Account ID #' + u.id}</div>
            </div>
          </div>
        </td>
        <td style="padding: 14px 18px; color: var(--text-secondary); font-family: var(--font-mono); font-size: 12px; word-break: break-all;">
          ${escapeHtml(u.email)}
        </td>
        <td style="padding: 14px 18px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            ${roleBadge}
            ${isSelf ? `
              <span title="Cannot change own role" style="color: var(--text-muted); font-size: 11px; cursor: not-allowed;"><i class="fa-solid fa-lock"></i></span>
            ` : `
              <button type="button" class="btn btn-sm btn-secondary" onclick="openRoleModal(${u.id}, '${escapeHtml(u.name)}', '${u.role}', '${escapeHtml(u.department || '')}')" title="Change user role" style="padding: 3px 8px; font-size: 10px;">
                <i class="fa-solid fa-pen"></i> Role
              </button>
            `}
          </div>
        </td>
        <td style="padding: 14px 18px; color: var(--text-secondary);">
          ${u.department ? `<span style="display: flex; align-items: center; gap: 6px;"><i class="fa-solid fa-building" style="color: var(--accent-cyan); font-size: 11px;"></i> ${escapeHtml(u.department)}</span>` : '<span style="color: var(--text-muted);">-</span>'}
        </td>
        <td style="padding: 14px 18px;">
          <span class="badge ${u.status === 'active' ? 'badge-resolved' : 'badge-rejected'}" style="display: inline-flex; align-items: center; gap: 6px;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background: currentColor; box-shadow: 0 0 6px currentColor;"></span>
            ${u.status.toUpperCase()}
          </span>
        </td>
        <td style="padding: 14px 18px; text-align: right;">
          ${isSelf ? `
            <span class="badge" style="background: rgba(245, 158, 11, 0.12); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 6px 12px; font-size: 11px;">
              <i class="fa-solid fa-shield-halved"></i> Protected
            </span>
          ` : `
            <button class="btn btn-sm ${u.status === 'active' ? 'btn-danger' : 'btn-success'}" onclick="toggleUserStatus(${u.id}, '${u.status === 'active' ? 'blocked' : 'active'}')" style="padding: 6px 12px; font-size: 11px;">
              <i class="fa-solid ${u.status === 'active' ? 'fa-ban' : 'fa-check'}"></i>
              ${u.status === 'active' ? 'Block' : 'Unblock'}
            </button>
          `}
        </td>
      </tr>
    `;
  }).join('');
}

async function toggleUserStatus(uid, status) {
  if (window.CURRENT_ADMIN_ID && uid === window.CURRENT_ADMIN_ID) {
    showToast('You cannot block or deactivate your own admin account!', 'error');
    return;
  }

  try {
    const res = await fetch(`/api/users/${uid}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message || `User status set to ${status}.`, 'info');
      await loadAdminUsers();
    } else {
      showToast(data.message || 'Failed to update user status.', 'error');
    }
  } catch (err) {
    showToast('Network error while updating user status.', 'error');
  }
}

function openRoleModal(uid, name, role, dept) {
  if (window.CURRENT_ADMIN_ID && uid === window.CURRENT_ADMIN_ID) {
    showToast('You cannot change your own administrator role.', 'warning');
    return;
  }
  currentManagingUserId = uid;
  const infoEl = document.getElementById('changeRoleUserInfo');
  if (infoEl) infoEl.innerHTML = `Modifying role for <strong>${escapeHtml(name)}</strong> (User #${uid})`;

  const roleSelect = document.getElementById('changeRoleSelect');
  if (roleSelect) roleSelect.value = role;

  const deptGroup = document.getElementById('changeRoleDeptGroup');
  const deptSelect = document.getElementById('changeRoleDept');
  if (deptGroup && deptSelect) {
    deptGroup.style.display = (role === 'department') ? 'block' : 'none';
    if (dept) deptSelect.value = dept;
  }

  document.getElementById('changeRoleModal').style.display = 'flex';
}

function closeRoleModal() {
  document.getElementById('changeRoleModal').style.display = 'none';
  currentManagingUserId = null;
}

function onChangeRoleSelect(role) {
  const deptGroup = document.getElementById('changeRoleDeptGroup');
  if (deptGroup) deptGroup.style.display = (role === 'department') ? 'block' : 'none';
}

async function confirmRoleChange() {
  if (!currentManagingUserId) return;
  if (window.CURRENT_ADMIN_ID && currentManagingUserId === window.CURRENT_ADMIN_ID) {
    showToast('You cannot change your own role.', 'error');
    closeRoleModal();
    return;
  }

  const role = document.getElementById('changeRoleSelect').value;
  const dept = (role === 'department') ? document.getElementById('changeRoleDept').value : null;
  const btn = document.getElementById('confirmRoleBtn');

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Updating...';
  }

  try {
    const res = await fetch(`/api/users/${currentManagingUserId}/role`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, department: dept })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message || 'User role updated successfully!', 'success');
      closeRoleModal();
      await loadAdminUsers();
    } else {
      showToast(data.message || 'Failed to update user role.', 'error');
    }
  } catch (err) {
    showToast('Network error while updating role.', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Update Role';
    }
  }
}

function openAddUserModal() {
  const modal = document.getElementById('addUserModal');
  if (!modal) return;
  modal.style.display = 'flex';
  const roleEl = document.getElementById('newUserRole');
  if (roleEl) {
    if (!roleEl.value || roleEl.value === 'citizen') {
      roleEl.value = 'department';
    }
    onNewUserRoleChange(roleEl.value);
  }
}

function closeAddUserModal() {
  const modal = document.getElementById('addUserModal');
  if (modal) modal.style.display = 'none';
}

function onNewUserRoleChange(role) {
  const deptGroup = document.getElementById('newUserDeptGroup');
  if (deptGroup) {
    deptGroup.style.display = (role === 'department') ? 'block' : 'none';
  }
}

async function saveNewUser() {
  const name = document.getElementById('newUserName').value.trim();
  const email = document.getElementById('newUserEmail').value.trim();
  const role = document.getElementById('newUserRole').value;
  const password = document.getElementById('newUserPass').value.trim();
  const deptEl = document.getElementById('newUserDept');
  const department = (role === 'department' && deptEl) ? deptEl.value : null;

  if (!name || !email || !password) {
    showToast('Please fill all required fields (Name, Email, Password)', 'error');
    return;
  }

  if (role !== 'department' && role !== 'admin') {
    showToast('Admin can only create Department Officer or Administrator accounts.', 'error');
    return;
  }

  if (role === 'department' && !department) {
    showToast('Please select a department for the officer account.', 'warning');
    return;
  }

  const btn = document.getElementById('createUserSubmitBtn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating...';
  }

  try {
    const res = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, role, password, department })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message || 'Account created successfully!', 'success');
      closeAddUserModal();
      // Clear form inputs
      document.getElementById('newUserName').value = '';
      document.getElementById('newUserEmail').value = '';
      document.getElementById('newUserPass').value = '';
      await loadAdminUsers();
    } else {
      showToast(data.message || 'Failed to create account.', 'error');
    }
  } catch (err) {
    showToast('Network error while creating account.', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-check"></i> Create Account';
    }
  }
}

// ─────────────────────────── 1. DSA QUEUE VISUAL LAB ───────────────────────────
function setQueueMode(isPriority) {
  isQueuePriorityMode = isPriority;
  document.getElementById('qModeStd').className = `btn btn-sm ${!isPriority ? 'btn-primary' : 'btn-secondary'}`;
  document.getElementById('qModePrio').className = `btn btn-sm ${isPriority ? 'btn-primary' : 'btn-secondary'}`;
  renderDSAQueue();
}

async function renderDSAQueue() {
  const res = await fetch(`/api/dsa/queue?priority_mode=${isQueuePriorityMode}`);
  const data = await res.json();
  const container = document.getElementById('queueVisualContainer');
  if (!container) return;

  if (data.items.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; margin: auto;">[ Queue is Empty ]</div>';
    return;
  }

  container.innerHTML = data.items.map((item, idx) => `
    <div style="display: flex; align-items: center; gap: 12px;">
      <div class="dsa-node">
        <div class="dsa-node-id">#${item.id}</div>
        <div class="dsa-node-title">${escapeHtml(item.title ? item.title.substring(0, 10) : 'Task')}</div>
        <div style="font-size: 10px; font-weight: 700; color: ${item.priority === 'High' ? '#ef4444' : '#f59e0b'}; margin-top: 4px;">● ${item.priority || 'Med'}</div>
      </div>
      ${idx < data.items.length - 1 ? '<div class="dsa-arrow">➔</div>' : ''}
    </div>
  `).join('');
}

async function dsaEnqueue() {
  const title = document.getElementById('qInputTitle').value.trim() || 'Civic Problem';
  const priority = document.getElementById('qInputPrio').value;
  const id = Math.floor(Math.random() * 800) + 100;

  await fetch(`/api/dsa/queue?priority_mode=${isQueuePriorityMode}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, title, priority, category: 'Civic' })
  });

  document.getElementById('queueLogBox').innerHTML = `▶ ENQUEUE: Inserted Node(#${id}) [${title}] (Priority: ${priority}) to REAR.`;
  document.getElementById('qInputTitle').value = '';
  renderDSAQueue();
}

async function dsaDequeue() {
  const res = await fetch(`/api/dsa/queue?priority_mode=${isQueuePriorityMode}`, { method: 'DELETE' });
  const data = await res.json();
  if (data.dequeued) {
    document.getElementById('queueLogBox').innerHTML = `▶ DEQUEUE: Processed Node(#${data.dequeued.id}) [${data.dequeued.title}] from FRONT.`;
  } else {
    document.getElementById('queueLogBox').innerHTML = `▶ Queue Underflow: Queue is already empty.`;
  }
  renderDSAQueue();
}

async function dsaClearQueue() {
  await fetch(`/api/dsa/queue?action=clear&priority_mode=${isQueuePriorityMode}`, { method: 'DELETE' });
  document.getElementById('queueLogBox').innerHTML = `▶ CLEAR: Queue memory cleared.`;
  renderDSAQueue();
}

// ─────────────────────────── 2. DSA STACK VISUAL LAB ───────────────────────────
async function renderDSAStack() {
  const res = await fetch('/api/dsa/stack');
  const data = await res.json();
  const container = document.getElementById('stackVisualContainer');
  if (!container) return;

  if (data.items.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; margin: auto;">[ Stack is Empty - Base Reached ]</div>';
    return;
  }

  container.innerHTML = data.items.map((item, idx) => {
    const isTop = (idx === data.items.length - 1);
    return `
      <div style="background: ${isTop ? 'rgba(6, 182, 212, 0.2)' : 'var(--bg-input)'}; border: ${isTop ? '2px solid var(--accent-cyan)' : '1px solid var(--border-color)'}; padding: 12px 16px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 700; font-size: 13px;">${escapeHtml(item.action || 'Action State')}</span>
        ${isTop ? '<span class="badge badge-approved" style="box-shadow: 0 0 10px var(--accent-cyan-glow);">TOP</span>' : ''}
      </div>
    `;
  }).join('');
}

async function dsaPushStack() {
  const txt = document.getElementById('stackInput').value.trim() || 'Modified Complaint Status';
  const id = Math.floor(Math.random() * 800) + 100;
  await fetch('/api/dsa/stack', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, action: `${txt} (#${id})`, status: 'Updated' })
  });
  document.getElementById('stackLogBox').innerHTML = `▶ PUSH: Pushed new action state '${txt}' onto TOP of Stack (LIFO).`;
  document.getElementById('stackInput').value = '';
  renderDSAStack();
}

async function dsaPopStack() {
  const res = await fetch('/api/dsa/stack', { method: 'DELETE' });
  const data = await res.json();
  if (data.popped) {
    document.getElementById('stackLogBox').innerHTML = `▶ POP / UNDO: Reverted action '${data.popped.action}'.`;
  } else {
    document.getElementById('stackLogBox').innerHTML = `▶ Stack Underflow: No actions left to undo.`;
  }
  renderDSAStack();
}

async function dsaClearStack() {
  await fetch('/api/dsa/stack?action=clear', { method: 'DELETE' });
  document.getElementById('stackLogBox').innerHTML = `▶ CLEAR: Stack audit history reset.`;
  renderDSAStack();
}

// ─────────────────────────── 3. DSA LINKED LIST LAB ───────────────────────────
async function renderDSALL() {
  const res = await fetch('/api/dsa/linked_list');
  const data = await res.json();
  const container = document.getElementById('llVisualContainer');
  if (!container) return;

  if (data.nodes.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; margin: auto;">HEAD ➔ NULL [ Linked List Empty ]</div>';
    return;
  }

  container.innerHTML = data.nodes.map((node, idx) => `
    <div style="display: flex; align-items: center; gap: 12px;">
      <div class="dsa-node" style="border-color: var(--accent-purple); box-shadow: 0 0 15px var(--shadow-glow-purple);">
        <div class="dsa-node-id" style="color: var(--accent-purple);">#${node.id}</div>
        <div class="dsa-node-title">${escapeHtml(node.title ? node.title.substring(0, 10) : 'Node')}</div>
        <div style="font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); margin-top: 4px;">Next ➔</div>
      </div>
      <div class="dsa-arrow">${idx < data.nodes.length - 1 ? '➔' : '➔ <span style="color: var(--status-rejected); font-size: 12px; margin-left: 6px;">NULL</span>'}</div>
    </div>
  `).join('');
}

async function dsaLLInsert(pos) {
  const title = document.getElementById('llInput').value.trim() || 'Civic Node';
  const id = Math.floor(Math.random() * 800) + 100;
  await fetch('/api/dsa/linked_list', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, title, position: pos })
  });
  document.getElementById('llLogBox').innerHTML = `▶ INSERT: Attached Node(#${id}) at ${pos.toUpperCase()} of pointer chain.`;
  document.getElementById('llInput').value = '';
  renderDSALL();
}

async function dsaLLReverse() {
  await fetch('/api/dsa/linked_list?action=reverse', { method: 'DELETE' });
  document.getElementById('llLogBox').innerHTML = `▶ REVERSE: In-place pointer redirection using 3 pointers (prev, current, next).`;
  renderDSALL();
}

async function dsaLLClear() {
  await fetch('/api/dsa/linked_list?action=clear', { method: 'DELETE' });
  document.getElementById('llLogBox').innerHTML = `▶ CLEAR: All linked list nodes unlinked.`;
  renderDSALL();
}

// ─────────────────────────── 4. DSA EXPRESSION PARSER ───────────────────────────
async function runExpression() {
  const expr = document.getElementById('exprInput').value.trim() || '( 3 + 5 ) * 2';
  const res = await fetch('/api/dsa/expression', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ expression: expr })
  });
  const data = await res.json();

  document.getElementById('exprInfix').textContent = data.infix;
  document.getElementById('exprPostfix').textContent = data.postfix || 'Syntax Error';
  document.getElementById('exprResult').textContent = data.result !== null ? data.result : 'N/A';

  const container = document.getElementById('exprTraceContainer');
  if (container && data.steps) {
    container.innerHTML = data.steps.map(s => `
      <div style="background: var(--bg-input); padding: 8px 12px; border-radius: 6px; font-family: var(--font-mono); font-size: 12px; display: grid; grid-template-columns: 80px 140px 140px 1fr; gap: 10px;">
        <span style="color: var(--accent-cyan); font-weight: 700;">Token: ${s.token}</span>
        <span style="color: var(--status-pending);">Stack: [${s.stack.join(' ')}]</span>
        <span style="color: var(--status-resolved);">Output: [${s.output.join(' ')}]</span>
        <span style="color: var(--text-muted);">${s.action}</span>
      </div>
    `).join('');
  }
}

// ─────────────────────────── 5. DSA ITERATIVE ALGORITHMS ───────────────────────────
function renderIterArray(hlIndices = [], swapped = false) {
  const container = document.getElementById('sortingContainer');
  if (!container) return;

  const maxVal = Math.max(...iterArray, 100);
  container.innerHTML = iterArray.map((val, idx) => {
    const isHl = hlIndices.includes(idx);
    const heightPct = Math.round((val / maxVal) * 100);
    return `
      <div class="sorting-bar ${isHl ? (swapped ? 'swapped' : 'comparing') : ''}" style="height: ${heightPct}%;">
        <span class="bar-val">${val}</span>
      </div>
    `;
  }).join('');
}

function shuffleIterArray() {
  iterArray = Array.from({ length: 10 }, () => Math.floor(Math.random() * 90) + 10);
  renderIterArray();
  document.getElementById('iterLogBox').textContent = '▶ Shuffled random array.';
}

async function runIterativeAlgo(algo) {
  const target = parseInt(document.getElementById('iterTarget').value || 67);
  const res = await fetch('/api/dsa/iterative', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ algorithm: algo, array: iterArray, target })
  });
  const data = await res.json();

  if (algo === 'bubble_sort' || algo === 'selection_sort') {
    animateSortSteps(data.steps, algo);
  } else {
    animateSearchSteps(data.steps, algo, target);
  }
}

function animateSortSteps(steps, name) {
  let i = 0;
  function step() {
    if (i >= steps.length) {
      document.getElementById('iterLogBox').textContent = `▶ ${name.replace('_', ' ').toUpperCase()} complete in O(n²) comparisons!`;
      renderIterArray();
      return;
    }
    const s = steps[i];
    iterArray = s.state;
    renderIterArray(s.comparing || [s.selected_index], s.swapped);
    document.getElementById('iterLogBox').textContent = `Pass ${s.pass}: Comparing [${s.values ? s.values.join(', ') : s.selected_index}]`;
    i++;
    setTimeout(step, 180);
  }
  step();
}

function animateSearchSteps(steps, name, target) {
  let i = 0;
  function step() {
    if (i >= steps.length) {
      document.getElementById('iterLogBox').textContent = `▶ Search ended. Target ${target} verified.`;
      return;
    }
    const s = steps[i];
    const idx = (s.index !== undefined) ? s.index : s.mid;
    renderIterArray([idx], s.found || s.mid_value === target);
    document.getElementById('iterLogBox').textContent = `Checking index [${idx}] = ${s.value || s.mid_value} -> ${s.action || (s.found ? 'FOUND!' : 'Next')}`;
    i++;
    setTimeout(step, 300);
  }
  step();
}

// ─────────────────────────── 6. DSA RECURSIVE ALGORITHMS ───────────────────────────
async function runRecursiveAlgo(algo) {
  const n = parseInt(document.getElementById('recN').value || 5);
  const res = await fetch('/api/dsa/recursive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ algorithm: algo, n })
  });
  const data = await res.json();
  const box = document.getElementById('recCallTreeBox');

  if (box && data.steps) {
    box.innerHTML = `
      <div style="color: var(--accent-cyan); font-weight: 700; margin-bottom: 10px;">
        ▶ Result: ${JSON.stringify(data.result)} (Stack Depth: ${data.steps.length})
      </div>
    ` + data.steps.map(s => {
      const indent = '&nbsp;'.repeat((s.depth || 0) * 4);
      return `<div style="padding: 2px 0;">${indent}↳ ${s.call || s.action + ': ' + JSON.stringify(s.data)}</div>`;
    }).join('');
  }
}


// ═══════════════════════════════════════════════════════════════════════════
//  CLO3 — CIVIC INTELLIGENCE ALGORITHMIC ENGINE
// ═══════════════════════════════════════════════════════════════════════════

/* ── Priority weight map (Max-Heap order: Critical > High > Medium > Low) ── */
const PRIO_WEIGHT = { critical: 4, high: 3, medium: 2, low: 1 };

function getPrioWeight(p) {
  return PRIO_WEIGHT[(p || 'medium').toLowerCase()] || 1;
}

/* ─────────────── MAX-HEAP helpers ─────────────── */
function heapify(arr, n, i) {
  let largest = i, l = 2 * i + 1, r = 2 * i + 2;
  if (l < n && getPrioWeight(arr[l].priority) > getPrioWeight(arr[largest].priority)) largest = l;
  if (r < n && getPrioWeight(arr[r].priority) > getPrioWeight(arr[largest].priority)) largest = r;
  if (largest !== i) {
    [arr[i], arr[largest]] = [arr[largest], arr[i]];
    heapify(arr, n, largest);
  }
}

function heapSort(arr) {
  const a = [...arr];
  const n = a.length;
  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) heapify(a, n, i);
  const result = [];
  let size = n;
  while (size > 0) {
    result.push(a[0]);
    a[0] = a[--size];
    heapify(a, size, 0);
  }
  return result;
}

/* ─────────────── MERGE SORT helper ─────────────── */
function mergeSort(arr, keyFn, dir) {
  if (arr.length <= 1) return arr;
  const mid = Math.floor(arr.length / 2);
  const left  = mergeSort(arr.slice(0, mid), keyFn, dir);
  const right = mergeSort(arr.slice(mid),    keyFn, dir);
  return mergeParts(left, right, keyFn, dir);
}
function mergeParts(l, r, keyFn, dir) {
  const out = [];
  let i = 0, j = 0;
  while (i < l.length && j < r.length) {
    const a = keyFn(l[i]), b = keyFn(r[j]);
    const cmp = (a < b) ? -1 : (a > b) ? 1 : 0;
    out.push((dir === 'asc' ? cmp <= 0 : cmp >= 0) ? l[i++] : r[j++]);
  }
  return out.concat(l.slice(i)).concat(r.slice(j));
}

/* ── Shared helper: glow + flash + scroll to main table ── */
function flashMainTable(color, flashElId) {
  // Glow the main table card border
  const card = document.getElementById('mainComplaintsTableCard');
  if (card) {
    card.style.borderColor = color;
    card.style.boxShadow = `0 0 28px ${color}55, 0 10px 30px rgba(0,0,0,0.35)`;
    setTimeout(() => {
      card.style.borderColor = 'rgba(255, 255, 255, 0.08)';
      card.style.boxShadow = '0 10px 30px rgba(0,0,0,0.35)';
    }, 2500);
  }

  // Show flash banner, auto-hide after 3s
  ['priorityAppliedFlash', 'searchAppliedFlash', 'sortAppliedFlash'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });
  if (flashElId) {
    const flashEl = document.getElementById(flashElId);
    if (flashEl) {
      flashEl.style.display = 'block';
      setTimeout(() => { flashEl.style.display = 'none'; }, 3000);
    }
  }

  // Smooth scroll to the main table
  setTimeout(() => {
    const card2 = document.getElementById('mainComplaintsTableCard');
    if (card2) card2.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 200);
}

/* ══════════════════════════════════════════════════════════
   1.  PRIORITY-BASED PROCESSING — Max-Heap → Main Table
   ══════════════════════════════════════════════════════════ */
async function p3RunPriorityWithTable() {
  const btn = document.getElementById('p3PriorityBtn');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing…'; }

  try {
    const t0 = performance.now();
    let records = [];

    // 1. Try real Python DSA Priority Queue backend (Max-Heap)
    try {
      const res = await fetch('/api/dsa/phase3/priority');
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.records && data.records.length > 0) {
          records = data.records;
        }
      }
    } catch (_) {}

    // 2. Fallback to in-memory Heap Sort if API is unavailable
    if (!records || records.length === 0) {
      if (!adminComplaints || adminComplaints.length === 0) {
        const res = await fetch('/api/complaints');
        adminComplaints = await res.json();
      }
      records = heapSort(adminComplaints);
    }

    const elapsed = (performance.now() - t0).toFixed(2);

    // Apply directly to the main real complaints table
    adminComplaints = records;
    renderAdminComplaints(records);

    showAlgoStatusRibbon(
      '👑 Max-Heap Priority Processing',
      `${records.length} complaints sequenced: Critical → High → Medium → Low (Active emergencies first)`,
      '#f59e0b',
      elapsed
    );
    flashMainTable('#f59e0b', 'priorityAppliedFlash');
    showToast(`👑 Max-Heap: ${records.length} complaints processed in ${elapsed} ms`, 'success');
  } catch (e) {
    console.error(e);
    showToast('Failed to run priority processing.', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Process by Priority'; }
  }
}

/* ══════════════════════════════════════════════════════════
   2.  SEARCH — Linear O(N) / Binary O(log N) → Main Table
   ══════════════════════════════════════════════════════════ */
async function p3RunSearch(mode) {
  const idVal = (document.getElementById('p3SearchId').value || '').trim();
  const targetId = parseInt(idVal);
  const linearBtn = document.getElementById('p3LinearBtn');
  const binaryBtn = document.getElementById('p3BinaryBtn');

  if (!idVal || isNaN(targetId)) {
    showToast('Please enter a valid Complaint ID to search.', 'warning');
    const input = document.getElementById('p3SearchId');
    if (input) input.focus();
    return;
  }

  const activeBtn = mode === 'linear' ? linearBtn : binaryBtn;
  if (activeBtn) { activeBtn.disabled = true; activeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>'; }

  try {
    const t0 = performance.now();
    let found = null;
    let steps = 0;

    // 1. Try real Python DSA Search backend
    try {
      const res = await fetch('/api/dsa/phase3/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_id: targetId, method: mode })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          if (data.found && data.record) {
            found = data.record;
            steps = data.steps_count || 1;
          } else {
            steps = data.steps_count || 0;
          }
        }
      }
    } catch (_) {}

    // 2. Fallback to in-memory search if backend was offline
    if (!found && steps === 0) {
      if (!adminComplaints || adminComplaints.length === 0) {
        const res = await fetch('/api/complaints');
        adminComplaints = await res.json();
      }

      if (mode === 'linear') {
        for (let i = 0; i < adminComplaints.length; i++) {
          steps++;
          if (adminComplaints[i].id === targetId) { found = adminComplaints[i]; break; }
        }
      } else {
        const sorted = [...adminComplaints].sort((a, b) => a.id - b.id);
        let lo = 0, hi = sorted.length - 1;
        while (lo <= hi) {
          steps++;
          const mid = Math.floor((lo + hi) / 2);
          if (sorted[mid].id === targetId)     { found = sorted[mid]; break; }
          else if (sorted[mid].id < targetId)  lo = mid + 1;
          else                                  hi = mid - 1;
        }
      }
    }

    const elapsed = (performance.now() - t0).toFixed(2);

    if (found) {
      if (!adminComplaints || adminComplaints.length === 0) {
        const res = await fetch('/api/complaints');
        adminComplaints = await res.json();
      }

      // Show ONLY this particular searched complaint in the main table
      renderAdminComplaints([found]);

      showAlgoStatusRibbon(
        mode === 'linear' ? '🔍 Linear Search O(N)' : '⚡ Binary Search O(log N)',
        `Showing Complaint #${found.id} — "${escapeHtml((found.title || '').substring(0, 40))}" · Found in ${steps} step(s) · Single Record View (Click "Reset Table View" to restore all)`,
        '#06b6d4',
        elapsed
      );
      flashMainTable('#06b6d4', 'searchAppliedFlash');
      showToast(`✅ Showing Complaint #${targetId} (Found in ${steps} step${steps === 1 ? '' : 's'})`, 'success');

      // Highlight the single row in the real table
      setTimeout(() => {
        const row = document.getElementById(`comp-row-${found.id}`);
        if (row) {
          row.style.background = 'rgba(6, 182, 212, 0.22)';
          row.style.outline = '2px solid #06b6d4';
          row.scrollIntoView({ behavior: 'smooth', block: 'center' });
          setTimeout(() => {
            row.style.background = 'transparent';
            row.style.outline = 'none';
          }, 3500);
        }
      }, 150);
    } else {
      // If not found, show empty state in main table with reset option
      renderAdminComplaints([]);
      const tbody = document.getElementById('adminComplaintsTableBody');
      if (tbody) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 42px 20px; color: #f87171; font-size: 13px; font-weight: 600;">
          <i class="fa-solid fa-circle-xmark" style="font-size: 32px; display: block; margin-bottom: 10px; color: #ef4444;"></i>
          Complaint #${targetId} was not found via ${mode === 'linear' ? 'Linear Search' : 'Binary Search'} (scanned ${steps} record${steps === 1 ? '' : 's'}).
          <div style="margin-top: 12px;">
            <button type="button" class="btn btn-sm btn-secondary" onclick="resetAdminComplaintsOrder()" style="padding: 5px 14px; font-size: 11px; border-radius: 6px; font-weight: 700; cursor: pointer;">
              <i class="fa-solid fa-rotate-left"></i> Restore All Complaints
            </button>
          </div>
        </td></tr>`;
      }

      showAlgoStatusRibbon(
        mode === 'linear' ? '🔍 Linear Search' : '⚡ Binary Search',
        `Complaint #${targetId} not found after scanning ${steps} record(s).`,
        '#ef4444',
        elapsed
      );
      flashMainTable('#ef4444', 'searchAppliedFlash');
      showToast(`❌ Complaint #${targetId} not found.`, 'error');
    }
  } catch (e) {
    console.error(e);
    showToast('Search failed. Please try again.', 'error');
  } finally {
    if (linearBtn) { linearBtn.disabled = false; linearBtn.innerHTML = '<i class="fa-solid fa-bars-staggered"></i> Linear'; }
    if (binaryBtn) { binaryBtn.disabled = false; binaryBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Binary'; }
  }
}

/* ══════════════════════════════════════════════════════════
   3.  RECURSIVE MERGE SORT → Main Table
   ══════════════════════════════════════════════════════════ */
async function p3RunSort() {
  const field = document.getElementById('p3SortField').value;
  const order = document.getElementById('p3SortOrder').value;
  const btn   = document.getElementById('p3SortBtn');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sorting…'; }

  try {
    const t0 = performance.now();
    let sorted = [];
    let stepsCount = null;

    // 1. Try real Python DSA Merge Sort backend
    try {
      const res = await fetch('/api/dsa/phase3/sort', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field, algorithm: 'merge', order })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.sorted_records && data.sorted_records.length > 0) {
          sorted = data.sorted_records;
          stepsCount = data.steps_count;
        }
      }
    } catch (_) {}

    // 2. Fallback to client-side mergeSort if API was unavailable
    if (!sorted || sorted.length === 0) {
      if (!adminComplaints || adminComplaints.length === 0) {
        const res = await fetch('/api/complaints');
        adminComplaints = await res.json();
      }

      const keyFn = c => {
        if (field === 'priority') return getPrioWeight(c.priority);
        if (field === 'id')       return c.id;
        return String(c[field] || '').toLowerCase();
      };
      sorted = mergeSort([...adminComplaints], keyFn, order === 'asc' ? 'asc' : 'desc');
    }

    const elapsed = (performance.now() - t0).toFixed(2);

    adminComplaints = sorted;
    renderAdminComplaints(sorted);

    const fieldLabel = { id: 'Complaint ID', priority: 'Priority Score', category: 'Category', location: 'Ward Location', status: 'Status' }[field] || field;
    const dirLabel   = order === 'asc' ? '▲ Ascending' : '▼ Descending';
    const stepsInfo  = stepsCount !== null ? ` · ${stepsCount} recursion steps` : '';

    showAlgoStatusRibbon(
      '⚙️ Merge Sort [Divide & Conquer · O(N log N)]',
      `${sorted.length} complaints sorted by ${fieldLabel} — ${dirLabel}${stepsInfo}`,
      '#8b5cf6',
      elapsed
    );
    flashMainTable('#8b5cf6', 'sortAppliedFlash');
    showToast(`✅ Sorted ${sorted.length} records by ${fieldLabel} in ${elapsed} ms`, 'success');
  } catch (e) {
    console.error(e);
    showToast('Sort failed. Please try again.', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-code-merge"></i> Merge Sort'; }
  }
}

/* ── Algo Status Ribbon helper ── */
function showAlgoStatusRibbon(title, detail, color, ms) {
  const ribbon  = document.getElementById('admAlgoStatusRibbon');
  const content = document.getElementById('admAlgoStatusContent');
  if (!ribbon || !content) return;

  content.innerHTML = `
    <span style="width:32px;height:32px;border-radius:8px;background:${color}22;border:1px solid ${color}66;display:flex;align-items:center;justify-content:center;color:${color};font-size:15px;flex-shrink:0;">
      <i class="fa-solid fa-microchip"></i>
    </span>
    <div>
      <div style="font-size:13px;font-weight:800;color:#f8fafc;">${title}</div>
      <div style="font-size:11px;color:#94a3b8;font-weight:500;margin-top:2px;">${detail}</div>
    </div>
    <span style="margin-left:auto;font-size:11px;font-weight:700;background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.08);padding:3px 10px;border-radius:6px;color:${color};white-space:nowrap;">⏱ ${ms} ms</span>
  `;
  ribbon.style.display = 'flex';
  ribbon.style.borderColor = color + '66';
}

/* ── Reset main table to original API order ── */
async function resetAdminComplaintsOrder() {
  const ribbon = document.getElementById('admAlgoStatusRibbon');
  if (ribbon) ribbon.style.display = 'none';

  // Clear all flash banners
  ['priorityAppliedFlash', 'searchAppliedFlash', 'sortAppliedFlash'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });

  // Reset table glow
  const card = document.getElementById('mainComplaintsTableCard');
  if (card) {
    card.style.borderColor = 'rgba(255, 255, 255, 0.08)';
    card.style.boxShadow = '0 10px 30px rgba(0,0,0,0.35)';
  }

  await loadAdminComplaints();
  showToast('Table reset to default order.', 'info');
}

// ═══════════════════════════════════════════════════════════════════════════

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[m]));
}

function escapeQuotes(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'");
}

// ─────────────────────────── Notifications ───────────────────────────
async function loadAdminNotifications() {
  try {
    const res = await fetch('/api/notifications');
    if (!res.ok) return;
    const notifs = await res.json();
    if (!Array.isArray(notifs)) return;
    const unread = notifs.filter(n => !n.is_read);

    const badge = document.getElementById('adminBadge');
    if (badge) {
      if (unread.length > 0) {
        badge.textContent = unread.length > 99 ? '99+' : unread.length;
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    }

    const list = document.getElementById('adminNotifList');
    if (!list) return;
    if (notifs.length === 0) {
      list.innerHTML = '<div class="notif-empty"><i class="fa-solid fa-bell-slash"></i><br>No notifications yet</div>';
      return;
    }
    list.innerHTML = notifs.map(n => `
      <div class="notif-item ${n.is_read ? '' : 'unread'}" onclick="handleAdminNotifClick(${n.id}, ${n.complaint_id})">
        <div class="notif-icon"><i class="fa-solid fa-bell"></i></div>
        <div class="notif-content">
          <div class="notif-message">${escapeHtml(n.message)}</div>
          <div class="notif-meta"><i class="fa-regular fa-clock"></i> ${n.created_at}</div>
        </div>
        ${!n.is_read ? '<div class="notif-dot"></div>' : ''}
      </div>
    `).join('');
  } catch (e) {}
}

function toggleAdminNotifDropdown() {
  const dd = document.getElementById('adminNotifDropdown');
  if (dd) {
    dd.classList.toggle('open');
    if (dd.classList.contains('open')) loadAdminNotifications();
  }
}

async function handleAdminNotifClick(notifId, complaintId) {
  await fetch(`/api/notifications/${notifId}/read`, { method: 'PUT' });
  loadAdminNotifications();
  const dd = document.getElementById('adminNotifDropdown');
  if (dd) dd.classList.remove('open');
  if (complaintId && typeof openManageComplaintModal === 'function') {
    openManageComplaintModal(complaintId);
  }
}

async function adminMarkAllRead() {
  await fetch('/api/notifications/read-all', { method: 'PUT' });
  loadAdminNotifications();
  if (typeof showToast === 'function') {
    showToast('All notifications marked as read.', 'success');
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// PHASE 4: GREEDY ALGORITHM — PRIORITY-BASED COMPLAINT PROCESSING
// ══════════════════════════════════════════════════════════════════════════════

let _greedyNextComplaintId = null;

function _greedyPriorityBadge(priority) {
  const p = (priority || '').trim();
  const map = {
    'Critical': { bg: 'rgba(239,68,68,0.18)', color: '#f87171', border: 'rgba(239,68,68,0.45)' },
    'High':     { bg: 'rgba(249,115,22,0.18)', color: '#fb923c', border: 'rgba(249,115,22,0.45)' },
    'Medium':   { bg: 'rgba(245,158,11,0.18)', color: '#fbbf24', border: 'rgba(245,158,11,0.45)' },
    'Low':      { bg: 'rgba(16,185,129,0.18)',  color: '#34d399', border: 'rgba(16,185,129,0.45)' },
  };
  const s = map[p] || { bg: 'rgba(100,116,139,0.18)', color: '#94a3b8', border: 'rgba(100,116,139,0.35)' };
  return `<span style="display:inline-block;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:800;background:${s.bg};color:${s.color};border:1px solid ${s.border};">${escapeHtml(p || 'Unknown')}</span>`;
}

function _greedyStatusBadge(status) {
  const st = (status || '').trim();
  const map = {
    'Pending':     'badge-pending',
    'Approved':    'badge-approved',
    'In Progress': 'badge-progress',
    'Resolved':    'badge-resolved',
    'Rejected':    'badge-rejected',
  };
  const cls = map[st] || 'badge-pending';
  return `<span class="badge ${cls}" style="font-size:11px;">${escapeHtml(st || 'Unknown')}</span>`;
}

function _greedyFormatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr.replace(' ', 'T'));
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
         + ' ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
  } catch {
    return dateStr;
  }
}

async function runGreedyAlgorithm() {
  const btn = document.getElementById('greedyRunBtn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
  }

  try {
    const res = await fetch('/api/dsa/greedy/next-complaint');
    const data = await res.json();

    if (!data.success) {
      if (typeof showToast === 'function') showToast(data.message || 'Failed to run greedy algorithm.', 'error');
      return;
    }

    // Update KPI stat cards safely
    const pc = data.priority_counts || {};
    const setGreedyText = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = (val !== undefined && val !== null) ? val : '—';
    };
    const setGreedyHtml = (id, html) => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = html || '';
    };

    setGreedyText('greedyEligibleCount', data.eligible_count ?? 0);
    setGreedyText('greedyCriticalCount', pc.Critical ?? 0);
    setGreedyText('greedyHighCount', pc.High ?? 0);
    setGreedyText('greedyMediumCount', pc.Medium ?? 0);
    setGreedyText('greedyLowCount', pc.Low ?? 0);

    const nextCard = document.getElementById('greedyNextCard');
    const emptyMsg = document.getElementById('greedyEmptyMsg');
    const tableCard = document.getElementById('greedyTableCard');

    if (!data.next_complaint) {
      // No eligible complaints
      if (nextCard) nextCard.style.display = 'none';
      if (tableCard) tableCard.style.display = 'none';
      if (emptyMsg) emptyMsg.style.display = 'block';
      _greedyNextComplaintId = null;
    } else {
      if (emptyMsg) emptyMsg.style.display = 'none';
      if (nextCard) nextCard.style.display = 'block';
      if (tableCard) tableCard.style.display = 'block';

      const nc = data.next_complaint;
      _greedyNextComplaintId = nc.id;

      setGreedyText('greedyNextId', '#' + nc.id);
      setGreedyText('greedyNextTitle', nc.title || 'Untitled');
      setGreedyText('greedyNextCategory', nc.category || '—');
      setGreedyText('greedyNextLocation', nc.location || '—');
      setGreedyHtml('greedyNextPriority', _greedyPriorityBadge(nc.priority));
      setGreedyHtml('greedyNextStatus', _greedyStatusBadge(nc.status));
      setGreedyText('greedyNextDate', _greedyFormatDate(nc.created_at));

      // Populate processing order table
      const tbody = document.getElementById('greedyTableBody');
      const orders = data.processing_order || [];
      const tableCount = document.getElementById('greedyTableCount');
      if (tableCount) tableCount.textContent = orders.length + ' complaint' + (orders.length !== 1 ? 's' : '');

      if (tbody) {
        if (orders.length === 0) {
          tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:30px;color:#64748b;">No eligible complaints.</td></tr>';
        } else {
          tbody.innerHTML = orders.map((c, i) => {
            const isFirst = (i === 0);
            const rowBg = isFirst
              ? 'background: linear-gradient(90deg, rgba(16,185,129,0.08) 0%, transparent 100%);'
              : (i % 2 === 0 ? '' : 'background: rgba(255,255,255,0.015);');
            const borderLeft = isFirst ? 'border-left: 3px solid #10b981;' : '';
            return `<tr style="${rowBg}${borderLeft} border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.2s;" onmouseenter="this.style.background='rgba(6,182,212,0.06)'" onmouseleave="this.style.background='${isFirst ? 'rgba(16,185,129,0.08)' : (i%2===0?'transparent':'rgba(255,255,255,0.015)')}'">
              <td style="padding:12px;text-align:center;font-weight:900;color:${isFirst ? '#10b981' : '#94a3b8'};font-size:${isFirst?'14px':'12px'};">${isFirst ? '<i class=\"fa-solid fa-crown\" style=\"margin-right:3px;\"></i>' : ''}${i + 1}</td>
              <td style="padding:12px;text-align:center;font-weight:800;color:#38bdf8;font-family:var(--font-mono);font-size:13px;">#${c.id}</td>
              <td style="padding:12px 16px;font-weight:600;color:#e2e8f0;font-size:13px;max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(c.title || '')}">${escapeHtml(c.title || 'Untitled')}</td>
              <td style="padding:12px 14px;font-size:12px;color:#cbd5e1;">${escapeHtml(c.category || '—')}</td>
              <td style="padding:12px 14px;font-size:12px;color:#94a3b8;">${escapeHtml(c.location || '—')}</td>
              <td style="padding:12px;text-align:center;">${_greedyPriorityBadge(c.priority)}</td>
              <td style="padding:12px;text-align:center;">${_greedyStatusBadge(c.status)}</td>
              <td style="padding:12px 14px;font-size:11px;color:#64748b;">${_greedyFormatDate(c.created_at)}</td>
            </tr>`;
          }).join('');
        }
      }
    }

    if (typeof showToast === 'function') {
      showToast(`Greedy Algorithm executed — ${data.eligible_count} eligible complaint${data.eligible_count !== 1 ? 's' : ''} analyzed.`, 'success');
    }

  } catch (err) {
    console.error('Greedy algorithm error:', err);
    if (typeof showToast === 'function') showToast('Failed to run Greedy Algorithm. Please try again.', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Find Next Complaint';
    }
  }
}


function greedyManageNext() {
  if (!_greedyNextComplaintId) {
    if (typeof showToast === 'function') showToast('No complaint selected.', 'error');
    return;
  }
  // Use the existing admin complaint management modal
  if (typeof openAdminManageModal === 'function') {
    openAdminManageModal(_greedyNextComplaintId);
  } else {
    // Fallback: switch to complaints tab and load that specific complaint
    switchAdminTab('complaints');
    if (typeof showToast === 'function') {
      showToast(`Complaint #${_greedyNextComplaintId} — switched to Complaints tab.`, 'info');
    }
  }
}
