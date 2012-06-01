#include	<iostream>
#include	<fstream>
#include	<ctime>
#include	<string>
#include	<cmath>
#include	<stdlib.h>
#include        "sort.h"

using namespace std;

int
cmp (const void *left, const void *right)
{
  if (*(double *)left < *(double *)right) {
    return 1;
  }
  if (*(double *)left > *(double *)right) {
    return -1;
  }

  return 0;
}

void
pagerank (int nodenr, const char *filename, double *source, double alpha);

int
main (int argc, char *argv[])
{
    size_t nodenr = 0;
    double alpha = 0.85;
    double *source = NULL;
    unsigned int *index = NULL;

    if (argc < 4) {
        exit (-1);
    }

    nodenr = atoi (argv[1]);
    if (nodenr < 1) {
        std::cerr << "Wrong node number: " << nodenr << std::endl;
        exit (-1);
    }
    alpha = atof (argv[2]);

    source = new double[nodenr];
    index = new unsigned int[nodenr];
    for (unsigned int n = 0; n < nodenr; ++n) {
      index[n] = n;
    }

    pagerank (nodenr, argv[3], source, alpha);

    ofstream pr_txt;
    string filename = argv[3];

    filename += ".pr.txt";

    pr_txt.open (filename.c_str (), std::ios_base::out);

    int i = 0;
    double	sum = 0.0;

    sort ((void *)source, index, nodenr, sizeof (double), cmp, NULL);

    while (i < nodenr) {
        sum += source[i];
        pr_txt << index[i] << "\t" << source[i] << std::endl;
        // std::cout << i << "\t" << source[i] << std::endl;
        ++i;
    }
    std::cout << "Sum: " << sum << std::endl;

    pr_txt.close();

    delete[] source;

    return 0;
}

void
pagerank (int nodenr, const char *filename, double *source, double alpha)
{
    double damp = alpha, threshold = 0.0000001;
    double init = 1.0 - damp;
    double *target = new double[nodenr];
    int iteration = 0, iterator = 25;
    ifstream istream;

    for (int i = 0; i < nodenr; ++i) {
        source[i] = init;
    }

    istream.open (filename, std::ios_base::in);
    if (istream.fail ()) {
        std::cerr << "open error: " << filename << std::endl;
        return;
    }

    while (true) {
        iteration++;
        time_t t = time (NULL);
        std::cerr << "Iteration " << iteration << " starts at: " << ctime (&t);
        for (unsigned int i = 0; i < nodenr; i++) {
            target[i] = 0.0;
        }
        unsigned int count = 0;
        double dangling = 0.0;
        int n = 0;
        for (n = 0; n < nodenr; ++n) {
            int sid = 0, outdegree = 0;

            istream >> sid >> outdegree;

            if ((count % 1000000) == 0) {
                t = time (NULL);
                std::cerr << "Processing " << count << " at: " << ctime (&t);
            }
            ++count;

            if ((sid < 0) or (sid >= nodenr)) {
                std::cerr << "Invalid sid: " << sid << std::endl;
                continue;
            }

            if (outdegree < 1) {
                dangling += source[sid];
                continue;
            }

            int tid;
            // double dist = source[sid] / (double)outdegree;
            double dist = source[sid];
            double probability = 0.0;

            for (int j = 0; j < outdegree; j++) {
                istream >> tid >> probability;
                if ((tid < 0) or (tid >= nodenr)) {
                    std::cerr << "Wrong sid -> tid: " << sid << " -> " << tid << std::endl;
                    continue;
                }
                target[tid] += (dist * probability);
            }
        }
        double dangling_score = dangling / nodenr;
        double deviation = 0.0, tmp;
        for (int i = 0; i < nodenr; i++) {
            // tmp = (((target[i] + dangling_score) * damp) + (1 - damp) / nodenr);
            tmp = (((target[i] + dangling_score) * damp) + (1 - damp));
            deviation += (tmp - source[i]) * (tmp - source[i]);
            source[i] = tmp;
            // std::cout << i << " : " << source[i] << std::endl;
        }
        deviation = sqrtl (deviation * deviation);
        std::cerr << "Deviation: " << deviation << std::endl;
        if (deviation < threshold) {
            break;
        }
        istream.clear ();
        istream.seekg (0, std::ios::beg);
        t = time (NULL);
        std::cerr << "Iteration " << iteration << " ends at: " << ctime (&t);
    } // while (true)

    istream.close();

    delete [] target;

    return;
}
