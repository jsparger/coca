#ifndef COCA_PV_H
#define COCA_PV_H

#include "TObject.h"
#include <array>
#include <string>
#include "TPython.h"
#include "Python.h"
#include "TClassTable.h"
#include "TClass.h"
#include <typeinfo>
#include <cxxabi.h>

#define FMT_HEADER_ONLY
#include "fmt/format.h"

namespace coca {

struct iPV
{
	iPV(std::string name)
		: name(name) {;}
	virtual ~iPV() {;}
	virtual bool isUpdated() = 0;
	std::string name;
};

template <typename T>
struct PV : public iPV
{
	PV(std::string name, T* value)
		: iPV(name), value(value), previous(*value) {;}
	virtual ~PV() {;}

	virtual bool isUpdated() override
	{
		bool updated = (*value != previous);
		if (updated) { previous = *value; }
		return updated;
	}

	virtual const T& getValue()
	{
		return *value;
	}

	virtual void setValue(T newval)
	{
		*value = newval;
	}

	virtual void setRange(std::array<T,2> range) {bRange = true; this->range = range;}
	virtual void setLimits(std::array<T,4> limits) {bLimits = true; this->limits = limits;}
	virtual void setPrecision(int precision) {bPrecision = true; this->precision = precision;}
	virtual void setUnits(std::string units) {bUnits= true; this->units = units;}
	virtual void setScan(double scan) {this->scan = scan;}

	virtual std::string asDict()
	{
		std::string s = fmt::format("{{'{}': {{ ", name); //"{'" + name + std::string("': { ");
		if (bPrecision) s += fmt::format("'prec': {},",precision);
		if (bLimits) s += fmt::format("'lolo': {}, 'low': {}, 'high': {}, 'hihi': {},",limits[0],limits[1],limits[2],limits[3]);
		if (bRange) s += fmt::format("'lolim': {}, 'hilim': {},",range[0],range[1]);
		if (bUnits) s += fmt::format("'unit': '{}',",units);
		s += fmt::format("'scan': {},",scan);
		s += "}}";
		return s;
	}

	T* value;
	T previous;
	std::array<T,2> range = {T(),T()};
	std::array<T,4> limits = {T(),T(),T(),T()};
	std::string units;
	int precision;
	double scan = 1.0;

	bool bRange = false; 
	bool bLimits = false; 
	bool bUnits = false;
	bool bPrecision = false;
	bool bScan = true;
};

template <typename T>
PV<T> create_pv(std::string name, T* value)
{
	return PV<T>(name,value);
}

struct Demangler
{
	static std::string demangle(const char* name)
	{
	    int status = -4; // some arbitrary value to eliminate the compiler warning

	    // enable c++11 by passing the flag -std=c++11 to g++
	    std::unique_ptr<char, void(*)(void*)> res {
	        abi::__cxa_demangle(name, NULL, NULL, &status),
	        std::free
	    };

	    return (status==0) ? res.get() : name ;
	}
};

// template <typename T>
// void broadcast_pv_safe(T& pv)
// {
// 	const std::type_info& info = typeid(pv);
// 	auto dict = TClassTable::GetDict(info);
// 	if (!dict)
// 	{
// 		throw std::runtime_error(
// 			fmt::format("Error in coca::broadcast_pv<T>() : No dictionary exists for type {}. "
// 				"Try adding '#pragma link C++ class coca::PV<double>+;' your LinkDef.h", info.name())
// 			);
// 	}
// 	TClass* klass = dict();
// 	auto proxy = TPython::ObjectProxy_FromVoidPtr((void*)&pv, klass->GetName());
// 	PyObject* coca = PyImport_Import(PyString_FromString((char*)"coca"));
// 	PyObject* broadcast_pv = PyObject_GetAttrString(coca,(char*)"broadcast_pv");
// 	PyObject* args = PyTuple_Pack(1,proxy);
// 	PyObject* result = PyObject_CallObject(broadcast_pv, args);
// }

template <typename T>
void broadcast_pv(T& pv)
{
	std::string klassName = Demangler::demangle(typeid(pv).name());
	auto proxy = TPython::ObjectProxy_FromVoidPtr((void*)&pv, klassName.c_str());
	PyObject* coca = PyImport_Import(PyString_FromString((char*)"coca"));
	PyObject* broadcast_pv = PyObject_GetAttrString(coca,(char*)"broadcast_pv");
	PyObject* args = PyTuple_Pack(1,proxy);
	PyObject* result = PyObject_CallObject(broadcast_pv, args);
}

struct dummy
{
	double test;
	PV<double> getPV()
	{
		auto pv = create_pv("COHERENT:proof",&test);
		pv.setPrecision(3);
		pv.setRange({-10,10});
		pv.setLimits({-8,-5,5,8});
		pv.setUnits("kProof");
		return pv;
	}
};



}

#endif