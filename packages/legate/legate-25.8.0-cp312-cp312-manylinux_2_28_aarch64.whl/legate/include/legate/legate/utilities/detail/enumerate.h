/*
 * SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights
 * reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legate_defines.h>

#include <legate/utilities/cpp_version.h>
#include <legate/utilities/detail/zip.h>

#include <cstddef>

// As of 3/14/2024, this include causes shadow warnings in GPU debug mode compilation
LEGATE_PRAGMA_PUSH();
LEGATE_PRAGMA_GNU_IGNORE("-Wshadow");
#include <thrust/iterator/counting_iterator.h>
LEGATE_PRAGMA_POP();

static_assert(LEGATE_CPP_MIN_VERSION <
                23,  // NOLINT(readability-magic-numbers) std::enumerate since C++23
              "Can remove this module in favor of std::ranges::views::enumerate and/or "
              "std::ranges::enumerate_view");

namespace legate::detail {

class Enumerator {
 public:
  using iterator          = thrust::counting_iterator<std::ptrdiff_t>;
  using const_iterator    = thrust::counting_iterator<std::ptrdiff_t>;
  using value_type        = typename iterator::value_type;
  using iterator_category = typename iterator::iterator_category;
  using difference_type   = typename iterator::difference_type;
  using pointer           = typename iterator::pointer;
  using reference         = typename iterator::reference;

  constexpr Enumerator() noexcept = default;
  constexpr explicit Enumerator(value_type start) noexcept;

  [[nodiscard]] constexpr value_type start() const noexcept;

  [[nodiscard]] iterator begin() const noexcept;
  [[nodiscard]] const_iterator cbegin() const noexcept;

  [[nodiscard]] iterator end() const noexcept;
  [[nodiscard]] const_iterator cend() const noexcept;

 private:
  value_type start_{};
};

/**
 * @brief Enumerate an iterable
 *
 * @param iterable The iterable to enumerate
 * @param start [optional] Set the starting value for the enumerator
 *
 * @return The enumerator iterator adaptor
 *
 * @details The enumerator is classed as a bidirectional iterator, so can be both incremented
 * and decremented. Decrementing the enumerator will decrease the count. However, this only
 * applies if \p iterable is itself at least bidirectional. If \p iterable does not satisfy
 * bidirectional iteration, then the returned enumerator will assume the iterator category of
 * \p iterable.
 *
 * @snippet noinit/enumerate.cc Constructing an enumerator
 */
template <typename T>
[[nodiscard]] zip_detail::Zipper<zip_detail::ZiperatorShortest, Enumerator, T> enumerate(
  T&& iterable, typename Enumerator::value_type start = {});

}  // namespace legate::detail

#include <legate/utilities/detail/enumerate.inl>
