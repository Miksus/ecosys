
## Naming Policies

 Attributes/variables:
  - "party": name/identification of the party of a trade, contract, offer et cetera
     - Use this instead of buyer/seller/longer/shorter
  - "bid": offer/order to buy. Use "buy" only on API level.
  - "ask": offer/order to sell. Use "sell" only on API level.
  - "position": {"ask", "bid"} in trading
  - "order_book": dict containing all information of the participants of trade

### Asset

Asset =  A thing that holds value and this value is universally the same
         for all the items in the asset in specific time. Ie.
            Asset: 
               - Nokia shares, 
               - Oil,
               - Banana 
            NOT Asset itself (too generic): 
               - Appartment (but can be if "Appartment in location X with N rooms"),
               - Car (but can be if "Mercedes Model XYZ"),
               - 


### Stockmarket

Stockmarket = Collection of markets

### Market

Market = Platform to trade one asset

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