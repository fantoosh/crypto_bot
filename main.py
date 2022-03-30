from discord.ext import commands, tasks
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from config.settings import (
    API_KEY,
    BASE_URL,
    BOT_ACCOUNT_NUMBER,
    DISCORD_TOKEN,
    HEADERS,
    MAXIMUM_CONFIRMATION_CHECKS,
    MINIMUM_CONFIRMATIONS,
    MONGO_HOST,
    MONGO_PORT,
    MONGO_DB_NAME,
)
from utils.blockchain import is_valid_account_number
from utils.discord import send_embed, generate_verification_code, send_verification_message
from utils.network import fetch

bot = commands.Bot(command_prefix='$')


mongo = MongoClient(MONGO_HOST, MONGO_PORT)
database = mongo[MONGO_DB_NAME]

DEPOSITS = database['deposits']
REGISTRATIONS = database['registrations']
USERS = database['users']


def check_confirmations():
    """
    Query unconfirmed deposits from database
    Check bank for confirmation status
    """

    unconfirmed_deposits = DEPOSITS.find({
        'confirmation_checks': {'$lt': MAXIMUM_CONFIRMATION_CHECKS},
        'is_confirmed': False
    })
    for deposit in unconfirmed_deposits:
        transaction_hash = deposit['hash']
        start_block = deposit['blockNumber']

        payload = {
            'module': 'account',
            'action': 'txlist',
            'address': BOT_ACCOUNT_NUMBER,
            'startblock': start_block,
            'endblock': 99999999,
            'page': 1,
            'offset': 10,
            'sort': 'desc',
            'apikey': API_KEY
        }
        try:
            data = fetch(base_url=BASE_URL, params=payload, headers=HEADERS)
            confirmations = data['confirmations']

            if int(confirmations) > MINIMUM_CONFIRMATIONS:
                handle_deposit_confirmation(deposit=deposit)

        except Exception:
            pass

        increment_confirmation_checks(deposit=deposit)


def check_deposit():
    """
    fetch transactions
    insert new deposit into database
    """
    payload = {
        'module': 'account',
        'action': 'txlist',
        'address': BOT_ACCOUNT_NUMBER,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 10,
        'sort': 'desc',
        'apikey': API_KEY
    }
    data = fetch(base_url=BASE_URL, params=payload, headers=HEADERS)
    transactions = data['result']

    for transaction in transactions:
        if int(transaction['confirmations']) > MINIMUM_CONFIRMATIONS:
            try:
                DEPOSITS.insert_one({
                    '_id': transaction['hash'],
                    'amount': transaction['value'],
                    'block_id': transaction['blockHash'],
                    'confirmed': True,
                    'confirmation_checks': 1,
                    'sender': transaction['from']
                })
            except DuplicateKeyError:
                break
        else:
            pass


def handle_deposit_confirmation(*, deposit):
    """
    Update confirmation status of deposit
    Increment balance if existing user or create new user
    """

    DEPOSITS.update_one(
        {'_id': deposit['_id']},
        {
            '$set': {
                'confirmations': True
            }
        }
    )

    registration = REGISTRATIONS.find({
        'account_number': deposit['sender']
    })

    if registration:
        handle_registration(registration=registration)
    else:
        USERS.update_one(
            {'account_number': deposit['sender']},
            {
                '$inc': {
                    'balance': deposit['amount']
                }
            }
        )


def handle_registration(*, registration):
    """
    Ensure account number is not already registered
    Create a new users or update account number of existing user
    """

    discord_user_id = registration['_id']
    account_number_registered = bool(USERS.find_one({'account_number': registration['account_number']}))

    if not account_number_registered:
        existing_user = USERS.find_one({'_id': discord_user_id})

        if existing_user:
            USERS.update_one(
                {'_id': discord_user_id},
                {
                    '$set': {
                        'account_number': registration['account_number']
                    }
                }
            )
        else:
            USERS.insert_one({
                '_id': discord_user_id,
                'account_number': registration['account_number'],
                'balance': 0
            })

    REGISTRATIONS.delete_one({'_id': discord_user_id})


def increment_confirmation_checks(*, deposit):
    """
    Increment the number of confirmation checks for the given deposit
    """
    DEPOSITS.update_one(
        {'_id': deposit['_id']},
        {
            '$inc': {
                'confirmation_checks': 1
            }
        }
    )


@tasks.loop(seconds=60)
async def poll_transactions():
    """
    poll transactions to check for transactions/deposits to the bot account
    """
    print('polling blockchain....')
    check_deposit()
    check_confirmations()


@bot.event
async def on_ready():
    """
    start pulling blockchain
    """
    print('crypto bot is online')
    poll_transactions.start()


@bot.command()
async def register(ctx, account_number):
    """
    &register a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f
    :param account_number:
    :param ctx:
    :return:
    """
    if not is_valid_account_number(account_number):
        await send_embed(
            ctx=ctx,
            title='Invalid',
            description='Invalid account number'
        )
        return

    user = USERS.find_one({'account_number': account_number})

    if user:
        await send_embed(
            ctx=ctx,
            title='Already registered',
            description=f'The account {account_number} has already been registered.'
        )
        return

    discord_user_id = ctx.author.id
    verification_code = generate_verification_code()

    results = REGISTRATIONS.update_one(
        {'_id': discord_user_id},
        {
            '$set': {
                'account_number': account_number,
                'verification_code': verification_code
            }
        },
        upsert=True
    )

    if results.modified_count:
        await send_embed(
            ctx=ctx,
            title='Registration updated',
            description=(
                'Your registration has been updated.'
                'Please follow the instructions sent to you to complete registration'
            )
        )

    else:
        await send_embed(
            ctx=ctx,
            title='Registration created',
            description=(
                'Registration created.'
                'Please follow the instructions sent to you to complete registration'
            )
        )

    await send_verification_message(
        ctx=ctx,
        verification_account_number=account_number,
        verification_code=verification_code
    )


if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
