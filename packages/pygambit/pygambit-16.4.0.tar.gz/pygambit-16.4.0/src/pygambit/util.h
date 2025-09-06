//
// This file is part of Gambit
// Copyright (c) 1994-2025, The Gambit Project (https://www.gambit-project.org)
//
// FILE: src/pygambit/util.h
// Convenience functions for Cython wrapper
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

//
// This file is used by the Cython wrappers to import the necessary namespaces
// and to provide some convenience functions to make interfacing with C++
// classes easier.
//

#include <string>
#include <fstream>
#include <sstream>
#include "gambit.h"
#include "games/nash.h"

using namespace std;
using namespace Gambit;
using namespace Gambit::Nash;

Game ParseGbtGame(std::string const &s)
{
  std::istringstream f(s);
  return ReadGbtFile(f);
}

Game ParseEfgGame(std::string const &s)
{
  std::istringstream f(s);
  return ReadEfgFile(f);
}

Game ParseNfgGame(std::string const &s)
{
  std::istringstream f(s);
  return ReadNfgFile(f);
}

Game ParseAggGame(std::string const &s)
{
  std::istringstream f(s);
  return ReadAggFile(f);
}

std::string WriteEfgFile(const Game &p_game)
{
  std::ostringstream f;
  p_game->WriteEfgFile(f);
  return f.str();
}

std::string WriteNfgFile(const Game &p_game)
{
  std::ostringstream f;
  p_game->WriteNfgFile(f);
  return f.str();
}

std::string WriteHTMLFile(const Game &p_game)
{
  return WriteHTMLFile(p_game, p_game->GetPlayer(1), p_game->GetPlayer(2));
}

std::string WriteLaTeXFile(const Game &p_game)
{
  return WriteLaTeXFile(p_game, p_game->GetPlayer(1), p_game->GetPlayer(2));
}

std::string WriteNfgFileSupport(const StrategySupportProfile &p_support)
{
  std::ostringstream f;
  p_support.WriteNfgFile(f);
  return f.str();
}

template <template <class> class C, class T, class X>
std::shared_ptr<T> sharedcopyitem(const C<T> &p_container, const X &p_index)
{
  return make_shared<T>(p_container[p_index]);
}

// Set item p_index to value p_value in container p_container
template <class C, class X, class T>
void setitem(C *p_container, const X &p_index, const T &p_value)
{
  (*p_container)[p_index] = p_value;
}

template <class C, class X, class T>
void setitem(C &p_container, const X &p_index, const T &p_value)
{
  p_container[p_index] = p_value;
}

template <class T> std::list<std::shared_ptr<T>> make_list_of_pointer(const std::list<T> &p_list)
{
  std::list<std::shared_ptr<T>> result;
  for (const auto &element : p_list) {
    result.push_back(std::make_shared<T>(element));
  }
  return result;
}
