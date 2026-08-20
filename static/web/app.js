(function () {
    const state = {
        access: localStorage.getItem("cashflow.access"),
        refresh: localStorage.getItem("cashflow.refresh"),
        username: localStorage.getItem("cashflow.username") || "usuario autenticado",
        organizations: [],
        accounts: [],
        categories: [],
        transactions: [],
        selectedOrganizationId: null,
    };

    if (!state.access) {
        window.location.replace("/");
        return;
    }

    const elements = {
        sessionStatus: document.getElementById("session-status"),
        feedback: document.getElementById("global-feedback"),
        logoutButton: document.getElementById("logout-button"),
        organizationSelect: document.getElementById("organization-select"),
        organizationForm: document.getElementById("organization-form"),
        accountForm: document.getElementById("account-form"),
        categoryForm: document.getElementById("category-form"),
        transactionForm: document.getElementById("transaction-form"),
        cashflowForm: document.getElementById("cashflow-form"),
        transactionAccount: document.getElementById("transaction-account"),
        transactionCategory: document.getElementById("transaction-category"),
        accountsList: document.getElementById("accounts-list"),
        categoriesList: document.getElementById("categories-list"),
        transactionsList: document.getElementById("transactions-list"),
        cashflowList: document.getElementById("cashflow-list"),
        organizationCount: document.getElementById("organization-count"),
        accountCount: document.getElementById("account-count"),
        categoryCount: document.getElementById("category-count"),
        transactionCount: document.getElementById("transaction-count"),
    };

    elements.sessionStatus.textContent = "Sessao ativa: " + state.username;

    const setFeedback = (message, tone) => {
        elements.feedback.textContent = message || "";
        elements.feedback.className = "feedback";
        if (tone) {
            elements.feedback.classList.add(tone);
        }
    };

    const clearSession = () => {
        localStorage.removeItem("cashflow.access");
        localStorage.removeItem("cashflow.refresh");
        localStorage.removeItem("cashflow.username");
        window.location.replace("/");
    };

    const formatCurrency = (value) =>
        new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL",
        }).format(Number(value || 0));

    const formatDate = (value) => {
        if (!value) {
            return "-";
        }
        return new Intl.DateTimeFormat("pt-BR").format(new Date(value + "T00:00:00"));
    };

    const apiFetch = async (url, options = {}, retry = true) => {
        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + state.access,
                ...(options.headers || {}),
            },
        });

        if (response.status === 401 && retry && state.refresh) {
            const refreshResponse = await fetch("/api/auth/token/refresh/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ refresh: state.refresh }),
            });

            if (refreshResponse.ok) {
                const refreshData = await refreshResponse.json();
                state.access = refreshData.access;
                localStorage.setItem("cashflow.access", refreshData.access);
                return apiFetch(url, options, false);
            }

            clearSession();
            throw new Error("Sua sessao expirou. Faca login novamente.");
        }

        if (response.status === 204) {
            return null;
        }

        const data = await response.json();
        if (!response.ok) {
            const firstError = typeof data === "object"
                ? Object.values(data).flat().join(" ")
                : null;
            throw new Error(firstError || data.detail || "Nao foi possivel completar a requisicao.");
        }

        return data;
    };

    const requireOrganization = () => {
        if (!state.selectedOrganizationId) {
            throw new Error("Crie ou selecione uma organizacao antes de continuar.");
        }
    };

    const renderOrganizations = () => {
        elements.organizationSelect.innerHTML = "";
        if (!state.organizations.length) {
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "Nenhuma organizacao cadastrada";
            elements.organizationSelect.appendChild(option);
            state.selectedOrganizationId = null;
            return;
        }

        state.organizations.forEach((organization) => {
            const option = document.createElement("option");
            option.value = organization.id;
            option.textContent = organization.name + " (" + organization.currency + ")";
            if (String(organization.id) === String(state.selectedOrganizationId)) {
                option.selected = true;
            }
            elements.organizationSelect.appendChild(option);
        });

        if (!state.selectedOrganizationId) {
            state.selectedOrganizationId = state.organizations[0].id;
            elements.organizationSelect.value = String(state.selectedOrganizationId);
        }
    };

    const renderCollection = (container, items, formatter) => {
        container.innerHTML = "";
        if (!items.length) {
            container.innerHTML = '<div class="empty-state">Nenhum item encontrado.</div>';
            return;
        }
        items.forEach((item) => {
            const node = document.createElement("div");
            node.className = "list-item";
            node.innerHTML = formatter(item);
            container.appendChild(node);
        });
    };

    const renderTransactions = () => {
        if (!state.transactions.length) {
            elements.transactionsList.innerHTML = '<div class="empty-state">Nenhuma transacao cadastrada.</div>';
            return;
        }

        const rows = state.transactions.map((transaction) => `
            <tr>
                <td>${transaction.description || "-"}</td>
                <td>${transaction.kind}</td>
                <td>${transaction.status}</td>
                <td>${transaction.account_detail ? transaction.account_detail.name : transaction.account}</td>
                <td>${formatCurrency(transaction.amount)}</td>
                <td>${formatDate(transaction.competence_date)}</td>
                <td>${formatDate(transaction.payment_date)}</td>
            </tr>
        `).join("");

        elements.transactionsList.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Descricao</th>
                        <th>Tipo</th>
                        <th>Status</th>
                        <th>Conta</th>
                        <th>Valor</th>
                        <th>Competencia</th>
                        <th>Pagamento</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    };

    const renderCashflow = (entries) => {
        if (!entries.length) {
            elements.cashflowList.innerHTML = '<div class="empty-state">Preencha o periodo para ver o resumo.</div>';
            return;
        }

        const rows = entries.map((entry) => `
            <tr>
                <td>${formatDate(entry.date)}</td>
                <td>${formatCurrency(entry.inflow)}</td>
                <td>${formatCurrency(entry.outflow)}</td>
                <td>${formatCurrency(entry.net)}</td>
                <td>${formatCurrency(entry.balance)}</td>
            </tr>
        `).join("");

        elements.cashflowList.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Entrada</th>
                        <th>Saida</th>
                        <th>Liquido</th>
                        <th>Saldo</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    };

    const refreshSelectors = () => {
        elements.transactionAccount.innerHTML = "";
        state.accounts.forEach((account) => {
            const option = document.createElement("option");
            option.value = account.id;
            option.textContent = account.name + " - " + account.type;
            elements.transactionAccount.appendChild(option);
        });

        elements.transactionCategory.innerHTML = '<option value="">Sem categoria</option>';
        state.categories.forEach((category) => {
            const option = document.createElement("option");
            option.value = category.id;
            option.textContent = category.name;
            elements.transactionCategory.appendChild(option);
        });
    };

    const updateCounters = () => {
        elements.organizationCount.textContent = String(state.organizations.length);
        elements.accountCount.textContent = String(state.accounts.length);
        elements.categoryCount.textContent = String(state.categories.length);
        elements.transactionCount.textContent = String(state.transactions.length);
    };

    const loadOrganizations = async () => {
        state.organizations = await apiFetch("/api/organizations/");
        if (
            state.selectedOrganizationId &&
            !state.organizations.some((item) => String(item.id) === String(state.selectedOrganizationId))
        ) {
            state.selectedOrganizationId = null;
        }
        renderOrganizations();
        updateCounters();
    };

    const loadOrganizationData = async () => {
        if (!state.selectedOrganizationId) {
            state.accounts = [];
            state.categories = [];
            state.transactions = [];
            renderCollection(elements.accountsList, [], () => "");
            renderCollection(elements.categoriesList, [], () => "");
            renderTransactions();
            renderCashflow([]);
            updateCounters();
            return;
        }

        const query = "?organization=" + encodeURIComponent(state.selectedOrganizationId);
        const [accounts, categories, transactions] = await Promise.all([
            apiFetch("/api/accounts/" + query),
            apiFetch("/api/categories/" + query),
            apiFetch("/api/transactions/" + query),
        ]);

        state.accounts = accounts;
        state.categories = categories;
        state.transactions = transactions;

        renderCollection(elements.accountsList, state.accounts, (item) => `
            <div>
                <strong>${item.name}</strong>
                <small>${item.type}</small>
            </div>
            <small>${item.description || "Sem descricao"}</small>
        `);

        renderCollection(elements.categoriesList, state.categories, (item) => `
            <div>
                <strong>${item.name}</strong>
            </div>
            <small>${item.description || "Sem descricao"}</small>
        `);

        refreshSelectors();
        renderTransactions();
        updateCounters();
    };

    const bootstrap = async () => {
        try {
            setFeedback("Carregando dados...", "");
            await loadOrganizations();
            await loadOrganizationData();
            renderCashflow([]);
            setFeedback("Painel pronto para uso.", "is-success");
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    };

    elements.logoutButton.addEventListener("click", clearSession);

    elements.organizationSelect.addEventListener("change", async (event) => {
        state.selectedOrganizationId = event.target.value || null;
        try {
            await loadOrganizationData();
            setFeedback("Organizacao alterada.", "is-success");
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    });

    elements.organizationForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(elements.organizationForm);
        const payload = {
            name: formData.get("name"),
            currency: formData.get("currency"),
            timezone: formData.get("timezone"),
        };

        try {
            const created = await apiFetch("/api/organizations/", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            elements.organizationForm.reset();
            elements.organizationForm.currency.value = "BRL";
            elements.organizationForm.timezone.value = "America/Sao_Paulo";
            state.selectedOrganizationId = created.id;
            await loadOrganizations();
            await loadOrganizationData();
            setFeedback("Organizacao criada com sucesso.", "is-success");
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    });

    elements.accountForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            requireOrganization();
            const formData = new FormData(elements.accountForm);
            await apiFetch("/api/accounts/", {
                method: "POST",
                body: JSON.stringify({
                    organization: state.selectedOrganizationId,
                    name: formData.get("name"),
                    description: formData.get("description"),
                    type: formData.get("type"),
                }),
            });
            elements.accountForm.reset();
            await loadOrganizationData();
            setFeedback("Conta criada com sucesso.", "is-success");
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    });

    elements.categoryForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            requireOrganization();
            const formData = new FormData(elements.categoryForm);
            await apiFetch("/api/categories/", {
                method: "POST",
                body: JSON.stringify({
                    organization: state.selectedOrganizationId,
                    name: formData.get("name"),
                    description: formData.get("description"),
                }),
            });
            elements.categoryForm.reset();
            await loadOrganizationData();
            setFeedback("Categoria criada com sucesso.", "is-success");
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    });

    elements.transactionForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            requireOrganization();
            const formData = new FormData(elements.transactionForm);
            await apiFetch("/api/transactions/", {
                method: "POST",
                body: JSON.stringify({
                    organization: state.selectedOrganizationId,
                    account: Number(formData.get("account")),
                    category: formData.get("category") ? Number(formData.get("category")) : null,
                    kind: formData.get("kind"),
                    status: formData.get("status"),
                    amount: formData.get("amount"),
                    competence_date: formData.get("competence_date"),
                    payment_date: formData.get("payment_date") || null,
                    description: formData.get("description"),
                    notes: formData.get("notes"),
                }),
            });
            elements.transactionForm.reset();
            await loadOrganizationData();
            setFeedback("Transacao criada com sucesso.", "is-success");
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    });

    elements.cashflowForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            requireOrganization();
            const formData = new FormData(elements.cashflowForm);
            const query = new URLSearchParams({
                organization: state.selectedOrganizationId,
                start: formData.get("start"),
                end: formData.get("end"),
            });
            const entries = await apiFetch("/api/cashflow/?" + query.toString(), { method: "GET" });
            renderCashflow(entries);
            setFeedback("Resumo de fluxo de caixa atualizado.", "is-success");
        } catch (error) {
            setFeedback(error.message, "is-error");
        }
    });

    const today = new Date();
    const todayString = today.toISOString().slice(0, 10);
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().slice(0, 10);
    elements.cashflowForm.start.value = startOfMonth;
    elements.cashflowForm.end.value = todayString;
    elements.transactionForm.competence_date.value = todayString;

    bootstrap();
})();
