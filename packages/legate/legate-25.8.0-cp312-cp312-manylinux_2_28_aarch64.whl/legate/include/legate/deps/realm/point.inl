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

// nop, but helps IDEs
#include "realm/point.h"

#include "realm/serialize.h"

#if defined(__CUDACC__) || defined(__HIPCC__)
#ifdef REALM_USE_HIP
#include <hip/hip_runtime.h>
#endif
#endif

TEMPLATE_TYPE_IS_SERIALIZABLE2(int N, typename T, Realm::Point<N, T>);
TEMPLATE_TYPE_IS_SERIALIZABLE2(int N, typename T, Realm::Rect<N, T>);
TEMPLATE_TYPE_IS_SERIALIZABLE3(int M, int N, typename T, Realm::Matrix<M, N, T>);

namespace Realm {

  ////////////////////////////////////////////////////////////////////////
  //
  // class Point<N,T>

  template <int N, typename T>
  REALM_CUDA_HD inline Point<N, T>::Point(value_type val)
  {
    for(int i = 0; i < N; i++) {
      values[i] = val;
    }
  }

  template <int N, typename T>
  template <typename Arg0, typename Arg1, typename... Args>
  REALM_CUDA_HD inline Point<N, T>::Point(Arg0 val0, Arg1 val1, Args... vals)
    // TODO(cperry): Very bad!  We should not static_cast these for the user, as it can
    // hide sign and casting issues.  Kept here for compatibility while we weed out all
    // the cases in our codebase
    : values{static_cast<value_type>(val0), static_cast<value_type>(val1),
             static_cast<value_type>(vals)...}
  {}

  template <int N, typename T>
  template <typename T2, std::enable_if_t<std::is_integral<T2>::value, bool>>
  REALM_CUDA_HD inline Point<N, T>::Point(T2 val)
  {
    for(int i = 0; i < N; i++) {
      values[i] = val;
    }
  }

  template <int N, typename T>
  template <typename T2, std::enable_if_t<std::is_integral<T2>::value, bool>>
  REALM_CUDA_HD inline Point<N, T>::Point(T2 vals[N])
  {
    for(int i = 0; i < N; i++) {
      values[i] = vals[i];
    }
  }

  template <int N, typename T>
  template <typename T2>
  REALM_CUDA_HD inline Point<N, T>::Point(const Point<N, T2> &copy_from)
  {
    for(int i = 0; i < N; i++) {
      values[i] = copy_from.values[i];
    }
  }

  template <int N, typename T>
  template <typename T2>
  REALM_CUDA_HD inline Point<N, T> &Point<N, T>::operator=(const Point<N, T2> &copy_from)
  {
    for(int i = 0; i < N; i++) {
      values[i] = copy_from.values[i];
    }
    return *this;
  }

  template <int N, typename T>
  REALM_CUDA_HD inline T &Point<N, T>::operator[](int index)
  {
    assert(index < N);
    return values[index];
  }

  template <int N, typename T>
  REALM_CUDA_HD inline const T &Point<N, T>::operator[](int index) const
  {
    assert(index < N);
    return values[index];
  }

  template <int N, typename T>
  template <typename T2>
  REALM_CUDA_HD inline T Point<N, T>::dot(const Point<N, T2> &rhs) const
  {
    T acc = values[0] * rhs.values[0];
    for(int i = 1; i < N; i++) {
      acc += values[i] * rhs.values[i];
    }
    return acc;
  }

  template <int N, typename T>
  REALM_CUDA_HD T &Point<N, T>::x()
  {
    static_assert(N > 0);
    return values[0];
  }
  template <int N, typename T>
  REALM_CUDA_HD T &Point<N, T>::y()
  {
    static_assert(N > 1);
    return values[1];
  }
  template <int N, typename T>
  REALM_CUDA_HD T &Point<N, T>::z()
  {
    static_assert(N > 2);
    return values[2];
  }
  template <int N, typename T>
  REALM_CUDA_HD T &Point<N, T>::w()
  {
    static_assert(N > 3);
    return values[3];
  }

