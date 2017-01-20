BINTARGET	=contour gridpbc griddoubler hull2yap hull2hull 
CDEBUGFLAGS	= -g
LDFLAGS=-lm


all: $(BINTARGET)
install: contour
	install contour griddoubler gridpbc ../../bin
clean:
	-rm *.o *~ contour

contour: cont3.o x3dcont3.o sdf3.o
	$(CC) $(CFLAGS) $^ -o $@
%.o: %.cpp
	$(CXX) $(CXXDEBUGFLAGS) -c $< -o $@

%.yap: %.hull
	./hull2hull < $< | ./hull2yap > $@
