/*
 * SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights
 * reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legate/experimental/stl/detail/config.hpp>
#include <legate/experimental/stl/detail/meta.hpp>
#include <legate/experimental/stl/detail/type_traits.hpp>

#if LEGATE_STL_HAS_STD_RANGES()

#include <ranges>

// Include this last
#include <prefix.hpp>

/**
 * @cond
 */

namespace legate::experimental::stl {

using std::ranges::begin;
using std::ranges::end;
using std::ranges::range;

using std::ranges::iterator_t;
using std::ranges::range_reference_t;
using std::ranges::range_value_t;
using std::ranges::sentinel_t;

}  // namespace legate::experimental::stl

/**
 * @endcond
 */

#else

#include <iterator>

// Include this last
#include <legate/experimental/stl/detail/prefix.hpp>

/**
 * @cond
 */

namespace legate::experimental::stl {

namespace detail {
namespace begin {

void begin();

template <typename Ty>
using member_begin_t = decltype(std::declval<Ty>().begin());

template <typename Ty>
using free_begin_t = decltype(begin(std::declval<Ty>()));

template <typename Ty>
using begin_fn = meta::if_c<meta::evaluable_q<member_begin_t, Ty>,
                            meta::quote<member_begin_t>,
                            meta::quote<free_begin_t>>;

template <typename Ty>
using begin_result_t = meta::eval<begin_fn<Ty>, Ty>;

class tag {
 public:
  template <typename Range>
  static constexpr bool nothrow_begin() noexcept
  {
    if constexpr (meta::evaluable_q<member_begin_t, Range>) {
      return noexcept(std::declval<Range>().begin());
    } else {
      return noexcept(begin(std::declval<Range>()));
    }
  }

  template <typename Range>
  [[nodiscard]] auto operator()(Range&& rng) const noexcept(nothrow_begin<Range>())
    -> begin_result_t<Range>
  {
    if constexpr (meta::evaluable_q<member_begin_t, Range>) {
      return std::forward<Range>(rng).begin();
    } else {
      return begin(std::forward<Range>(rng));
    }
  }
};

}  // namespace begin

namespace end {

void end();

template <typename Ty>
using member_end_t = decltype(std::declval<Ty>().end());

template <typename Ty>
using free_end_t = decltype(end(std::declval<Ty>()));

template <typename Ty>
using end_fn = meta::
  if_c<meta::evaluable_q<member_end_t, Ty>, meta::quote<member_end_t>, meta::quote<free_end_t>>;

template <typename Ty>
using end_result_t = meta::eval<end_fn<Ty>, Ty>;

class tag {
 public:
  template <typename Range>
  static constexpr bool nothrow_end() noexcept
  {
    if constexpr (meta::evaluable_q<member_end_t, Range>) {
      return noexcept(std::declval<Range>().end());
    } else {
      return noexcept(end(std::declval<Range>()));
    }
  }

  template <typename Range>
  [[nodiscard]] auto operator()(Range&& rng) const noexcept(nothrow_end<Range>())
    -> end_result_t<Range>
  {
    if constexpr (meta::evaluable_q<member_end_t, Range>) {
      return std::forward<Range>(rng).end();
    } else {
      return end(std::forward<Range>(rng));
    }
  }
};

}  // namespace end
}  // namespace detail

namespace tag {

// NOLINTBEGIN(readability-identifier-naming)
inline constexpr detail::begin::tag begin{};
inline constexpr detail::end::tag end{};
// NOLINTEND(readability-identifier-naming)

}  // namespace tag

// Fully qualify the namespace to ensure that the compiler doesn't pick some other random one
// NOLINTNEXTLINE(google-build-using-namespace)
using namespace ::legate::experimental::stl::tag;

//////////////////////////////////////////////////////////////////////////////////////////////////
template <typename Range>
using iterator_t = decltype(stl::begin((std::declval<Range>())));

template <typename Range>
using sentinel_t = decltype(stl::end((std::declval<Range>())));

template <typename Range>
using range_reference_t = decltype(*stl::begin((std::declval<Range>())));

template <typename Range>
using range_value_t = typename std::iterator_traits<iterator_t<Range>>::value_type;

//////////////////////////////////////////////////////////////////////////////////////////////////
namespace detail {

template <typename Iter>
auto is_iterator_like(Iter iter, Iter other)
  -> decltype((void)++iter, (void)*iter, (void)(iter == other));

template <typename Range>
auto is_range_like(Range&& rng)
  -> decltype(detail::is_iterator_like(stl::begin(rng), stl::begin(rng)),
              (void)(stl::begin(rng) == stl::end(rng)));

template <typename Range>
using is_range_like_t = decltype(detail::is_range_like(std::declval<Range>()));

}  // namespace detail

template <typename Range>
inline constexpr bool is_range_v = meta::evaluable_q<detail::is_range_like_t, Range>;

}  // namespace legate::experimental::stl

/**
 * @endcond
 */

#endif

/**
 * @cond
 */

namespace legate::experimental::stl {
//////////////////////////////////////////////////////////////////////////////////////////////////
namespace tags {
namespace as_range {

void as_range();

template <typename T>
using as_range_t = decltype(as_range(std::declval<T>()));

template <typename T>
inline constexpr bool is_range_like_v = meta::evaluable_q<as_range_t, T>;

template <typename T>
using as_range_result_t =
  meta::eval<meta::if_c<is_range_v<T>, meta::always<T>, meta::quote<as_range_t>>, T>;

class tag {
 public:
  template <typename T>
  static constexpr bool noexcept_as_range() noexcept
  {
    if constexpr (is_range_v<T>) {
      return noexcept(std::decay_t<T>{std::declval<T>()});
    } else {
      return noexcept(as_range(std::declval<T>()));
    }
  }

  template <typename T>
  [[nodiscard]] as_range_result_t<T> operator()(T&& rng) const noexcept(noexcept_as_range<T>())
  {
    if constexpr (is_range_v<T>) {
      return std::forward<T>(rng);
    } else {
      return as_range(std::forward<T>(rng));
    }
  }
};

}  // namespace as_range

inline namespace obj {

inline constexpr as_range::tag as_range{};  // NOLINT(readability-identifier-naming)

}  // namespace obj
}  // namespace tags

// Fully qualify the namespace to ensure that the compiler doesn't pick some other random one
// NOLINTNEXTLINE(google-build-using-namespace)
using namespace ::legate::experimental::stl::tags::obj;

template <typename T>
using as_range_t = call_result_c_t<as_range, T>;

}  // namespace legate::experimental::stl

/**
 * @endcond
 */

#include <legate/experimental/stl/detail/suffix.hpp>
