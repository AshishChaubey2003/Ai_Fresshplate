// ===== API CONFIG =====
// Local machine -> local Django server, live site -> Render server
const IS_LOCAL = ["localhost", "127.0.0.1", ""].includes(
  window.location.hostname,
);
const API_BASE =
  window.API_BASE_OVERRIDE ||
  (IS_LOCAL
    ? "http://127.0.0.1:8000/api"
    : "https://ai-fresshplate.onrender.com/api");

const REQUEST_TIMEOUT_MS = 30000; // Render free server can take time to wake up

// ===== SECURITY HELPERS =====
// Always escape anything that comes from the API or a user before putting it
// into innerHTML. Without this, a donor could save a food name like
// <img src=x onerror="..."> and run JavaScript in the admin's browser
// (stored XSS) - which could steal the admin's JWT from localStorage.
function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// Turn a DRF error response into one readable sentence
function apiErrorMessage(
  err,
  fallback = "Something went wrong. Please try again.",
) {
  const data = err && err.data;
  if (!data) return fallback;
  if (typeof data === "string") return data;
  if (data.error) return data.error;
  if (data.detail) return data.detail;

  const firstKey = Object.keys(data)[0];
  if (!firstKey) return fallback;
  const raw = data[firstKey];
  const value = Array.isArray(raw) ? raw[0] : raw;
  if (typeof value === "object") return fallback;
  return firstKey === "non_field_errors"
    ? String(value)
    : `${firstKey.replace(/_/g, " ")}: ${value}`;
}

// ===== AUTH HELPERS =====
const Auth = {
  getToken() {
    return localStorage.getItem("access_token");
  },
  getRefreshToken() {
    return localStorage.getItem("refresh_token");
  },
  getUser() {
    // Corrupted JSON used to crash the whole page here
    try {
      const user = localStorage.getItem("user");
      return user ? JSON.parse(user) : null;
    } catch {
      this.clearAuth();
      return null;
    }
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
    return !!user && user.role === "admin";
  },
  isDonor() {
    const user = this.getUser();
    return !!user && user.role === "donor";
  },
};

// ===== API HELPER =====
const Api = {
  _refreshPromise: null, // single-flight guard for token refresh

  // Send one request with a timeout. Returns { res, data }.
  async _send(endpoint, method, body, auth) {
    const headers = { "Content-Type": "application/json" };
    if (auth && Auth.getToken()) {
      headers["Authorization"] = `Bearer ${Auth.getToken()}`;
    }
    const config = { method, headers };
    if (body) config.body = JSON.stringify(body);

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    config.signal = controller.signal;

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, config);
      // Server errors (502/503) often return HTML, so don't crash on res.json()
      const text = await res.text();
      let data = {};
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        data = { detail: "Server returned an invalid response" };
      }
      return { res, data };
    } catch (err) {
      if (err.name === "AbortError") {
        throw {
          status: 0,
          data: {
            detail: "Server is taking too long. Please try again in a minute.",
          },
        };
      }
      throw { status: 0, data: { detail: "Cannot reach the server." } };
    } finally {
      clearTimeout(timer);
    }
  },

  // Get a new access token using the refresh token (SimpleJWT rotates both).
  // Several requests can fail with 401 at the same time (e.g. the dashboard
  // loads 4 endpoints at once). Because the backend rotates and blacklists
  // refresh tokens, parallel refreshes would log the user out - so all callers
  // share ONE refresh promise.
  _refreshToken() {
    if (this._refreshPromise) return this._refreshPromise;

    this._refreshPromise = (async () => {
      const refresh = Auth.getRefreshToken();
      if (!refresh) return false;
      try {
        const { res, data } = await this._send(
          "/users/token/refresh/",
          "POST",
          { refresh },
          false,
        );
        if (!res.ok || !data.access) return false;
        localStorage.setItem("access_token", data.access);
        if (data.refresh) localStorage.setItem("refresh_token", data.refresh);
        return true;
      } catch {
        return false;
      } finally {
        // Let the next 401 start a fresh attempt
        setTimeout(() => (this._refreshPromise = null), 0);
      }
    })();

    return this._refreshPromise;
  },

  _sessionExpired() {
    Auth.clearAuth();
    showToast("Session expired. Please login again.", "warning");
    setTimeout(() => (window.location.href = "login.html"), 1500);
  },

  async request(endpoint, method = "GET", body = null, auth = true) {
    let { res, data } = await this._send(endpoint, method, body, auth);

    // Access token expired -> refresh once and retry
    if (res.status === 401 && auth && Auth.getRefreshToken()) {
      const refreshed = await this._refreshToken();
      if (refreshed) {
        ({ res, data } = await this._send(endpoint, method, body, auth));
      } else {
        this._sessionExpired();
        throw { status: 401, data: { detail: "Session expired" } };
      }
    }

    if (!res.ok) throw { status: res.status, data };
    return data;
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

  const icons = { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" };
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || ""}</span><span>${esc(message)}</span>`;
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
      const firstName = esc((user?.full_name || "").split(" ")[0]);
      navActions.innerHTML = `
        <a href="cart.html" class="cart-icon">
          🛒 <span class="cart-badge" id="cartCount">0</span>
        </a>
        <div style="display:flex;align-items:center;gap:0.5rem;">
          <span style="font-size:0.9rem;color:var(--text-secondary)">Hi, ${firstName}</span>
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

  // Set active nav link ("/" and "/index.html" are the same page)
  const currentPage = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".navbar-nav a").forEach((link) => {
    if (link.getAttribute("href") === currentPage) {
      link.classList.add("active");
    }
  });
}