  template <int N, typename T>
  REALM_CUDA_HD const T &Point<N, T>::x() const
  {
    static_assert(N > 0);
    return values[0];
  }
  template <int N, typename T>
  REALM_CUDA_HD const T &Point<N, T>::y() const
  {
    static_assert(N > 1);
    return values[1];
  }
  template <int N, typename T>
  REALM_CUDA_HD const T &Point<N, T>::z() const
  {
    static_assert(N > 2);
    return values[2];
  }
  template <int N, typename T>
  REALM_CUDA_HD const T &Point<N, T>::w() const
  {
    static_assert(N > 3);
    return values[3];
  }

  template <int N, typename T>
  REALM_CUDA_HD
      /*static*/ constexpr inline Point<N, T>
      Point<N, T>::ZEROES(void)
  {
    return Point<N, T>(static_cast<T>(0));
  }

  template <int N, typename T>
  REALM_CUDA_HD
      /*static*/ constexpr inline Point<N, T>
      Point<N, T>::ONES(void)
  {
    return Point<N, T>(static_cast<T>(1));
  }

  template <int N, typename T>
  inline std::ostream &operator<<(std::ostream &os, const Point<N, T> &p)
  {
    os << '<' << p[0];
    for(int i = 1; i < N; i++) {
      os << ',' << p[i];
    }
    os << '>';
    return os;
  }

  // 1D specialization (needed for implicit conversion of coordinate to 1D point)
  template <typename T>
  struct REALM_PUBLIC_API Point<1, T> {

    typedef ONLY_IF_INTEGRAL(T) value_type;
    value_type value;

    REALM_CUDA_HD
    Point(void) {}
    REALM_CUDA_HD
    Point(value_type val)
      : value(val)
    {}
    template <typename T2, std::enable_if_t<std::is_integral<T2>::value, bool> = true>
    REALM_CUDA_HD explicit Point(T2 vals[1])
      : value(vals[0])
    {}
    // construct from any integral value
    template <typename T2, std::enable_if_t<std::is_integral<T2>::value, bool> = true>
    REALM_CUDA_HD explicit Point(T2 val)
      : value(val)
    {}
    // copies allow type coercion (assuming the underlying type does)
    template <typename T2>
    REALM_CUDA_HD Point(const Point<1, T2> &copy_from)
      : value(copy_from.value)
    {}
    template <typename T2>
    REALM_CUDA_HD Point<1, T> &operator=(const Point<1, T2> &copy_from)
    {
      value = copy_from.value;
      return *this;
    }

    REALM_CUDA_HD
    T &operator[](int index)
    {
      assert(index == 0);
      return value;
    }
    REALM_CUDA_HD
    const T &operator[](int index) const
    {
      assert(index == 0);
      return value;
    }

    template <typename T2>
    REALM_CUDA_HD T dot(const Point<1, T2> &rhs) const
    {
      return value * rhs.value;
    }

    // 1-4D accessors.  These will only be available if the class's dimensioned allow for
    // it, otherwise it is a compiler error to use them
    REALM_CUDA_HD T &x() { return value; }
    REALM_CUDA_HD const T &x() const { return value; }

    REALM_CUDA_HD
    operator T() const { return value; }

    REALM_CUDA_HD
    static constexpr Point<1, T> ZEROES(void) { return Point<1, T>(0); }
    REALM_CUDA_HD
    static constexpr Point<1, T> ONES(void) { return Point<1, T>(1); }
  };

