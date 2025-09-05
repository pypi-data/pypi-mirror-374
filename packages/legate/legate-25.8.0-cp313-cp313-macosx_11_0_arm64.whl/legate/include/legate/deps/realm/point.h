/* Copyright 2024 Stanford University, NVIDIA Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// points and rects (i.e. dense index spaces) in Realm

#ifndef REALM_POINT_H
#define REALM_POINT_H

#include "realm/realm_config.h"

#include "realm/event.h"
#include "realm/utils.h"

#include <iostream>
#include <type_traits>

namespace Realm {

  template <int N, typename T = int>
  struct Point;
  template <int N, typename T = int>
  struct Rect;
  template <int N, typename T = int>
  class PointInRectIterator;
  template <int M, int N, typename T = int>
  struct Matrix;
  template <int N, typename T = int>
  struct IndexSpace;

  struct CopySrcDstField;
  class ProfilingRequestSet;

  // adding this as a parameter to a templated method uses SFINAE to only allow
  //  the template to be instantiated with an integral type
#define ONLY_IF_INTEGRAL(Type) std::enable_if_t<std::is_integral<Type>::value, Type>

  // a Point is a tuple describing a point in an N-dimensional space - the default "base
  // type"
  //  for each dimension is int, but 64-bit indices are supported as well
  template <int N, typename T>
  struct REALM_PUBLIC_API Point {

    typedef ONLY_IF_INTEGRAL(T) value_type;
    value_type values[N]; // use operator[] instead

    Point(void) = default;
    REALM_CUDA_HD
    explicit Point(value_type val);
    template <typename Arg0, typename Arg1, typename... Args>
    REALM_CUDA_HD Point(Arg0 val0, Arg1 val1, Args... vals);
    // construct from any integral value, same for all dimensions
    template <typename T2, std::enable_if_t<std::is_integral<T2>::value, bool> = true>
    REALM_CUDA_HD explicit Point(T2 val);
    template <typename T2, std::enable_if_t<std::is_integral<T2>::value, bool> = true>
    REALM_CUDA_HD explicit Point(T2 vals[N]);
    // copies allow type coercion (assuming the underlying type does)
    template <typename T2>
    REALM_CUDA_HD Point(const Point<N, T2> &copy_from);
    template <typename T2>
    REALM_CUDA_HD Point<N, T> &operator=(const Point<N, T2> &copy_from);

    REALM_CUDA_HD
    T &operator[](int index);
    REALM_CUDA_HD
    const T &operator[](int index) const;

    template <typename T2>
    REALM_CUDA_HD T dot(const Point<N, T2> &rhs) const;

    // 1-4D accessors.  These will only be available if the class's dimensioned allow for
    // it, otherwise it is a compiler error to use them
    REALM_CUDA_HD T &x();
    REALM_CUDA_HD T &y();
    REALM_CUDA_HD T &z();
    REALM_CUDA_HD T &w();
    REALM_CUDA_HD const T &x() const;
    REALM_CUDA_HD const T &y() const;
    REALM_CUDA_HD const T &z() const;
    REALM_CUDA_HD const T &w() const;

    REALM_CUDA_HD
    static constexpr Point<N, T> ZEROES(void);
    REALM_CUDA_HD
    static constexpr Point<N, T> ONES(void);
  };

  /// @brief Helper function to initialize Point from a list of types without needing to
  /// explicitly specify the dimension or type of the resulting Point.
  template <typename T = int, typename... U>
  [[nodiscard]] constexpr auto make_point(const U &...rest) -> Point<sizeof...(rest), T>
  {
    return Point<sizeof...(rest), ONLY_IF_INTEGRAL(T)>(rest...);
  }

  template <int N, typename T>
  std::ostream &operator<<(std::ostream &os, const Point<N, T> &p);

  // component-wise operators defined on Point<N,T> (with optional coercion)
  template <int N, typename T, typename T2>
  REALM_CUDA_HD bool operator==(const Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD bool operator!=(const Point<N, T> &lhs, const Point<N, T2> &rhs);

  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> operator+(const Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> &operator+=(Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> operator-(const Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> &operator-=(Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> operator*(const Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> &operator*=(Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> operator/(const Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> &operator/=(Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> operator%(const Point<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Point<N, T> &operator%=(Point<N, T> &lhs, const Point<N, T2> &rhs);

  // a Rect is a pair of points defining the lower and upper bounds of an N-D rectangle
  //  the bounds are INCLUSIVE

  template <int N, typename T>
  struct REALM_PUBLIC_API Rect {
    Point<N, T> lo, hi;

    REALM_CUDA_HD
    Rect(void);
    REALM_CUDA_HD
    Rect(const Point<N, T> &_lo, const Point<N, T> &_hi);
    // copies allow type coercion (assuming the underlying type does)
    template <typename T2>
    REALM_CUDA_HD Rect(const Rect<N, T2> &copy_from);
    template <typename T2>
    REALM_CUDA_HD Rect<N, T> &operator=(const Rect<N, T2> &copy_from);

    // constructs a guaranteed-empty rectangle
    REALM_CUDA_HD
    static Rect<N, T> make_empty(void);

    REALM_CUDA_HD
    bool empty(void) const;
    REALM_CUDA_HD
    size_t volume(void) const;

    REALM_CUDA_HD
    bool contains(const Point<N, T> &p) const;

    // true if all points in other are in this rectangle
    REALM_CUDA_HD
    bool contains(const Rect<N, T> &other) const;
    REALM_CUDA_HD
    bool contains(const IndexSpace<N, T> &is) const;

    // true if there are any points in the intersection of the two rectangles
    REALM_CUDA_HD
    bool overlaps(const Rect<N, T> &other) const;

    REALM_CUDA_HD
    Rect<N, T> intersection(const Rect<N, T> &other) const;

    // returns the _bounding box_ of the union of two rectangles (the actual union
    //  might not be a rectangle)
    REALM_CUDA_HD
    Rect<N, T> union_bbox(const Rect<N, T> &other) const;

    template <int N2, typename T2>
    Rect<N2, T2> REALM_CUDA_HD apply_transform(const Matrix<N2, N, T2> &transform,
                                               const Point<N2, T2> &offset) const;

    // copy and fill operations (wrappers for IndexSpace versions)
    Event fill(const std::vector<CopySrcDstField> &dsts,
               const ProfilingRequestSet &requests, const void *fill_value,
               size_t fill_value_size, Event wait_on = Event::NO_EVENT,
               int priority = 0) const;

    Event copy(const std::vector<CopySrcDstField> &srcs,
               const std::vector<CopySrcDstField> &dsts,
               const ProfilingRequestSet &requests, Event wait_on = Event::NO_EVENT,
               int priority = 0) const;

    Event copy(const std::vector<CopySrcDstField> &srcs,
               const std::vector<CopySrcDstField> &dsts, const IndexSpace<N, T> &mask,
               const ProfilingRequestSet &requests, Event wait_on = Event::NO_EVENT,
               int priority = 0) const;
  };

  template <int N, typename T>
  std::ostream &operator<<(std::ostream &os, const Rect<N, T> &p);

  template <int M, int N, typename T>
  std::ostream &operator<<(std::ostream &os, const Matrix<M, N, T> &p);

  template <int N, typename T, typename T2>
  REALM_CUDA_HD bool operator==(const Rect<N, T> &lhs, const Rect<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD bool operator!=(const Rect<N, T> &lhs, const Rect<N, T2> &rhs);

  // rectangles may be displaced by a vector (i.e. point)
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Rect<N, T> operator+(const Rect<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Rect<N, T> &operator+=(Rect<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Rect<N, T> operator-(const Rect<N, T> &lhs, const Point<N, T2> &rhs);
  template <int N, typename T, typename T2>
  REALM_CUDA_HD Rect<N, T> &operator-=(Rect<N, T> &lhs, const Rect<N, T2> &rhs);

  template <int M, int N, typename T>
  struct REALM_PUBLIC_API Matrix {
    Point<N, T> rows[M];

    REALM_CUDA_HD
    Matrix(void);
    // copies allow type coercion (assuming the underlying type does)
    template <typename T2>
    REALM_CUDA_HD Matrix(const Matrix<M, N, T2> &copy_from);
    template <typename T2>
    REALM_CUDA_HD Matrix<M, N, T> &operator=(const Matrix<M, N, T2> &copy_from);

    REALM_CUDA_HD
    Point<N, T> &operator[](int index);
    REALM_CUDA_HD
    const Point<N, T> &operator[](int index) const;
  };

  template <int M, int N, typename T, typename T2>
  REALM_CUDA_HD Point<M, T> operator*(const Matrix<M, N, T> &m, const Point<N, T2> &p);
  template <int M, int P, int N, typename T, typename T2>
  REALM_CUDA_HD Matrix<M, N, T> operator*(const Matrix<M, P, T> &m,
                                          const Matrix<P, N, T2> &n);

  template <int N, typename T>
  class PointInRectIterator {
  public:
    Point<N, T> p;
    bool valid;
    Rect<N, T> rect;
    bool fortran_order;

    REALM_CUDA_HD
    PointInRectIterator(void);
    REALM_CUDA_HD
    PointInRectIterator(const Rect<N, T> &_r, bool _fortran_order = true);
    REALM_CUDA_HD
    void reset(const Rect<N, T> &_r, bool _fortran_order = true);
    REALM_CUDA_HD
    bool step(void);
  };

}; // namespace Realm

// specializations of std::less<T> for Point/Rect<N,T> allow
//  them to be used in STL containers
namespace std {
  template <int N, typename T>
  struct less<Realm::Point<N, T>> {
    bool operator()(const Realm::Point<N, T> &p1, const Realm::Point<N, T> &p2) const;
  };

  template <int N, typename T>
  struct less<Realm::Rect<N, T>> {
    bool operator()(const Realm::Rect<N, T> &r1, const Realm::Rect<N, T> &r2) const;
  };
}; // namespace std

#include "realm/point.inl"

#undef ONLY_IF_INTEGRAL

#endif // ifndef REALM_POINT_H
