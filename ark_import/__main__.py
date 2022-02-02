"""Generate SQL queries from Noid/Egg Berkeley DB dump.

This script formats a Noid/Egg db dump into a series of SQL queries,
grouped into multiple files, suitable for importing into arklet.

As written, will only work for naan 13960 and shoulders /t, /fk.
Modify the extract_ark function to work for your DB file.

Supply a path to the db dump and a prefix for the query files.

Example call:
python -m ark_import sample_noid_output.txt output-prefix
"""

import sys

infile = sys.argv[1]
out_prefix = sys.argv[2]
queries_per_file = 10000


def signal_line(line):
    return line.startswith("ark:/") and line.endswith("_t")


def extract_ark(line):
    ark, record_type = line.split("|")
    proto, naan, number = ark.split("/")
    naan = int(naan)
    if naan != 13960:
        raise ValueError(f"bad naan: {naan}")
    if number.startswith("t"):
        shoulder = "/t"
        number = number[1:]
    elif number.startswith("fk"):
        shoulder = "/fk"
        number = number[2:]
    else:
        raise ValueError(number)
    if len(number) != 8:
        raise ValueError(f"unexpected number: {number}")
    return naan, shoulder, number


def query_format(naan, shoulder, number, url):
    ark = f"{naan}{shoulder}{number}"
    return repr((ark, shoulder, number, url, naan))


def ark_input_iter(ark_input_file):
    with open(ark_input_file, "r") as f:
        take_next = False
        for line in f:
            line = line.strip()
            if signal_line(line):
                take_next = True
                naan, shoulder, number = extract_ark(line)
            elif take_next:
                yield query_format(naan, shoulder, number, line)
                take_next = False
            else:
                take_next = False


def write_query_values(prefix, file_num, vals):
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    head = "insert into ark_ark (ark, shoulder, assigned_name, url, naan_id) values "
    with open(f"{prefix}-{file_num:0>6}.sql", "w") as f:
        query_tail = ",\n".join(vals)
        query = f"{head}\n{query_tail};"
        f.write(query)


query_vals = []
outfile_num = 0
for query_val in ark_input_iter(infile):
    query_vals.append(query_val)
    if len(query_vals) >= queries_per_file:
        write_query_values(out_prefix, outfile_num, query_vals)
        query_vals.clear()
        outfile_num += 1
write_query_values(out_prefix, outfile_num, query_vals)  # write remaining values
