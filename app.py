import pandas
import yfinance
import altair
import streamlit

streamlit.title('米国株価可視化アプリ')

streamlit.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定出来ます。
""")

streamlit.sidebar.write("""
## 表示日数選択
""")

days = streamlit.sidebar.slider('日数', 1, 50, 20)

streamlit.write(f"""
### 過去 **{days}日間** のGAFA株価
""")

@streamlit.cache
def get_data(days, tickers):
    df = pandas.DataFrame()
    for company in tickers.keys():
        tkr = yfinance.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist. index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pandas.concat([df, hist])
    return df

streamlit.sidebar.write("""
## 株価の範囲指定
""")

ymin, ymax = streamlit.sidebar.slider(
    '範囲を指定してください。',
    0.00, 3500.00, (0.00, 3500.00)
)

tickers = {
    'apple': 'AAPL',
    'facebook': 'FB',
    'google': 'GOOGL',
    'microsoft': 'MSFT',
    'netflix': 'NFLX',
    'amazon': 'AMZN'
}

try:
    df = get_data(days, tickers)
    companies = streamlit.multiselect(
        '会社名を選択してください。',
        list(df.index),
    default=['google', 'amazon', 'facebook', 'apple'] 
    )

    if not companies:
        streamlit.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]
        streamlit.write('### 株価 (USD)', data.sort_index())
        data = data.T.reset_index()
        data = pandas.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            altair.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x='Date:T',
                y=altair.Y('Stock Prices(USD):Q', stack=None, scale=altair.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        streamlit.altair_chart(chart, use_container_width=True)
except:
    streamlit.error(
        'エラーが起きました。'
    )