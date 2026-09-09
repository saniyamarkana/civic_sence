# CivicSense Management System
## System Access Guide & Panel-Wise Credentials

This document provides a clean, panel-wise reference of all login credentials, roles, assigned departments, and access instructions for the **CivicSense** system.

> [!NOTE]
> All credentials operate directly on [`database/static_data.json`](file:///c:/xampp/htdocs/KJU/civic_sence/database/static_data.json). Passwords can be entered as plain text (`admin123`, `citizen123`, `dept123`).

---

## 1. How to Launch and Access the Panels

### A. Web Application (Flask / Browser)
If the web server is already running, open your web browser and visit:
```
http://127.0.0.1:5000
```
*(If you need to start or restart the server, run: `py app.py` or `python app.py` in your terminal)*

### B. Desktop Application (CustomTkinter GUI)
To launch the desktop interface, use the Python launcher `py`:
```powershell
py main.py
```
*(Or use your virtual environment: `.venv\Scripts\python main.py`)*

---

## 2. Panel-Wise Credentials

### 🛡️ 1. Administrator Panel
**Access URL (Web):** `http://127.0.0.1:5000/admin`  
**Description:** Full access to manage users, inspect and resolve all complaints across all municipal departments, view the **Binary Tree Civic Governance Hierarchy**, search complaints via **Binary Search Tree (BST)** in $O(\log n)$, and view system analytics.

| Attribute | Details |
| :--- | :--- |
| **Role** | System Administrator (`admin`) |
| **Email** | `admin@civicsense.com` |
| **Password** | `admin123` |
| **Account Name** | Municipal Administrator |
| **Phone** | `9999988888` |
| **Address** | Municipal Corporation Central HQ, New Delhi |
| **Permissions** | Full CRUD on Users & Complaints, Officer Assignment, Analytics |

---

### 👤 2. Citizen Panel
**Access URL (Web):** `http://127.0.0.1:5000/citizen`  
**Description:** Citizens can file civic complaints with automated **Infix-to-Postfix urgency score calculation**, preview **BFS shortest-path vehicle routing**, browse their complaints sequentially via **Singly Linked List**, and submit star ratings and feedback.

#### Primary Citizen Account (Pre-populated with active complaints):
| Attribute | Details |
| :--- | :--- |
| **Role** | Citizen (`citizen`) |
| **Email** | `citizen@civicsense.com` |
| **Password** | `citizen123` |
| **Account Name** | Rahul Sharma |
| **Phone** | `9876543210` |
| **Address** | Flat 402, Sunshine Heights, Sector 4, Civil Lines |
| **Linked Complaints** | 6 active tickets (Garbage, Potholes, Water Leakage, etc.) |

#### Additional Citizen Accounts:
| Name | Email | Password | Phone | Location |
| :--- | :--- | :--- | :--- | :--- |
| **Priya Patel** | `priya@example.com` | `citizen123` | `9876543211` | B-12, Green Park Avenue, Market Area |
| **Amit Kumar** | `amit@example.com` | `citizen123` | `9876543212` | House 55, East Industrial Area |

---

### 🏢 3. Department Panels (Municipal Officers)
**Access URL (Web):** `http://127.0.0.1:5000/department`  
**Description:** Department officers log in to manage tickets assigned specifically to their sector. Complaints are automatically ordered using an **Emergency Priority Queue (Max-Heap)** so high-severity civic hazards appear first. Status updates feature an **Action Stack (LIFO Undo)** mechanism to instantly roll back errors.

#### All 5 Department Officer Credentials:

| Department | Officer Name | Email | Password | Contact Phone | Assigned Zonal Office |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sanitation Department** | Officer Suresh Verma | `sanitation@civicsense.com` | `dept123` | `9811122233` | Sanitation Zonal Office, North Suburb |
| **Road Department** | Officer Anil Kapoor | `road@civicsense.com` | `dept123` | `9822233344` | Roads & Infrastructure Depot, Central Hub |
| **Water Department** | Officer Ramesh Rao | `water@civicsense.com` | `dept123` | `9833344455` | Water Works & Sewage Division, South Suburb |
| **Electricity Department** | Officer Neha Sharma | `electric@civicsense.com` | `dept123` | `9844455566` | Municipal Power & Lighting Office, Downtown |
| **Traffic Department** | Officer Vikram Singh | `traffic@civicsense.com` | `dept123` | `9855566677` | Traffic Police Enforcement HQ, Railway Station |

---

## 3. Quick Reference Matrix

```text
========================================================================================================
PANEL               EMAIL                     PASSWORD       ROLE         PRIMARY FEATURE
========================================================================================================
Admin               admin@civicsense.com      admin123       admin        User & Complaint CRUD, BST, Hierarchy
Citizen             citizen@civicsense.com    citizen123     citizen      File Complaint, Infix/Postfix, Linked List
Citizen (Alt 1)     priya@example.com         citizen123     citizen      File Complaint, Feedback
Citizen (Alt 2)     amit@example.com          citizen123     citizen      File Complaint, Feedback
Sanitation Dept     sanitation@civicsense.com dept123        department   Priority Queue, Waste Management, Undo
Road Dept           road@civicsense.com       dept123        department   Potholes & Pavement Repair, Undo
Water Dept          water@civicsense.com      dept123        department   Pipeline & Drainage Management, Undo
Electricity Dept    electric@civicsense.com   dept123        department   Streetlights & Transformer Issues, Undo
Traffic Dept        traffic@civicsense.com    dept123        department   Traffic Congestion & Obstruction, Undo
========================================================================================================
```

---

## 4. Troubleshooting & Notes

- **"Python was not found" error**:
  In Windows, the Python executable is commonly aliased to `py`.
  - Instead of `python main.py`, run: **`py main.py`**
  - Or run through your virtual environment: **`.venv\Scripts\python main.py`**
- **Data Persistence**:
  Any edits made in the application (adding complaints, changing status, deleting users) are automatically written to [`database/static_data.json`](file:///c:/xampp/htdocs/KJU/civic_sence/database/static_data.json) in real time.
