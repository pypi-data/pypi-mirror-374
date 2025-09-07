import numpy as np
import pandas as pd

class LaggedFeatures:
    def __init__(self, df):
        self.df = df.copy() 
    
    def return_close(self, k=1):
        if not (1 <= k <= 4):
            raise ValueError("k must be between 1 and 4")
        col = f'ret_close{k}'
        self.df[col] = np.log(self.df['Close'].shift(k - 1) / self.df['Close'].shift(k))
        
        return self

    def return_high_open(self, i=0, j=0):
        if not (0 <= i <= 3 and 0 <= j <= 3):
            raise ValueError("i and j must be between 0 and 3")
        if j < i:
            raise ValueError("j must be greater than or equal to i")
        col = f'ret_ho_{i}_{j}'
        self.df[col] = np.log(self.df['High'].shift(i) / self.df['Open'].shift(j))
        
        return self

    def return_low_open(self, k=0):
        if not (0 <= k <= 3):
            raise ValueError("k must be between 0 and 3")
        col = f'ret_lo_{k}'
        self.df[col] = np.log(self.df['Low'].shift(k) / self.df['Open'].shift(k))
        
        return self

    def get_df(self):
        return self.df


class MovingAverages:
    def __init__(self, df):
        self.df = df.copy()

    def simple_moving_average(self, window=14):
        column_name = f'SMA_{window}'
        self.df[column_name] = self.df['Close'].rolling(window=window).mean()
        
        return self

    def weighted_moving_average(self, window=14):
        column_name = f'WMA_{window}'
        weights = np.arange(1, window + 1)
        denominator = weights.sum()
        self.df[column_name] = self.df['Close'].rolling(window).apply(
            lambda x: np.dot(x, weights) / denominator, raw=True)
        
        return self

    def exponential_moving_average(self, window=14):
        column_name = f'EMA_{window}'
        smooth_f = 2 / (window + 1)
        prices = self.df['Close'].values
        ema_values = [prices[0]] 

        for price in prices[1:]:
            prev_ema = ema_values[-1]
            new_ema = (price * smooth_f) + (prev_ema * (1 - smooth_f))
            ema_values.append(new_ema)

        self.df[column_name] = ema_values
        return self
    
    def exponential_moving_avg(self, window=14):
        column_name = f'EMA_{window}'
        self.df[column_name] = self.df['Close'].ewm(span=window, adjust=False).mean()
        return self

    def hull_moving_average(self, window=14):
        half_length = int(window / 2)
        sqrt_length = int(np.sqrt(window))
        self.weighted_moving_average(window=half_length).get_df()
        self.weighted_moving_average(window=window).get_df()
        diff = 2 * self.df[f'WMA_{half_length}'] - self.df[f'WMA_{window}']
        temp_df = pd.DataFrame({'Close': diff})
        temp_ma = MovingAverages(temp_df)
        hma_df = temp_ma.weighted_moving_average(window=sqrt_length).get_df()
        self.df[f'HMA_{window}'] = hma_df[f'WMA_{sqrt_length}']
        self.df.drop(columns=[f'WMA_{half_length}', f'WMA_{window}'], inplace=True)

        return self

    def macd(self, fast=12, slow=26, signal=9):
        self.exponential_moving_avg(fast).get_df()
        self.exponential_moving_avg(slow).get_df()
        self.df['MACD'] = self.df[f'EMA_{fast}'] - self.df[f'EMA_{slow}']
        macd_series = self.df['MACD'].dropna()
        temp_df = pd.DataFrame({'Close': macd_series})
        temp_ma = MovingAverages(temp_df)
        signal_ema = temp_ma.exponential_moving_avg(signal).get_df()[f'EMA_{signal}']
        self.df[f'MACD_Signal_{signal}'] = signal_ema.reindex(self.df.index)
        self.df['MACD_Hist'] = self.df['MACD'] - self.df[f'MACD_Signal_{signal}']

        return self
    
    def get_df(self):
        return self.df


