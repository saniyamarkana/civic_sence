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

  const tabs = ['dashboard', 'complaints', 'users', 'dsa_queue', 'dsa_stack', 'dsa_ll', 'dsa_expr', 'dsa_iter', 'dsa_rec'];
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
    dsa_rec: '<i class="fa-solid fa-sitemap" style="color: var(--accent-purple);"></i> Recursive Call Tree Visualizer'
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

function renderAdminComplaints(data) {
  const tbody = document.getElementById('adminComplaintsTableBody');
  if (!tbody) return;

  if (data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 30px; color: var(--text-muted);">No complaints recorded.</td></tr>';
    return;
  }

  tbody.innerHTML = data.map(c => `
    <tr style="border-bottom: 1px solid var(--border-color);">
      <td style="padding: 12px 10px; font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 700;">#${c.id}</td>
      <td style="padding: 12px 10px; font-weight: 600;">${escapeHtml(c.title)}</td>
      <td style="padding: 12px 10px; color: var(--text-secondary);">${c.category}</td>
      <td style="padding: 12px 10px; color: var(--text-secondary);">${c.location || '-'}</td>
      <td style="padding: 12px 10px;"><span class="badge ${c.priority === 'High' ? 'badge-rejected' : 'badge-pending'}">${c.priority}</span></td>
      <td style="padding: 12px 10px; font-weight: 600; color: var(--accent-cyan);">
        ${c.department || '<span style="color: var(--text-muted);">Unassigned</span>'}<br>
        <small style="color: var(--text-muted); font-weight: normal;">${c.assigned_officer_name ? '\u{1F477} ' + c.assigned_officer_name : 'No officer assigned'}</small>
      </td>
      <td style="padding: 12px 10px;"><span class="badge badge-${c.status.toLowerCase().replace(' ', '_')}">● ${c.status}</span></td>
      <td style="padding: 12px 10px;">
        <button class="btn btn-sm btn-primary" onclick="openAdminModal(${c.id})">
          <i class="fa-solid fa-gear"></i> Manage
        </button>
      </td>
    </tr>
  `).join('');
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
    document.getElementById('admModalTitle').textContent = `🗂️ Manage & Assign Complaint #${id}`;

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

    // Editable Admin fields: Department, Officer, Remarks
    document.getElementById('admModalDept').value = c.department || 'Sanitation Department';
    document.getElementById('admModalRemarks').value = c.admin_remarks || '';

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

    // Load officers for the department
    await loadOfficersForDept(c.department || 'Sanitation Department', c.assigned_officer_id);
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
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Assigning...';
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
      btn.innerHTML = '<i class="fa-solid fa-user-check"></i> Assign Department &amp; Officer';
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

