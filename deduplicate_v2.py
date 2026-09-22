import csv
import os
import shlex

def deduplicate_multiple_csvs(valid_file_paths, output_name="unique_students.csv"):
    seen_matrics = set()
    unique_rows = []
    headers = []
    
    total_records = 0
    discarded_records = 0

    def process_file(filepath):
        nonlocal total_records, discarded_records
        
        with open(filepath, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            try:
                # Extract header
                header = next(reader)
                if not headers:
                    headers.extend(header)
            except StopIteration:
                return # File is empty, skip silently

            # Process rows
            for row in reader:
                # Ensure row has at least 3 columns (NO, MATRIC, NAME)
                if len(row) >= 3:
                    total_records += 1
                    
                    # Disregard row[0]. Work specifically on row[1] (Matric Number)
                    matric_no = row[1].strip()
                    
                    # If we've seen this matric number already, count it as discarded
                    if matric_no in seen_matrics:
                        discarded_records += 1
                    else:
                        seen_matrics.add(matric_no)
                        unique_rows.append(row)

    # Process all validated files
    for path in valid_file_paths:
        process_file(path)

    # Output to current working directory
    output_path = os.path.join(os.getcwd(), output_name)

    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
            
        # Re-number the first column sequentially (1, 2, 3...) as we write
        for index, row in enumerate(unique_rows, start=1):
            row[0] = str(index)
            writer.writerow(row)

    # Display the requested analytics summary
    print(f"\n--- Processing Summary ---")
    print(f"Total records checked: {total_records}")
    print(f"Duplicates discarded:  {discarded_records}")
    print(f"Final unique records:  {len(unique_rows)}")
    print(f"--------------------------")
    print(f"Success! File saved to: {output_path}")

if __name__ == "__main__":
    print("--- Multi-File CSV Deduplication Tool ---")
    
    valid_files = []
    
    # Keep asking for files and validating them immediately
    while True:
        raw_input = input("\nEnter full path(s) to CSV file(s) (or '0' to finish): ").strip()
        
        if raw_input == '0':
            break
            
        if not raw_input:
            continue
            
        # Use shlex to intelligently split multiple paths separated by spaces,
        # respecting quotes. posix=False preserves Windows backslashes (\).
        try:
            paths = shlex.split(raw_input, posix=False)
        except ValueError:
            print("  [X] Error: Unbalanced quotes in input. Please try again.")
            continue
            
        for p in paths:
            # Clean up the surrounding quotes from each individual path
            clean_path = p.strip("\"'")
            
            # Immediate validation
            if os.path.isfile(clean_path):
                valid_files.append(clean_path)
                print(f"  [✓] Confirmed: Added '{os.path.basename(clean_path)}'")
            else:
                print(f"  [X] Error: Invalid file path '{clean_path}'. Discarded.")
            
    if not valid_files:
        print("\nNo valid files were provided.")
        input("\nPress Enter to exit...")
        exit()
        
    # Ask for custom output name
    custom_name = input("\nEnter name for the output CSV file (press Enter for default): ").strip()
    
    if custom_name:
        # Ensure it ends with .csv
        if not custom_name.lower().endswith('.csv'):
            custom_name += '.csv'
        output_filename = custom_name
    else:
        output_filename = "unique_students.csv"
        
    print(f"\nProcessing {len(valid_files)} valid file(s)...")
    deduplicate_multiple_csvs(valid_files, output_name=output_filename)
    
    # Final prompt to prevent the CLI window from closing immediately
    input("\nPress Enter to exit...")