import random
import sqlite3


class Bank:
    IIN = "400000"
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()

    def __random_generator(self, n):
        number = ""
        for i in range(n):
            number += str(random.randint(0, 9))
        return number

    def luhn_sum(self, n):
        N = [int(x) for x in n]
        n = map(lambda x: 2 * N[x] if not x % 2 else N[x], range(len(N)))
        n = map(lambda x: x - 9 if x > 9 else x, n)
        return sum(n)

    def luhn_generator(self, num):
        sum2 = self.luhn_sum(num)
        dv = 0
        while sum2 % 10:
            dv += 1
            sum2 += 1
        return num + str(dv)

    def luhn_verify(self, num):
        sum2 = self.luhn_sum(num[:-1])
        dv = int(num[-1])
        if (sum2 + dv) % 10:
            return False
        return True

    def check_card_number(self, card_number):
        if self.luhn_verify(card_number):
            sql = f"SELECT EXISTS (SELECT 1 FROM card WHERE number = {card_number}) "
            return self.conn.execute(sql).fetchone()[0]
        return 0

    def check_pin(self, pin):
        sql = f"SELECT EXISTS (SELECT 1 FROM card WHERE pin = {pin})"
        return self.conn.execute(sql).fetchone()[0]

    def get_balance(self, id):
        sql = f"SELECT balance FROM card WHERE id = {id}"
        return self.conn.execute(sql).fetchone()[0]

    def get_id(self, card_number):
        sql = f"SELECT id FROM card WHERE number = {card_number}"
        return self.conn.execute(sql).fetchone()[0]

    def create_account(self):
        card_number = self.IIN + self.__random_generator(9)

        while self.check_card_number(card_number):
            card_number = self.IIN + self.__random_generator(9)
        card_number = self.luhn_generator(card_number)
        pin = self.__random_generator(4)
        sql = f"INSERT INTO card (number, pin) VALUES" \
              f" ({card_number}, {pin})"
        self.cur.execute(sql)
        self.conn.commit()
        print("Your card has been created")
        print("Your card numbers:")
        print(card_number)
        print("Your card PIN:")
        print(pin)
        print("")

    def log_account(self):
        card_number = input("\nEnter your card number:")
        pin = input("Enter your PIN:")

        if self.check_card_number(card_number) and self.check_pin(pin):
            print("\nYou have successfully logged in!")
            self.account_menu(self.get_id(card_number))
        else:
            print("\nWrong card number or PIN!\n")

    def add_income(self, id):
        income = int(input("Enter income:\n"))
        if income < 0:
            print("You can't add a negative income.")
            return

        sql = f"SELECT balance FROM card WHERE id = {id}"
        income += self.conn.execute(sql).fetchone()[0]
        sql = f"UPDATE card SET balance = {income} WHERE id = {id}"
        self.cur.execute(sql)
        self.conn.commit()
        print("Income wad added!\n")
        return

    def do_transfer(self, id):
        print("\nTransfer")
        card = input("Enter card number:\n")
        if not self.luhn_verify(card):
            print("Probably you made mistake in the card number. Please try "
                  "again!")
            return
        if not self.check_card_number(card):
            print("Such card does not exist.")
            return

        transfer = int(input("How much money you want to transfer:\n"))

        if transfer > self.get_balance(id):
            print("Not enough money!")
            return

        sql = f"SELECT balance FROM card WHERE number = {card}"
        amount = transfer + self.conn.execute(sql).fetchone()[0]
        sql = f"UPDATE card SET balance = {amount} WHERE number = {card}"
        self.cur.execute(sql)
        self.conn.commit()
        sql = f"SELECT balance FROM card WHERE id = {id}"
        balance = self.conn.execute(sql).fetchone()[0] - transfer
        sql = f"UPDATE card SET balance = {balance} WHERE id = {id}"
        self.cur.execute(sql)
        self.conn.commit()
        print("Success!")
        return

    def close_account(self, id):
        sql = f"DELETE FROM card WHERE id = {id}"
        self.cur.execute(sql)
        self.conn.commit()
        print("Bye")
        return

    def account_menu(self, id):
        while True:
            opt = int(input("\n1.Balance\n"
                            "2. Add income\n"
                            "3. Do transfer\n"
                            "4. Close account\n"
                            "5. Log out\n"
                            "0. Exit\n"))

            if opt == 1:
                print(f"\nBalance: {self.get_balance(id)}")
            elif opt == 2:
                self.add_income(id)
            elif opt == 3:
                self.do_transfer(id)
            elif opt == 4:
                self.close_account(id)
                break
            elif opt == 5:
                break
            elif opt == 0:
                exit()
            else:
                pass


bank = Bank()

while True:
    print("1. Create an account\n"
          "2. Log into account\n"
          "0. Exit")
    opt = input()
    if opt == "1":
        bank.create_account()
    elif opt == "2":
        bank.log_account()
    elif opt == "0":
        break
    else:
        pass
