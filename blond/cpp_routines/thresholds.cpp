/*
 Copyright 2016 CERN. This software is distributed under the
 terms of the GNU General Public Licence version 3 (GPL Version 3),
 copied verbatim in the file LICENCE.md.
 In applying this licence, CERN does not waive the privileges and immunities
 granted to it by virtue of its status as an Intergovernmental Organization or
 submit itself to any jurisdiction.
 Project website: http://blond.web.cern.ch/
 */

// Optimised C++ routine that calculates the histogram
// Author: Danilo Quartullo, Alexandre Lasheen, Konstantinos Iliakis

#include <string.h>     // memset()
#include <stdlib.h>     // mmalloc()
#include <math.h>

//#ifdef PARALLEL
//#include <omp.h>        // omp_get_thread_num(), omp_get_num_threads()
//#else
//int omp_get_max_threads() {return 1;}
//int omp_get_num_threads() {return 1;}
//int omp_get_thread_num() {return 0;}
//#endif

extern "C" void threshold(const double *__restrict__ input,
                          bool *__restrict__ output, const double thresh,
                          const int n_macroparticles)
{
    for (int i = 0; i < n_macroparticles; i++){
        output[i] = signbit(input[i] - thresh);
    }
}
