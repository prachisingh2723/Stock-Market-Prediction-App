import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score

class StockPredictor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.lin_model = LinearRegression()
        self.log_model = LogisticRegression()
        self.data = None

    def load_data(self, stock_name=None):
        df = pd.read_csv(self.filepath)

        if stock_name and "Stock" in df.columns:
            df = df[df["Stock"] == stock_name]

        df['Return'] = df['Close'].pct_change()
        df['Target'] = (df['Return'] > 0).astype(int)
        df['MA10'] = df['Close'].rolling(10).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df = df.dropna()

        self.data = df
        return df

    def train_models(self):
        X = self.data[['MA10', 'MA50']]
        y_price = self.data['Close']
        y_trend = self.data['Target']

        X_train, X_test, y_price_train, y_price_test = train_test_split(
            X, y_price, test_size=0.2, shuffle=False
        )
        _, _, y_trend_train, y_trend_test = train_test_split(
            X, y_trend, test_size=0.2, shuffle=False
        )

        self.lin_model.fit(X_train, y_price_train)
        self.log_model.fit(X_train, y_trend_train)

        price_pred = self.lin_model.predict(X_test)
        trend_pred = self.log_model.predict(X_test)

        metrics = {
            "Linear MSE": mean_squared_error(y_price_test, price_pred),
            "Logistic Accuracy": accuracy_score(y_trend_test, trend_pred)
        }
        return metrics

    def predict_next(self):
        if len(self.data) < 50:
            raise ValueError("Not enough data to compute MA50")

        ma10 = self.data['Close'].rolling(10).mean().iloc[-1]
        ma50 = self.data['Close'].rolling(50).mean().iloc[-1]

        if pd.isna(ma10) or pd.isna(ma50):
            raise ValueError("Rolling averages not available yet")

        X_new = pd.DataFrame([[ma10, ma50]], columns=['MA10', 'MA50'])
        price = self.lin_model.predict(X_new)[0]
        trend = self.log_model.predict(X_new)[0]
        return price, trend
