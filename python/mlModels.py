import pandas as pd
from xgboost import XGBRegressor


class mlModel:
    def __init__(self, model_path: str) -> None:
        self.model = XGBRegressor()
        self.model.load_model(model_path)

    def stressCalculation(self, data:list) -> int:
        return int(self.model.predict(data)[0])


