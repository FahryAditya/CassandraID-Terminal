from __future__ import annotations

from cassandra_terminal.modules.notes import (
    add_note,
    clear_completed_notes,
    delete_note,
    list_notes,
    toggle_note_status,
)


def test_notes_lifecycle() -> None:
    test_proj = "/test/project/sample"

    # Add notes
    id1 = add_note("Implement auth feature", project_path=test_proj)
    id2 = add_note("Fix database connection pool", project_path=test_proj)
    assert id1 > 0
    assert id2 > 0

    # List notes
    notes = list_notes(project_path=test_proj)
    assert len(notes) >= 2
    contents = [n.content for n in notes]
    assert "Implement auth feature" in contents
    assert "Fix database connection pool" in contents

    # Toggle status
    ok, new_status = toggle_note_status(id1)
    assert ok is True
    assert new_status == "done"

    # Filter done
    done_notes = list_notes(project_path=test_proj, filter_status="done")
    assert any(n.id == id1 for n in done_notes)

    # Delete note
    deleted = delete_note(id2)
    assert deleted is True

    # Clear completed
    cleaned = clear_completed_notes(project_path=test_proj)
    assert cleaned >= 1
