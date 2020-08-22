# SEP592


Required Modules: argparse, math, random, copy, numpy and datetime



Running

1. Generate .citmodel and .constraint

> python Model_Generator.py data/Test_Case.csv data/TLM_Example.csv -s 2

2. Generate .coveringarray

> python CIT.py Power_Check -n 6

3. Generate test code or procedure

> python Code_Generator.py Power_Check data/Test_Case.csv data/CMD_Example.csv data/TLM_Example.csv -c 1

> python Procedure_Generator.py Power_Check data/Test_Case.csv data/CMD_Example.csv data/TLM_Example.csv -c 1
