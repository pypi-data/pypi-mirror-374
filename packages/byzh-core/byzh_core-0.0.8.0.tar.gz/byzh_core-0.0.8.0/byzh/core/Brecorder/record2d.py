import pandas as pd
from typing import Any

from .. import B_os

class B_Record2d:
    def __init__(self, csv_path, mode="a"):
        self.csv_path = csv_path

        B_os.makedirs(csv_path)
        self.data = pd.DataFrame()
        if mode == "w":
            B_os.rm(csv_path)
            self.__read()
        elif mode == "a":
            self.__read()

    def write(self, row, col, value):
        row, col, value = str(row), str(col), str(value)

        # 如果行不存在，pandas 会自动创建
        # 如果列不存在，pandas 也会自动扩展
        self.data.loc[row, col] = value

        # 保存
        self.__save()

    def get(self, row, col) -> Any:
        row, col = str(row), str(col)
        result = self.data.loc[row, col]
        return result
    def get_str(self, row, col) -> str:
        row, col = str(row), str(col)
        result = self.data.loc[row, col]
        return str(result)

    def get_int(self, row, col) -> int:
        row, col = str(row), str(col)
        result = self.data.loc[row, col]
        return int(result)
    def get_float(self, row, col) -> float:
        row, col = str(row), str(col)
        result = self.data.loc[row, col]
        return float(result)
    def get_bool(self, row, col) -> bool:
        row, col = str(row), str(col)
        result = self.data.loc[row, col]
        if result == "True" or result == "true" or result == "1":
            return True
        elif result == "False" or result == "false" or result == "0":
            return False
        else:
            raise ValueError(f"无法转换为布尔值 -> {result}")

    def __read(self):
        try:
            self.data = pd.read_csv(self.csv_path, index_col=0)
        except FileNotFoundError:
            self.data = pd.DataFrame()
        except pd.errors.EmptyDataError:
            self.data = pd.DataFrame()

    def __save(self, csv_path=None):
        if csv_path is None:
            csv_path = self.csv_path
        self.data.to_csv(csv_path, index=True, encoding='utf-8-sig')

    def __str__(self):
        return str(self.data)

if __name__ == '__main__':
    csv_file = "test_data.csv"

    recorder = B_Record2d(csv_file, mode="w")

    # 写入一些单元格
    recorder.write("awa", "OvO", 10)
    recorder.write("awa", "TwT", 20)
    recorder.write("qwq", "OvO", 30)
    recorder.write("qwq", "TwT", 40)

    print("当前内容：")
    print(recorder)

    recorder = B_Record2d(csv_file, mode="a")
    print(recorder)