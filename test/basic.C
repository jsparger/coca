#include "coca/PV.h"

// Must update include path in root to point to coca, python and fmt, then compile and run:
// Example:
// gSystem->AddIncludePath("-I/usr/local/lib/rootbeer/include/");
// gSystem->AddIncludePath("-I/usr/local/Cellar/python/2.7.11/Frameworks/Python.framework/Versions/2.7/include/python2.7/");
// gSystem->AddIncludePath("-I/Users/s7o/github/fmt");
// .x basic.C+d

void basic()
{
	double x = 10.0; 
	auto dog = coca::create_pv("dog",&x); 
	coca::broadcast_pv(dog);

	int z = 10; 
	auto cat = coca::create_pv("cat",&z); 
	coca::broadcast_pv(cat);
}