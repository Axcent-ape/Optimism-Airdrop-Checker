import asyncio
from urllib import parse as urllib
import aiohttp
import random


class CheckEligible:
    def __init__(self, thread: int):
        self.thread = thread
        self.session = aiohttp.ClientSession(trust_env=True)

    async def check_eligible(self):
        address = self.get_wallet()
        if address:
            str_dict = f'{{"0":{{"json":{{"chainId":10,"address":"{address}","id":"4"}}}},"1":{{"json":{{"address":"{address}"}}}}}}'

            percent_unicode = urllib.quote(str_dict.encode('utf-8'))
            url = f'https://prod-gateway-backend-mainnet.optimism.io/api/v0/eligibility.eligibilityAmounts,screenaddressv2.checkAddress?batch=1&input={percent_unicode}'

            resp = await self.session.get(url)
            resp_json = await resp.json()

            if resp_json and resp_json[0]["result"]["data"]["json"] is not None:
                res_text = f'{address}:{round(int(resp_json[0]["result"]["data"]["json"]["totalAmount"]) / 1e18, 2)}'
                with open('eligible.txt', 'a') as f:
                    f.write(f'\n{res_text}')
                print(f'{self.thread} | {res_text}')

            return True
        return False

    async def logout(self):
        await self.session.close()

    @staticmethod
    def get_wallet():
        with open('wallets.txt', 'r') as file:
            keys = file.readlines()

        if not keys:
            return False
        random_key = random.choice(keys)
        keys.remove(random_key)

        with open('wallets.txt', 'w') as file:
            file.writelines(keys)

        return random_key.strip()


async def check(thread):
    checker = CheckEligible(thread)

    while True:
        if not await checker.check_eligible(): break
    await checker.logout()


async def main():
    print("Автор чекера: https://t.me/ApeCryptor")

    thread_count = int(input("Введите кол-во потоков: "))
    thread_count = 50 if thread_count > 50 else thread_count
    tasks = []
    for thread in range(1, thread_count+1):
        tasks.append(asyncio.create_task(check(thread)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
