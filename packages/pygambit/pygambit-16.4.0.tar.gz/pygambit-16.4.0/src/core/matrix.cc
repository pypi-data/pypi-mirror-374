//
// This file is part of Gambit
// Copyright (c) 1994-2025, The Gambit Project (https://www.gambit-project.org)
//
// FILE: src/core/matrix.cc
// Instantiation of common matrix types
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

#include "core.h"
#include "matrix.imp"

namespace Gambit {

template class Matrix<double>;
template class Matrix<Rational>;
template class Matrix<Integer>;
template class Matrix<int>;

template Vector<double> operator*(const Vector<double> &, const Matrix<double> &);
template Vector<Rational> operator*(const Vector<Rational> &, const Matrix<Rational> &);
template Vector<Integer> operator*(const Vector<Integer> &, const Matrix<Integer> &);
template Vector<int> operator*(const Vector<int> &, const Matrix<int> &);

} // end namespace Gambit
