all: libhello.so

libhello.so: hello.c
	gcc -shared -fPIC hello.c -o libhello.so

clean:
	rm -f libhello.so
