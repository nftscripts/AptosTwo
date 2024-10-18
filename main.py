import random
from asyncio import sleep, gather, create_task, run

from loguru import logger

from config import PAUSE_BETWEEN_WALLETS
from src.minting.aptos_two_nft import AptosTwoNFT

with open('wallets.txt', 'r') as file:
    private_keys = [line.strip() for line in file]


async def main() -> None:
    tasks = []
    for private_key in private_keys:
        nft = AptosTwoNFT(
            private_key=private_key
        )
        logger.debug(nft)

        task = create_task(nft.mint_nft())
        tasks.append(task)

        time_to_sleep = random.randint(PAUSE_BETWEEN_WALLETS[0], PAUSE_BETWEEN_WALLETS[1]) if isinstance(
            PAUSE_BETWEEN_WALLETS, list) else PAUSE_BETWEEN_WALLETS

        logger.info(f'Sleeping {time_to_sleep} seconds...')
        await sleep(time_to_sleep)

    await gather(*tasks)


if __name__ == '__main__':
    run(main())
