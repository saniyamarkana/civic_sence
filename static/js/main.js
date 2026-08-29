/* ==========================================================================
   CivicSense — Core JavaScript (Particle Canvas, Auth, Toast Notifications)
   ========================================================================== */

let currentAuthRole = 'citizen';

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
    info: 'fa-solid fa-circle-info'
  };
  const colors = {
    success: '#10b981',
    error: '#ef4444',
    info: '#06b6d4'
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
  document.querySelectorAll('.role-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.role === role);
  });
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
  const errDiv = document.getElementById('regError');
  errDiv.style.display = 'none';

  try {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone, address, password })
    });
    const data = await res.json();

    if (data.success) {
      showToast('Account created! Please sign in.', 'success');
      switchAuthTab('login');
      document.getElementById('loginEmail').value = email;
    } else {
      errDiv.textContent = data.message || 'Registration failed.';
      errDiv.style.display = 'block';
    }
  } catch (err) {
    errDiv.textContent = 'Server connection error. Please try again.';
    errDiv.style.display = 'block';
  }
}
