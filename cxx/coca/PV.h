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
#include <iostream>
#include <functional>

#define FMT_HEADER_ONLY
#include "fmt/format.h"

namespace coca {

struct GIL
{
	GIL()
		: threadState(PyEval_SaveThread())
	{
		// do nothing else
	}

	void acquire()
	{
		PyEval_RestoreThread(threadState);
		gState = PyGILState_Ensure();
	}

	void release()
	{
		PyGILState_Release(gState);
		threadState = PyEval_SaveThread();
	}

	PyThreadState* threadState;
	PyGILState_STATE gState;
};

static GIL* gil = nullptr;

struct PyLock
{
	PyLock()
	{
		gil->acquire();
	}

	~PyLock()
	{
		gil->release();
	}
};

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

template <typename T>
PyObject* get_python_proxy(T& pv)
{

	if (!gil)
	{
		TPython::Exec("import sys");
		gil = new GIL();
	} 
	PyLock lock;
	std::string klassName = Demangler::demangle(typeid(pv).name());
	auto object = TPython::ObjectProxy_FromVoidPtr((void*)&pv, klassName.c_str());
	return object;
}

struct PythonUtility
{
	static void broadcast_pv(PyObject* proxy)
	{
		PyLock lock;
		PyObject* coca = PyImport_Import(PyString_FromString((char*)"coca"));
		PyObject* broadcast_pv = PyObject_GetAttrString(coca,(char*)"broadcast_cxx_pv");
		PyObject* args = PyTuple_Pack(1,proxy);
		PyObject* result = PyObject_CallObject(broadcast_pv, args);
	}

	static void update_pv(PyObject* proxy)
	{
		PyLock lock;
		PyObject* coca = PyImport_Import(PyString_FromString((char*)"coca"));
		PyObject* update_pv = PyObject_GetAttrString(coca,(char*)"update_cxx_pv");
		PyObject* args = PyTuple_Pack(1,proxy);
		PyObject* result = PyObject_CallObject(update_pv, args);
	}

	static void quit()
	{
		PyLock lock;
		TPython::Exec("quit()");
	}
};

struct iPV
{
	iPV(std::string name)
		: name(name) {;}
	virtual ~iPV() {;}
	virtual bool isUpdated() = 0;
	virtual void fill() = 0;
	std::string name;
};

template <typename T>
struct PV : public iPV
{
	PV(std::string name, T* value, std::function<void(PV<T>*)> onRead=nullptr, std::function<void(PV<T>*)> onWrite=nullptr)
		: iPV(name), value(value), previous(*value), onReadTarget(onRead), onWriteTarget(onWrite)
		{
			this->proxy = get_python_proxy(*this);
		}

	virtual ~PV() {;}

	virtual bool isUpdated() override
	{
		bool updated = (*value != previous);
		if (updated) { previous = *value; }
		return updated;
	}

	virtual void fill() override
	{
		PythonUtility::update_pv(this->proxy);
	}

	virtual const T* getValue()
	{
		return value;
	}

	virtual void setValue(T newval)
	{
		*value = newval;
	}

	virtual void onRead(PyObject* pv)
	{
		if (onReadTarget)
		{
			onReadTarget(this);
		}
	}

	virtual void onWrite(PyObject* pv)
	{
		if (onWriteTarget)
		{
			onWriteTarget(this);
		}
	}

	virtual void setRange(std::array<T,2> range) {bRange = true; this->range = range;}
	virtual void setLimits(std::array<T,4> limits) {bLimits = true; this->limits = limits;}
	virtual void setPrecision(int precision) {bPrecision = true; this->precision = precision;}
	virtual void setUnits(std::string units) {bUnits= true; this->units = units;}
	virtual void setScan(double scan) {this->scan = scan;}

	virtual std::string asDict()
	{
		std::string s = fmt::format("{{'{}': {{ ", name); //"{'" + name + std::string("': { ");
		s += fmt::format("'prec': {},",precision);
		s += fmt::format("'lolo': {}, 'low': {}, 'high': {}, 'hihi': {},",limits[0],limits[1],limits[2],limits[3]);
		s += fmt::format("'lolim': {}, 'hilim': {},",range[0],range[1]);
		s += fmt::format("'unit': '{}',",units);
		s += fmt::format("'scan': {},",scan);
		s += "}}";
		return s;
	}

	T* value;
	T previous;
	std::array<T,2> range = {T(),T()};
	std::array<T,4> limits = {T(),T(),T(),T()};
	std::string units = "";
	int precision = 0;
	double scan = 1.0;

	bool bRange = false; 
	bool bLimits = false; 
	bool bUnits = false;
	bool bPrecision = false;
	bool bScan = true;

	PyObject* proxy = nullptr;

	std::function<void(PV<T>*)> onReadTarget, onWriteTarget;
};

template <typename T, typename F=std::function<void(PV<T>*)>, typename G=std::function<void(PV<T>*)>>
PV<T> create_pv(std::string name, T* value, F onRead = nullptr, G onWrite = nullptr)
{
	return PV<T>(name,value,onRead,onWrite);
}

template <typename T>
void broadcast_pv(T& pv)
{
	PythonUtility::broadcast_pv(pv.proxy);
}

template <typename T>
void shutdown(T val)
{
	(void)val; // suppress unused variable warning
	PyLock lock;
	TPython::Exec("quit()");
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

	void bcast(PV<double>& pv)
	{
		broadcast_pv(pv);
	}
};


struct init
{
	// do nothing
};


}

#endif