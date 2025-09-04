import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta


def random_string(length=10):
    letters = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choices(letters, k=length))


def random_date(start_year=2000, end_year=2025):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).isoformat()


def generate_csv(num_rows, output_file):
    with open(output_file, mode="w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "id",
                "int_field",
                "unsigned_field",
                "double_field",
                "numeric_field",
                "text_field",
                "varchar_field",
                "bool_field",
                "date_field",
                "uuid_field",
            ]
        )

        for i in range(1, num_rows + 1):
            row = [
                i,  # id
                random.randint(-1000, 1000),  # int_field
                random.randint(0, 10000),  # unsigned_field
                round(random.uniform(-1000, 1000), 6),  # double_field
                round(random.uniform(-10000, 10000), 2),  # numeric_field
                random_string(20),  # text_field
                random_string(random.randint(1, 100)),  # varchar_field
                random.choice([True, False]),  # bool_field
                random_date(),  # date_field (ISO 8601)
                str(uuid.uuid4()),  # uuid_field
            ]
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate data file in CSV format")
    parser.add_argument("--rows", type=int, default=10000, help="Number of rows to generate")
    parser.add_argument("--output", type=str, default="data.csv", help="Output CSV file name")
    args = parser.parse_args()

    generate_csv(args.rows, args.output)

    print(f"File '{args.output}' created and contains {args.rows} rows.")
