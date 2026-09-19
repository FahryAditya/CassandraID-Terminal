from fileforge.modules.activity import clear_activity_logs, get_activity_logs, log_activity


def test_activity_logging():
    log_activity("CREATE", "test_file.txt", "SUCCESS", "Created file")
    log_activity("DELETE", "test_file.txt", "SUCCESS", "Deleted file")

    logs = get_activity_logs()
    assert len(logs) == 2
    assert logs[0].operation == "DELETE"
    assert logs[1].operation == "CREATE"


def test_activity_filtering():
    log_activity("COPY", "a.txt", "SUCCESS")
    log_activity("MOVE", "b.txt", "SUCCESS")

    copy_logs = get_activity_logs(operation_filter="COPY")
    assert len(copy_logs) == 1
    assert copy_logs[0].operation == "COPY"


def test_clear_activity_logs():
    log_activity("OP1", "target", "SUCCESS")
    assert len(get_activity_logs()) == 1

    cleared = clear_activity_logs()
    assert cleared == 1
    assert len(get_activity_logs()) == 0
