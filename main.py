from random import shuffle, randint
import sqlite3
from inquirer import List, Text, prompt, Checkbox, Path

# Database connections
cursor = None
conn = None

# Table operations
SELECT_ALL = "SELECT * FROM partecipants"
CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS partecipants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            gift TEXT
        );
    """
INSERT_PARTECIPANT = """
        INSERT INTO partecipants (name)
        VALUES (?)
    """
INSERT_GIFT = """
            UPDATE partecipants
            SET gift = ?
            WHERE name = ?
        """


# Initialize the database creating the table if it doesn't exist
def init_db():
    global cursor, conn
    conn = sqlite3.connect("secretsanta.sqlite3")
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE)
    conn.commit()


# Add a new participant
def add_participant():
    global cursor, conn
    name = prompt([Text('name', message="Enter the name of the participant")])['name']
    cursor.execute(INSERT_PARTECIPANT, (name, ))
    conn.commit()
    print(f"Added participant {name}\n\n")


# Load participants from a file
def load_from_file():
    global cursor, conn
    file = prompt([Path('file', message="Enter the file name", exists=True)])['file']
    with open(file, "r") as f:
        for name in f.readlines():
            name = name.replace("\n", "")
            try:
                cursor.execute(INSERT_PARTECIPANT, (name, ))
            except sqlite3.IntegrityError:
                print(f"\t{name} already exists")
    conn.commit()
    print("Loaded!\n")


def delete_partecipants():
    global cursor, conn
    cursor.execute(SELECT_ALL)
    result = cursor.fetchall()
    partecipants = []
    for row in result:
        partecipants.append(row[1])
    names = prompt([Checkbox('names', message="Enter the names of the participants", choices=partecipants)])['names']
    for name in names:
        cursor.execute(f"DELETE FROM partecipants WHERE name = '{name}'")
    conn.commit()
    print(f"Deleted participant {names}\n\n")

# Show all participants
def show_participants():
    global cursor
    cursor.execute(SELECT_ALL)
    print("\n\nPartecipants:")
    for i, row in enumerate(cursor.fetchall(), start=1):
        print(f"\t{i}) {row[1]}")


# Show all gifted participants
def show_gifted():
    global cursor
    cursor.execute(SELECT_ALL)
    for row in cursor.fetchall():
        if row[2] != None:
            print(row[2])


# Generate the gift list
def generate_gift_list():
    global cursor, conn

    cursor.execute(SELECT_ALL)
    partecipants = cursor.fetchall()
    to_gift = partecipants.copy()

    shuffle(partecipants)
    shuffle(to_gift)

    while len(partecipants) != 0:
        secret_santa = partecipants.pop()

        extraction = randint(0, len(to_gift) - 1)
        gift_santa = to_gift[extraction]

        while (secret_santa[1] == gift_santa[1]):
            extraction = randint(0, len(to_gift) - 1)
            gift_santa = to_gift[extraction]

        cursor.execute(INSERT_GIFT, (gift_santa[1], secret_santa[1]))

        del to_gift[extraction]
    conn.commit()
    print("Gift list generated!\n")


def print_gifts():
    global cursor
    cursor.execute(SELECT_ALL)
    for i, row in enumerate(cursor.fetchall(), start=1):
        print(f"{i}) {row[1]} -> {row[2]}")


# Main function, select the action to perform
def main():
    options = [
        'Add new partecipant', 'Load all partecipants from file', 'Delete partecipants',
        'Show all partecipants', 'Show all gifted partecipents',
        'Generate the gift list', 'Print the gift list', 'Exit'
    ]
    questions = [
        List('action',
                      message="What do you want to do?",
                      choices=options)
    ]
    init_db()
    print("Welcome to the Secret Santa Generator!")
    while True:

        choice = prompt(questions)
        match choice['action']:
            case 'Add new partecipant':
                add_participant()
            case 'Load all partecipants from file':
                load_from_file()
            case 'Delete partecipants':
                delete_partecipants()
            case 'Show all partecipants':
                show_participants()
            case 'Show all gifted partecipents':
                show_gifted()
            case 'Generate the gift list':
                generate_gift_list()
            case 'Print the gift list':
                print_gifts()
            case 'Exit':
                print("Bye!")
                break
            case _:
                print("Invalid choice!")


# Run the main function
if __name__ == "__main__":
    main()
