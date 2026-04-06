// ===== API CONFIG =====
const API_BASE = "http://127.0.0.1:8000/api";

// ===== AUTH HELPERS =====
const Auth = {
  getToken() {
    return localStorage.getItem("access_token");
  },
  getRefreshToken() {
    return localStorage.getItem("refresh_token");
  },
  getUser() {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },
  setAuth(data) {
    localStorage.setItem("access_token", data.tokens.access);
    localStorage.setItem("refresh_token", data.tokens.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));
  },
  clearAuth() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  },
  isLoggedIn() {
    return !!this.getToken();
  },
  isAdmin() {
    const user = this.getUser();
    return user && user.role === "admin";
  },
  isDonor() {
    const user = this.getUser();
    return user && user.role === "donor";
  },
};

// ===== API HELPER =====
const Api = {
  async request(endpoint, method = "GET", body = null, auth = true) {
    const headers = { "Content-Type": "application/json" };
    if (auth && Auth.getToken()) {
      headers["Authorization"] = `Bearer ${Auth.getToken()}`;
    }
    const config = { method, headers };
    if (body) config.body = JSON.stringify(body);

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, config);
      const data = await res.json();
      if (!res.ok) throw { status: res.status, data };
      return data;
    } catch (err) {
      throw err;
    }
  },

  get(endpoint, auth = true) {
    return this.request(endpoint, "GET", null, auth);
  },
  post(endpoint, body, auth = true) {
    return this.request(endpoint, "POST", body, auth);
  },
  patch(endpoint, body, auth = true) {
    return this.request(endpoint, "PATCH", body, auth);
  },
  delete(endpoint, auth = true) {
    return this.request(endpoint, "DELETE", null, auth);
  },
};

// ===== TOAST =====
function showToast(message, type = "success") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const icons = { success: "✅", error: "❌", warning: "⚠️" };
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideIn 0.3s ease reverse";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ===== NAVBAR =====
function initNavbar() {
  const user = Auth.getUser();
  const navActions = document.querySelector(".navbar-actions");
  const hamburger = document.querySelector(".hamburger");
  const navMenu = document.querySelector(".navbar-nav");

  if (navActions) {
    if (Auth.isLoggedIn()) {
      navActions.innerHTML = `
        <a href="cart.html" class="cart-icon">
          🛒 <span class="cart-badge" id="cartCount">0</span>
        </a>
        <div style="display:flex;align-items:center;gap:0.5rem;">
          <span style="font-size:0.9rem;color:var(--text-secondary)">Hi, ${user?.full_name?.split(" ")[0]}</span>
          <button class="btn btn-outline btn-sm" onclick="logout()">Logout</button>
        </div>
      `;
      updateCartCount();
    } else {
      navActions.innerHTML = `
        <a href="login.html" class="btn btn-ghost btn-sm">Login</a>
        <a href="register.html" class="btn btn-primary btn-sm">Sign Up</a>
      `;
    }
  }

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", () => {
      navMenu.classList.toggle("open");
    });
  }

  // Set active nav link
  const currentPage = window.location.pathname.split("/").pop();
  document.querySelectorAll(".navbar-nav a").forEach((link) => {
    if (link.getAttribute("href") === currentPage) {
      link.classList.add("active");
    }
  });
}

// ===== LOGOUT =====
async function logout() {
  try {
    await Api.post("/users/logout/", { refresh: Auth.getRefreshToken() });
  } catch (e) {}
  Auth.clearAuth();
  showToast("Logged out successfully!");
  setTimeout(() => (window.location.href = "login.html"), 1000);
}

// ===== CART COUNT =====
async function updateCartCount() {
  if (!Auth.isLoggedIn()) return;
  try {
    const cart = await Api.get("/orders/cart/");
    const badge = document.getElementById("cartCount");
    if (badge) badge.textContent = cart.total_items || 0;
  } catch (e) {}
}

