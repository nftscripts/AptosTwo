from time import time
from asyncio import sleep
import random

from aptos_sdk.transactions import TransactionPayload, EntryFunction, TransactionArgument, RawTransaction
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.bcs import Serializer
from loguru import logger

from config import QUANTITY
from src.utils.user.account import AptosAccount
from src.utils.wrappers.decorators import retry


class AptosTwoNFT(AptosAccount):
    def __init__(
            self,
            private_key: str
    ):
        super().__init__(private_key)

    def __str__(self) -> str:
        return f'[{self.wallet_address}] | Minting NFT...'

    @retry(retries=3, delay=30, backoff=1.5)
    async def mint_nft(self) -> None:
        balance = await self.get_balance()
        if balance == 0:
            logger.error(f'[{self.wallet_address}] | APT balance is 0')
            return

        quantity = random.randint(QUANTITY[0], QUANTITY[1]) if isinstance(QUANTITY, list) else QUANTITY
        payload = self._get_payload(quantity)
        raw_transaction = RawTransaction(
            sender=self.wallet_address,
            sequence_number=await self.rest_client.account_sequence_number(self.wallet_address),
            payload=payload,
            max_gas_amount=10_000,
            gas_unit_price=100,
            expiration_timestamps_secs=int(time()) + 600,
            chain_id=await self.rest_client.chain_id()
        )
        tx_hash = await self.sign_transaction(raw_transaction)
        await sleep(2)
        await self.rest_client.wait_for_transaction(tx_hash)
        logger.success(
            f'[{self.wallet_address}] | Successfully minted {quantity}'
            f' NFTs: https://explorer.aptoslabs.com/txn/{tx_hash}'
        )

    @staticmethod
    def _get_payload(quantity: int) -> TransactionPayload:
        return TransactionPayload(
            EntryFunction.natural(
                module='0x96c192a4e3c529f0f6b3567f1281676012ce65ba4bb0a9b20b46dec4e371cccd::unmanaged_launchpad',
                function='mint',
                ty_args=[],
                args=[
                    TransactionArgument(
                        AccountAddress.from_str(
                            '0xd42cd397c41a62eaf03e83ad0324ff6822178a3e40aa596c4b9930561d4753e5'
                        ),
                        Serializer.struct
                    ),
                    TransactionArgument(
                        [quantity], Serializer.sequence_serializer(value_encoder=Serializer.u64)
                    )
                ]
            )
        )
