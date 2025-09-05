#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "ndarray.h"
#include "isosplit5.h"
#include "isocut5.h"

int isosplit5_interface(py::array_t<int> labels_out,py::array_t<double> X)
{
    NDArray<double> Xa(X);
    NDArray<int> La(labels_out);
    bigint M=Xa.shape[0];
    bigint N=Xa.shape[1];
    isosplit5_opts opts;
    isosplit5(La.ptr,M,N,Xa.ptr,opts);
    return 0;
}

int isocut5_interface(py::array_t<double> outputs,py::array_t<double> X)
{
    NDArray<double> Xa(X);
    NDArray<double> outputsa(outputs);
    bigint N=Xa.shape[0];
    isocut5_opts opts;

    double dipscore;
    double cutpoint;
    isocut5(&dipscore, &cutpoint, N, Xa.ptr, opts);
    outputsa.ptr[0] = dipscore;
    outputsa.ptr[1] = cutpoint;
    return 0;
}

PYBIND11_MODULE(isosplit5_interface, m) {
    m.doc() = "Python interface to isosplit clustering"; // optional module docstring
    
    m.def("isosplit5_interface", &isosplit5_interface, "ISO-SPLIT clustering",
          py::arg("labels_out").noconvert(),
          py::arg("X").noconvert()
    );

    m.def("isocut5_interface", &isocut5_interface, "ISO-CUT",
          py::arg("output").noconvert(),
          py::arg("X").noconvert()
    );
}