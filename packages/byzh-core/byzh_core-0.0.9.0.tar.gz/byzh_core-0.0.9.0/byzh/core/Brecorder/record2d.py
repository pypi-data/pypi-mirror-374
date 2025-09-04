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

    # 支持 recorder[row, col] 访问
    def __getitem__(self, key):
        row, col = key
        row, col = str(row), str(col)
        return self.data.loc[row, col]

    # 支持 recorder[row, col] = value
    def __setitem__(self, key, value):
        row, col = key
        row, col, value = str(row), str(col), str(value)
        self.data.loc[row, col] = value
        self.__save()

    def write(self, row, col, value):
        self[row, col] = value

    def get(self, row, col):
        return self[row, col]

    def get_str(self, row, col) -> str:
        return str(self[row, col])

    def get_int(self, row, col) -> int:
        return int(self[row, col])

    def get_float(self, row, col) -> float:
        return float(self[row, col])

    def get_bool(self, row, col) -> bool:
        result = self[row, col]
        if result in ("True", "true", "1"):
            return True
        elif result in ("False", "false", "0"):
            return False
        else:
            raise ValueError(f"无法转换为布尔值 -> {result}")

    def __read(self):
        try:
            self.data = pd.read_csv(self.csv_path, index_col=0)
        except (FileNotFoundError, pd.errors.EmptyDataError):
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

    # 用索引方式赋值
    recorder["awa", "OvO"] = 10
    recorder["awa", "TwT"] = 20
    recorder["qwq", "OvO"] = 30
    recorder["qwq", "TwT"] = 40

    print("当前内容：")
    print(recorder)

    # 用索引方式读取
    print("awa, OvO =", recorder["awa", "OvO"])