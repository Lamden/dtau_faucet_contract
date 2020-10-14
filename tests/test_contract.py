#tests/test_contract.py
import unittest
import base64
from contracting.client import ContractingClient
client = ContractingClient()

initial_args = {
    'owner': 'stu_man',
    'wait_period_hours': 0,
    'max_send': 2,
    'drip': 1,
    'currency_symbol': 'jTAU'
}

new_args = {
    'owner': 'jeff_man',
    'wait_period_hours': 1,
    'max_send': 100,
    'drip': 100,
    'currency_symbol': 'dTAU'
}

icon_svg_base64 = ""

with open('./currency.py') as f:
    code = f.read()
    client.submit(code, name='currency')
with open('../contracts/con_faucet.py') as f:
    code = f.read()
    client.submit(
        code,
        name='con_faucet',
        constructor_args=initial_args
    )

class MyTestCase(unittest.TestCase):
    con_faucet = None
    currency_contract = None

    def change_signer(self, name):
        client.signer = name
        self.con_faucet = client.get_contract('con_faucet')
        self.currency_contract = client.get_contract('currency')

    def test_1_seed_constants(self):
        self.change_signer('stu_man')
        print("TEST SEED CONSTANTS")

        self.assertEqual(self.con_faucet.quick_read('S', 'OWNER'), initial_args['owner'])
        self.assertEqual(self.con_faucet.quick_read('S', 'WAIT_PERIOD_HOURS'), initial_args['wait_period_hours'])
        self.assertEqual(self.con_faucet.quick_read('S', 'MAX_SEND'), initial_args['max_send'])
        self.assertEqual(self.con_faucet.quick_read('S', 'DRIP'), initial_args['drip'])
        self.assertEqual(self.con_faucet.quick_read('S', 'CURRENCY_SYMBOL'), initial_args['currency_symbol'])

    def test_1a_change_constants(self):
        self.change_signer('stu_man')
        print("TEST CHANGE OWNER")

        self.con_faucet.change_wait_period_hours(wait_period_hours=new_args['wait_period_hours'])
        self.con_faucet.change_max_send(max_send=new_args['max_send'])
        self.con_faucet.change_drip(drip=new_args['drip'])
        self.con_faucet.change_currency_symbol(currency_symbol=new_args['currency_symbol'])
        self.con_faucet.change_owner(owner=new_args['owner'])

        self.assertEqual(self.con_faucet.quick_read('S', 'OWNER'), new_args['owner'])
        self.assertEqual(self.con_faucet.quick_read('S', 'WAIT_PERIOD_HOURS'), new_args['wait_period_hours'])
        self.assertEqual(self.con_faucet.quick_read('S', 'MAX_SEND'), new_args['max_send'])
        self.assertEqual(self.con_faucet.quick_read('S', 'DRIP'), new_args['drip'])
        self.assertEqual(self.con_faucet.quick_read('S', 'CURRENCY_SYMBOL'), new_args['currency_symbol'])

    def test_1b_assert_owner(self):
        self.change_signer('stu_man')
        print("TEST ASSERT OWNER")

        self.assertRaises(
            AssertionError,
            lambda: self.con_faucet.change_owner(owner=new_args['owner'])
        )

    def test_2_get(self):
        self.change_signer('stu_man')
        print("TEST GET")
        self.con_faucet.get()

        self.assertEqual(self.currency_contract.quick_read('balances', 'stu_man'), new_args['drip'])

    def test_2a_get_time_limit(self):
        self.change_signer('stu_man')
        print("TEST TIME LIMIT")
        self.assertRaises(
            AssertionError,
            lambda: self.con_faucet.get()
        )

        self.assertEqual(self.currency_contract.quick_read('balances', 'stu_man'), new_args['drip'])

    def test_3_give(self):
        self.change_signer('alex_man')
        print("TEST GIVE")
        self.con_faucet.give(account='jeff_man')
        self.assertEqual(self.currency_contract.quick_read('balances', 'jeff_man'), new_args['drip'])

    def test_3a_give_time_limit(self):
        self.change_signer('alex_man')
        print("TEST GIVE TIME LIMIT")

        self.assertRaises(
            AssertionError,
            lambda: self.con_faucet.give(account='jeff_man')
        )
        self.assertEqual(self.currency_contract.quick_read('balances', 'jeff_man'), new_args['drip'])


    def test_3b_give_max_limit_signer(self):
        print("TEST GIVE MAX LIMIT - SIGNER")
        # disable wait time for this test
        self.change_signer('jeff_man')
        self.con_faucet.change_wait_period_hours(wait_period_hours=0)

        self.change_signer('alex_man')
        self.assertRaises(
            AssertionError,
            lambda: self.con_faucet.give(account='stu_man')
        )

        self.assertEqual(self.currency_contract.quick_read('balances', 'stu_man'), new_args['drip'])

        # change wait time back
        self.change_signer('jeff_man')
        self.con_faucet.change_wait_period_hours(wait_period_hours=1)

    def test_3c_give_max_limit_2(self):
        print("TEST GIVE MAX LIMIT- RECEIVER")
        # disable wait time for this test
        self.change_signer('jeff_man')
        self.con_faucet.change_wait_period_hours(wait_period_hours=0)

        self.change_signer('doug_man')
        self.assertRaises(
            AssertionError,
            lambda: self.con_faucet.give(account='stu_man')
        )
        self.assertEqual(self.currency_contract.quick_read('balances', 'stu_man'), new_args['drip'])

        # change wait time back
        self.change_signer('jeff_man')
        self.con_faucet.change_wait_period_hours(wait_period_hours=1)

    def test_3d_give_as_owner(self):
        print("TEST GIVE AS OWNER")
        #change owener to alex_man who has already given his daily limits
        self.change_signer('jeff_man')
        self.con_faucet.change_owner(owner='alex_man')

        self.change_signer('alex_man')
        self.con_faucet.give(account='doug_man')
        self.assertEqual(self.currency_contract.quick_read('balances', 'doug_man'), new_args['drip'])

        # Change owner back
        self.con_faucet.change_owner(owner='jeff_man')

    def test_4_contract_no_call(self):
        self.change_signer('con_contract')
        print("TEST CONTRACT CAN'T CALL")
        self.assertRaises(
            AssertionError,
            lambda: self.con_faucet.get()
        )
        self.assertEqual(self.currency_contract.quick_read('balances', 'con_contract'), None)

    def test_5_empty_faucet(self):
        self.change_signer('jeff_man')
        print("TEST EMPTY FAUCET")
        self.con_faucet.empty_faucet()
        self.assertEqual(self.currency_contract.quick_read('balances', 'jeff_man'), 200)
if __name__ == '__main__':
    unittest.main()