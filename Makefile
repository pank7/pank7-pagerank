SRCDIR		= $(shell pwd)

TARGET		= pagerank
OBJECTS		= pagerank.o sort.o

INCLUDES	= -I./
LIBPATH		= 
LIBS		= 

# CC		= gcc
CC		= clang
# CPP		= g++
CPP		= clang++

CFLAGS		= -c
OFLAGS		= 

CFLAGS		+= $(INCLUDES)
OFLAGS		+= $(LIBPATH)

%.o : %.cpp
	$(CPP) $(CFLAGS) $^

%.o : %.c
	$(CC) $(CFLAGS) $^

all : $(TARGET)

clean :
	-rm -f *.o
	-rm -f $(TARGET)

allclean : clean
	-rm -f tags TAGS

ctags :
	find $(SRCDIR) -name '*.h' -or -name '*.hh' -or -name '*.c' -or -name '*.cpp' -or -name '*.l' -or -name '*.y' | xargs ctags -a;

etags : 
	find $(SRCDIR) -name '*.h' -or -name '*.hh' -or -name '*.c' -or -name '*.cpp' -or -name '*.l' -or -name '*.y' | xargs etags -a;

pagerank : $(OBJECTS)
	$(CPP) $(OFLAGS) -o $@ $^