class TechnicalIndicators:
    def __init__(self, df):
        self.df = df.copy()

    def relative_strength_index(self, window=14):
        delta = self.df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self.df[f'RSI_{window}'] = rsi
        
        return self

    def momentum(self, window=14):
        self.df[f'Momentum_{window}'] = self.df['Close'] - self.df['Close'].shift(window)
        
        return self

    def true_range(self):
        high = self.df['High']
        low = self.df['Low']
        prev_close = self.df['Close'].shift(1)
        tr = pd.concat([
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)
        self.df['TR'] = tr
        
        return self

    def average_true_range(self, window=14):
        self.true_range()
        temp_df = pd.DataFrame({'Close': self.df['TR']})
        ma = MovingAverages(temp_df)
        temp_df = ma.exponential_moving_avg(window).get_df()
        self.df[f'ATR_{window}'] = temp_df[f'EMA_{window}']
        self.df.drop(columns =[f'TR'], inplace = True)
        
        return self

    def parabolic_SAR(self, step=0.02, max_af=0.2):
        high = self.df['High'].values
        low = self.df['Low'].values
        close = self.df['Close'].values
        length = len(self.df)
        psar = close.copy()
        bull = True
        af = step
        ep = high[0]
        sar = low[0]

        for i in range(2, length):
            sar = sar + af * (ep - sar)
            if bull:
                sar = min(sar, low[i - 1], low[i - 2])
                if close[i] < sar:
                    bull = False
                    sar = ep
                    ep = low[i]
                    af = step
                else:
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + step, max_af)
            else:
                sar = max(sar, high[i - 1], high[i - 2])
                if close[i] > sar:
                    bull = True
                    sar = ep
                    ep = high[i]
                    af = step
                else:
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + step, max_af)
            psar[i] = sar

        self.df['PSAR'] = psar
        
        return self

    def commodity_channel_index(self, window=14):
        tp = (self.df['High'] + self.df['Low'] + self.df['Close']) / 3
        sma_tp = tp.rolling(window).mean()
        mad = tp.rolling(window).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
        cci = (tp - sma_tp) / (0.015 * mad)
        self.df[f'CCI_{window}'] = cci
        
        return self

    def average_directional_index(self, window=14):
        high = self.df['High']
        low = self.df['Low']
        close = self.df['Close']
        prev_close = close.shift(1)

        self.df['TR'] = pd.concat([
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)

        self.df['plus_dm'] = np.where((high - high.shift(1)) > (low.shift(1) - low),
                                      np.maximum(high - high.shift(1), 0), 0)
        self.df['minus_dm'] = np.where((low.shift(1) - low) > (high - high.shift(1)),
                                       np.maximum(low.shift(1) - low, 0), 0)

        tr_smooth = self.df['TR'].rolling(window).sum()
        plus_dm_smooth = self.df['plus_dm'].rolling(window).sum()
        minus_dm_smooth = self.df['minus_dm'].rolling(window).sum()
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window).mean()

        self.df['ADX'] = adx
        self.df.drop(columns=['TR', 'plus_dm', 'minus_dm'], inplace=True)
        return self

    def williams_R(self, window=14):
        high = self.df['High'].rolling(window).max()
        low = self.df['Low'].rolling(window).min()
        wr = -100 * (high - self.df['Close']) / (high - low)
        self.df[f'Williams_%R_{window}'] = wr
        
        return self

    def percent_K(self, window=14):
        low_min = self.df['Low'].rolling(window).min()
        high_max = self.df['High'].rolling(window).max()
        percent_k = 100 * (self.df['Close'] - low_min) / (high_max - low_min)
        self.df[f'%K_{window}'] = percent_k
        
        return self

    def percent_Dslow(self, window=14, d_window=3):
        self.percent_K(window)
        self.df[f'%Dslow_{d_window}'] = self.df[f'%K_{window}'].rolling(d_window).mean()
        
        return self

    def bollinger_bands(self, window=14, num_std=2):
        ma = self.df['Close'].rolling(window).mean()
        std = self.df['Close'].rolling(window).std()
        self.df['MiddleBand'] = ma
        self.df['UpperBand'] = ma + num_std * std
        self.df['LowerBand'] = ma - num_std * std
        
        return self

    def get_df(self):
        return self.df
    
### -----------------xxx---- testing---xxx-----------------------###


