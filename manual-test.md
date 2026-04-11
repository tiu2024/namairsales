# Manual Test Checklist

Base URL: `http://127.0.0.1:8000`

## Auth

| URL | Expected |
|---|---|
| `http://127.0.0.1:8000/` | Not logged in → redirect to login |
| `http://127.0.0.1:8000/` | Logged in → redirect to /sotuvlar/ |
| `http://127.0.0.1:8000/accounts/login/` | Show login form |
| `http://127.0.0.1:8000/accounts/login/` | Wrong credentials → error banner |
| `http://127.0.0.1:8000/accounts/logout/` | Logs out → redirect to login |

## Sales

| URL | Expected |
|---|---|
| `http://127.0.0.1:8000/sotuvlar/` | Salesman's own sales list |
| `http://127.0.0.1:8000/sotuvlar/yangi/` | Load sale form via HTMX (redirects if direct) |
| `http://127.0.0.1:8000/sotuvlar/qoshish/` | Submit sale form via HTMX POST (redirects if direct) |

## Suppliers (Accountant only)

| URL | Expected |
|---|---|
| `http://127.0.0.1:8000/yetkazib-beruvchilar/` | Accountant → supplier list with balances |
| `http://127.0.0.1:8000/yetkazib-beruvchilar/` | Salesman → 403 Forbidden |
| `http://127.0.0.1:8000/yetkazib-beruvchilar/` | Not logged in → redirect to login |
| `http://127.0.0.1:8000/yetkazib-beruvchilar/` | POST valid form → creates supplier, redirects back |
| `http://127.0.0.1:8000/yetkazib-beruvchilar/1/` | Supplier detail: debt summary + acquisitions table |
| `http://127.0.0.1:8000/yetkazib-beruvchilar/1/?type=TICKET` | Filtered to Aviabilet only |
| `http://127.0.0.1:8000/yetkazib-beruvchilar/1/?type=UMRA` | Filtered to Umra only |
| `http://127.0.0.1:8000/yetkazib-beruvchilar/1/?type=TOUR` | Filtered to Turi only |
