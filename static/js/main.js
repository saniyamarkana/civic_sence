/* ==========================================================================
   CivicSense — Core JavaScript (Particle Canvas, Auth, Toast Notifications)
   ========================================================================== */

// ─────────────────────────── Particle Background Animation ───────────────────────────
const canvas = document.getElementById('particleCanvas');
if (canvas) {
  const ctx = canvas.getContext('2d');
  let particles = [];

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  class Particle {
    constructor() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.size = Math.random() * 2 + 1;
      this.speedX = (Math.random() - 0.5) * 0.6;
      this.speedY = (Math.random() - 0.5) * 0.6;
      this.color = Math.random() > 0.5 ? '#06b6d4' : '#8b5cf6';
      this.alpha = Math.random() * 0.5 + 0.2;
    }
    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
      if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = this.color;
      ctx.globalAlpha = this.alpha;
      ctx.fill();
    }
  }

  for (let i = 0; i < 45; i++) {
    particles.push(new Particle());
  }

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let p of particles) {
      p.update();
      p.draw();
    }
    requestAnimationFrame(animateParticles);
  }
  animateParticles();
}

// ─────────────────────────── Toast Notifications ───────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer') || document.body;
  const toast = document.createElement('div');
  toast.className = 'toast';

  const icons = {
    success: 'fa-solid fa-circle-check',
    error: 'fa-solid fa-circle-exclamation',
    info: 'fa-solid fa-circle-info',
    warning: 'fa-solid fa-triangle-exclamation'
  };
  const colors = {
    success: '#10b981',
    error: '#ef4444',
    info: '#06b6d4',
    warning: '#f59e0b'
  };

  toast.innerHTML = `
    <i class="${icons[type] || icons.info}" style="color: ${colors[type] || colors.info}; font-size: 18px;"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

let currentAuthRole = 'citizen';
let currentRegRole = 'citizen';

// ─────────────────────────── Auth Page Functions ───────────────────────────
function switchAuthTab(mode) {
  const isLogin = (mode === 'login');
  document.getElementById('loginForm').style.display = isLogin ? 'block' : 'none';
  document.getElementById('registerForm').style.display = isLogin ? 'none' : 'block';
  document.getElementById('roleSwitcher').style.display = isLogin ? 'flex' : 'none';

  document.getElementById('tabLogin').className = `btn btn-sm ${isLogin ? 'btn-primary' : 'btn-secondary'}`;
  document.getElementById('tabRegister').className = `btn btn-sm ${isLogin ? 'btn-secondary' : 'btn-primary'}`;
}

function selectRole(role) {
  currentAuthRole = role;
  document.querySelectorAll('#roleSwitcher .role-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.role === role);
  });
}

function selectRegRole(role) {
  currentRegRole = role;
  document.querySelectorAll('#regRoleSwitcher .reg-role-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.role === role);
  });

  const nameLabel = document.getElementById('regNameLabel');
  const nameInput = document.getElementById('regName');
  const emailLabel = document.getElementById('regEmailLabel');
  const emailInput = document.getElementById('regEmail');
  const deptGroup = document.getElementById('regDeptGroup');
  const phoneLabel = document.getElementById('regPhoneLabel');
  const phoneInput = document.getElementById('regPhone');
  const addressLabel = document.getElementById('regAddressLabel');
  const addressInput = document.getElementById('regAddress');
  const submitBtn = document.getElementById('regSubmitBtn');

  if (role === 'department') {
    nameLabel.innerHTML = '<i class="fa-solid fa-id-badge"></i> Officer / Staff Name';
    nameInput.placeholder = 'e.g. Officer Vikram Singh';
    emailLabel.innerHTML = '<i class="fa-regular fa-envelope"></i> Official Department Email';
    emailInput.placeholder = 'vikram.sanitation@civicsense.com';
    deptGroup.style.display = 'block';
    phoneLabel.innerHTML = '<i class="fa-solid fa-phone"></i> Official Contact / Mobile Number';
    phoneInput.placeholder = '9876543210';
    addressLabel.innerHTML = '<i class="fa-solid fa-building"></i> Department Office / Branch Location';
    addressInput.placeholder = 'Municipal Zone 2 Office, City Center';
    submitBtn.className = 'btn btn-primary';
    submitBtn.innerHTML = '<i class="fa-solid fa-building-user"></i> <span>Create Department Account</span>';
  } else if (role === 'admin') {
    nameLabel.innerHTML = '<i class="fa-solid fa-user-shield"></i> Administrator Full Name';
    nameInput.placeholder = 'e.g. Rajesh Verma';
    emailLabel.innerHTML = '<i class="fa-regular fa-envelope"></i> Official Admin Email';
    emailInput.placeholder = 'admin.rajesh@civicsense.com';
    deptGroup.style.display = 'none';
    phoneLabel.innerHTML = '<i class="fa-solid fa-phone"></i> Official Phone Number';
    phoneInput.placeholder = '9999999999';
    addressLabel.innerHTML = '<i class="fa-solid fa-landmark"></i> Headquarters / City Hall Location';
    addressInput.placeholder = 'City Hall, Central Secretariat, Ward 1';
    submitBtn.className = 'btn btn-primary';
    submitBtn.innerHTML = '<i class="fa-solid fa-shield-halved"></i> <span>Create Admin Account</span>';
  } else {
    // citizen
    nameLabel.innerHTML = '<i class="fa-regular fa-user"></i> Full Name';
    nameInput.placeholder = 'e.g. Rahul Sharma';
    emailLabel.innerHTML = '<i class="fa-regular fa-envelope"></i> Email Address';
    emailInput.placeholder = 'rahul@example.com';
    deptGroup.style.display = 'none';
    phoneLabel.innerHTML = '<i class="fa-solid fa-phone"></i> Phone Number';
    phoneInput.placeholder = '9876543210';
    addressLabel.innerHTML = '<i class="fa-solid fa-location-dot"></i> Area / Ward / Address';
    addressInput.placeholder = 'Area A, Sector 4';
    submitBtn.className = 'btn btn-success';
    submitBtn.innerHTML = '<i class="fa-solid fa-user-plus"></i> <span>Create Citizen Account</span>';
  }
}

function quickFill(email, password, role) {
  document.getElementById('loginEmail').value = email;
  document.getElementById('loginPassword').value = password;
  selectRole(role);
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value.trim();
  const errDiv = document.getElementById('loginError');
  errDiv.style.display = 'none';

  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, role: currentAuthRole })
    });
    const data = await res.json();

    if (data.success) {
      showToast('Login successful! Redirecting...', 'success');
      setTimeout(() => {
        if (data.role === 'admin') window.location.href = '/admin';
        else if (data.role === 'department') window.location.href = '/department';
        else window.location.href = '/citizen';
      }, 500);
    } else {
      errDiv.textContent = data.message || 'Invalid credentials.';
      errDiv.style.display = 'block';
    }
  } catch (err) {
    errDiv.textContent = 'Server connection error. Please try again.';
    errDiv.style.display = 'block';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById('regName').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const phone = document.getElementById('regPhone').value.trim();
  const address = document.getElementById('regAddress').value.trim();
  const password = document.getElementById('regPassword').value.trim();
  const department = currentRegRole === 'department' ? document.getElementById('regDepartment').value : '';
  const errDiv = document.getElementById('regError');
  errDiv.style.display = 'none';

  if (!name || !email || !password) {
    errDiv.textContent = 'Please fill all required fields.';
    errDiv.style.display = 'block';
    return;
  }

  if (currentRegRole === 'department' && !department) {
    errDiv.textContent = 'Please select a department for the officer account.';
    errDiv.style.display = 'block';
    return;
  }

  try {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        email,
        phone,
        address,
        password,
        role: currentRegRole,
        department
      })
    });
    const data = await res.json();

    if (data.success) {
      showToast(data.message || 'Account created! Please sign in.', 'success');
      switchAuthTab('login');
      selectRole(currentRegRole);
      document.getElementById('loginEmail').value = email;
      document.getElementById('loginPassword').value = password;
    } else {
      errDiv.textContent = data.message || 'Registration failed.';
      errDiv.style.display = 'block';
    }
  } catch (err) {
    errDiv.textContent = 'Server connection error. Please try again.';
    errDiv.style.display = 'block';
  }
}
