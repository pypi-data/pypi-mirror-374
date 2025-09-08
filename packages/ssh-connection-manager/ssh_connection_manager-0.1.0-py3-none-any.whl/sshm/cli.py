import os
import sys
import re
from typing import List

from fuzzyfinder.main import fuzzyfinder
from sqlalchemy import select
from sqlalchemy.orm import Session

import subprocess
from .data import Connection, engine
from .utils import print_index_table

def start_connection(args: list[str]):
    if args[0] != "ssh":
        args.insert(0, "ssh")
    subprocess.run(args)

def connect_from_list(connections: List[Connection]):
    args = None

    while True:
        print_index_table(connections)
        try:
            index = int(input("Select session: "))
            if index < 1 or index > len(connections):
                raise IndexError
            args = connections[index - 1].args
            break
        except (ValueError, IndexError):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Invalid selection. Please enter a valid number between 0 and {len(connections) - 1}.")

    start_connection(args)

def connect_from_new(host: str, args: list[str]):
    with Session(engine) as session:
        stmt = select(Connection).where(Connection.host == host)
        existing_connection = session.scalars(stmt).one_or_none()
        if not existing_connection:
            new_connection = Connection(
                host=host,
                args=args,
            )
            session.add(new_connection)
            session.commit()

    args.insert(0, "ssh")
    # Open SSH in the current terminal (blocking until exit)
    start_connection(args)

def run():
    try:
        all_connections = List[Connection]

        with Session(engine) as session:
            all_connections = session.query(Connection).all()

        if len(sys.argv) < 2:
            connect_from_list(all_connections)
            return

        if len(sys.argv) == 2:
            host_names = list(map(lambda c: c.host, all_connections))
            suggestions = list(fuzzyfinder(sys.argv[1], host_names))
            found_connections = [c for c in all_connections if c.host in suggestions]
            if len(found_connections) == 1:
                start_connection(found_connections[0].args)
                sys.exit(0)
            elif len(suggestions) > 1:
                connect_from_list(found_connections)
                sys.exit(0)

        user_host_pattern = re.compile(r"^[^@]+@[^@]+$")
        ssh_args = sys.argv[1:]


        host = next((arg for arg in ssh_args if user_host_pattern.match(arg)), None)

        if not host:
            print("missing host")
            sys.exit(1)
        else:
            connect_from_new(host, ssh_args)

    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    run()