// ===== ADD TO CART =====
async function addToCart(foodItemId, name) {
  if (!Auth.isLoggedIn()) {
    showToast("Please login to add items to cart!", "warning");
    setTimeout(() => (window.location.href = "login.html"), 1500);
    return;
  }
  try {
    await Api.post("/orders/cart/", { food_item_id: foodItemId, quantity: 1 });
    showToast(`${name} added to cart! 🛒`);
    updateCartCount();
  } catch (e) {
    showToast("Failed to add item to cart!", "error");
  }
}

// ===== FORMAT PRICE =====
function formatPrice(price) {
  return `₹${parseFloat(price).toFixed(2)}`;
}

// ===== FORMAT DATE =====
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ===== ORDER STATUS LABEL =====
function getStatusBadge(status) {
  const map = {
    pending: '<span class="badge badge-warning">⏳ Pending</span>',
    confirmed: '<span class="badge badge-info">✅ Confirmed</span>',
    preparing: '<span class="badge badge-primary">👨‍🍳 Preparing</span>',
    out_for_delivery:
      '<span class="badge badge-primary">🚴 Out for Delivery</span>',
    delivered: '<span class="badge badge-success">🎉 Delivered</span>',
    cancelled: '<span class="badge badge-danger">❌ Cancelled</span>',
  };
  return map[status] || status;
}

// ===== DONATION STATUS LABEL =====
function getDonationBadge(status) {
  const map = {
    pending: '<span class="badge badge-warning">⏳ Pending</span>',
    approved: '<span class="badge badge-success">✅ Approved</span>',
    picked_up: '<span class="badge badge-info">📦 Picked Up</span>',
    distributed: '<span class="badge badge-success">🎉 Distributed</span>',
    rejected: '<span class="badge badge-danger">❌ Rejected</span>',
  };
  return map[status] || status;
}

// ===== PROTECT ROUTES =====
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    showToast("Please login first!", "warning");
    setTimeout(() => (window.location.href = "login.html"), 1000);
    return false;
  }
  return true;
}

function requireAdmin() {
  if (!Auth.isAdmin()) {
    showToast("Admin access only!", "error");
    setTimeout(() => (window.location.href = "index.html"), 1000);
    return false;
  }
  return true;
}

// ===== FOOD CARD TEMPLATE =====
function createFoodCard(item) {
  const hasDiscount =
    item.discount_price &&
    parseFloat(item.discount_price) < parseFloat(item.price);
  return `
    <div class="food-card fade-up">
      <div class="food-card-img">
        ${item.image ? `<img src="${item.image}" alt="${item.name}" style="width:100%;height:100%;object-fit:cover;">` : "🍽️"}
      </div>
      <div class="food-card-body">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
          <span class="veg-badge ${item.is_veg ? "veg" : "non-veg"}">
            ${item.is_veg ? "🟢 Veg" : "🔴 Non-Veg"}
          </span>
          ${item.status === "rescue" ? '<span class="badge badge-warning">🤝 Rescue</span>' : ""}
        </div>
        <h3 class="food-card-title">${item.name}</h3>
        <p class="food-card-desc">${item.description}</p>
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
          <span style="font-size:0.8rem;color:var(--text-muted)">⏱️ ${item.preparation_time} min</span>
          ${item.calories ? `<span style="font-size:0.8rem;color:var(--text-muted)">🔥 ${item.calories} cal</span>` : ""}
          <span style="font-size:0.8rem;color:var(--text-muted)">⭐ ${item.rating}</span>
        </div>
        <div class="food-card-footer">
          <div>
            <span class="food-price">${formatPrice(item.final_price)}</span>
            ${hasDiscount ? `<span class="food-price-original">${formatPrice(item.price)}</span>` : ""}
          </div>
          <button class="btn btn-primary btn-sm" onclick="addToCart(${item.id}, '${item.name}')">
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  `;
}

// ===== INIT =====
document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
});
