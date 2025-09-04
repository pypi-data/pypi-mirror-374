import sys
from xlpkg.x            import f_conn,f_pc,f_curexec
from PyQt5.QtCore       import Qt, pyqtSignal , pyqtSlot
from PyQt5.QtGui        import QColor, QKeySequence as QKSQ
from PyQt5.QtWidgets    import QAction as QA, QShortcut as QSC
from PyQt5.QtWidgets    import QTableWidget as QTW, QTableWidgetItem as QTWI, QDialog as QDL, QVBoxLayout as QVBLY, \
    QApplication as QAPP, QMenu, QMessageBox as QMB, \
    QGroupBox as QGB, QRadioButton as QRB, QPushButton as QPB, QHBoxLayout as QHBLY

class Win11(QTW):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.f_initui()

    def f_initui(self):
        self.f_createwidget()
        self.f_setslot()
        self.f_setshortcut()

    def f_createwidget(self):
        self.a_copy   = QA("复制", self)
        self.a_paste  = QA("粘贴", self)
        self.a_clear  = QA("清空", self)
        self.a_delete = QA("删除", self)
        self.a_align_l= QA("左对齐", self)
        self.a_align_r= QA("右对齐", self)
        self.a_align_c= QA("居中对齐", self)

        self.a_exp_all= QA("全部", self)
        self.a_exp_selected= QA("选定项", self)
        self.a_exp_unselected= QA("未选定项", self)

        self.a_hlight= QA("高亮", self)
        self.a_cancle_hlight= QA("取消高亮", self)
        self.a_bold= QA("加粗", self)
        self.a_cancle_bold= QA("取消加粗", self)

    def f_setslot(self):
        self.a_copy.triggered.connect(self.sel_copy)
        self.a_paste.triggered.connect(self.sel_paste)
        self.a_clear.triggered.connect(self.sel_clear)
        self.a_delete.triggered.connect(self.sel_delete)
        self.a_align_l.triggered.connect(self.f_alignl)
        self.a_align_r.triggered.connect(self.f_alignr)
        self.a_align_c.triggered.connect(self.f_alignc)

        self.a_exp_all.triggered.connect(self.f_exp_all)
        self.a_exp_selected.triggered.connect(self.f_exp_selected)
        self.a_exp_unselected.triggered.connect(self.f_exp_unselected)
        self.a_hlight.triggered.connect(self.hlight_bg(choice='Y'))
        self.a_cancle_hlight.triggered.connect(self.hlight_bg(choice='T'))
        self.a_bold.triggered.connect(self.bold_text(choice='Y'))
        self.a_cancle_bold.triggered.connect(self.bold_text(choice='N'))

        # 设置快捷键
    def f_setshortcut(self):
        self.a_copy.setShortcut('Ctrl+C')
        self.a_paste.setShortcut('Ctrl+V')
        self.a_clear.setShortcut('Ctrl+0')
        self.a_delete.setShortcut('Del')
        self.a_align_l.setShortcut('Ctrl+L')
        self.a_align_r.setShortcut('Ctrl+R')
        self.a_align_c.setShortcut('Ctrl+E')
        QSC(QKSQ("Ctrl+C"), self).activated.connect(self.sel_copy)
        QSC(QKSQ("Ctrl+V"), self).activated.connect(self.sel_paste)
        QSC(QKSQ("Ctrl+0"), self).activated.connect(self.sel_clear)
        QSC(QKSQ("Del"), self).activated.connect(self.sel_delete)
        QSC(QKSQ("Ctrl+L"), self).activated.connect(self.f_alignl)
        QSC(QKSQ("Ctrl+R"), self).activated.connect(self.f_alignr)
        QSC(QKSQ("Ctrl+E"), self).activated.connect(self.f_alignc)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.f_rmenu)

    def f_rmenu(self, pos):
        menu = QMenu(self)
        m_align = QMenu('对齐方式', self)
        m_exp = QMenu('导出', self)

        a_insert = QA("1插入", self)
        a_insert_common = QA("2插入", self)
        a_insert_common.triggered.connect(self.insert_base_on_selection)

        menu.addAction(self.a_copy)
        menu.addAction(self.a_paste)
        menu.addAction(self.a_clear)
        menu.addAction(self.a_delete)
        m_align.addAction(self.a_align_c)
        m_align.addAction(self.a_align_l)
        m_align.addAction(self.a_align_r)
        m_exp.addAction(self.a_exp_all)
        m_exp.addAction(self.a_exp_selected)
        m_exp.addAction(self.a_exp_unselected)

        # 插入操作
        selected = self.selectedRanges()
        if len(selected) == 0:
            return
        elif len(selected) > 1:  # 不支持多重选择场景
            return
        else:
            s = selected[0]
            srn = s.bottomRow() - s.topRow() + 1
            scn = s.rightColumn() - s.leftColumn() + 1
            if srn == self.rowCount():  # 选中区域行数等于表格最大行数, 选中整列, 向左侧插入新列
                a_insert.triggered.connect(self.insert_whole_base_on_selection(insert_type='C'))
                menu.addAction(a_insert)
            elif scn == self.columnCount():  # 选中区域列数等于表格最大列数, 选中整行, 向上方插入新行
                a_insert.triggered.connect(self.insert_whole_base_on_selection(insert_type='R'))
                menu.addAction(a_insert)
            else:
                menu.addAction(a_insert_common)

        menu.addMenu(m_align)
        menu.addMenu(m_exp)

        menu.addAction(self.a_hlight)
        menu.addAction(self.a_bold)
        menu.addAction(self.a_cancle_hlight)
        menu.addAction(self.a_cancle_bold)

        menu.exec(self.viewport().mapToGlobal(pos))
    pass

    def get_first_empty_row_id(self):
        first_empty_row_id = 0
        for row in range(self.rowCount()):
            exist_item = False
            for column in range(self.columnCount()):
                if self.item(row, column) is not None and self.item(row, column).text() not in ['', ' ']:
                    exist_item = True
                    break
            if not exist_item:
                return first_empty_row_id
            first_empty_row_id += 1
        return first_empty_row_id

    def read_table_context(self):
        context = [[self.item(row, col).text() if self.item(row, col) is not None else ''
                    for col in range(self.columnCount())] for row in range(self.rowCount())]
        return context

    def _insert_add_row_helper(self, selected_top, selected_bottom):
        finaly_unempty_row_id = self.rowCount()
        end = False
        for row in sorted(range(self.rowCount()), reverse=True):
            finaly_unempty_row_id -= 1
            for column in range(selected_top, selected_bottom + 1):
                if self.item(row, column) is not None and self.item(row, column).text() not in ['', ' ']:
                    end = True
                    break
            if end:
                break
        return finaly_unempty_row_id

    def _insert_add_col_helper(self, selected_left, selected_right):
        finaly_unempty_col_id = self.columnCount()
        end = False
        for column in sorted(range(self.columnCount()), reverse=True):
            finaly_unempty_col_id -= 1
            for row in range(selected_left, selected_right + 1):
                if self.item(row, column) is not None and self.item(row, column).text() not in ['', ' ']:
                    end = True
                    break
            if end:
                break
        return finaly_unempty_col_id

    def _judge_rectangular_selected(self):
        selection = self.selectedRanges()
        if len(selection) != 1:
            QMB.warning(self, "选中区域非法", "多重选择或未选中任何区域, 当前操作不支持多重选择")
            return False
        return True

    def sel_copy(self):
        if not self._judge_rectangular_selected():
            return
        selected = self.selectedRanges()[0]
        text = "\n".join(['\t'.join([self.item(row, col).text() if self.item(row, col) is not None else ''
                                     for col in range(selected.leftColumn(), selected.rightColumn() + 1)])
                          for row in range(selected.topRow(), selected.bottomRow() + 1)])
        QAPP.clipboard().setText(text)

    def sel_paste(self):
        if not self._judge_rectangular_selected():
            return
        selected = self.selectedRanges()[0]
        text = QAPP.clipboard().text()
        rows = text.split('\n')
        if '' in rows:
            rows.remove('')

        for r, row in enumerate(rows):
            if selected.topRow() + r >= self.rowCount():
                self.insertRow(selected.topRow() + r)
            cols = row.split('\t')
            for c, text in enumerate(cols):
                if selected.leftColumn() + c >= self.columnCount():
                    self.insertColumn(selected.leftColumn() + c)
                self.setItem(selected.topRow() + r, selected.leftColumn() + c, QTWI(text))

    def sel_clear(self):
        for item in self.selectedItems():
            self.setItem(item.row(), item.column(), QTWI(""))

    def sel_delete(self):
        if not self._judge_rectangular_selected():
            return
        dl_del = Win13(dialog_type='delete')
        dl_del.DelSignal.connect(self._f_delete)
        dl_del.setWindowModality(Qt.WindowModality.ApplicationModal)
        dl_del.exec()

    @pyqtSlot(str)
    def _f_delete(self, msg):
        selected = self.selectedRanges()[0]
        if msg == 'Move Left':
            selected_cols_num = selected.rightColumn() - selected.leftColumn() + 1
            start_col_index = selected.leftColumn() + selected_cols_num
            for col in range(start_col_index, self.columnCount() + selected_cols_num):
                ori_col = col - selected_cols_num
                for row in range(selected.topRow(), selected.bottomRow() + 1):
                    if col < self.columnCount():
                        text = self.item(row, col).text() if self.item(row, col) is not None \
                            else self.item(row, col).text
                        self.setItem(row, ori_col, QTWI(text))
                    else:
                        self.setItem(row, ori_col, QTWI(''))
        elif msg == 'Move Up':
            selected_rows_num = selected.bottomRow() - selected.topRow() + 1
            start_row_index = selected.topRow() + selected_rows_num
            for row in range(start_row_index, self.rowCount() + selected_rows_num):
                ori_row = row - selected_rows_num
                for col in range(selected.leftColumn(), selected.rightColumn() + 1):
                    if row < self.rowCount():
                        text = self.item(row, col).text() if self.item(row, col) is not None \
                            else self.item(row, col).text
                        self.setItem(ori_row, col, QTWI(text))
                    else:
                        self.setItem(ori_row, col, QTWI(''))
        elif msg == 'Delete Selected Rows':
            # 从最后一列开始删除，避免删除后索引变化
            for row in sorted(range(selected.topRow(), selected.bottomRow() + 1), reverse=True):
                self.removeRow(row)
        elif msg == 'Delete Selected Cols':
            # 从最后一列开始删除，避免删除后索引变化
            for column in sorted(range(selected.leftColumn(), selected.rightColumn() + 1), reverse=True):
                self.removeColumn(column)
        else:
            print('Empty Message')

    def insert_whole_base_on_selection(self, insert_type):
        def insert():
            selected = self.selectedRanges()[0]
            if insert_type == 'R':
                row_id = selected.topRow()
                for i in range(selected.bottomRow() - selected.topRow() + 1):
                    self.insertRow(row_id)
            elif insert_type == 'C':
                col_id = selected.leftColumn()
                for i in range(selected.rightColumn() - selected.leftColumn() + 1):
                    self.insertColumn(col_id)

        return insert

    def insert_base_on_selection(self):
        if not self._judge_rectangular_selected():
            return
        dl_insert= Win13(dialog_type='insert')
        dl_insert.InsertSignal.connect(self._f_insert)
        dl_insert.setWindowModality(Qt.WindowModality.ApplicationModal)
        dl_insert.exec()

    @pyqtSlot(str)
    def _f_insert(self, msg):
        selected = self.selectedRanges()[0]
        if msg == 'Move Right':
            selected_cols_num = selected.rightColumn() - selected.leftColumn() + 1
            final_col = self._insert_add_col_helper(selected.topRow(), selected.bottomRow()) + 1 + selected_cols_num
            while self.columnCount() < final_col:
                self.insertColumn(self.columnCount())
            for col in sorted(range(selected.leftColumn(), final_col), reverse=True):
                ori_col = col - selected_cols_num
                for row in range(selected.topRow(), selected.bottomRow() + 1):
                    if col >= selected.leftColumn() + selected_cols_num:
                        text = self.item(row, ori_col).text() if self.item(row, ori_col) is not None else ''
                        self.setItem(row, col, QTWI(text))
                    else:
                        self.setItem(row, col, QTWI(''))
            print('OK')

        elif msg == 'Move Down':
            selected_rows_num = selected.bottomRow() - selected.topRow() + 1
            final_row = self._insert_add_row_helper(selected.leftColumn(),
                                                    selected.rightColumn()) + 1 + selected_rows_num
            while self.rowCount() < final_row:
                self.insertRow(self.rowCount())
            for row in sorted(range(selected.topRow(), final_row), reverse=True):
                ori_row = row - selected_rows_num
                for col in range(selected.leftColumn(), selected.rightColumn() + 1):
                    if row >= selected.topRow() + selected_rows_num:
                        text = self.item(ori_row, col).text() if self.item(ori_row, col) is not None else ''
                        self.setItem(row, col, QTWI(text))
                    else:
                        self.setItem(row, col, QTWI(''))
        elif msg == 'Insert Rows Above':
            self.insert_whole_base_on_selection('R')()
        elif msg == 'Insert Cols Left':
            self.insert_whole_base_on_selection('C')()
        else:
            print('Empty Message')


    def _set_null_item(self):
        if not self._judge_rectangular_selected():
            return
        s = self.selectedRanges()[0]
        for row in range(s.topRow(), s.bottomRow() + 1):
            for col in range(s.leftColumn(), s.rightColumn() + 1):
                item = self.item(row, col)
                if item is None:
                    self.setItem(row, col, QTWI(''))

    #右对齐
    def f_alignr(self):
        self._set_null_item()
        for item in self.selectedItems():
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    #左对齐
    def f_alignl(self):
        self._set_null_item()
        for item in self.selectedItems():
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    #居中对齐
    def f_alignc(self):
        self._set_null_item()
        for item in self.selectedItems():
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def f_exp_all(self):
        f_pc(32,'Exp all!')
        pass

    def f_exp_selected(self):
        f_pc(32,'Exp selected!')
        pass

    def f_exp_unselected(self):
        f_pc(32,'Exp unselected!')
        pass

    #背景高亮
    def hlight_bg(self, choice):
        def hlight_operation():
            self._set_null_item()
            yellow_bg = QColor(255, 255, 0)
            transparent_bg = QColor(255, 255, 255, 0)
            for item in self.selectedItems():
                if choice == 'Y':
                    item.setBackground(yellow_bg)
                elif choice == 'T':
                    item.setBackground(transparent_bg)
                else:
                    print('highlight background error input')
        return(hlight_operation)

    def bold_text(self, choice):
        def bold_operation():
            self._set_null_item()
            for item in self.selectedItems():
                item_font = item.font()
                if choice == 'Y':
                    item_font.setBold(True)
                    item.setFont(item_font)
                elif choice == 'N':
                    item_font.setBold(False)
                    item.setFont(item_font)
                else:
                    print('bold operation error input')
        return(bold_operation)
    pass