// ===== LOGOUT =====
async function logout() {
  const refresh = Auth.getRefreshToken();
  try {
    // Tells the backend to blacklist the refresh token
    if (refresh) await Api.post("/users/logout/", { refresh });
  } catch (e) {
    // Even if the server call fails, clear the browser side
  }
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
    if (badge) {
      const count = cart.total_items || 0;
      badge.textContent = count;
      badge.style.display = count > 0 ? "" : "none";
    }
  } catch (e) {
    // A failed badge update should never break the page
  }
}

// ===== ADD TO CART =====
async function addToCart(foodItemId, name, quantity = 1) {
  if (!Auth.isLoggedIn()) {
    showToast("Please login to add items to cart!", "warning");
    setTimeout(() => (window.location.href = "login.html"), 1500);
    return;
  }
  try {
    await Api.post("/orders/cart/", {
      food_item_id: Number(foodItemId),
      quantity: Number(quantity) || 1,
    });
    showToast(`${name} added to cart! 🛒`);
    updateCartCount();
  } catch (e) {
    showToast(apiErrorMessage(e, "Failed to add item to cart!"), "error");
  }
}

// ===== FORMAT PRICE =====
function formatPrice(price) {
  const value = parseFloat(price);
  return `₹${(isNaN(value) ? 0 : value).toFixed(2)}`;
}

// ===== FORMAT DATE =====
function formatDate(dateStr) {
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return "-";
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
  return map[status] || esc(status);
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
  return map[status] || esc(status);
}

// ===== PROTECT ROUTES =====
// Note: this is only for user experience. Real security is enforced by the
// backend permission classes - never trust the browser for access control.
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    showToast("Please login first!", "warning");
    setTimeout(() => (window.location.href = "login.html"), 1000);
    return false;
  }
  return true;
}

function requireAdmin() {
  if (!requireAuth()) return false;
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
        ${
          item.image
            ? `<img src="${esc(item.image)}" alt="${esc(item.name)}" loading="lazy" style="width:100%;height:100%;object-fit:cover;">`
            : "🍽️"
        }
      </div>
      <div class="food-card-body">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
          <span class="veg-badge ${item.is_veg ? "veg" : "non-veg"}">
            ${item.is_veg ? "🟢 Veg" : "🔴 Non-Veg"}
          </span>
          ${item.status === "rescue" ? '<span class="badge badge-warning">🤝 Rescue</span>' : ""}
        </div>
        <h3 class="food-card-title">${esc(item.name)}</h3>
        <p class="food-card-desc">${esc(item.description)}</p>
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
          <span style="font-size:0.8rem;color:var(--text-muted)">⏱️ ${esc(item.preparation_time)} min</span>
          ${item.calories ? `<span style="font-size:0.8rem;color:var(--text-muted)">🔥 ${esc(item.calories)} cal</span>` : ""}
          <span style="font-size:0.8rem;color:var(--text-muted)">⭐ ${esc(item.rating)}</span>
        </div>
        <div class="food-card-footer">
          <div>
            <span class="food-price">${formatPrice(item.final_price)}</span>
            ${hasDiscount ? `<span class="food-price-original">${formatPrice(item.price)}</span>` : ""}
          </div>
          <button class="btn btn-primary btn-sm"
                  data-name="${esc(item.name)}"
                  onclick="addToCart(${Number(item.id)}, this.dataset.name)">
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
