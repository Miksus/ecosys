
## Naming Policies

 Attributes/variables:
  - "party": name/identification of the party of a trade, contract, offer et cetera
     - Use this instead of buyer/seller/longer/shorter
  - "bid": offer/order to buy. Use "buy" only on API level.
  - "ask": offer/order to sell. Use "sell" only on API level.
  - "position": {"ask", "bid"} in trading
  - "order_book": dict containing all information of the participants of trade

### Market

Attributes/variables:
  - "party": name/identification of the party of a trade, contract, offer et cetera
     - Use this instead of buyer/seller/longer/shorter
  - "bid": offer/order to buy. Use "buy" only on API level.
  - "ask": offer/order to sell. Use "sell" only on API level.
  - "position": {"ask", "bid"} in trading or {"short", "long"} in stock
  
 Keys, Order book:
 - "limit": limit orders
 - "market": market orders
 - "stop": stop orders

Methods:
 Common
 - "place": putting or setting an offer/order
 - 

### Auction


 Keys, Order book:
 - "consignor": person who set up the auction
 - "offer": all bid (or ask) offers of the auction