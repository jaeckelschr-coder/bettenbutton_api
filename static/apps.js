// ====== Minimalversion für Login & View-Wechsel ======

let currentUser = null; // { username, role, customerId? }

function showView(viewId) {
    document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
    const view = document.getElementById(viewId);
    if (view) {
        view.classList.add("active");
    } else {
        console.warn("View not found:", viewId);
    }
}

function handleLogin(evt) {
    // Falls das Event von einem Submit kommt, verhindern wir das Neu-Laden der Seite
    if (evt && typeof evt.preventDefault === "function") {
        evt.preventDefault();
    }

    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const error = document.getElementById("login-error");

    if (!usernameInput || !passwordInput) {
        console.error("Login-Felder nicht gefunden");
        return;
    }

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    console.log("Login-Versuch:", username, password); // Debug

    if (username === "admin" && password === "admin") {
        currentUser = { username, role: "admin" };
        error.textContent = "";
        enterAdminView();
    } else if (username === "ti" && password === "ti") {
        currentUser = { username, role: "customer", customerId: 1 };
        error.textContent = "";
        enterCustomerView();
    } else {
        error.textContent = "Benutzername oder Passwort ist ungültig (Demo-Login: admin/admin oder ti/ti).";
    }
}

function enterAdminView() {
    showView("admin-view");
    const u = document.getElementById("admin-username");
    if (u && currentUser) u.textContent = currentUser.username;
}

function enterCustomerView() {
    showView("customer-view");
    const u = document.getElementById("customer-username");
    if (u && currentUser) u.textContent = currentUser.username;
}

function logout() {
    currentUser = null;
    const form = document.getElementById("login-form");
    if (form) form.reset();
    const error = document.getElementById("login-error");
    if (error) error.textContent = "";
    showView("login-view");
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("Betten-Button Minimal-JS geladen");

    const loginButton = document.getElementById("login-button");
    if (loginButton) {
        loginButton.addEventListener("click", handleLogin);
    } else {
        console.error("Login-Button mit id='login-button' nicht gefunden");
    }

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        // Nur zur Sicherheit: auch Submit abfangen
        loginForm.addEventListener("submit", handleLogin);
    }

    const logoutAdmin = document.getElementById("logout-admin");
    if (logoutAdmin) {
        logoutAdmin.addEventListener("click", logout);
    }

    const logoutCustomer = document.getElementById("logout-customer");
    if (logoutCustomer) {
        logoutCustomer.addEventListener("click", logout);
    }

    // Startansicht
    showView("login-view");
});
