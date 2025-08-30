from PyQt5 import QtWidgets
class customDialog(QtWidgets.QFileDialog):
    def __init__(self, *args, **kwargs):
        super(customDialog, self).__init__(*args, **kwargs)
        # self.setLabelText(QtWidgets.QFileDialog.Accept, "确定")  # 修改按钮文字
        # self.setLabelText(QtWidgets.QFileDialog.Reject, "取消")  # 修改按钮文字
        self.setLabelText(QtWidgets.QFileDialog.DialogLabel.FileName, "自定义文件名")  # 修改文件名标签文字
        widgets = self.findChildren(QtWidgets.QWidget)
        for widget in widgets:
            if isinstance(widget, QtWidgets.QLabel):
                print(widget.text())
                # and widget.text().startswith("文件名"):
                # widget.setText("自定义文件名:")
                break
        
