import asyncio
import base58
import base64
import json
import os

from tg_bot import send_message

from dotenv import load_dotenv
from solders import message
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from jupiter_python_sdk.jupiter import Jupiter
from solders.signature import Signature
from solders.transaction_status import TransactionConfirmationStatus

load_dotenv()  # Загружаем переменные окружения из .env файла


async def check_transaction_status(async_client, transaction_id):
    await send_message("Проверка статуса транзакции")
    await asyncio.sleep(3)
    for i in range(2, 6):
        response = await async_client.get_signature_statuses([Signature.from_string(transaction_id)])
        statuses = response.value

        if statuses and statuses[0] is not None:
            confirmation_status = statuses[0].confirmation_status
            err = statuses[0].err

            if err is None and confirmation_status in [TransactionConfirmationStatus.Confirmed,
                                                       TransactionConfirmationStatus.Finalized]:
                return True  # Транзакция успешна

            if err is not None:
                await send_message(f"Транзакция {transaction_id} завершилась с ошибкой: {err}")
                return False  # Ошибка в транзакции

        await send_message(f"Не удалось получить статус транзакции, повтор попытки номер {i}")
        await asyncio.sleep(2)

    await send_message(f"Не удалось получить статус транзакции {transaction_id}")
    return False


async def swap(address, amount, slippage=300, attempt=1):
    private_key_str = os.getenv("PRIVATE_KEY")
    if not private_key_str:
        await send_message("Переменная окружения PRIVATE_KEY не установлена!")
        return
    solana_url = os.getenv("SOLANA_URL")
    if not solana_url:
        await send_message("Переменная окружения SOLANA_URL не установлена!")
        return

    private_key = Keypair.from_bytes(base58.b58decode(private_key_str))
    async_client = AsyncClient(solana_url)

    jupiter = Jupiter(
        async_client=async_client,
        keypair=private_key,
        quote_api_url="https://quote-api.jup.ag/v6/quote?",
        swap_api_url="https://quote-api.jup.ag/v6/swap"
    )

    try:
        await send_message("Формируется транзакция")
        transaction_data = await jupiter.swap(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint=address,
            amount=int(amount * 1_000_000_000),
            slippage_bps=slippage
        )

        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])

        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
        result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        transaction_id = json.loads(result.to_json())["result"]
        await send_message("Транзакция отправлена")

        # Проверяем статус транзакции
        success = await check_transaction_status(async_client, transaction_id)

        if not success:
            if slippage <= 3000:
                await send_message(
                    f"Повтор попытки №{attempt + 1} с увеличенным проскальзыванием: {(slippage + 100) / 100} %")
                await swap(address, amount, slippage + 100, attempt + 1)
            else:
                await send_message("Достигнут предел проскальзывания. Транзакция не выполнена.")
        else:
            await send_message(f"Транзакция подтверждена: https://explorer.solana.com/tx/{transaction_id}")
            return True

    except Exception as e:
        await send_message(f"Ошибка при выполнении свопа: {e}")
        return False

    finally:
        await async_client.close()