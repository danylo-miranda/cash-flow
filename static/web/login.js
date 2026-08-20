(function () {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const feedback = document.getElementById("login-feedback");
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");

    // 1. Redireciona se o usuário já possuir token ativo
    if (localStorage.getItem("cashflow.access")) {
        window.location.replace("/app/");
        return;
    }

    // Função para tratar e formatar erros vindos do Django/DRF
    const parseApiError = (data, defaultMessage) => {
        if (!data) return defaultMessage;
        if (typeof data === "string") return data;
        if (data.detail) return data.detail;
        if (data.error) return data.error;

        // Trata erros de validação por campo (ex: { "email": ["Email já cadastrado"] })
        if (typeof data === "object") {
            const firstKey = Object.keys(data)[0];
            if (firstKey) {
                const val = data[firstKey];
                const msg = Array.isArray(val) ? val[0] : val;
                return `${firstKey}: ${msg}`;
            }
        }
        return defaultMessage;
    };

    // Função de auxílio para mensagens de feedback na tela
    const setFeedback = (message, tone) => {
        if (!feedback) return;
        feedback.textContent = message;
        feedback.className = "feedback";
        if (tone) {
            feedback.classList.add(tone);
        }
    };

    // Processa a resposta HTTP com segurança contra HTML (erros 500/502/Nginx)
    const handleApiResponse = async (response, defaultErrorMsg) => {
        const contentType = response.headers.get("content-type") || "";
        let data = null;

        // Só tenta converter para JSON se o servidor realmente respondeu com JSON
        if (contentType.includes("application/json")) {
            data = await response.json();
        }

        if (!response.ok) {
            if (data) {
                throw new Error(parseApiError(data, defaultErrorMsg));
            }
            // Trata falhas de servidor que retornam HTML (ex: Tela amarela do Django / Erro 500)
            throw new Error(`Erro interno do servidor (${response.status}). Tente novamente mais tarde.`);
        }

        return data;
    };

    // Salva chaves no localStorage e redireciona
    const saveSessionAndRedirect = (access, refresh, username) => {
        if (!access || !refresh) {
            setFeedback("Erro ao processar tokens de acesso. Tente novamente.", "is-error");
            return;
        }

        localStorage.setItem("cashflow.access", access);
        localStorage.setItem("cashflow.refresh", refresh);
        if (username) {
            localStorage.setItem("cashflow.username", username);
        }
        setFeedback("Sessão iniciada com sucesso. Redirecionando...", "is-success");
        window.location.replace("/app/");
    };

    // 2. Alternância de Abas (Entrar / Cadastrar)
    const switchTab = (targetTab) => {
        setFeedback("", "");
        if (targetTab === "login") {
            if (loginForm) loginForm.classList.remove("hidden");
            if (registerForm) registerForm.classList.add("hidden");
            if (tabLogin) tabLogin.classList.add("active");
            if (tabRegister) tabRegister.classList.remove("active");
        } else {
            if (loginForm) loginForm.classList.add("hidden");
            if (registerForm) registerForm.classList.remove("hidden");
            if (tabLogin) tabLogin.classList.remove("active");
            if (tabRegister) tabRegister.classList.add("active");
        }
    };

    if (tabLogin) tabLogin.addEventListener("click", () => switchTab("login"));
    if (tabRegister) tabRegister.addEventListener("click", () => switchTab("register"));

    // 3. Submissão do Formulário de LOGIN
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            setFeedback("Autenticando...", "");

            const formData = new FormData(loginForm);
            const payload = {
                username: formData.get("username") || formData.get("email"),
                password: formData.get("password"),
            };

            try {
                const response = await fetch("/api/auth/token/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });

                const data = await handleApiResponse(response, "Credenciais inválidas. Verifique usuário e senha.");

                const access = data.access || data.tokens?.access;
                const refresh = data.refresh || data.tokens?.refresh;

                saveSessionAndRedirect(access, refresh, payload.username);
            } catch (error) {
                setFeedback(error.message, "is-error");
            }
        });
    }

    // 4. Submissão do Formulário de CADASTRO
    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            setFeedback("Criando sua conta...", "");

            const formData = new FormData(registerForm);
            const payload = {
                name: formData.get("name"),
                email: formData.get("email"),
                password: formData.get("password"),
            };

            try {
                const response = await fetch("/api/auth/register/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });

                const data = await handleApiResponse(response, "Não foi possível concluir o cadastro.");

                const access = data.tokens?.access || data.access;
                const refresh = data.tokens?.refresh || data.refresh;
                const userIdentifier = data.user?.email || payload.email;

                saveSessionAndRedirect(access, refresh, userIdentifier);
            } catch (error) {
                setFeedback(error.message, "is-error");
            }
        });
    }

    // 5. Callback Global para o Google OAuth (SSO)
    window.handleGoogleCredentialResponse = async (googleResponse) => {
        setFeedback("Autenticando com o Google...", "");

        try {
            const response = await fetch("/api/auth/google/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id_token: googleResponse.credential }),
            });

            const data = await handleApiResponse(response, "Falha na autenticação com o Google.");

            const access = data.tokens?.access || data.access;
            const refresh = data.tokens?.refresh || data.refresh;
            const userIdentifier = data.user?.email || "Google User";

            saveSessionAndRedirect(access, refresh, userIdentifier);
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    };
})();