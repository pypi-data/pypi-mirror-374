/*
 * SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights
 * reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legate_defines.h>

#include <legate/utilities/detail/type_traits.h>
#include <legate/utilities/hash.h>
#include <legate/utilities/span.h>

#include <cstdint>
#include <initializer_list>
#include <iosfwd>
#include <string>
#include <vector>

namespace legate {

// A simple wrapper around an STL vector to provide common utilities
template <typename T>
class tuple {
 public:
  using container_type = std::vector<T>;
  using value_type     = typename container_type::value_type;
  using size_type      = typename container_type::size_type;
  using iterator       = typename container_type::iterator;
  using const_iterator = typename container_type::const_iterator;

  tuple() noexcept = default;

  explicit tuple(const container_type& values);
  explicit tuple(container_type&& values);
  tuple(std::initializer_list<T> list);

  tuple(const tuple&)                = default;
  tuple(tuple&&) noexcept            = default;
  tuple& operator=(const tuple&)     = default;
  tuple& operator=(tuple&&) noexcept = default;

  [[nodiscard]] const T& at(std::uint32_t idx) const;
  [[nodiscard]] T& at(std::uint32_t idx);
  [[nodiscard]] const T& operator[](std::uint32_t idx) const;
  [[nodiscard]] T& operator[](std::uint32_t idx);

  bool operator==(const tuple& other) const;
  bool operator!=(const tuple& other) const;
  // These functions do ELEMENTWISE comparisons, not lexicographic ones.
  [[nodiscard]] bool less(const tuple& other) const;
  [[nodiscard]] bool less_equal(const tuple& other) const;
  [[nodiscard]] bool greater(const tuple& other) const;
  [[nodiscard]] bool greater_equal(const tuple& other) const;
  template <typename U = T>
  auto operator+(const tuple<U>& other) const;
  template <typename U = T>
  auto operator+(const U& other) const;
  template <typename U = T>
  auto operator-(const tuple<U>& other) const;
  template <typename U = T>
  auto operator-(const U& other) const;
  template <typename U = T>
  auto operator*(const tuple<U>& other) const;
  template <typename U = T>
  auto operator*(const U& other) const;
  template <typename U = T>
  auto operator%(const tuple<U>& other) const;
  template <typename U = T>
  auto operator%(const U& other) const;
  template <typename U = T>
  auto operator/(const tuple<U>& other) const;
  template <typename U = T>
  auto operator/(const U& other) const;

  [[nodiscard]] bool empty() const;
  [[nodiscard]] size_type size() const;
  void reserve(size_type size);

  template <typename U = T>
  [[nodiscard]] tuple insert(std::int32_t pos, U&& value) const;
  template <typename U = T>
  [[nodiscard]] tuple append(U&& value) const;
  [[nodiscard]] tuple remove(std::int32_t pos) const;
  template <typename U = T>
  [[nodiscard]] tuple update(std::int32_t pos, U&& value) const;

  template <typename U = T>
  void insert_inplace(std::int32_t pos, U&& value);
  template <typename U = T>
  void append_inplace(U&& value);
  void remove_inplace(std::int32_t pos);

  template <typename FUNC, typename U>
  [[nodiscard]] T reduce(FUNC&& func, U&& init) const;
  [[nodiscard]] T sum() const;
  [[nodiscard]] T volume() const;
  [[nodiscard]] bool all() const;
  template <typename PRED>
  [[nodiscard]] bool all(PRED&& pred) const;
  [[nodiscard]] bool any() const;
  template <typename PRED>
  [[nodiscard]] bool any(PRED&& pred) const;
  [[nodiscard]] tuple map(Span<const std::int32_t> mapping) const;
  void map_inplace(std::vector<std::int32_t>& mapping);

  [[nodiscard]] std::string to_string() const;
  template <typename U>
  friend std::ostream& operator<<(std::ostream& out, const tuple<U>& tpl);

  [[nodiscard]] container_type& data();
  [[nodiscard]] const container_type& data() const;

  [[nodiscard]] iterator begin();
  [[nodiscard]] const_iterator cbegin() const;
  [[nodiscard]] const_iterator begin() const;

  [[nodiscard]] iterator end();
  [[nodiscard]] const_iterator cend() const;
  [[nodiscard]] const_iterator end() const;

  [[nodiscard]] std::size_t hash() const;

 private:
  container_type data_{};
};

template <typename T>
[[nodiscard]] tuple<T> from_range(T stop);

template <typename T>
[[nodiscard]] tuple<T> from_range(T start, T stop);

template <typename T>
[[nodiscard]] tuple<T> full(detail::type_identity_t<typename tuple<T>::size_type> size, T init);

template <typename FUNC, typename T>
[[nodiscard]] auto apply(FUNC&& func, const tuple<T>& rhs);

template <typename FUNC, typename T1, typename T2>
[[nodiscard]] auto apply(FUNC&& func, const tuple<T1>& rhs1, const tuple<T2>& rhs2);

template <typename FUNC, typename T1, typename T2>
[[nodiscard]] auto apply(FUNC&& func, const tuple<T1>& rhs1, const T2& rhs2);

template <typename FUNC, typename T1, typename T2>
[[nodiscard]] bool apply_reduce_all(FUNC&& func, const tuple<T1>& rhs1, const tuple<T2>& rhs2);

}  // namespace legate

#include <legate/utilities/tuple.inl>
