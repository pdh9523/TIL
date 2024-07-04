import {useState, useEffect} from "react"

function App() {
  const [loading, setLoading] = useState(true)
  const [coins, setCoins] = useState([]);
  // useEffect가 빈 리스트를 감시하므로 로드 시 한번만 실행될 예정
  useEffect(() => {
    fetch("https://api.coinpaprika.com/v1/tickers")
    .then(response => response.json())
    .then(json => {
      setCoins(json)
      setLoading(false)
    })
  }, [])
  


  return (
    <div>
      <h1>The Coins! {loading ? "" : `(${coins.length})` }</h1>
      {loading ? <strong>Loading...</strong> : null}
      <ul>
        {coins.map((coin,index) => (
          <li key={index}>
            {coin.name} ({coin.symbol}): {coin.quotes.USD.price}USD
            </li>
        ))}
      </ul>
    </div>
  )
}

export default App;

// api.coinpaprika.com/v1/tickers