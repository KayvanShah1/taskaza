import pytest
from utils import _signup_and_login


@pytest.mark.asyncio
async def test_create_and_list_with_tree(async_client):
    headers = await _signup_and_login(async_client, "treeuser", "pw")

    # Create a task with nested subtasks (create_subtree defaults to True)
    payload = {
        "title": "Parent",
        "description": "root",
        "status": "todo",
        "subtasks": [
            {"title": "Child 1", "status": "in_progress"},
            {"title": "Child 2", "status": "todo"},
        ],
    }
    r = await async_client.post("/tasks", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    root = r.json()
    assert root["title"] == "Parent"

    # List with include_tree to hydrate subtasks
    r = await async_client.get("/tasks?include_tree=true", headers=headers)
    assert r.status_code == 200
    items = r.json()
    parent = next(x for x in items if x["id"] == root["id"])
    assert parent.get("subtasks") and len(parent["subtasks"]) == 2

    # roots_only should only return parents (no children as top-level)
    r = await async_client.get("/tasks?roots_only=true", headers=headers)
    assert r.status_code == 200
    roots = r.json()
    assert all(t.get("parent_id") is None for t in roots)


@pytest.mark.asyncio
async def test_read_with_include_tree_and_then_update_child_status(async_client):
    headers = await _signup_and_login(async_client, "treeuser2", "pw")

    # Create root with two levels of nesting to ensure recursion works
    payload = {
        "title": "Root",
        "status": "todo",
        "subtasks": [
            {"title": "L1-A", "status": "todo", "subtasks": [{"title": "L2-A1", "status": "todo"}]},
            {"title": "L1-B", "status": "in_progress"},
        ],
    }
    r = await async_client.post("/tasks", json=payload, headers=headers)
    assert r.status_code == 201
    root = r.json()

    # Read with include_tree
    r = await async_client.get(f"/tasks/{root['id']}?include_tree=true", headers=headers)
    assert r.status_code == 200
    tree = r.json()
    assert len(tree.get("subtasks", [])) == 2
    has_grandchild = any(
        c.get("subtasks") and any(gc["title"] == "L2-A1" for gc in c["subtasks"]) for c in tree["subtasks"]
    )
    assert has_grandchild

    # Update a child status via PATCH
    # Find the first-level child "L1-B"
    l1b_id = next(c["id"] for c in tree["subtasks"] if c["title"] == "L1-B")
    r = await async_client.patch(f"/tasks/{l1b_id}", json={"status": "completed"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_nested_does_not_leak_into_roots_only_and_can_be_individually_deleted(async_client):
    headers = await _signup_and_login(async_client, "treeuser3", "pw")

    # Create nested
    payload = {
        "title": "Top",
        "status": "todo",
        "subtasks": [{"title": "C1", "status": "todo"}, {"title": "C2", "status": "in_progress"}],
    }
    r = await async_client.post("/tasks", json=payload, headers=headers)
    assert r.status_code == 201
    top = r.json()

    # roots_only: children should not appear
    r = await async_client.get("/tasks?roots_only=true", headers=headers)
    assert r.status_code == 200
    roots = r.json()
    assert any(t["id"] == top["id"] for t in roots)
    assert all(t.get("parent_id") is None for t in roots)

    # fetch with tree to get a child id
    r = await async_client.get(f"/tasks/{top['id']}?include_tree=true", headers=headers)
    assert r.status_code == 200
    top_full = r.json()
    child_id = top_full["subtasks"][0]["id"]

    # delete a child directly
    r = await async_client.delete(f"/tasks/{child_id}", headers=headers)
    assert r.status_code == 204

    # verify it's gone, parent still exists
    r = await async_client.get(f"/tasks/{child_id}", headers=headers)
    assert r.status_code == 404
    r = await async_client.get(f"/tasks/{top['id']}", headers=headers)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_ultra_nested_subtasks_full_flow(async_client):
    # -----------------------
    # Helpers (local to test)
    # -----------------------
    def find_by_title(node: dict, title: str):
        if node.get("title") == title:
            return node
        for c in node.get("subtasks", []) or []:
            found = find_by_title(c, title)
            if found:
                return found
        return None

    def find_by_id(node: dict, _id: int):
        if node.get("id") == _id:
            return node
        for c in node.get("subtasks", []) or []:
            found = find_by_id(c, _id)
            if found:
                return found
        return None

    # ---- Auth ----
    headers = await _signup_and_login(async_client, "ultranest", "pw")

    # ---- Create: ultra-nested with multiple branches ----
    payload = {
        "title": "Complete project proposal",
        "priority": "high",
        "tags": ["proposal", "marketing", "Q4", "work"],
        "due_date": "2025-12-25T00:00:00Z",
        "estimated_hours": 8,
        "subtasks": [
            {
                "title": "Outline",
                "status": "completed",
                "subtasks": [
                    {
                        "title": "L2-A1",
                        "status": "todo",
                        "subtasks": [
                            {
                                "title": "L3-A1",
                                "status": "todo",
                                "subtasks": [
                                    {"title": "L4-A1", "status": "todo"},
                                    {"title": "L4-A2", "status": "in_progress"},
                                ],
                            }
                        ],
                    },
                    {
                        "title": "L2-A2",
                        "status": "in_progress",
                        "subtasks": [
                            {"title": "L3-A2", "status": "todo"},
                            {"title": "L3-A3", "status": "todo"},
                        ],
                    },
                ],
            },
            {
                "title": "Draft content",
                "status": "in_progress",
                "subtasks": [
                    {"title": "L2-B1", "status": "todo"},
                    {"title": "L2-B2", "status": "todo"},
                ],
            },
            {
                "title": "Design slides",
                "status": "todo",
                "subtasks": [
                    {
                        "title": "L2-C1",
                        "status": "todo",
                        "subtasks": [
                            {"title": "L3-C1", "status": "todo"},
                            {"title": "L3-C2", "status": "todo"},
                        ],
                    }
                ],
            },
        ],
    }

    r = await async_client.post("/tasks", json=payload, headers=headers)
    assert r.status_code == 201
    root_shallow = r.json()
    root_id = root_shallow["id"]
    assert root_shallow["title"] == "Complete project proposal"
    # Shallow response MUST NOT contain subtasks
    assert "subtasks" not in root_shallow

    # ---- Read single (tree) and verify deep structure is fully present ----
    r = await async_client.get(f"/tasks/{root_id}?include_tree=true", headers=headers)
    assert r.status_code == 200
    tree = r.json()
    assert tree["id"] == root_id

    # Top-level should have 3 children
    assert len(tree.get("subtasks", [])) == 3  # Outline, Draft content, Design slides

    # Confirm deep descendants exist (L4)
    assert find_by_title(tree, "L4-A1") is not None
    assert find_by_title(tree, "L4-A2") is not None
    assert find_by_title(tree, "L3-C2") is not None

    # Grab a couple of IDs for subsequent operations
    l1_outline = find_by_title(tree, "Outline")
    l1_draft = find_by_title(tree, "Draft content")
    l2_a1 = find_by_title(tree, "L2-A1")
    l3_a1 = find_by_title(tree, "L3-A1")
    l4_a2 = find_by_title(tree, "L4-A2")

    assert l1_outline and l1_draft and l2_a1 and l3_a1 and l4_a2
    l1_draft_id = l1_draft["id"]
    l2_a1_id = l2_a1["id"]
    l3_a1_id = l3_a1["id"]
    l4_a2_id = l4_a2["id"]

    # Some explicit count checks lower down the tree
    # Design slides -> L2-C1 -> (L3-C1, L3-C2)
    design_slides = find_by_title(tree, "Design slides")
    assert design_slides is not None
    assert len(design_slides.get("subtasks", [])) == 1
    l2_c1 = find_by_title(design_slides, "L2-C1")
    assert l2_c1 is not None
    assert len(l2_c1.get("subtasks", [])) == 2

    # ---- Update status (PATCH) on a deep child ----
    r = await async_client.patch(f"/tasks/{l4_a2_id}", json={"status": "completed"}, headers=headers)
    assert r.status_code == 200
    updated_child = r.json()
    assert updated_child["id"] == l4_a2_id
    assert updated_child["status"] == "completed"
    # Shallow response (PATCH) must NOT have subtasks
    assert "subtasks" not in updated_child

    # Verify via fresh tree read
    r = await async_client.get(f"/tasks/{root_id}?include_tree=true", headers=headers)
    assert r.status_code == 200
    tree = r.json()
    assert find_by_id(tree, l4_a2_id)["status"] == "completed"

    # ---- Update (PUT) root title (shallow) ----
    r = await async_client.put(
        f"/tasks/{root_id}",
        json={"title": "Complete project proposal (v2)"},
        headers=headers,
    )
    assert r.status_code == 200
    root_after_put = r.json()
    assert root_after_put["title"] == "Complete project proposal (v2)"
    assert "subtasks" not in root_after_put

    # ---- Reparent (move) a subtree: move L3-A1 under "Draft content" ----
    # Use PATCH for partial update semantics (only changing parent_id)
    r = await async_client.put(
        f"/tasks/{l3_a1_id}",
        json={"parent_id": l1_draft_id},
        headers=headers,
    )
    assert r.status_code == 200
    moved = r.json()
    assert moved["parent_id"] == l1_draft_id

    # Verify the tree reflects the move and children are intact
    r = await async_client.get(f"/tasks/{root_id}?include_tree=true", headers=headers)
    assert r.status_code == 200
    tree = r.json()
    draft_branch = find_by_title(tree, "Draft content")
    assert draft_branch is not None
    assert any(c["id"] == l3_a1_id for c in draft_branch.get("subtasks", []))

    moved_node = find_by_id(tree, l3_a1_id)
    assert moved_node is not None
    assert any(c["title"] == "L4-A1" for c in moved_node.get("subtasks", []))
    assert any(c["title"] == "L4-A2" for c in moved_node.get("subtasks", []))

    # ---- List shallow (no subtasks in items) ----
    r = await async_client.get("/tasks?include_tree=false&roots_only=true", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert any(i["id"] == root_id for i in items)
    # Shallow means no 'subtasks' key present
    assert all("subtasks" not in i for i in items)

    # ---- List with tree (include_tree=true) for roots ----
    r = await async_client.get("/tasks?include_tree=true&roots_only=true&limit=5", headers=headers)
    assert r.status_code == 200
    roots = r.json()
    the_root = next(i for i in roots if i["id"] == root_id)
    assert len(the_root.get("subtasks", [])) >= 1
    # Confirm moved node still findable
    assert find_by_id(the_root, l3_a1_id) is not None

    # ---- Bulk: create a couple shallow tasks + bulk status updates on existing IDs ----
    r = await async_client.post(
        "/tasks/bulk",
        json={
            "create": [
                {"title": "Follow-up email", "status": "todo"},
                {"title": "Publish deck", "status": "todo"},
            ],
            "update_status": [
                {"id": root_id, "status": "in_progress"},
                {"id": l2_a1_id, "status": "completed"},
            ],
        },
        headers=headers,
    )
    assert r.status_code == 200
    bulk_res = r.json()
    # created/updated should be shallow items
    for item in bulk_res.get("created", []) + bulk_res.get("updated", []):
        assert "subtasks" not in item

    # Verify bulk effects (explicitly request tree since we'll traverse)
    r = await async_client.get(f"/tasks/{root_id}?include_tree=true", headers=headers)
    assert r.status_code == 200
    maybe_tree = r.json()
    # Root should now be in_progress
    assert maybe_tree["status"] == "in_progress"
    # L2-A1 should be completed
    assert find_by_id(maybe_tree, l2_a1_id)["status"] == "completed"

    # Verify bulk-created tasks exist and are todo (search via list)
    r = await async_client.get("/tasks?include_tree=false&roots_only=false&limit=50", headers=headers)
    assert r.status_code == 200
    all_items = r.json()
    created_titles = {"Follow-up email", "Publish deck"}
    created_found = [i for i in all_items if i["title"] in created_titles]
    assert len(created_found) == 2
    assert all(i["status"] == "todo" for i in created_found)

    # ---- Delete root (cascade delete children) ----
    r = await async_client.delete(f"/tasks/{root_id}", headers=headers)
    assert r.status_code == 204

    # Confirm root is gone
    r = await async_client.get(f"/tasks/{root_id}", headers=headers)
    assert r.status_code == 404

    # Confirm a known descendant is also gone (cascade)
    r = await async_client.get(f"/tasks/{l4_a2_id}", headers=headers)
    assert r.status_code == 404
