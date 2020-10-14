import currency

S = Hash(default_value='')

@construct
def seed(owner: str, wait_period_hours: int, max_send: float, drip: float, currency_symbol: str):
    S['OWNER'] = owner
    S['WAIT_PERIOD_HOURS'] = wait_period_hours
    S['MAX_SEND'] = max_send
    S['DRIP'] = drip
    S['CURRENCY_SYMBOL'] = currency_symbol

@export
def get():
    run_checks()
    transfer(ctx.signer)

@export
def give(account: str):
    run_checks()
    if is_owner():
        transfer_as_owner(account)
    else:
        transfer(account)

@export
def change_wait_period_hours(wait_period_hours: int):
    assert_owner()
    S['WAIT_PERIOD_HOURS'] = wait_period_hours

@export
def change_max_send(max_send: float):
    assert_owner()
    S['MAX_SEND'] = max_send

@export
def change_drip(drip: float):
    assert_owner()
    S['DRIP'] = drip

@export
def change_owner(owner: str):
    assert_owner()
    S['OWNER'] = owner

@export
def change_currency_symbol(currency_symbol: str):
    assert_owner()
    S['CURRENCY_SYMBOL'] = currency_symbol

@export
def empty_faucet():
    assert_owner()
    currency.transfer(currency.balance_of(ctx.this), S['OWNER'])

def is_owner():
    return ctx.signer == S['OWNER']

def assert_owner():
    assert is_owner(), 'Only ' + S['OWNER'] + ' can call this method.'

def run_checks():
    assert_caller_is_signer()
    check_faucet_balance()
    assert_not_contract(ctx.signer)

def assert_caller_is_signer():
    assert ctx.caller == ctx.signer, 'faucet can only be called directly'

def assert_not_contract(to: str):
    assert len(to) > 4, 'Receiver Account not long enough'
    assert to[0:4].lower() != "con_", 'The faucet cannot be called by contracts.'

def check_faucet_balance():
    faucet_bal = currency.balance_of(ctx.this)
    assert faucet_bal >= S['DRIP'], "Faucet needs Funding. Balance " + str(faucet_bal) + ' ' + S['CURRENCY_SYMBOL']

def transfer(to: str):
    # Create wait period time delta
    WAIT_PERIOD = datetime.timedelta(hours=S['WAIT_PERIOD_HOURS'])

    # Check if signer has used the faucet before
    if S[ctx.signer]:
        # Assert last call was more than a day ago
        assert WAIT_PERIOD <= now - S[ctx.signer], "Can only call once per day."

        # Prevent 1 account from initiating too many sends.
        assert S[ctx.signer, 'amount'] < S['MAX_SEND'], "This account has given too much currency."

    # Check if the "to" account has used the faucet before
    if S[to]:
        # Assert the to account hasn't received currency today
        assert WAIT_PERIOD <= now - S[to], "Can only call once per day."

        # Prevent 1 account from receiving too much currency.
        assert S[to, 'amount'] < S['MAX_SEND'], "This account has received MAX amount from faucet."

    # Transfer currency to caller
    currency.transfer(S['DRIP'], to)

    # Set set last call time to NOW for signer
    S[ctx.signer] = now

    if not S[ctx.signer, 'amount']:
        S[ctx.signer, 'amount'] = S['DRIP']
    else:
        S[ctx.signer, 'amount'] = S[ctx.signer, 'amount'] + S['DRIP']

    # Set the receiving account has already go sent currency today
    S[to] = now

    if ctx.signer != to:
        # Keep a running total of currency given to a specific address
        if not S[to, 'amount']:
            S[to, 'amount'] = S['DRIP']
        else:
            S[to, 'amount'] = S[to, 'amount'] + S['DRIP']

def transfer_as_owner(to: str):
    # Create wait period time delta
    WAIT_PERIOD = datetime.timedelta(hours=S['WAIT_PERIOD_HOURS'])

    # Check if caller has previously used faucet
    if S[to]:
        # Prevent 1 vk from using facet too many times
        assert S[to, 'amount'] < S['MAX_SEND'], "Account has received MAX amount from faucet."

        # Assert last call was more than a day ago
        assert WAIT_PERIOD <= now - S[to], "Can only call once per day."

    # Transfer currency to caller
    currency.transfer(S['DRIP'], to)

    # Set set last call time to NOW for caller
    S[to] = now
    # Keep a running total of currency given to a specific address
    if not S[to, 'amount']:
        S[to, 'amount'] = S['DRIP']
    else:
        S[to, 'amount'] = S[to, 'amount'] + S['DRIP']