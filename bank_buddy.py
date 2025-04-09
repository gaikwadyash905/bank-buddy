import sqlite3
import os
from datetime import datetime

class BankBuddy:
    def __init__(self, db_name='bank_buddy.db'):
        self.db_name = db_name
        self.setup_database()
    
    def setup_database(self):
        # Check if database exists
        db_exists = os.path.exists(self.db_name)
        
        # Connect to database
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Create tables if database doesn't exist
        if not db_exists:
            # Create accounts table
            self.cursor.execute('''
                CREATE TABLE accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    balance REAL NOT NULL
                )
            ''')
            
            # Create transactions table
            self.cursor.execute('''
                CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')
            
            self.conn.commit()
            print(f"Database '{self.db_name}' created successfully!")
        else:
            print(f"Connected to existing database '{self.db_name}'")
    
    # Account management methods
    def create_account(self, name, balance=0.0):
        self.cursor.execute(
            "INSERT INTO accounts (name, balance) VALUES (?, ?)",
            (name, balance)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_account(self, account_id):
        self.cursor.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,)
        )
        return self.cursor.fetchone()
    
    def get_all_accounts(self):
        self.cursor.execute("SELECT * FROM accounts")
        return self.cursor.fetchall()
    
    def update_account_name(self, account_id, name):
        self.cursor.execute(
            "UPDATE accounts SET name = ? WHERE id = ?",
            (name, account_id)
        )
        self.conn.commit()
    
    def update_balance(self, account_id, amount_change):
        self.cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount_change, account_id)
        )
        self.conn.commit()
    
    # Transaction methods
    def add_transaction(self, account_id, transaction_type, amount):
        self.cursor.execute(
            "INSERT INTO transactions (account_id, type, amount) VALUES (?, ?, ?)",
            (account_id, transaction_type, amount)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_transactions(self):
        self.cursor.execute(
            "SELECT * FROM transactions ORDER BY date DESC"
        )
        return self.cursor.fetchall()
    
    def get_account_transactions(self, account_id):
        self.cursor.execute(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY date DESC",
            (account_id,)
        )
        return self.cursor.fetchall()
    
    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

# Main application loop
def run_app():
    bank = BankBuddy()
    
    while True:
        print("\n" + "=" * 40)
        print("||{:^36}||".format("BANK BUDDY"))
        print("=" * 40)
        print("|| 1. Manage Accounts              ||")
        print("|| 2. Make Transactions            ||")
        print("|| 3. View Transaction History     ||")
        print("|| 4. Exit                         ||")
        print("=" * 40)
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            # Account Management Menu
            while True:
                print("\n" + "-" * 40)
                print("|{:^38}|".format("ACCOUNT MANAGEMENT"))
                print("-" * 40)
                print("| 1. View All Accounts             |")
                print("| 2. Create New Account            |")
                print("| 3. Edit Account Name             |")
                print("| 4. Back to Main Menu             |")
                print("-" * 40)
                
                account_choice = input("Enter your choice (1-4): ")
                
                if account_choice == '1':
                    accounts = bank.get_all_accounts()
                    if not accounts:
                        print("No accounts found.")
                    else:
                        print("\nID | Name | Balance")
                        print("-" * 30)
                        for account in accounts:
                            print(f"{account['id']} | {account['name']} | ${account['balance']:.2f}")
                
                elif account_choice == '2':
                    name = input("Enter account name: ")
                    initial_balance = 0.0
                    balance_input = input("Enter initial balance (default 0.00): ")
                    
                    if balance_input:
                        try:
                            initial_balance = float(balance_input)
                            if initial_balance < 0:
                                print("Initial balance cannot be negative. Using 0.00")
                                initial_balance = 0.0
                        except ValueError:
                            print("Invalid amount. Using default 0.00")
                    
                    account_id = bank.create_account(name, initial_balance)
                    print(f"Account created successfully with ID: {account_id}")
                
                elif account_choice == '3':
                    account_id_input = input("Enter account ID to edit: ")
                    try:
                        account_id = int(account_id_input)
                        account = bank.get_account(account_id)
                        
                        if not account:
                            print(f"No account found with ID: {account_id}")
                        else:
                            print(f"Current name: {account['name']}")
                            new_name = input("Enter new name: ")
                            bank.update_account_name(account_id, new_name)
                            print("Account updated successfully!")
                    except ValueError:
                        print("Invalid account ID. Please enter a number.")
                
                elif account_choice == '4':
                    break
                
                else:
                    print("Invalid choice. Please try again.")
        
        elif choice == '2':
            # Transaction Menu
            accounts = bank.get_all_accounts()
            if not accounts:
                print("No accounts found. Please create an account first.")
                continue
                
            print("\n" + "-" * 40)
            print("|{:^38}|".format("MAKE TRANSACTION"))
            print("-" * 40)
            print("Available accounts:")
            print("ID | Name | Balance")
            print("-" * 30)
            
            for account in accounts:
                print(f"{account['id']} | {account['name']} | ${account['balance']:.2f}")
            
            account_id_input = input("\nEnter account ID: ")
            try:
                account_id = int(account_id_input)
                account = bank.get_account(account_id)
                
                if not account:
                    print(f"No account found with ID: {account_id}")
                    continue
                
                print(f"\nSelected: {account['name']} (Balance: ${account['balance']:.2f})")
                print("-" * 40)
                print("| 1. Deposit                      |")
                print("| 2. Withdraw                     |")
                print("-" * 40)
                
                tx_choice = input("Enter choice (1-2): ")
                
                if tx_choice not in ['1', '2']:
                    print("Invalid choice.")
                    continue
                
                amount_input = input("Enter amount: $")
                try:
                    amount = float(amount_input)
                    if amount <= 0:
                        print("Amount must be positive.")
                        continue
                        
                    if tx_choice == '1':
                        # Deposit
                        bank.add_transaction(account_id, "deposit", amount)
                        bank.update_balance(account_id, amount)
                        print(f"Successfully deposited ${amount:.2f}")
                    else:
                        # Withdraw
                        if amount > account['balance']:
                            print("Insufficient funds.")
                            continue
                        
                        bank.add_transaction(account_id, "withdraw", -amount)
                        bank.update_balance(account_id, -amount)
                        print(f"Successfully withdrew ${amount:.2f}")
                
                except ValueError:
                    print("Invalid amount. Please enter a valid number.")
            
            except ValueError:
                print("Invalid account ID. Please enter a number.")
        
        elif choice == '3':
            # Transaction History
            print("\n" + "-" * 40)
            print("|{:^38}|".format("TRANSACTION HISTORY"))
            print("-" * 40)
            print("| 1. View All Transactions          |")
            print("| 2. View Account Transactions      |")
            print("-" * 40)
            
            history_choice = input("Enter choice (1-2): ")
            
            if history_choice == '1':
                transactions = bank.get_all_transactions()
                if not transactions:
                    print("No transactions found.")
                else:
                    print("\nID | Account | Type | Amount | Date")
                    print("-" * 60)
                    for tx in transactions:
                        account = bank.get_account(tx['account_id'])
                        account_name = account['name'] if account else "Unknown"
                        amount_str = f"${abs(tx['amount']):.2f}"
                        print(f"{tx['id']} | {account_name} | {tx['type']} | {amount_str} | {tx['date']}")
            
            elif history_choice == '2':
                account_id_input = input("Enter account ID: ")
                try:
                    account_id = int(account_id_input)
                    account = bank.get_account(account_id)
                    
                    if not account:
                        print(f"No account found with ID: {account_id}")
                        continue
                    
                    transactions = bank.get_account_transactions(account_id)
                    if not transactions:
                        print(f"No transactions found for account: {account['name']}")
                    else:
                        print(f"\nTransactions for: {account['name']}")
                        print("ID | Type | Amount | Date")
                        print("-" * 50)
                        for tx in transactions:
                            amount_str = f"${abs(tx['amount']):.2f}"
                            print(f"{tx['id']} | {tx['type']} | {amount_str} | {tx['date']}")
                
                except ValueError:
                    print("Invalid account ID. Please enter a number.")
            
            else:
                print("Invalid choice.")
        
        elif choice == '4':
            # Exit application
            bank.close()
            print("Thank you for using Bank Buddy! Goodbye.")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    run_app()
