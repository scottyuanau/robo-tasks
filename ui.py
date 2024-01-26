

def ui():
    from PyQt5.QtWidgets import QApplication, QDateEdit
    from PyQt5.QtCore import QDate

    app = QApplication([])
    date_edit = QDateEdit()
    date_edit.setDate(QDate.currentDate())
    date_edit.setMinimumDate(QDate(2000, 1, 1))
    date_edit.setMaximumDate(QDate(2022, 12, 31))
    date_edit.setCalendarPopup(True)
    date_edit.show()
    app.exec_()


if __name__ == '__main__':
    ui()