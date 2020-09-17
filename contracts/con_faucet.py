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
    transfer(ctx.caller)

@export
def give(account: str):
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

def assert_owner():
    assert ctx.caller == S['OWNER'], 'Only ' + S['OWNER'] + ' can call this method.'

def check_faucet_balance():
    faucet_bal = currency.balance_of(ctx.this)
    assert faucet_bal > S['DRIP'], "Faucet needs Funding. Balance " + str(faucet_bal) + ' ' + S['CURRENCY_SYMBOL']

def transfer(account):
    # Create wait period time delta
    WAIT_PERIOD = datetime.timedelta(hours=S['WAIT_PERIOD_HOURS'])

    # Check if caller has previously used faucet
    if S[account]:
        # Prevent 1 vk from using facet too many times
        assert S[account, 'amount'] < S['MAX_SEND'], "Account has received MAX amount from faucet."

        # Assert last call was more than a day ago
        assert WAIT_PERIOD < now - S[account], "Can only call once per day."

    # Transfer dTAU to caller
    currency.transfer(S['DRIP'], account)

    # Set set last call time to NOW for caller
    S[account] = now
    # Keep a running total of TAU given to a specific address
    if not S[account, 'amount']:
        S[account, 'amount'] = S['DRIP']
    else:
        S[account, 'amount'] = S[account, 'amount'] + S['DRIP']