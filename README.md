# KAIST 2020 Summer Semester SEP592 Project <br> CIT-based Automatic Test Code and Procedure Generation for Spacecraft

> The objective of this project is automatically to generate test codes and/or procedures for the spacecraft by the CIT (Combinatorial Interaction Test) tool.

> The main idea came from the paper:<br>
> Y. Jia, M. Cohen, M. Harman, and J. Petke.<br>
> **Learning combinatorial interaction test generation strategies using hyperheuristic search** <br>
> In International Conference on Software Engineering (ICSE’15), 2015.

> All the programs is implemented using Python, and it requires Python modules: argparse, math, random, copy, numpy and datetime.

> And dataset was atificially generated to test our progeam.



## Running

1. Generate .citmodel and .constraint

```bash
python Model_Generator.py data/Test_Case.csv data/TLM_Example.csv -s 2
```

2. Generate .coveringarray

```bash
python CIT.py Power_Check -n 6
python CIT.py Payload1_Data_Reception
python CIT.py Payload2_Data_Reception
python CIT.py Payload3_Data_Reception
python CIT.py Payload4_Data_Reception -n 7
python CIT.py Payload2_Data_Transmission
python CIT.py All_Payload_Data_Reception -i 50000
```

3. Generate test code or procedure

```bash
python Code_Generator.py Power_Check ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 1
python Code_Generator.py Payload1_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 2
python Code_Generator.py Payload2_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 3
python Code_Generator.py Payload3_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 4
python Code_Generator.py Payload4_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 5
python Code_Generator.py Payload2_Data_Transmission ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 6
python Code_Generator.py All_Payload_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 7
```

```bash
python Procedure_Generator.py Power_Check ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 1
python Procedure_Generator.py Payload1_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 2
python Procedure_Generator.py Payload2_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 3
python Procedure_Generator.py Payload3_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 4
python Procedure_Generator.py Payload4_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 5
python Procedure_Generator.py Payload2_Data_Transmission ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 6
python Procedure_Generator.py All_Payload_Data_Reception ./data/Test_Case.csv ./data/CMD_Example.csv ./data/TLM_Example.csv  -c 7
```