class Win13(QDL):
    DelSignal = pyqtSignal(str)
    InsertSignal = pyqtSignal(str)

    def __init__(self, dialog_type):
        super().__init__()
        self.dialog_type = dialog_type
        self.setWindowFlags(Qt.WindowType.Drawer | Qt.WindowType.WindowCloseButtonHint)
        self.dialog_typ_ch = '删除' if dialog_type.lower() == 'delete' else '插入'
        self.setWindowTitle(self.dialog_typ_ch)
        self.resize(250, 150)

        # 1. 创建GroupBox
        self.groupBox = QGB(self.dialog_typ_ch)
        self.groupBox.setFlat(True)

        # 1.1 创建RadioButton
        self.rb_A = QRB()
        self.rb_B = QRB()
        self.rb_C = QRB()
        self.rb_D = QRB()

        # 1.2 将RadioButton添加到GroupBox中
        gb_vbox = QVBLY()
        gb_vbox.addWidget(self.rb_A)
        gb_vbox.addWidget(self.rb_B)
        gb_vbox.addWidget(self.rb_C)
        gb_vbox.addWidget(self.rb_D)
        self.groupBox.setLayout(gb_vbox)

        # 2. 创建确定和取消按钮
        self.buttonOK = QPB("确定")
        self.buttonCancel = QPB("取消")

        # 2.1 将按钮添加到水平布局中
        hbox = QHBLY()
        hbox.addWidget(self.buttonOK)
        hbox.addWidget(self.buttonCancel)

        # 3. 将GroupBox和按钮添加到垂直布局中
        vbox = QVBLY()
        vbox.addWidget(self.groupBox)
        vbox.addLayout(hbox)

        # 4. 设置对话框的布局
        self.setLayout(vbox)
        self.buttonCancel.clicked.connect(self.close)
        self._preperation()

    def _preperation(self):
        if self.dialog_type.lower() == 'delete':
            # 1. 设置文本
            self.rb_A.setText('右侧单元格左移(L)')
            self.rb_B.setText('下方单元格上移(U)')
            self.rb_C.setText('整行(R)')
            self.rb_D.setText('整列(C)')

            # 2 设置热键
            QSC(QKSQ("L"), self).activated.connect(self.rb_A.toggle)
            QSC(QKSQ("U"), self).activated.connect(self.rb_B.toggle)
            QSC(QKSQ("R"), self).activated.connect(self.rb_C.toggle)
            QSC(QKSQ("C"), self).activated.connect(self.rb_D.toggle)

            self.buttonOK.clicked.connect(self.delete_button_ok_clicked)
        else:
            # 1. 设置文本
            self.rb_A.setText('活动单元格右移(R)')
            self.rb_B.setText('活动单元格下移(D)')
            self.rb_C.setText('整行(R)')
            self.rb_D.setText('整列(C)')

            # 2 设置热键
            QSC(QKSQ("R"), self).activated.connect(self.rb_A.toggle)
            QSC(QKSQ("D"), self).activated.connect(self.rb_B.toggle)
            QSC(QKSQ("R"), self).activated.connect(self.rb_C.toggle)
            QSC(QKSQ("C"), self).activated.connect(self.rb_D.toggle)

            self.buttonOK.clicked.connect(self.insert_button_ok_clicked)

    def delete_button_ok_clicked(self):
        if self.rb_A.isChecked():
            self.DelSignal.emit('Move Left')
        elif self.rb_B.isChecked():
            self.DelSignal.emit('Move Up')
        elif self.rb_C.isChecked():
            self.DelSignal.emit('Delete Selected Rows')
        elif self.rb_D.isChecked():
            self.DelSignal.emit('Delete Selected Cols')
        else:
            self.DelSignal.emit('')
        self.close()

    def insert_button_ok_clicked(self):
        if self.rb_A.isChecked():
            self.InsertSignal.emit('Move Right')
        elif self.rb_B.isChecked():
            self.InsertSignal.emit('Move Down')
        elif self.rb_C.isChecked():
            self.InsertSignal.emit('Insert Rows Above')
        elif self.rb_D.isChecked():
            self.InsertSignal.emit('Insert Cols Left')
        else:
            self.InsertSignal.emit('')
        self.close()


