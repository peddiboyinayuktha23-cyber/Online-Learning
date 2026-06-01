(function () {
    "use strict";

    const root = document.documentElement;
    const loader = document.getElementById("pageLoader");
    const navbar = document.querySelector(".app-navbar");
    const backToTop = document.querySelector(".back-to-top");

    window.addEventListener("load", () => {
        loader?.classList.add("loaded");
        if (window.AOS) {
            AOS.init({ duration: 700, easing: "ease-out-cubic", once: true, offset: 80 });
        }
    });

    const savedTheme = localStorage.getItem("learnhub-theme");
    if (savedTheme) root.setAttribute("data-theme", savedTheme);

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
        const syncIcon = () => {
            const isDark = root.getAttribute("data-theme") === "dark";
            button.innerHTML = isDark ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
        };
        syncIcon();
        button.addEventListener("click", () => {
            const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
            root.setAttribute("data-theme", next);
            localStorage.setItem("learnhub-theme", next);
            syncIcon();
            showToast(next === "dark" ? "Dark mode enabled" : "Light mode enabled");
        });
    });

    window.addEventListener("scroll", () => {
        const active = window.scrollY > 20;
        navbar?.classList.toggle("is-scrolled", active);
        backToTop?.classList.toggle("show", window.scrollY > 500);
    }, { passive: true });

    backToTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

    document.querySelectorAll(".needs-validation").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showToast("Please check the highlighted fields.", "warning");
            } else if (!form.hasAttribute("method") || form.getAttribute("method")?.toLowerCase() !== "post") {
                event.preventDefault();
                showToast("Success! Your request was received.", "success");
            }
            form.classList.add("was-validated");
        });
    });

    document.querySelectorAll(".password-toggle").forEach((toggle) => {
        toggle.addEventListener("click", () => {
            const input = toggle.parentElement?.querySelector(".password-field");
            if (!input) return;
            input.type = input.type === "password" ? "text" : "password";
            toggle.innerHTML = input.type === "password" ? '<i class="fa-regular fa-eye"></i>' : '<i class="fa-regular fa-eye-slash"></i>';
        });
    });

    document.querySelectorAll(".strength-input").forEach((input) => {
        input.addEventListener("input", () => {
            const meter = input.closest("form")?.querySelector(".password-meter span");
            if (!meter) return;
            const value = input.value;
            let score = 0;
            if (value.length >= 8) score += 25;
            if (/[A-Z]/.test(value)) score += 25;
            if (/[0-9]/.test(value)) score += 25;
            if (/[^A-Za-z0-9]/.test(value)) score += 25;
            meter.style.width = `${score}%`;
            meter.style.background = score < 50 ? "#60a5fa" : score < 75 ? "#38bdf8" : "#2563eb";
        });
    });

    document.querySelectorAll(".otp-grid input").forEach((input, index, inputs) => {
        input.addEventListener("input", () => {
            input.value = input.value.replace(/\D/g, "");
            if (input.value && inputs[index + 1]) inputs[index + 1].focus();
        });
        input.addEventListener("keydown", (event) => {
            if (event.key === "Backspace" && !input.value && inputs[index - 1]) inputs[index - 1].focus();
        });
    });

    const filterButtons = document.querySelectorAll("[data-filter]");
    const courseCards = document.querySelectorAll(".course-card");
    const courseSearch = document.getElementById("courseSearch");

    function filterCourses() {
        const activeFilter = document.querySelector("[data-filter].active")?.dataset.filter || "all";
        const query = (courseSearch?.value || "").trim().toLowerCase();
        courseCards.forEach((card) => {
            const categoryMatch = activeFilter === "all" || card.dataset.category === activeFilter;
            const titleMatch = !query || card.dataset.title?.includes(query);
            card.closest("[class*='col-']").style.display = categoryMatch && titleMatch ? "" : "none";
        });
    }

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            filterButtons.forEach((item) => item.classList.remove("active"));
            button.classList.add("active");
            filterCourses();
        });
    });
    courseSearch?.addEventListener("input", filterCourses);

    const counters = document.querySelectorAll("[data-counter]");
    if ("IntersectionObserver" in window && counters.length) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                const target = entry.target;
                const finalValue = Number(target.dataset.counter || 0);
                const duration = 1200;
                const start = performance.now();
                const tick = (now) => {
                    const progress = Math.min((now - start) / duration, 1);
                    target.textContent = Math.floor(finalValue * progress).toLocaleString();
                    if (progress < 1) requestAnimationFrame(tick);
                };
                requestAnimationFrame(tick);
                observer.unobserve(target);
            });
        }, { threshold: .35 });
        counters.forEach((counter) => observer.observe(counter));
    }

    document.querySelectorAll(".typed-text").forEach((target) => {
        let words = [];
        try { words = JSON.parse(target.dataset.typed || "[]"); } catch (error) { words = []; }
        if (!words.length) return;
        let wordIndex = 0;
        let charIndex = 0;
        let deleting = false;
        const type = () => {
            const word = words[wordIndex];
            target.textContent = word.slice(0, charIndex);
            if (!deleting && charIndex < word.length) charIndex += 1;
            else if (deleting && charIndex > 0) charIndex -= 1;
            else {
                deleting = !deleting;
                if (!deleting) wordIndex = (wordIndex + 1) % words.length;
            }
            setTimeout(type, deleting ? 45 : 85);
        };
        type();
    });

    document.addEventListener("click", (event) => {
        const button = event.target.closest(".btn");
        if (!button) return;
        const ripple = document.createElement("span");
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        ripple.style.cssText = `position:absolute;width:${size}px;height:${size}px;left:${event.clientX - rect.left - size / 2}px;top:${event.clientY - rect.top - size / 2}px;background:rgba(255,255,255,.35);border-radius:50%;transform:scale(0);animation:ripple .55s ease-out;pointer-events:none;`;
        button.style.position = "relative";
        button.style.overflow = "hidden";
        button.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    });

    const style = document.createElement("style");
    style.textContent = "@keyframes ripple{to{transform:scale(2.6);opacity:0}}";
    document.head.appendChild(style);

    function showToast(message, type = "info") {
        const container = getToastContainer();
        const toast = document.createElement("div");
        const palette = { success: "text-bg-success", warning: "text-bg-warning", info: "text-bg-dark" };
        toast.className = `toast align-items-center ${palette[type] || palette.info} border-0 show`;
        toast.setAttribute("role", "status");
        toast.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3200);
    }

    function getToastContainer() {
        let container = document.querySelector(".client-toast-zone");
        if (!container) {
            container = document.createElement("div");
            container.className = "client-toast-zone toast-container position-fixed top-0 end-0 p-3";
            container.style.zIndex = "2200";
            document.body.appendChild(container);
        }
        return container;
    }
})();
