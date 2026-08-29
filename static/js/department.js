/* ==========================================================================
   CivicSense — Department Portal Logic (Work Overview, Quick Transitions)
   ========================================================================== */

let deptComplaints = [];

document.addEventListener('DOMContentLoaded', () => {
  loadDeptData();
});

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

    document.getElementById('deptStatTotal').textContent = stats.total || 0;
    document.getElementById('deptStatPending').textContent = stats.pending || 0;
    document.getElementById('deptStatProgress').textContent = stats.in_progress || 0;
    document.getElementById('deptStatResolved').textContent = stats.resolved || 0;

    const compRes = await fetch('/api/complaints');
    deptComplaints = await compRes.json();

    renderUrgentTasks(deptComplaints);
    renderDeptTable(deptComplaints);
    populateDeptSelect();
  } catch (err) {
    showToast('Failed to load department data', 'error');
  }
}

function renderUrgentTasks(data) {
  const container = document.getElementById('deptUrgentList');
  if (!container) return;

  const urgent = data.filter(c => c.priority === 'High' && c.status !== 'Resolved');
  if (urgent.length === 0) {
    container.innerHTML = '<div style="color: var(--status-resolved); font-size: 13px; font-weight: 600;"><i class="fa-solid fa-circle-check"></i> All urgent high-priority tasks are currently clear!</div>';
    return;
  }

  container.innerHTML = urgent.map(c => `
    <div style="background: var(--bg-input); border-left: 4px solid var(--status-rejected); padding: 12px 16px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div style="font-weight: 700; font-size: 13px; color: var(--text-primary);">#${c.id} — ${escapeHtml(c.title)}</div>
        <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">📍 ${c.location || 'Area A'} &nbsp;|&nbsp; 📅 ${c.created_at}</div>
      </div>
      <div style="display: flex; gap: 8px;">
        ${c.status !== 'In Progress' ? `<button class="btn btn-sm btn-primary" onclick="quickDeptUpdate(${c.id}, 'In Progress')">Start Work</button>` : ''}
        <button class="btn btn-sm btn-success" onclick="quickDeptUpdate(${c.id}, 'Resolved')">Resolve</button>
      </div>
    </div>
  `).join('');
}

function renderDeptTable(data) {
  const tbody = document.getElementById('deptAssignedTableBody');
  if (!tbody) return;

  if (data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 30px; color: var(--text-muted);">No complaints currently assigned to this department.</td></tr>';
    return;
  }

  tbody.innerHTML = data.map(c => `
    <tr style="border-bottom: 1px solid var(--border-color);">
      <td style="padding: 12px 10px; font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 700;">#${c.id}</td>
      <td style="padding: 12px 10px; font-weight: 600;">${escapeHtml(c.title)}</td>
      <td style="padding: 12px 10px; color: var(--text-secondary);">${c.location || '-'}</td>
      <td style="padding: 12px 10px;"><span class="badge ${c.priority === 'High' ? 'badge-rejected' : 'badge-pending'}">${c.priority}</span></td>
      <td style="padding: 12px 10px;"><span class="badge badge-${c.status.toLowerCase().replace(' ', '_')}">● ${c.status}</span></td>
      <td style="padding: 12px 10px;">
        <div style="display: flex; gap: 6px;">
          ${c.status !== 'In Progress' && c.status !== 'Resolved' ? `<button class="btn btn-sm btn-primary" onclick="quickDeptUpdate(${c.id}, 'In Progress')"><i class="fa-solid fa-play"></i> Start</button>` : ''}
          ${c.status === 'In Progress' ? `<span class="badge badge-pending" style="padding: 6px 10px;"><i class="fa-solid fa-person-digging"></i> In Process</span>` : ''}
          ${c.status !== 'Resolved' ? `<button class="btn btn-sm btn-success" onclick="quickDeptUpdate(${c.id}, 'Resolved')"><i class="fa-solid fa-circle-check"></i> Solve</button>` : `<span class="badge badge-resolved"><i class="fa-solid fa-check"></i> Solved</span>`}
        </div>
      </td>
    </tr>
  `).join('');
}

function populateDeptSelect() {
  const select = document.getElementById('deptComplaintSelect');
  if (!select) return;

  select.innerHTML = '<option value="">-- Choose an Assigned Complaint --</option>';
  deptComplaints.forEach(c => {
    select.innerHTML += `<option value="${c.id}">#${c.id} — ${c.title} (${c.status})</option>`;
  });
}

let activeSolvingId = null;

function promptDeptSolve(cid) {
  activeSolvingId = cid;
  document.getElementById('deptSolveModalTitle').innerHTML = `<i class="fa-solid fa-circle-check"></i> Solve Complaint #${cid}`;
  document.getElementById('deptSolveNotes').value = '';
  document.getElementById('deptSolveModal').style.display = 'flex';
}

function closeDeptSolveModal() {
  document.getElementById('deptSolveModal').style.display = 'none';
}

async function confirmDeptSolve() {
  const notes = document.getElementById('deptSolveNotes').value.trim();
  if (!notes) {
    showToast('Please provide resolution details.', 'error');
    return;
  }

  try {
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
      body: JSON.stringify({ status, remarks: `Officer started field work (${status})` })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Complaint #${cid} status changed to ${status}!`, 'success');
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
    showToast('Please select a complaint.', 'error');
    return;
  }

  try {
    const res = await fetch(`/api/complaints/${cid}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, admin_remarks, remarks: `Field update: ${admin_remarks}` })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Complaint #${cid} successfully updated!`, 'success');
      document.getElementById('deptWorkRemarks').value = '';
      switchDeptTab('assigned');
    }
  } catch (err) {
    showToast('Failed to update complaint', 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[m]));
}
