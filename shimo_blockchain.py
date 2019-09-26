# 4/2019

from functools import reduce
from collections import OrderedDict
import json
import pickle

from util_hash import hash_string_256, hash_block

SHIMOCOIN = 10

blockchain = []
open_transactions = []

owner = 'CJ'
participants = {'CJ'}


def load_data():
    global blockchain
    global open_transactions

    try:
        with open('blockchain.txt', mode='r') as f:
            # file_content = pickle.loads(f.read())
            file_content = f.readlines()
            print(file_content)

            # converts data into binary via pickle for string to object conversion
            # blockchain = file_content['chain']
            # open_transactions = file_content['ot']

            # Converts data into json for sufficient string conversion into objects
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []

            for block in blockchain:
                updated_block = {
                    'previous_hash' : block['previous_hash'],
                    'index': block['index'],
                    'proof': block['proof'],
                    'transactions': [OrderedDict([
                        ('sender', tx['sender']),
                        ('recipient', tx['recipient']),
                        ('amount', tx['amount'])
                    ]) for tx in block['transactions']]
                }
                updated_blockchain.append(updated_block)

            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1])
            updated_transactions = []

            for tx in open_transactions:
                updated_transaction = OrderedDict([
                        ('sender', tx['sender']),
                        ('recipient', tx['recipient']),
                        ('amount', tx['amount'])
                    ])
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions

    except IOError:
        genesis_block = {'previous_hash': '',
                         'index': 0,
                         'transactions': [],
                         'proof': 101
                         }

        blockchain = [genesis_block]
        open_transactions = []
    finally:
        print('Cleanup!')


load_data()


def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:
            json.dump(blockchain, f)
            f.write('\n')
            json.dump(open_transactions, f)
            # save_data = {
            #     'chain': blockchain,
            #     'ot': open_transactions
            # }
            # f.write(pickle.dumps(save_data))
    except IOError:
        print('Saving failed')


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    print(guess)
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:3] == '369'


def proof_of_work():
    last_block = blockchain[-1] # selects a list element from the right of the array
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof +=1
    return proof


def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]

    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0 )
    
    return amount_received - amount_sent


def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])

    if sender_balance >= transaction['amount']:
        return True
    else:
        return False 


def add_transaction(recipient, sender=owner, amount=1.0):
    transaction = OrderedDict([
        ('sender', sender),
        ('recipient', recipient),
        ('amount', amount)
        ])

    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    else:
        return False


def mine_block():
    """Transaction Variables/Metadata"""
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)

    proof = proof_of_work()
    
    """Mining reward"""
    reward_transaction = OrderedDict([
        ('sender','SHIMO_MINER'),
        ('recipient', owner),
        ('amount', SHIMOCOIN)
        ])
    
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    
    block = {'previous_hash': hashed_block,
             'index': len(blockchain),
             'transactions': copied_transactions,
             'proof': proof
             }

    blockchain.append(block)
    save_data()
    return True


def get_transaction_value():
    tx_recipient = input('Enter the recipient of this transaction: ')
    tx_amount = float(input('Please enter your transaction amount: '))
    return tx_recipient, tx_amount


def get_user_choice():
    user_input = input('Option Selection: ')
    return user_input


def print_blockchain_elements():
    for block in blockchain:
        print('Outputting Blocks')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid!!!')
            return False
    return True


waiting_for_input = True

# A while loop for the user input interface
# It's a loop that exits once waiting_for_input becomes False or when break is called
while waiting_for_input:
    print('******Permafrost Blockchain******')
    print('***System Options***')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Output participants on network')
    print('h: Manipulate the chain')
    print('q: Quit')

    user_choice = get_user_choice()

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data

        # Add the transaction amount to the blockchain
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == 'h':
        # Make sure that you don't try to "hack" the blockchain if it's empty
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Admin', 'recipient': 'CJ', 'amount': 33.0}]
            }
    elif user_choice == 'q':
        # This will lead to the loop to exist because it's running condition becomes False
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a correct value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        # Break out of the loop
        break
    print('Balance of {}: {:6.2f}'.format('CJ', get_balance('CJ')))
else:
    print('User has left!')


print('Done!')
