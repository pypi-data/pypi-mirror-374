# python-trading-212 (WIP)

This project defines two clients for the Trading 212 api.

## Setup
Set the two environment variables:
```bash
export T212_API_KEY=123_YOUR_API_KEY
export T212_ENVIRONMENT="live" or "demo"
```


## AsyncTrading212Client
This uses aiohttp to make requests asyncronously.

Usage:
```python
from t212.async_client import AsyncTrading212Client

# To run from synchronous code
import asyncio
asyncio.run(AsyncTrading212Client.fetch_account_cash())

...

# To run from async, simply call
await AsyncTrading212Client.exchange_list()

...

# you can get the response as a python dict by running 
response = await AsyncTrading212Client.exchange_list()
response.model_dump(mode="json")

...

# remember to close the client when you're done
AsyncTrading212Client.close_client()

```

### Roadmap
[x] All get endpoint implemented for async class - done 02/09/2025

[ ] All post endpoints implemented for async class - target 10/09/2025

[ ] All get endpoint implemented for sync class - target 20/09/2025

[ ] All post endpoints implemented for sync class - target 30/09/2025

[ ] Deploy on pypi