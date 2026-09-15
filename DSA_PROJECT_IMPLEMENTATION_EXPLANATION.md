# CivicSense Management System
## DSA Architecture & Project Integration Manual (Phase 1 & Phase 2)

This document provides a comprehensive, file-by-file and line-by-line explanation of where and how all **Phase 1** and **Phase 2 (CLO2)** Data Structures and Algorithms are directly embedded, executed, and utilized throughout the **CivicSense** project.

> [!NOTE]
> None of these concepts are kept as isolated toy exercises. They are directly wired into the core operational workflows of Citizens, Administrators, Department Officers, and Database Managers across both the **Desktop GUI (CustomTkinter)** and the **Web Application (Flask / REST APIs)**.

---

## Quick Reference Summary Table

| DSA Concept | Category / Phase | Primary File(s) | Exact Line Numbers | Functional Role in CivicSense |
| :--- | :--- | :--- | :--- | :--- |
| **Singly Linked List (`ComplaintLinkedList`)** | Phase 1 (Linear) | [`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py)<br>[`citizen/my_complaints.py`](file:///c:/xampp/htdocs/KJU/civic_sence/citizen/my_complaints.py) | `database.py:1228-1271`<br>`my_complaints.py:100-120` | Stores and traverses sequential citizen ticket timelines and audit event logs node-by-node ($O(1)$ head prepend). |
| **LIFO Stack (`ActionStack`)** | Phase 1 (Linear) | [`admin/manage_complaints.py`](file:///c:/xampp/htdocs/KJU/civic_sence/admin/manage_complaints.py)<br>[`department/update_status.py`](file:///c:/xampp/htdocs/KJU/civic_sence/department/update_status.py)<br>[`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py) | `manage_complaints.py:290-305, 324-345`<br>`update_status.py:118-130, 151-170`<br>`database.py:1273-1297` | Operational **Undo Mechanism**: Pushes previous ticket states before edits. Clicking "↩️ Undo" pops the last state and reverts changes in the database. |
| **FIFO Queue (`ComplaintQueue`)** | Phase 1 (Linear) | [`citizen/submit_complaint.py`](file:///c:/xampp/htdocs/KJU/civic_sence/citizen/submit_complaint.py)<br>[`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py)<br>[`app.py`](file:///c:/xampp/htdocs/KJU/civic_sence/app.py) | `submit_complaint.py:56, 348`<br>`database.py:1299-1320`<br>`app.py:81, 347, 670-698` | Standard first-come, first-served complaint triage and routine municipal task dispatch. |
| **Emergency Priority Queue (`EmergencyPriorityQueue`)** | Phase 1 (Linear) | [`department/assigned_complaints.py`](file:///c:/xampp/htdocs/KJU/civic_sence/department/assigned_complaints.py)<br>[`citizen/submit_complaint.py`](file:///c:/xampp/htdocs/KJU/civic_sence/citizen/submit_complaint.py)<br>[`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py) | `assigned_complaints.py:48, 126-146`<br>`submit_complaint.py:57, 350`<br>`database.py:1322-1354` | Max-Priority dispatch: High-severity complaints (hazardous gas, water main bursts) bypass the standard queue and appear at the top of officer workloads. |
| **Infix to Postfix & Stack Evaluation** | Phase 1 (Expressions) | [`citizen/submit_complaint.py`](file:///c:/xampp/htdocs/KJU/civic_sence/citizen/submit_complaint.py)<br>[`app.py`](file:///c:/xampp/htdocs/KJU/civic_sence/app.py) | `submit_complaint.py:257-310`<br>`app.py:96-115, 330-336, 779-802` | Converts formula `(priority * 3 + category * 2) / 5` from Infix to Postfix using Shunting-Yard and evaluates with an operand stack to score ticket urgency. |
| **Iterative Search & Sort** | Phase 1 (Algorithms) | [`admin/manage_users.py`](file:///c:/xampp/htdocs/KJU/civic_sence/admin/manage_users.py)<br>[`admin/manage_complaints.py`](file:///c:/xampp/htdocs/KJU/civic_sence/admin/manage_complaints.py) | `manage_users.py:102-126, 137-145`<br>`manage_complaints.py:126-136, 172` | Iterative Selection Sort & Iterative Binary Search ($O(\log n)$) to locate user records; Iterative Insertion Sort to sort complaint tables by ID/date. |
| **Recursive Algorithms** | Phase 1 (Recursion) | [`admin/dashboard.py`](file:///c:/xampp/htdocs/KJU/civic_sence/admin/dashboard.py)<br>[`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py) | `dashboard.py:228-234`<br>`database.py:1438-1449` | Recursive bottom-up rollup calculating aggregate complaint cases across nested departmental directorates and leaf departments. |
| **1. Binary Tree (Hierarchical Representation)** | Phase 2 (CLO2) | [`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py)<br>[`admin/dashboard.py`](file:///c:/xampp/htdocs/KJU/civic_sence/admin/dashboard.py)<br>[`app.py`](file:///c:/xampp/htdocs/KJU/civic_sence/app.py) | `database.py:1172-1199, 1356-1372`<br>`dashboard.py:236-295`<br>`app.py:851-876` | Models the Municipal Administrative Governance Hierarchy: Root is Municipal Commissioner; Left subtree is Infrastructure Directorate; Right subtree is Public Health Directorate. |
| **2. Tree Traversals (Pre/In/Post-Order)** | Phase 2 (CLO2) | [`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py)<br>[`admin/dashboard.py`](file:///c:/xampp/htdocs/KJU/civic_sence/admin/dashboard.py)<br>[`app.py`](file:///c:/xampp/htdocs/KJU/civic_sence/app.py) | `database.py:1374-1436`<br>`dashboard.py:265-290`<br>`app.py:851-876` | **Pre-Order**: Top-down executive delegation sequence.<br>**In-Order**: Symmetrical departmental audit.<br>**Post-Order**: Bottom-up caseload and budget rollup. |
| **3. Binary Search Tree (BST Storage & Search)** | Phase 2 (CLO2) | [`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py)<br>[`admin/manage_complaints.py`](file:///c:/xampp/htdocs/KJU/civic_sence/admin/manage_complaints.py)<br>[`app.py`](file:///c:/xampp/htdocs/KJU/civic_sence/app.py) | `database.py:1154-1161, 1451-1532`<br>`manage_complaints.py:47, 85, 142-155`<br>`app.py:829-849` | Indexes complaints in a BST keyed by ID. Provides $O(\log n)$ instant ticket retrieval without linear table scans, plus ordered in-order sequence extraction. |
| **4. Graph Representation (Adjacency List)** | Phase 2 (CLO2) | [`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py)<br>[`citizen/submit_complaint.py`](file:///c:/xampp/htdocs/KJU/civic_sence/citizen/submit_complaint.py)<br>[`department/assigned_complaints.py`](file:///c:/xampp/htdocs/KJU/civic_sence/department/assigned_complaints.py)<br>[`app.py`](file:///c:/xampp/htdocs/KJU/civic_sence/app.py) | `database.py:1201-1221, 1534-1552`<br>`submit_complaint.py:60, 321-325`<br>`assigned_complaints.py:49, 164-172`<br>`app.py:878-896` | Models city wards/zones network as an **Adjacency List** mapping municipal centers (`Central Depot`, `Ward 1 - Downtown`, `Ward 2 - Civil Lines`, etc.) with transit distances. |
| **5. Graph Traversal (BFS & DFS)** | Phase 2 (CLO2) | [`database/database.py`](file:///c:/xampp/htdocs/KJU/civic_sence/database/database.py)<br>[`department/assigned_complaints.py`](file:///c:/xampp/htdocs/KJU/civic_sence/department/assigned_complaints.py)<br>[`citizen/submit_complaint.py`](file:///c:/xampp/htdocs/KJU/civic_sence/citizen/submit_complaint.py)<br>[`app.py`](file:///c:/xampp/htdocs/KJU/civic_sence/app.py) | `database.py:1554-1596`<br>`assigned_complaints.py:164-172`<br>`submit_complaint.py:322-328`<br>`app.py:878-896` | **BFS (Breadth-First Search)**: Finds shortest vehicle dispatch path from Depot to incident location.<br>**DFS (Depth-First Search)**: Explores full sanitary inspection coverage across connected municipal zones. |

---

## Detailed File-by-File Explanations

### 1. `database/database.py` & `database/__init__.py`
- **Location in Code**:
  - `database.py:1154-1221` (Database Helper Methods)
  - `database.py:1228-1354` (Phase 1 Linear Structures: `ComplaintNode`, `ComplaintLinkedList`, `ActionStack`, `ComplaintQueue`, `EmergencyPriorityQueue`)
  - `database.py:1356-1449` (Phase 2 Item 1 & 2: `TreeNode`, `CivicHierarchyTree`, Traversals & Recursive Rollup)
  - `database.py:1451-1532` (Phase 2 Item 3: `BSTNode`, `ComplaintBST` with $O(\log n)$ Search & Insertion)
  - `database.py:1534-1596` (Phase 2 Item 4 & 5: `MunicipalWardGraph` Adjacency List, BFS Shortest Path, DFS Coverage)
- **Description**:
  The central database manager encapsulates both relational persistence (SQLite/MySQL) and live in-memory algorithmic indices. Any component calling `self.db.get_complaints_bst()` gets an instant BST of complaints, while `self.db.get_department_hierarchy_tree()` builds the binary governance tree with live caseload numbers.

---

### 2. `citizen/submit_complaint.py`
- **Location in Code**:
  - `submit_complaint.py:56-60`: Initializes in-memory `ComplaintQueue`, `EmergencyPriorityQueue`, `ActionStack`, `ComplaintLinkedList`, and `MunicipalWardGraph`.
  - `submit_complaint.py:257-310` (`_calc_urgency_infix_postfix`): **Phase 1 Infix to Postfix Conversion & Stack Evaluation**. Converts token stream `['(', p_val, '*', '3', '+', c_val, '*', '2', ')', '/', '5']` to postfix notation via Shunting-Yard using an operator stack, then evaluates it using an operand stack.
  - `submit_complaint.py:313-333` (`_update_preview`): Calls `_calc_urgency_infix_postfix` and uses `self.ward_graph.bfs_shortest_path` (**Phase 2 BFS Traversal**) to calculate and display the live emergency response route in the ticket preview.
  - `submit_complaint.py:335-375` (`_submit_complaint`):
    - Inserts ticket into database.
    - Enqueues record into FIFO `self.live_queue` (**Phase 1 FIFO Queue**).
    - Enqueues record into `self.priority_queue` with urgency score (**Phase 1 Priority Queue**).
    - Prepends into `self.live_ll` (**Phase 1 Singly Linked List**).
    - Pushes submission action to `self.live_stack` (**Phase 1 LIFO Stack**).

---

### 3. `citizen/my_complaints.py`
- **Location in Code**:
  - `my_complaints.py:45, 83`: Instantiates `ComplaintLinkedList` and creates the `🔗 Linked List Chain` status badge.
  - `my_complaints.py:100-120` (`load_complaints`):
    - Retrieves the citizen's complaints as a `ComplaintLinkedList` using `self.db.get_complaint_linked_list()`.
    - Traverses node-by-node starting from `curr_node = self.complaints_ll.head` and advancing via `curr_node = curr_node.next`.
    - Renders the complaint cards directly from the linked list traversal and updates the node count badge.

---

### 4. `admin/manage_complaints.py`
- **Location in Code**:
  - `manage_complaints.py:46-47`: Initializes `self.undo_stack = ActionStack(max_size=30)` and `self.complaint_bst`.
  - `manage_complaints.py:83-93`: Renders the `↩️ Undo (Stack: 0)` button and `🌳 BST Index: Active` badge.
  - `manage_complaints.py:126-136` (`_iterative_insertion_sort`): **Phase 1 Iterative Insertion Sort**. Sorts complaint records by ID or priority in-place.
  - `manage_complaints.py:138-165` (`load_complaints`):
    - Builds `self.complaint_bst` (**Phase 2 BST**).
    - If the administrator searches for an ID (e.g. `#14` or `14`), executes `self.complaint_bst.search(cid)` in **$O(\log n)$ average time** instead of scanning the full list.
    - Applies `_iterative_insertion_sort` to arrange the complaints table.
  - `manage_complaints.py:290-305` (`save_changes`): Pushes previous status, department, and priority to `self.undo_stack` before updating the database.
  - `manage_complaints.py:324-345` (`_undo_last_action`): **Phase 1 LIFO Stack Undo**. Pops the last action from `self.undo_stack` and restores the previous complaint state in the database.

---

### 5. `admin/manage_users.py`
- **Location in Code**:
  - `manage_users.py:75-80`: Adds the `⚡ Iterative Binary Search: Active` indicator badge.
  - `manage_users.py:102-112` (`_iterative_sort_users`): **Phase 1 Iterative Selection Sort**. Sorts user dictionaries by ID.
  - `manage_users.py:114-127` (`_iterative_binary_search_users`): **Phase 1 Iterative Binary Search ($O(\log n)$)**. Finds user records in $O(\log n)$ time by repeatedly halving `[low, high]`.
  - `manage_users.py:138-146`: When searching by numeric user ID, sorts users and invokes `_iterative_binary_search_users` with instant lookup feedback.

---

### 6. `admin/dashboard.py`
- **Location in Code**:
  - `dashboard.py:111-113`: Mounts the dedicated Municipal Governance Binary Tree card.
  - `dashboard.py:228-234` (`_recursive_tree_rollup`): **Phase 1 Recursive Algorithm**. Traverses subtrees recursively (`left_cnt + right_cnt + cases`) to calculate aggregate municipal caseloads.
  - `dashboard.py:236-295` (`_render_hierarchy_binary_tree_card`):
    - **Phase 2 Item 1 (Binary Tree Representation)**: Fetches and displays the administrative hierarchy (`tree = self.db.get_department_hierarchy_tree()`).
    - **Phase 2 Item 2 (Basic Tree Traversals)**: Provides interactive buttons to inspect:
      1. **Pre-Order Traversal** (`tree.preorder_traversal()`): Executive delegation order (Root $\rightarrow$ Left $\rightarrow$ Right).
      2. **In-Order Traversal** (`tree.inorder_traversal()`): Symmetrical audit order (Left $\rightarrow$ Root $\rightarrow$ Right).
      3. **Post-Order Traversal** (`tree.postorder_traversal()`): Bottom-up workload rollup order (Left $\rightarrow$ Right $\rightarrow$ Root).

---

### 7. `department/assigned_complaints.py`
- **Location in Code**:
  - `assigned_complaints.py:48-49`: Initializes `self.p_queue = EmergencyPriorityQueue()` (**Phase 1**) and `self.ward_graph = self.db.get_municipal_ward_graph()` (**Phase 2 Adjacency List**).
  - `assigned_complaints.py:126-146` (`load_complaints`):
    - Evaluates priority scores (`High=10, Medium=5, Low=1`).
    - Enqueues complaints into `EmergencyPriorityQueue`.
    - Dequeues complaints in strict priority order so urgent hazards are prioritized at the top of the officer's work queue.
  - `assigned_complaints.py:164-172`: **Phase 2 Item 5 (BFS Traversal)**. Runs `self.ward_graph.bfs_shortest_path("Central Depot", target_ward)` to automatically render the shortest transit dispatch route for municipal service vehicles.

---

### 8. `department/update_status.py`
- **Location in Code**:
  - `update_status.py:30`: Initializes `self.undo_stack = ActionStack(max_size=20)` (**Phase 1 LIFO Stack**).
  - `update_status.py:102-107`: Mounts the `↩️ Undo Status (Stack: 0)` button.
  - `update_status.py:118-130` (`_save_update`): Fetches the current complaint state and pushes `{id, old_status, old_remarks}` onto `self.undo_stack` before applying the update.
  - `update_status.py:151-170` (`_undo_last_status`): **Phase 1 LIFO Stack Undo**. Pops the last update and reverts the complaint back to its previous status in the database.

---

### 9. `app.py` (Flask Web Application & APIs)
- **Location in Code**:
  - `app.py:81-84`: Initializes global in-memory `Queue`, `PriorityQueue`, `Stack`, and `LinkedList`.
  - `app.py:96-115, 330-336, 427-435`: Infix-to-Postfix Stack Urgency Score Evaluation executed on every complaint creation and status update.
  - `app.py:346-350`: Adds submitted complaints to `live_ll` (Linked List), `live_queue` (FIFO), `live_p_queue` (Priority Queue), and `live_stack` (Stack).
  - `app.py:829-840`: **Phase 2 Item 3 BST Search API** (`GET /api/dsa/bst/search/<cid>`) executing $O(\log n)$ binary tree search.
  - `app.py:841-850`: **Phase 2 Item 3 BST In-Order API** (`GET /api/dsa/bst/inorder`) returning complaints in sorted order.
  - `app.py:851-877`: **Phase 2 Items 1 & 2 Binary Tree Hierarchy API** (`GET /api/dsa/tree/hierarchy?traversal=preorder|inorder|postorder`).
  - `app.py:878-897`: **Phase 2 Items 4 & 5 Graph Adjacency List & BFS/DFS Route API** (`GET /api/dsa/graph/route?destination=...`).
  - `app.py:898-912`: **Phase 1 Stack Undo API** (`POST /api/dsa/stack/undo`).

---

### 9. Dedicated Basic Reference Implementations in `dsa/` Folder
For modular study, standalone execution, and curriculum submission, clean standalone Python reference files are also provided inside the [`dsa/`](file:///c:/xampp/htdocs/KJU/civic_sence/dsa) directory:

1. **[`dsa/binary_tree.py`](file:///c:/xampp/htdocs/KJU/civic_sence/dsa/binary_tree.py)**:
   - `TreeNode` & `BinaryTree` classes for hierarchical data representation.
   - Basic Tree Traversals: `preorder()`, `inorder()`, `postorder()`, and `level_order()` (BFS).
   - Tree metrics: `height()`, `count_nodes()`, and `total_caseload()`.
   - `build_sample_hierarchy()` with complete executable test script (`__main__`).
2. **[`dsa/binary_search_tree.py`](file:///c:/xampp/htdocs/KJU/civic_sence/dsa/binary_search_tree.py)**:
   - `BSTNode` & `BinarySearchTree` classes for efficient $O(\log n)$ data storage and retrieval.
   - Operations: `insert()`, `search()`, `inorder()` (sorted output), `find_min()`, `find_max()`, and `delete()`.
   - `build_sample_bst()` with complete executable test script (`__main__`).
3. **[`dsa/graph.py`](file:///c:/xampp/htdocs/KJU/civic_sence/dsa/graph.py)**:
   - `Graph` class with Adjacency List representation (`self.adj_list`).
   - Traversal methods: `bfs()` (queue-based) and `dfs()` (recursive/stack-based).
   - Application: `bfs_shortest_path()` for vehicle and dispatch routing.
   - `build_sample_ward_graph()` with complete executable test script (`__main__`).

---

## Conclusion & Verification
All Phase 1 linear structures and Phase 2 structured representations are fully provided both as standalone modules in `dsa/` and directly integrated into real application workflows (`database/`, `admin/`, `department/`, `citizen/`, and `app.py`). Every algorithm solves a tangible problem in the civic complaint management lifecycle:
- Hierarchical administrative delegation (Binary Tree)
- Dynamic auditing & aggregation (Tree Traversals)
- High-efficiency ticket indexing & $O(\log n)$ retrieval (Binary Search Tree)
- Municipal ward connectivity (Graph Adjacency List)
- Service vehicle dispatch routing (Breadth-First Search)

