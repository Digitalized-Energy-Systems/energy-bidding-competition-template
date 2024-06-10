import asyncio
from httpx import AsyncClient
import asyncio
import requests
import json
import random

"""
Loop over time
Method for
- registration
- unit information
- read open auctions
- placing order
- receiving auction results
"""
URL = "http://localhost:8000"
PARTICIPANT_ID = "Admin123"


class AgentTemplate:
    def __init__(self, step_duration_rts):
        self.step_duration_rts = step_duration_rts
        self.actions = []
        self.configurations = []
        self.rng = random.Random(42)

    def configure(self):
        self.configurations.append(self.register)

    def action(self):
        self.actions.append(self.get_unit_information)
        self.actions.append(self.read_open_auctions)
        self.actions.append(self.place_order)
        self.actions.append(self.read_auction_results)

    async def run(self):
        for config_func in self.configurations:
            await config_func()

        while True:
            await asyncio.sleep(self.step_duration_rts)

            for action_func in self.actions:
                await action_func()

    def check_response(self, response):
        if response.status_code == 200:
            print("Input sent successfully!")
        else:
            print("Failed to send input. Please try again.")

    async def register(self):
        async with AsyncClient() as client:
            endpoint = "/hackathon/register/"
            response = await client.post(
                f"{URL}{endpoint}?participant_id={PARTICIPANT_ID}"
            )
            self.check_response(response)

        data = json.loads(response.text)
        print(data)

        # Access actor and units
        self.actor_id = data["actor_id"]
        self.units = data["units"]

        # print(f'Actor ID: {self.actor_id}')
        # print('Units:')
        # for unit in self.units:
        #     print(unit)

    async def get_unit_information(self):
        async with AsyncClient() as client:
            endpoint = "/units/information/"
            response = await client.get(f"{URL}{endpoint}?actor_id={self.actor_id}")
            self.check_response(response)
            unit_information = json.loads(response.text)
            print(unit_information)

    async def read_open_auctions(self):
        async with AsyncClient() as client:
            endpoint = "/market/auction/open/"
            response = await client.get(f"{URL}{endpoint}?actor_id={self.actor_id}")
            self.check_response(response)
            self.open_auctions = json.loads(response.text)["auctions"]
            print(self.open_auctions)

    async def place_order(self):
        async with AsyncClient() as client:
            if self.open_auctions:
                actor_id = self.actor_id
                amount_kw = 1
                price_ct = self.rng.random() * 100
                supply_time = self.open_auctions[-1]["supply_start_time"]

                endpoint = "/market/auction/order/"
                response = await client.post(
                    f"{URL}{endpoint}?"
                    f"actor_id={actor_id}&"
                    f"amount_kw={amount_kw}&"
                    f"price_ct={price_ct}&"
                    f"supply_time={supply_time}"
                )
                self.check_response(response)
                placed_order = json.loads(response.text)
                print(placed_order)

    async def read_auction_results(self):
        async with AsyncClient() as client:
            endpoint = "/market/auction/result/"
            response = await client.get(f"{URL}{endpoint}?actor_id={self.actor_id}")
            self.check_response(response)
            self.auction_results = json.loads(response.text)
            print(self.auction_results)


if __name__ == "__main__":
    agent = AgentTemplate(step_duration_rts=20)
    agent.configure()
    agent.action()

    asyncio.run(agent.run())