class Win12(QDL):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TableWidget 右键操作")
        self.setWindowFlags(
            Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        self.tw_01 = Win11()
        self.tw_01.setRowCount(10)
        self.tw_01.setColumnCount(5)

        ly_01 = QVBLY()
        ly_01.addWidget(self.tw_01)
        self.setLayout(ly_01)

        env='test'
        product='ptkc'
        sql="select * from runfast_trade.order_record limit 20;"
        params=None
        self.f_addcontent(env,product,sql,params)
        self.resize(700, 400)
        self.show()

    def f_addcontent(self,env,product,sql,params):
        conn,cur=f_conn(env,product)
        rows,cols,sqle=f_curexec(cur,sql,params)
        # 设置列数
        self.tw_01.setColumnCount(len(cols))
        # 设置行数
        self.tw_01.setRowCount(len(rows))
        # 设置表头
        self.tw_01.setHorizontalHeaderLabels(cols)

        # 遍历rows,逐项填充每个单元格
        self.f_fillcell(self.tw_01,rows,cols)
        """
        for i in range(len(rows)):
            for j in range(len(cols)):
                if not rows[i][j]:
                    item = QTWI(str(""))
                else:
                    item = QTWI(str(rows[i][j]))
                    item.setToolTip(str(rows[i][j]))  # 鼠标悬停提示气泡，方便显示过长内容
                self.tw_01.setItem(i, j, item)  # 设置i行j列的内容
        """
        """
        for i_r, row_data in enumerate(r):
            for i_c, cell_data in enumerate(row_data):
                #self.tw_01.setItem(row_index, column_index, self.tw_01(str(cell_data)))
                f_pc(32,i_r, i_c, str(cell_data))
                
        for col in range(len(c)):
            for row in range(len(r)):
                f_pc(32,row,col)
        for i in range(10):
            for j in range(5):
                item = QTWI('{}{}'.format(i + 1, j + 1))
                self.tw_01.setItem(i, j, item)
        """
    def f_fillcell(self,tw,rows,cols):
        tw.setHorizontalHeaderLabels(cols)
        # 遍历records 逐项填充每个单元格
        for i in range(len(rows)):
            for j in range(len(cols)):
                if not rows[i][j]:
                    item = QTWI(str(""))
                else:
                    item = QTWI(str(rows[i][j]))
                    item.setToolTip(str(rows[i][j]))  # 鼠标悬停提示气泡，方便显示过长内容
                tw.setItem(i, j, item)  # 设置i行j列的内容
        pass

if __name__ == '__main__':
    app = QAPP(sys.argv)
    w = Win12()
    w.show()
    sys.exit(app.exec())
    pass
