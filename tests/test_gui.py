from gui.idact_app import IdactApp


def test_basics(qtbot):
    window = IdactApp()
    qtbot.addWidget(window)
    window.show()

    assert window.isVisible()
    assert window.windowTitle() == 'Idact GUI'