  // component-wise operators defined on Point<N,T> (with optional coercion)
  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline bool operator==(const Point<N, T> &lhs, const Point<N, T2> &rhs)
  {
    for(int i = 0; i < N; i++) {
      if(lhs[i] != rhs[i]) {
        return false;
      }
    }
    return true;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline bool operator!=(const Point<N, T> &lhs, const Point<N, T2> &rhs)
  {
    for(int i = 0; i < N; i++) {
      if(lhs[i] != rhs[i]) {
        return true;
      }
    }
    return false;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> operator+(const Point<N, T> &lhs,
                                             const Point<N, T2> &rhs)
  {
    Point<N, T> out;
    for(int i = 0; i < N; i++) {
      out[i] = lhs[i] + rhs[i];
    }
    return out;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> &operator+=(Point<N, T> &lhs, const Point<N, T2> &rhs)
  {
    for(int i = 0; i < N; i++) {
      lhs[i] += rhs[i];
    }
    return lhs;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> operator-(const Point<N, T> &lhs,
                                             const Point<N, T2> &rhs)
  {
    Point<N, T> out;
    for(int i = 0; i < N; i++) {
      out[i] = lhs[i] - rhs[i];
    }
    return out;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> &operator-=(Point<N, T> &lhs, const Point<N, T2> &rhs)
  {
    for(int i = 0; i < N; i++) {
      lhs[i] -= rhs[i];
    }
    return lhs;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> operator*(const Point<N, T> &lhs,
                                             const Point<N, T2> &rhs)
  {
    Point<N, T> out;
    for(int i = 0; i < N; i++) {
      out[i] = lhs[i] * rhs[i];
    }
    return out;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> &operator*=(Point<N, T> &lhs, const Point<N, T2> &rhs)
  {
    for(int i = 0; i < N; i++) {
      lhs[i] *= rhs[i];
    }
    return lhs;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> operator/(const Point<N, T> &lhs,
                                             const Point<N, T2> &rhs)
  {
    Point<N, T> out;
    for(int i = 0; i < N; i++) {
      out[i] = lhs[i] / rhs[i];
    }
    return out;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> &operator/=(Point<N, T> &lhs, const Point<N, T2> &rhs)
  {
    for(int i = 0; i < N; i++) {
      lhs[i] /= rhs[i];
    }
    return lhs;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> operator%(const Point<N, T> &lhs,
                                             const Point<N, T2> &rhs)
  {
    Point<N, T> out;
    for(int i = 0; i < N; i++) {
      out[i] = lhs[i] % rhs[i];
    }
    return out;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<N, T> &operator%=(Point<N, T> &lhs, const Point<N, T2> &rhs)
  {
    for(int i = 0; i < N; i++) {
      lhs[i] %= rhs[i];
    }
    return lhs;
  }

  ////////////////////////////////////////////////////////////////////////
  //
  // class Rect<N,T>

  template <int N, typename T>
  REALM_CUDA_HD inline Rect<N, T>::Rect(void)
  {}

  template <int N, typename T>
  REALM_CUDA_HD inline Rect<N, T>::Rect(const Point<N, T> &_lo, const Point<N, T> &_hi)
    : lo(_lo)
    , hi(_hi)
  {}

  template <int N, typename T>
  template <typename T2>
  REALM_CUDA_HD inline Rect<N, T>::Rect(const Rect<N, T2> &copy_from)
    : lo(copy_from.lo)
    , hi(copy_from.hi)
  {}

  template <int N, typename T>
  template <typename T2>
  REALM_CUDA_HD inline Rect<N, T> &Rect<N, T>::operator=(const Rect<N, T2> &copy_from)
  {
    lo = copy_from.lo;
    hi = copy_from.hi;
    return *this;
  }

  template <int N, typename T>
  REALM_CUDA_HD inline /*static*/ Rect<N, T> Rect<N, T>::make_empty(void)
  {
    Rect<N, T> r;
    T v = T(); // assume any user-defined default constructor initializes things
    for(int i = 0; i < N; i++) {
      r.hi[i] = v;
    }
    ++v;
    for(int i = 0; i < N; i++) {
      r.lo[i] = v;
    }
    return r;
  }

  template <int N, typename T>
  REALM_CUDA_HD inline bool Rect<N, T>::empty(void) const
  {
    for(int i = 0; i < N; i++) {
      if(lo[i] > hi[i]) {
        return true;
      }
    }
    return false;
  }

  template <int N, typename T>
  REALM_CUDA_HD inline size_t Rect<N, T>::volume(void) const
  {
    size_t v = 1;
    for(int i = 0; i < N; i++) {
      if(lo[i] > hi[i]) {
        return 0;
      } else {
        // have to convert both 'hi' and 'lo' to size_t before subtracting
        //  to avoid potential signed integer overflow
        v *= (static_cast<size_t>(hi[i]) - static_cast<size_t>(lo[i]) + 1);
      }
    }
    return v;
  }

  template <int N, typename T>
  REALM_CUDA_HD inline bool Rect<N, T>::contains(const Point<N, T> &p) const
  {
    for(int i = 0; i < N; i++) {
      if((p[i] < lo[i]) || (p[i] > hi[i])) {
        return false;
      }
    }
    return true;
  }

  // true if all points in other are in this rectangle
  template <int N, typename T>
  REALM_CUDA_HD inline bool Rect<N, T>::contains(const Rect<N, T> &other) const
  {
    // containment is weird w.r.t. emptiness: if other is empty, the answer is
    //  always true - if we're empty, the answer is false, unless other was empty
    // this means we can early-out with true if other is empty, but have to remember
    //  our emptiness separately
    bool ctns = true;
    for(int i = 0; i < N; i++) {
      if(other.lo[i] > other.hi[i]) {
        return true; // other is empty
      }
      // now that we know the other is nonempty, we need:
      //  lo[i] <= other.lo[i] ^ other.hi[i] <= hi[i]
      // (which can only be satisfied if we're non-empty)
      if((lo[i] > other.lo[i]) || (other.hi[i] > hi[i])) {
        ctns = false;
      }
    }
    return ctns;
  }

  // true if all points in other are in this rectangle
  // FIXME: the bounds of an index space aren't necessarily tight - is that ok?
  template <int N, typename T>
  REALM_CUDA_HD inline bool Rect<N, T>::contains(const IndexSpace<N, T> &other) const
  {
    return contains(other.bounds);
  }

  // true if there are any points in the intersection of the two rectangles
  template <int N, typename T>
  REALM_CUDA_HD inline bool Rect<N, T>::overlaps(const Rect<N, T> &other) const
  {
    // overlapping requires there be an element that lies in both ranges, which
    //  is equivalent to saying that both lo's are <= both hi's - this catches
    //  cases where either rectangle is empty
    for(int i = 0; i < N; i++) {
      if((lo[i] > hi[i]) || (lo[i] > other.hi[i]) || (other.lo[i] > hi[i]) ||
         (other.lo[i] > other.hi[i])) {
        return false;
      }
    }
    return true;
  }

  template <int N, typename T>
  REALM_CUDA_HD inline Rect<N, T> Rect<N, T>::intersection(const Rect<N, T> &other) const
  {
    Rect<N, T> out;
    for(int i = 0; i < N; i++) {
      out.lo[i] = (lo[i] < other.lo[i]) ? other.lo[i] : lo[i]; // max
      out.hi[i] = (hi[i] < other.hi[i]) ? hi[i] : other.hi[i]; // min
    }
    return out;
  };

  template <int N, typename T>
  REALM_CUDA_HD inline Rect<N, T> Rect<N, T>::union_bbox(const Rect<N, T> &other) const
  {
    if(empty()) {
      return other;
    }
    if(other.empty()) {
      return *this;
    }
    // the code below only works if both rectangles are non-empty
    Rect<N, T> out;
    for(int i = 0; i < N; i++) {
      out.lo[i] = (lo[i] < other.lo[i]) ? lo[i] : other.lo[i]; // min
      out.hi[i] = (hi[i] < other.hi[i]) ? other.hi[i] : hi[i]; // max
    }
    return out;
  };

  template <int N, typename T>
  template <int N2, typename T2>
  REALM_CUDA_HD inline Rect<N2, T2>
  Rect<N, T>::apply_transform(const Matrix<N2, N, T2> &transform,
                              const Point<N2, T2> &offset) const
  {
    Rect<N2, T2> tranformed_rect(offset, offset);
    for(int i = 0; i < N2; i++) {
      for(int j = 0; j < N; j++) {
        T2 e = transform.rows[i][j];
        if(e > 0) {
          tranformed_rect.lo[i] += e * lo[j];
          tranformed_rect.hi[i] += e * hi[j];
        }
        if(e < 0) {
          tranformed_rect.lo[i] += e * hi[j];
          tranformed_rect.hi[i] += e * lo[j];
        }
      }
    }
    return tranformed_rect;
  }

  template <int N, typename T>
  inline std::ostream &operator<<(std::ostream &os, const Rect<N, T> &p)
  {
    os << p.lo << ".." << p.hi;
    return os;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline bool operator==(const Rect<N, T> &lhs, const Rect<N, T2> &rhs)
  {
    return (lhs.lo == rhs.lo) && (lhs.hi == rhs.hi);
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline bool operator!=(const Rect<N, T> &lhs, const Rect<N, T2> &rhs)
  {
    return (lhs.lo != rhs.lo) || (lhs.hi != rhs.hi);
  }

  // rectangles may be displaced by a vector (i.e. point)
  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Rect<N, T> operator+(const Rect<N, T> &lhs,
                                            const Point<N, T2> &rhs)
  {
    return Rect<N, T>(lhs.lo + rhs, lhs.hi + rhs);
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Rect<N, T> &operator+=(Rect<N, T> &lhs, const Point<N, T2> &rhs)
  {
    lhs.lo += rhs;
    lhs.hi += rhs;
    return lhs;
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Rect<N, T> operator-(const Rect<N, T> &lhs,
                                            const Point<N, T2> &rhs)
  {
    return Rect<N, T>(lhs.lo - rhs, lhs.hi - rhs);
  }

  template <int N, typename T, typename T2>
  REALM_CUDA_HD inline Rect<N, T> &operator-=(Rect<N, T> &lhs, const Rect<N, T2> &rhs)
  {
    lhs.lo -= rhs;
    lhs.hi -= rhs;
    return lhs;
  }

  ////////////////////////////////////////////////////////////////////////
  //
  // class Matrix<M,N,T>

  template <int M, int N, typename T>
  REALM_CUDA_HD inline Matrix<M, N, T>::Matrix(void)
  {}

  // copies allow type coercion (assuming the underlying type does)
  template <int M, int N, typename T>
  template <typename T2>
  REALM_CUDA_HD inline Matrix<M, N, T>::Matrix(const Matrix<M, N, T2> &copy_from)
  {
    for(int i = 0; i < M; i++) {
      rows[i] = copy_from[i];
    }
  }

  template <int M, int N, typename T>
  template <typename T2>
  REALM_CUDA_HD inline Matrix<M, N, T> &
  Matrix<M, N, T>::operator=(const Matrix<M, N, T2> &copy_from)
  {
    for(int i = 0; i < M; i++) {
      rows[i] = copy_from[i];
    }
    return *this;
  }

  template <int M, int N, typename T, typename T2>
  REALM_CUDA_HD inline Point<M, T> operator*(const Matrix<M, N, T> &m,
                                             const Point<N, T2> &p)
  {
    Point<M, T> out;
    for(int j = 0; j < M; j++) {
      out[j] = m.rows[j].dot(p);
    }
    return out;
  }

  template <int M, int P, int N, typename T, typename T2>
  REALM_CUDA_HD inline Matrix<M, N, T> operator*(const Matrix<M, P, T> &m,
                                                 const Matrix<P, N, T2> &n)
  {
    Matrix<M, N, T> out;
    for(int i = 0; i < M; i++) {
      for(int j = 0; j < N; j++) {
        out[i][j] = m[i][0] * n[0][j];
        for(int k = 1; k < P; k++) {
          out[i][j] += m[i][k] * n[k][j];
        }
      }
    }
    return out;
  }

  template <int M, int N, typename T>
  REALM_CUDA_HD inline Point<N, T> &Matrix<M, N, T>::operator[](int index)
  {
    return rows[index];
  }

  template <int M, int N, typename T>
  REALM_CUDA_HD inline const Point<N, T> &Matrix<M, N, T>::operator[](int index) const
  {
    return rows[index];
  }

  template <int M, int N, typename T>
  inline std::ostream &operator<<(std::ostream &os, const Matrix<M, N, T> &matrix)
  {
    os << '[';
    for(int i = 0; i < M; i++) {
      for(int j = 0; j < N; j++) {
        os << matrix[i][j] << (j == N - 1 ? "" : " ");
      }
      os << (i == M - 1 ? "" : ";");
    }
    os << "]";
    return os;
  }

  ////////////////////////////////////////////////////////////////////////
  //
  // class PointInRectIterator<N,T>

  template <int N, typename T>
  REALM_CUDA_HD inline PointInRectIterator<N, T>::PointInRectIterator(void)
    : valid(false)
  {}

  template <int N, typename T>
  REALM_CUDA_HD inline PointInRectIterator<N, T>::PointInRectIterator(
      const Rect<N, T> &_r, bool _fortran_order /*= true*/)
    : p(_r.lo)
    , valid(!_r.empty())
    , rect(_r)
    , fortran_order(_fortran_order)
  {}

  template <int N, typename T>
  REALM_CUDA_HD inline void
  PointInRectIterator<N, T>::reset(const Rect<N, T> &_r, bool _fortran_order /*= true*/)
  {
    p = _r.lo;
    valid = !_r.empty();
    rect = _r;
    fortran_order = _fortran_order;
  }

  template <int N, typename T>
  REALM_CUDA_HD inline bool PointInRectIterator<N, T>::step(void)
  {
    assert(valid); // can't step an iterator that's already done
    if(!valid) {
      return false;
    }
    // despite the check above, g++ 11.1 in c++20 mode complains that `rect`
    //  might be uninitialized even though the only way `valid` can become
    //  true is with an initialization of `rect`
#ifdef REALM_COMPILER_IS_GCC
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"
#endif
    if(N == 1) {
      // 1-D doesn't care about fortran/C order
      if(p[0] < rect.hi[0]) {
        p[0]++;
        return true;
      }
    } else {
      if(fortran_order) {
        // do dimensions in increasing order
        for(int i = 0; i < N; i++) {
          if(p[i] < rect.hi[i]) {
            p[i]++;
            return true;
          }
          p[i] = rect.lo[i];
        }
      } else {
        // do dimensions in decreasing order
        for(int i = N - 1; i >= 0; i--) {
          if(p[i] < rect.hi[i]) {
            p[i]++;
            return true;
          }
          p[i] = rect.lo[i];
        }
      }
    }
#ifdef REALM_COMPILER_IS_GCC
#pragma GCC diagnostic pop
#endif
    // if we fall through, we're out of points
    valid = false;
    return false;
  }

}; // namespace Realm

namespace std {
  template <int N, typename T>
  inline bool less<Realm::Point<N, T>>::operator()(const Realm::Point<N, T> &p1,
                                                   const Realm::Point<N, T> &p2) const
  {
    for(int i = 0; i < N; i++) {
      if(p1[i] < p2[i]) {
        return true;
      }
      if(p1[i] > p2[i]) {
        return false;
      }
    }
    return false;
  }

  template <int N, typename T>
  inline bool less<Realm::Rect<N, T>>::operator()(const Realm::Rect<N, T> &r1,
                                                  const Realm::Rect<N, T> &r2) const
  {
    if(std::less<Realm::Point<N, T>>()(r1.lo, r2.lo)) {
      return true;
    }
    if(std::less<Realm::Point<N, T>>()(r2.lo, r1.lo)) {
      return false;
    }
    if(std::less<Realm::Point<N, T>>()(r1.hi, r2.hi)) {
      return true;
    }
    if(std::less<Realm::Point<N, T>>()(r2.hi, r1.hi)) {
      return false;
    }
    return false;
  }

}; // namespace std
