(function () {
    const form = document.getElementById("login-form");
    const feedback = document.getElementById("login-feedback");

    if (!form) {
        return;
    }

    const setFeedback = (message, tone) => {
        feedback.textContent = message;
        feedback.className = "feedback";
        if (tone) {
            feedback.classList.add(tone);
        }
    };

    if (localStorage.getItem("cashflow.access")) {
        window.location.replace("/app/");
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        setFeedback("Autenticando...", "");

        const formData = new FormData(form);
        const payload = {
            username: formData.get("username"),
            password: formData.get("password"),
        };

        try {
            const response = await fetch("/api/auth/token/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            if (!response.ok) {
                const detail = data.detail || "Nao foi possivel autenticar com as credenciais informadas.";
                throw new Error(detail);
            }

            localStorage.setItem("cashflow.access", data.access);
            localStorage.setItem("cashflow.refresh", data.refresh);
            localStorage.setItem("cashflow.username", payload.username);
            setFeedback("Login realizado. Redirecionando...", "is-success");
            window.location.replace("/app/");
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    });
})();
