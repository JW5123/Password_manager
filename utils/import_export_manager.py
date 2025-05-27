import pandas as pd
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class ImportExportManager:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        
    def import_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "選擇檔案", "", 
            "Excel Files CSV Files (*.csv);;(*.xlsx *.xls);;All Files (*)"
        )
        
        if not file_path:
            return

        try:
            # 讀取檔案
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            else:
                df = pd.read_excel(file_path)

            # 檢查必要欄位
            required_columns = ['名稱', '帳號', '密碼']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                QMessageBox.warning(self.parent, "匯入錯誤", 
                                    f"檔案缺少必要欄位：{', '.join(missing_columns)}\n"
                                    f"請確保檔案包含以下欄位：{', '.join(required_columns)}")
                return

            # 如果沒有備註或類別欄位，添加空的欄位
            if '備註' not in df.columns:
                df['備註'] = ''

            if '類別' not in df.columns:
                df['類別'] = ''

            # 獲取現有資料以避免重複
            existing_entries = self.db_manager.get_all_entries()
            existing_set = {(entry[0], entry[1], entry[2]) for entry in existing_entries}

            # 初始化計數器
            success_count = 0
            duplicate_count = 0
            fail_count = 0

            # 處理每一行資料
            for _, row in df.iterrows():
                name = str(row['名稱']).strip()
                account = str(row['帳號']).strip()
                password = str(row['密碼']).strip()
                notes = str(row['備註']) if not pd.isna(row['備註']) else ''
                category = str(row['類別']) if not pd.isna(row['類別']) else ''

                # 檢查名稱是否為空
                if not name:
                    fail_count += 1
                    continue

                # 檢查是否重複
                if (name, account, password) in existing_set:
                    duplicate_count += 1
                    continue

                # 嘗試添加資料
                try:
                    self.db_manager.add_password_entry(name, account, password, notes, category)
                    success_count += 1
                    existing_set.add((name, account, password))
                except Exception:
                    fail_count += 1

            # 顯示匯入結果
            self._show_import_result(success_count, duplicate_count, fail_count)
        
        except Exception as e:
            QMessageBox.critical(self.parent, "匯入錯誤", f"檔案匯入過程中發生錯誤：\n{str(e)}")

    # 顯示匯入結果
    def _show_import_result(self, success_count, duplicate_count, fail_count):
        message = f"匯入結果：\n成功添加：{success_count} 項\n"
        if duplicate_count > 0:
            message += f"已跳過（重複項目）：{duplicate_count} 項\n"
        if fail_count > 0:
            message += f"匯入失敗：{fail_count} 項\n"

        QMessageBox.information(self.parent, "匯入完成", message)
        
        # 通知父元件刷新資料
        if hasattr(self.parent, 'load_names'):
            self.parent.load_names()

    # 匯出資料為Excel檔案
    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "儲存檔案", "密碼儲存簿", 
            "Excel Files CSV Files (*.csv);;(*.xlsx);;All Files (*)"
        )

        if not file_path:
            return
            
        try:
            # 獲取所有資料
            entries = self.db_manager.get_all_entries()
            df = pd.DataFrame(entries, columns=['名稱', '帳號', '密碼', '備註', '類別'])
            
            # 根據檔案擴展名決定匯出格式
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                df.to_excel(file_path, index=False)

            QMessageBox.information(self.parent, "訊息", f"資料成功匯出至 {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self.parent, "匯出錯誤", f"檔案匯出過程中發生錯誤：\n{str(e)}")

    def export_filtered_data(self, filter_category=None):
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "儲存檔案", "密碼儲存簿", 
            "Excel Files CSV Files (*.csv);;(*.xlsx);;All Files (*)"
        )

        if not file_path:
            return
            
        try:
            # 根據篩選條件獲取資料
            if filter_category and filter_category != "全部":
                entries = self.db_manager.get_entries_by_category(filter_category)
            else:
                entries = self.db_manager.get_all_entries()
                
            df = pd.DataFrame(entries, columns=['名稱', '帳號', '密碼', '備註', '類別'])
            
            # 根據檔案擴展名決定匯出格式
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                df.to_excel(file_path, index=False)

            QMessageBox.information(self.parent, "訊息", f"資料成功匯出至 {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self.parent, "匯出錯誤", f"檔案匯出過程中發生錯誤：\n{str(e)}")