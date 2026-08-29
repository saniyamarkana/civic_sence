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

function renderCategoryChart(data) {
  const ctx = document.getElementById('categoryChart');
  if (!ctx) return;

  const labels = data.map(d => d.category);
  const counts = data.map(d => d.cnt);

  if (categoryChartInstance) categoryChartInstance.destroy();

  categoryChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [{
        label: 'Complaints',
        data: counts.length ? counts : [0],
        backgroundColor: [
          '#06b6d4', '#3b82f6', '#10b981', '#f59e0b',
          '#8b5cf6', '#ec4899', '#14b8a6', '#6366f1'
        ],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { display: false } },
        y: { ticks: { color: '#94a3b8', precision: 0 }, grid: { color: 'rgba(255,255,255,0.05)' } }
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
        <small style="color: var(--text-muted); font-weight: normal;">${c.assigned_officer_name ? '👷 ' + c.assigned_officer_name : 'No officer assigned'}</small>
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
    document.getElementById('admModalTitle').textContent = `🗂️ Manage Complaint #${id}`;

    // Set form values
    document.getElementById('admModalStatus').value = c.status || 'Pending';
    document.getElementById('admModalPriority').value = c.priority || 'Medium';
    document.getElementById('admModalDept').value = c.department || 'Sanitation Department';
    document.getElementById('admModalRemarks').value = c.admin_remarks || '';

    // Show citizen info banner
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
  const status = document.getElementById('admModalStatus').value;
  const priority = document.getElementById('admModalPriority').value;
  const department = document.getElementById('admModalDept').value;
  const officerSelect = document.getElementById('admModalOfficer');
  const assigned_officer_id = officerSelect.value ? parseInt(officerSelect.value) : null;
  const selectedOpt = officerSelect.options[officerSelect.selectedIndex];
  const assigned_officer_name = (assigned_officer_id && selectedOpt)
    ? (selectedOpt.getAttribute('data-name') || selectedOpt.textContent.trim())
    : null;
  const admin_remarks = document.getElementById('admModalRemarks').value.trim();

  // Button loading state
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
  }

  try {
    const payload = {
      status,
      priority,
      department,
      admin_remarks,
      remarks: assigned_officer_name
        ? `Assigned to Officer: ${assigned_officer_name} | Status: ${status}`
        : `Status updated to ${status}`
    };

    // Only include officer if selected
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

    if (data.success) {
      const msg = assigned_officer_name
        ? `✅ Complaint #${currentManagingId} assigned to ${assigned_officer_name}!`
        : `✅ Complaint #${currentManagingId} updated to "${status}"!`;
      showToast(msg, 'success');
      closeAdminModal();
      loadAdminComplaints();
      // Refresh dashboard stats too
      loadAdminDashboard();
    } else {
      showToast(data.message || 'Failed to save changes', 'error');
    }
  } catch (err) {
    showToast('Network error. Please check server connection.', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-user-check"></i> Save & Assign';
    }
  }
}

// ─────────────────────────── User Management ───────────────────────────
async function loadAdminUsers() {
  try {
    const res = await fetch('/api/users');
    allUsers = await res.json();
    renderUsers(allUsers);
  } catch (e) {
    showToast('Failed to load users', 'error');
  }
}

function renderUsers(users) {
  const tbody = document.getElementById('usersTableBody');
  if (!tbody) return;

  tbody.innerHTML = users.map(u => `
    <tr style="border-bottom: 1px solid var(--border-color);">
      <td style="padding: 12px 10px; font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 700;">#${u.id}</td>
      <td style="padding: 12px 10px; font-weight: 600;">${escapeHtml(u.name)}</td>
      <td style="padding: 12px 10px; color: var(--text-secondary);">${u.email}</td>
      <td style="padding: 12px 10px;"><span class="badge badge-approved">${u.role.toUpperCase()}</span></td>
      <td style="padding: 12px 10px; color: var(--text-secondary);">${u.department || '-'}</td>
      <td style="padding: 12px 10px;">
        <span class="badge ${u.status === 'active' ? 'badge-resolved' : 'badge-rejected'}">● ${u.status}</span>
      </td>
      <td style="padding: 12px 10px;">
        <button class="btn btn-sm ${u.status === 'active' ? 'btn-danger' : 'btn-success'}" onclick="toggleUserStatus(${u.id}, '${u.status === 'active' ? 'blocked' : 'active'}')">
          ${u.status === 'active' ? 'Block' : 'Unblock'}
        </button>
      </td>
    </tr>
  `).join('');
}

function filterUsers() {
  const q = document.getElementById('userSearch').value.toLowerCase().trim();
  const filtered = allUsers.filter(u => `${u.id} ${u.name} ${u.email} ${u.role}`.toLowerCase().includes(q));
  renderUsers(filtered);
}

async function toggleUserStatus(uid, status) {
  await fetch(`/api/users/${uid}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  showToast(`User status set to ${status}`, 'info');
  loadAdminUsers();
}

function openAddUserModal() { document.getElementById('addUserModal').style.display = 'flex'; }
function closeAddUserModal() { document.getElementById('addUserModal').style.display = 'none'; }

async function saveNewUser() {
  const name = document.getElementById('newUserName').value.trim();
  const email = document.getElementById('newUserEmail').value.trim();
  const role = document.getElementById('newUserRole').value;
  const password = document.getElementById('newUserPass').value.trim();

  if (!name || !email || !password) {
    showToast('Please fill all fields', 'error');
    return;
  }

  const res = await fetch('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, role, password })
  });
  const data = await res.json();
  if (data.success) {
    showToast('User created!', 'success');
    closeAddUserModal();
    loadAdminUsers();
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
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[m]));
}

function escapeQuotes(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'");
}
