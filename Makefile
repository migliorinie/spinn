TARGETS = runizhi cpp/runobiz

CC = gcc
LDLIBS   += -lm -lpcg_random

all: $(TARGETS)

clean:
	rm -f *.o $(TARGETS)

runizhi: izhibase.c
	$(CC) izhibase.c -o runizhi $(LDLIBS) $(CPPFLAGS)

cpp/runobiz: cpp/izhi_objects.cpp
	g++ cpp/izhi_objects.cpp -o cpp/runobiz -lm -lpcg_random -larmadillo -lpng