

import os
import json
import glob
import argparse


def extract_unique_contexts(input_directory, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    jsonl_files = glob.glob(os.path.join(input_directory, "*.jsonl"))
    print(f"Found {len(jsonl_files)} JSONL files.")
# fmt: off  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlZGc013PT06NmY0ZjBlOGY=

    for file_path in jsonl_files:
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_unique_contexts.json"
        output_path = os.path.join(output_directory, output_filename)

        unique_contexts_dict = {}

        print(f"Processing file: {filename}")
# type: ignore  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlZGc013PT06NmY0ZjBlOGY=

        try:
            with open(file_path, "r", encoding="utf-8") as infile:
                for line_number, line in enumerate(infile, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        json_obj = json.loads(line)
                        context = json_obj.get("context")
                        if context and context not in unique_contexts_dict:
                            unique_contexts_dict[context] = None
                    except json.JSONDecodeError as e:
                        print(
                            f"JSON decoding error in file {filename} at line {line_number}: {e}"
                        )
        except FileNotFoundError:
            print(f"File not found: {filename}")
            continue
        except Exception as e:
            print(f"An error occurred while processing file {filename}: {e}")
            continue

        unique_contexts_list = list(unique_contexts_dict.keys())
        print(
            f"There are {len(unique_contexts_list)} unique `context` entries in the file {filename}."
        )

        try:
            with open(output_path, "w", encoding="utf-8") as outfile:
                json.dump(unique_contexts_list, outfile, ensure_ascii=False, indent=4)
            print(f"Unique `context` entries have been saved to: {output_filename}")
        except Exception as e:
            print(f"An error occurred while saving to the file {output_filename}: {e}")

    print("All files have been processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", type=str, default="../datasets")
    parser.add_argument(
        "-o", "--output_dir", type=str, default="../datasets/unique_contexts"
    )

    args = parser.parse_args()
# pylint: disable  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlZGc013PT06NmY0ZjBlOGY=

    extract_unique_contexts(args.input_dir, args.output_dir)
