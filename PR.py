#!/usr/bin/env python

import sys, os, subprocess, bsddb, ConfigParser

def ReadConfig():
    config = ConfigParser.ConfigParser()
    try:
        config.read(["PR.conf"])
    except Exception, msg:
        print >> sys.stderr, msg
        sys.exit()
    config.write(sys.stdout)

    if not config.has_section("Parameters"):
        print >> sys.stderr, "Bad configuration file, missing section \"Parameters\"!"
        sys.exit()

    try:
        namesfile = open(config.get("Parameters", "names"), 'r')
        adjfile = open(config.get("Parameters", "adj"), 'r')
        basename = config.get("Parameters", "adj").split('.')[0]
    except ConfigParser.NoOptionError, msg:
        print >> sys.stderr, msg
        sys.exit()
    except IOError, msg:
        print >> sys.stderr, msg
        sys.exit()
    try:
        alpha = config.getfloat("Parameters", "alpha")
    except ValueError, msg:
        print >> sys.stderr, msg
        sys.exit()
    except ConfigParser.NoOptionError, msg:
        alpha = 0.85

    try:
        simrank = config.getboolean("Parameters", "simrank")
    except ValueError, msg:
        print >> sys.stderr, msg
        sys.exit()
    except ConfigPaser.NoOptionError, msg:
        simrank = False

    logfile = open(basename + ".log", 'w')

    return config, namesfile, adjfile, alpha, simrank, basename, logfile

def ReadNames(namesfile, logfile):
    names = dict()
    ids = dict()
    i = 0
    for line in namesfile:
        line = line.strip()
        if len(line) == 0:
            continue
        if names.has_key(line):
            print >> sys.stderr, "Duplicated name:", line
            print >> sys.stderr, "Ignore!"
            print >> logfile, "Duplicated name:", line
            print >> logfile, "Ignore!"
        else:
            names[line] = [i, 0, 0]
            ids[i] = line
            i += 1
    namesfile.close()
    nodenr = len(names)

    return names, ids, nodenr

def ReadAdj(adjfile, names, logfile):
    A = dict()

    for line in adjfile:
        line = line.strip()
        if len(line) == 0:
            continue
        s = line.split()
        name = s[0]
        if not names.has_key(name):
            print >> sys.stderr, "Unknown name:", name
            print >> logfile, "Unknown name:", name
            sys.exit()
        neighbors = []
        arcnums = []
        for i in range(1, len(s), 2):
            if not names.has_key(s[i]):
                print >> sys.stderr, "Unknown name:", s[i]
                print >> logfile, "Unknown name:", s[i]
                sys.exit()
            try:
                arcnum = int(s[i + 1])
            except ValueError, msg:
                print >> sys.stderr, msg, "-- Invalid arc number:", s[i + 1]
                print >> logfile, msg, "-- Invalid arc number:", s[i + 1]
                sys.exit()
            neighbors.append(names[s[i]][0])
            arcnums.append(arcnum)
            names[s[i]][2] += 1
        A[names[name][0]] = [neighbors, arcnums]
        # names[name][1] = sum(arcnums)
        names[name][1] = len(neighbors)

    return A

def ReadAdjSimRank(adjfile, names, logfile):
    A = dict()

    for line in adjfile:
        line = line.strip()
        if len(line) == 0:
            continue
        s = line.split()
        name = s[0]
        if not names.has_key(name):
            print >> sys.stderr, "Unknown name:", name
            print >> logfile, "Unknown name:", name
            sys.exit()
        neighbors = set()
        for i in range(1, len(s)):
            if not names.has_key(s[i]):
                print >> sys.stderr, "Unknown name:", s[i]
                print >> logfile, "Unknown name:", s[i]
                sys.exit()
            neighbors.add(names[s[i]][0])
            names[s[i]][2] += 1
        A[names[name][0]] = neighbors
        names[s[i]][1] = len(neighbors)

    return A

def ConstructTransMatrix(A):
    T = dict()

    for key, value in A.iteritems():
        ansum = sum(value[1])
        tout = []
        for i in range(len(value[0])):
            out = value[0][i]
            probability = float(value[1][i]) / float(ansum)
            tout.append([out, probability])
        T[key] = [len(value[0]), tout]

    return T

def ConstructTransMatrixSimRank(A):
    T = dict()

    for key, value in A.iteritems():
        tout = []
        sout = []
        for out in value:
            nu = len(value.union(A[out]))
            ni = len(value.intersection(A[out]))
            if nu > 0:
                probability = float(ni) / float(nu)
            else:
                probability = 0.0
            score = 0.2
            if probability <= 0.2:
                score = 0.2
            elif probability <= 0.4:
                score = 0.4
            elif probability <= 0.6:
                score = 0.6
            elif probability <= 0.8:
                score = 0.8
            else:
                score = 1.0
            tout.append(out)
            sout.append(score)
        sumtmp = sum(sout)
        T[key] = [len(tout), []]
        for i in range(len(tout)):
            T[key][1].append([tout[i], sout[i] / sumtmp])

    return T

def OutputTransMatrix(T, outfile):
    for key, value in T.iteritems():
        print >> outfile, key, value[0],
        for pair in value[1]:
            print >> outfile, pair[0], pair[1],
        print >> outfile

    return

if __name__ == "__main__":
    # Read configuration file.
    config, namesfile, adjfile, alpha, simrank, basename, logfile = ReadConfig()

    # Read names file.
    names, ids, nodenr = ReadNames(namesfile, logfile)

    # Read adjacency matrix.
    if simrank:
        A = ReadAdjSimRank(adjfile, names, logfile)
    else:
        A = ReadAdj(adjfile, names, logfile)

    adjfile.close()

    # Construct transition matrix. 
    if simrank:
        T = ConstructTransMatrixSimRank(A)
    else:
        T = ConstructTransMatrix(A)

    # Output transition matrix.
    tname = basename + "-T.txt"
    try:
        outfile = open(tname, 'w')
    except IOError, msg:
        print >> sys.stderr, msg
        sys.exit()
    OutputTransMatrix(T, outfile)
    outfile.close()

    # Execute PageRank computation.
    cmd = ["./pagerank", "%d" % nodenr, "%f" % alpha, "./%s" % tname]

    print "Execute:", cmd

    prsp = subprocess.Popen(args = cmd, stdout = logfile, stderr = logfile)
    rc = prsp.wait()
    logfile.close()

    rawprfile = open("./%s.pr.txt" % tname, 'r')
    prfile = open("./%s.pr.txt" % basename, 'w')

    for line in rawprfile:
        p = line.split()
        id = int(p[0])
        name = ids[id]
        print >> prfile, name, names[name][0], names[name][1], names[name][2], p[1]

    rawprfile.close()
    prfile.close()
