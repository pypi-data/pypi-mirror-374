//
// This file is part of Gambit
// Copyright (c) 1994-2025, The Gambit Project (https://www.gambit-project.org)
//
// FILE: src/core/function.h
// Interface to function and function minimization routines
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
//

#ifndef GAMBIT_CORE_FUNCTION_H
#define GAMBIT_CORE_FUNCTION_H

#include "vector.h"

namespace Gambit {

class Function {
public:
  virtual ~Function() = default;
  virtual double Value(const Vector<double> &) const = 0;
  virtual bool Gradient(const Vector<double> &, Vector<double> &) const = 0;
};

// A specialization of a Function to the case where the domain of the function
// is a product of simplices.
class FunctionOnSimplices : public Function {
public:
  ~FunctionOnSimplices() override = default;

protected:
  // Project the gradient 'x' onto the plane of the product of simplices.
  void Project(Vector<double> &x, const Array<int> &lengths) const;
};

class FunctionMinimizerError : public std::runtime_error {
public:
  FunctionMinimizerError() : std::runtime_error("Internal error in function minimization") {}
  ~FunctionMinimizerError() noexcept override = default;
};

// An abstract base class for function minimization
class FunctionMinimizer {
public:
  virtual ~FunctionMinimizer() = default;

  virtual void Set(const Function &fdf, const Vector<double> &x, double &f,
                   Vector<double> &gradient, double step_size, double p_tol) = 0;
  virtual void Restart() = 0;

  virtual bool Iterate(const Function &fdf, Vector<double> &x, double &f, Vector<double> &gradient,
                       Vector<double> &dx) = 0;
};

// Implements Polak-Ribiere conjugate gradient descent
class ConjugatePRMinimizer : public FunctionMinimizer {
public:
  explicit ConjugatePRMinimizer(int n);
  ~ConjugatePRMinimizer() override = default;

  void Set(const Function &fdf, const Vector<double> &x, double &f, Vector<double> &gradient,
           double step_size, double p_tol) override;
  void Restart() override;

  bool Iterate(const Function &fdf, Vector<double> &x, double &f, Vector<double> &gradient,
               Vector<double> &dx) override;

private:
  int iter{0};
  double step{0.0};
  double max_step{0.0};
  double m_tol{0.0};
  Vector<double> x1;
  Vector<double> dx1;
  Vector<double> x2;
  double pnorm{0.0};
  Vector<double> p;
  double g0norm{0.0};
  Vector<double> g0;

  void AlphaXPlusY(double alpha, const Vector<double> &x, Vector<double> &y);
  void TakeStep(const Vector<double> &x, const Vector<double> &p, double step, double lambda,
                Vector<double> &x1, Vector<double> &dx);
  void IntermediatePoint(const Function &fdf, const Vector<double> &x, const Vector<double> &p,
                         double lambda, double pg, double stepa, double stepc, double fa,
                         double fc, Vector<double> &x1, Vector<double> &dx,
                         Vector<double> &gradient, double &step, double &f);
  void Minimize(const Function &fdf, const Vector<double> &x, const Vector<double> &p,
                double lambda, double stepa, double stepb, double stepc, double fa, double fb,
                double fc, double tol, Vector<double> &x1, Vector<double> &dx1, Vector<double> &x2,
                Vector<double> &dx2, Vector<double> &gradient, double &step, double &f,
                double &gnorm);
};

} // end namespace Gambit

#endif // GAMBIT_CORE_FUNCTION_H
