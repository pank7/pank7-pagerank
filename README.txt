PageRank
Author: Li Yi <liyi(AT)net.pku.edu.cn>
Date: May 14th, 2009

* System Requirements:
	* Python 2.5.4 (http://www.python.org/)
	* gcc-3.2 or later
	* g++-3.2 or later
	* GNU make

* HOWTO
	* Run:
		* 1. Prepare configuration file: PR.conf
		* 2. Run PR.py
	* Prepare PR.conf:
		* Must contain a section named: Parameters
		* These options are needed:
			* adj: path of the adjacency matrix file
			* names: path of the names file
		* These options have defaults:
			* alpha: 0.85
			* simrank: no

* Output:
	* basename: adj file name
	* Log file: ${basename}.log
		* Errors, if any.
		* Time consumed for every iteration.
		* Standard deviation after every iteration.
	* Transition matrix: ${basename}-T.txt
	* PR file: ${basename}.pr.txt
		* Format:
			* name: vertex name.
			* id: internal id.
			* o: outdegree.
			* i: indegree.
			* pr: PageRank value.
			* Sorted by PageRank value.
			"
			name_1 id_1 o_1 i_1 pr_1
			name_2 id_2 o_2 i_2 pr_2
			...
			name_n id_n o_n i_n pr_n
			"

* Source Files:
	* pagerank.cpp
	* sort.h
	* sort.c
	* PR.py
	* Makefile
	* README.txt
