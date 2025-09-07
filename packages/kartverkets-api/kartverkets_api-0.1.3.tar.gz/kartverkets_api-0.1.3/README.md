# Kartverket API Client

This Python module provides a simple, asynchronous client for interacting with the [Kartverket (Norwegian Mapping Authority) API](https://kartverket.no/data/kartdata/api-og-wms-tjenester). It allows you to search for place names (stedsnavn) and retrieve location data.

## Features

-   Asynchronous API client using `aiohttp`.
-   Search for place names with various filtering options.
-   Pydantic models for type-safe data handling.

## Installation

1.  Install package:
    ```bash
    pip install kartverkets-api
    ```

## Usage

Here's a basic example of how to use the `KartverketAPI` client to search for a place name.

```python
import asyncio
from kartverket.api import KartverketAPI

async def main():
    """
    Example usage of the KartverketAPI client.
    """
    # The client is an async context manager
    properties_eier = [{"kommuenummer" : "0301",
                   "gardsnummer" : 240,
                   "bruksnummer" : 12,
                   "festenummer" : 0,
                   "seksjonsnummer" : 0}]
    
    properties_andel = [{"borettslagnummer" : 903456235,
                         "andelsnummer" : 72 }]
    async with KartverketAPI() as client:
        try:
            #Search for a specific property with eier ownership
            result_eier = await client.get_by_property(properties_eier,ownership_type="eier")
            
            #or with andel ownership type
            result_andel = await client.get_by_property(properties_andel,ownership_type="andel")

            print(f'Eier: {result_eier}\nAndel: {result_andel}')
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```