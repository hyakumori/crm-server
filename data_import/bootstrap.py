#!/usr/bin/env python3
import importlib
import os
import pickle
from pathlib import Path

import click
import pandas as pd
from django.db import transaction
from dotenv import load_dotenv

from data_import.lib.utils import prepare_env

load_dotenv(Path(__file__).parent.joinpath(".env"))

EXCEL_FILE_PATH = Path(os.getenv("ORIGINAL_XLSX_PATH"))
EXCEL_PICKLE_FILE_PATH = EXCEL_FILE_PATH.parent.joinpath(
    EXCEL_FILE_PATH.name + ".pickle"
)
MASTER_DATA_PICKLE_FILE_PATH = EXCEL_FILE_PATH.parent.joinpath("master-data.pickle")


@click.group()
def cli():
    pass


@cli.command()
def xlsx_to_pickle():
    print("Importing from XLSX ... ", end="", flush=True)
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=None, parse_dates=True)
    print("DONE")

    print("Writing to pickle ... ", end="", flush=True)
    pickle.dump(df, open(EXCEL_PICKLE_FILE_PATH, "wb"))
    print("DONE")

    return df


def load_data():
    if not EXCEL_PICKLE_FILE_PATH.exists():
        df = xlsx_to_pickle()
    else:
        print("Importing from PICKLE ... ", end="", flush=True)
        df = pickle.load(open(EXCEL_PICKLE_FILE_PATH, "rb"))
        print("DONE")

    customer = df["顧客情報一覧"]
    forest = df["森林情報一覧"]

    return dict(customer=customer, forest=forest, )


def import_customer(data):
    from data_import.importer.customer import CustomerImporter as Importer

    importer = Importer(data.get("customer"))
    importer.run()
    importer.validate()
    return importer


def import_forest(data):
    from data_import.importer.forest import ForestImporter as Importer

    importer = Importer(data.get("forest"))
    importer.run()
    importer.validate()
    return importer


def generate_master_pickle(forest, customer):
    if not click.confirm("This will override old master file. Continue?"):
        return

    try:
        master = pickle.load(open(MASTER_DATA_PICKLE_FILE_PATH, "rb"))
    except OSError:
        master = dict()

    data = load_data()

    if customer:
        print("Importing Customer ... ", end="", flush=True)
        master["customer"] = import_customer(data).results
        print("OK")

    if forest:
        print("Importing Forest ... ", end="", flush=True)
        master["forest"] = import_forest(data).results
        print("OK")

    if forest or customer:
        print("Writing ... ", end="", flush=True)
        pickle.dump(master, open(MASTER_DATA_PICKLE_FILE_PATH, "wb"))


@cli.command("gen-master")
@click.option("--forest", default=False, help="import forest", type=bool)
@click.option("--customer", default=False, help="import customer", type=bool)
def command_generate_master(forest, customer):
    generate_master_pickle(forest, customer)
    print("DONE")


@cli.command()
def rm_xlsx_pickle():
    if not click.confirm("Do you want to continue?"):
        return

    if EXCEL_PICKLE_FILE_PATH.exists():
        os.remove(EXCEL_PICKLE_FILE_PATH)

    print(f"Deleted {EXCEL_PICKLE_FILE_PATH}")


@cli.command()
def truncate_db():
    """
    This will truncate all related database tables. Use with caution.
    """
    if not click.confirm("Do you REALLY want to continue?"):
        return

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            """
            truncate table crm_forestcustomer cascade;
            truncate table crm_customercontact cascade;
            truncate table crm_attachment cascade;
            truncate table crm_archiveforest cascade;
            truncate table crm_forest cascade;
            truncate table crm_archivecustomer cascade;
            truncate table crm_archive cascade;
            truncate table crm_contact cascade;
            truncate table crm_customer cascade;
        """
        )

    print("OK")


def insert_db(forest, customer):
    prepare_env()

    data = pickle.load(open(MASTER_DATA_PICKLE_FILE_PATH, "rb"))

    if customer:
        from data_import.db_importer.customer import CustomerDbImporter

        print("INSERTING CUSTOMER")
        CustomerDbImporter.insert_db(data["customer"])
        print("DONE")

    if forest:
        from data_import.db_importer.forest import ForestDbImporter

        print("INSERTING FOREST")
        ForestDbImporter.insert_db(data["forest"])
        print("DONE")


@cli.command("insert-db")
@click.option("--forest", default=False, help="import forest", type=bool)
@click.option("--customer", default=False, help="import customer", type=bool)
def command_insert_db(forest, customer):
    if not click.confirm("This command will insert data into database, continue?"):
        return
    insert_db(forest, customer)
    print("FINISHED")


def create_link_forest_customer():
    prepare_env()

    data = pickle.load(open(MASTER_DATA_PICKLE_FILE_PATH, "rb"))
    from data_import.db_importer.relations import RelationDbImporter

    importer = RelationDbImporter(data)
    importer.search_customers()
    importer.link_forest_customer()


@cli.command(
    "link-forest-customer",
    help="Check and insert forest, customer relation. Also generate intermediate pickle under db_importer."
         + "Remove pickle file if want to refresh database information (eg: reimport)",
)
def command_link_forest_customer():
    if not click.confirm(
        "This command will link customer and forest together, can take some times to finish, continue?"
    ):
        return
    create_link_forest_customer()
    print("DONE")


@cli.command("migrate", help="simply run migrate task")
@click.option("--name", required=True, type=str, help="name of the migration")
def command_migrate(name):
    migration_file = f"{name}.py"
    migration_path = Path(__file__).parent.joinpath("migrations")

    if not migration_path.joinpath(migration_file).exists():
        print(f"{migration_file} not found under {migration_path}")
        print("Options are: ")

        for file in os.listdir(migration_path):
            if file.name != "__init__.py":
                print(file.name.replace(".py", ""))

    prepare_env()

    migrate_function_module = f"data_import.migrations.{name}"
    module = importlib.import_module(migrate_function_module)

    if not click.confirm(f"About to run migration: {name}, continue?"):
        return

    try:
        with transaction.atomic():
            migration = module.Migration()
            migration.migrate()
    except Exception as e:
        module.rollback()


if __name__ == "__main__":
    cli()
