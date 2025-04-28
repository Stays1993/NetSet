# -*-coding:utf-8-*-
import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtWidgets import (QListWidget, QAbstractItemView, QMenu, QWidget,
                             QHBoxLayout, QApplication, QListWidgetItem)


class DropInList(QListWidget):
    def __init__(self):
        super(DropInList, self).__init__()
        # 拖拽设置
        self.setAcceptDrops(True)  # 开启接受拖入事件
        self.setDragEnabled(True)  # 开启拖出功能
        # 修改为 PyQt6 枚举值
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)  # 开启多选模式
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)  # 设置拖放
        self.setDefaultDropAction(Qt.DropAction.CopyAction)

        # 双击可编辑
        self.edited_item = self.currentItem()
        self.close_flag = True
        self.doubleClicked.connect(self.item_double_clicked)  # 双击事件
        self.currentItemChanged.connect(self.close_edit)  # 结束编辑事件

        # 右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.custom_right_menu)

    def dropEvent(self, QDropEvent):
        """拖拽结束以后触发的事件"""
        source_Widget = QDropEvent.source()  # 获取拖入元素的父组件
        items = source_Widget.selectedItems()
        # print(items)
        for i in items:
            source_Widget.takeItem(source_Widget.indexFromItem(i).row())  # 通过实时计算选中的item的索引来删除listItem
            self.addItem(i)

    def item_double_clicked(self, modelindex: QModelIndex) -> None:
        """双击事件"""
        self.close_edit()
        item = self.item(modelindex.row())
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)

    def close_edit(self, *_) -> None:
        """关闭edit"""
        if self.edited_item and self.isPersistentEditorOpen(self.edited_item):
            self.closePersistentEditor(self.edited_item)

    def custom_right_menu(self, pos):
        menu = QtWidgets.QMenu()
        opt1 = menu.addAction("新增")
        opt2 = menu.addAction("删除")
        opt3 = menu.addAction("排序")
        opt4 = menu.addAction("清空")
        # hitIndex = self.indexAt(pos).column()
        # if hitIndex > -1:  #确保有至少一个项
        # 	#获取item内容
        #     name=self.item(hitIndex).text()
        action = menu.exec(self.mapToGlobal(pos))

        if action == opt1:
            item = QtWidgets.QListWidgetItem("新增")
            self.addItem(item)
        elif action == opt2:
            for j in range(len(self.selectedIndexes()) - 1, -1, -1):  # 反向删除
                self.takeItem(self.selectedIndexes()[j].row())
        elif action == opt3:
            self.sortItems()
        elif action == opt4:
            self.clear()


class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.setWindowTitle('自定义ListWidget实现相互拖拽和双击编辑右键菜单功能')
        self.main_layout = QHBoxLayout()
        self.left_widget = DropInList()
        self.right_widget = DropInList()
        pre_list = ['item1', 'item2', 'item3', 'item4']
        self.right_widget.addItems(pre_list)
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)
        self.setLayout(self.main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWidget()
    m.show()
    sys.exit(app.exec())
