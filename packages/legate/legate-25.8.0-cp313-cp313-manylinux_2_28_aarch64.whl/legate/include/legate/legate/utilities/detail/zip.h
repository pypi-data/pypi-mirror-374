/*
 * SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights
 * reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legate/utilities/cpp_version.h>

#include <cstddef>
#include <iterator>
#include <tuple>
#include <type_traits>
#include <utility>

static_assert(
  LEGATE_CPP_MIN_VERSION < 23,  // NOLINT(readability-magic-numbers) std::zip since C++23
  "Can remove this module in favor of std::ranges::views::zip and/or std::ranges::zip_view");

/**
 * @file
 * @brief Definitions for zip iterator adaptor
 */

namespace legate::detail {

namespace zip_detail {

// A helper struct to generate the iterator types from a tuple of containers for use as ...T in
// ZiperatorBase. Furthermore, it also correctly infers the const-iterator versions, i.e. it
// takes
//
// std::tuple<Type_A, Type_B, ..., Type_N>
//
// and produces
//
// IteratorKind<Type_A::iterator, Type_B::iterator, ..., Type_N::iterator>
//
// If is_const is true, it produces
//
// IteratorKind<Type_A::const_iterator, Type_B::const_iterator, ..., Type_N::const_iterator>
//
// instead
template <template <typename...> class It,
          typename ObjTupleT,
          typename IndexSequence,
          bool is_const>
struct ZiperatorSelector;

// overload for normal iterators
template <template <typename...> class It, typename ObjTupleT, std::size_t... Idx>
struct ZiperatorSelector<It, ObjTupleT, std::index_sequence<Idx...>, false> {
  using type = It<decltype(std::begin(std::get<Idx>(std::declval<ObjTupleT&>())))...>;
};

// overload for const-iterators
template <template <typename...> class It, typename ObjTupleT, std::size_t... Idx>
struct ZiperatorSelector<It, ObjTupleT, std::index_sequence<Idx...>, true> {
  using type = It<decltype(std::cbegin(std::get<Idx>(std::declval<const ObjTupleT&>())))...>;
};

template <template <typename...> typename ZiperatorType, typename... T>
class Zipper;

// A Zip-Iterator, A.K.A. ziperator
template <typename Derived, typename... T>
class ZiperatorBase {
 protected:
  using derived_type    = Derived;
  using iter_tuple_type = std::tuple<T...>;
  using sequence        = std::index_sequence_for<T...>;

 private:
  explicit ZiperatorBase(T&&... its);

  friend Derived;

  template <template <typename...> typename ZiperatorType, typename... U>
  friend class Zipper;

 public:
  using iterator_category =
    std::common_type_t<typename std::iterator_traits<T>::iterator_category...>;
  using value_type      = std::tuple<decltype(*std::declval<T>())...>;
  using difference_type = std::common_type_t<typename std::iterator_traits<T>::difference_type...>;
  using pointer         = value_type*;
  using reference       = value_type&;
  using const_reference = const value_type&;

  [[nodiscard]] value_type operator*() const;

  derived_type& operator++();
  derived_type& operator--();

  [[nodiscard]] derived_type operator+(difference_type n) const;
  [[nodiscard]] derived_type operator-(difference_type n) const;
  [[nodiscard]] difference_type operator-(const ZiperatorBase& other) const;

  derived_type& operator+=(difference_type n);
  derived_type& operator-=(difference_type n);

  [[nodiscard]] bool operator<(const ZiperatorBase& other) const;
  [[nodiscard]] bool operator<=(const ZiperatorBase& other) const;
  [[nodiscard]] bool operator>(const ZiperatorBase& other) const;
  [[nodiscard]] bool operator>=(const ZiperatorBase& other) const;

  [[nodiscard]] bool operator==(const ZiperatorBase& other) const;
  [[nodiscard]] bool operator!=(const ZiperatorBase& other) const;

 protected:
  [[nodiscard]] derived_type& derived_() noexcept;
  [[nodiscard]] const derived_type& derived_() const noexcept;
  [[nodiscard]] std::tuple<T...>& iters_() noexcept;
  [[nodiscard]] const std::tuple<T...>& iters_() const noexcept;

  template <std::size_t... Idx>
  [[nodiscard]] value_type dereference_(std::index_sequence<Idx...>) const;

  template <std::size_t... Idx>
  void increment_(std::index_sequence<Idx...>);

  template <std::size_t... Idx>
  void pluseq_(std::index_sequence<Idx...>, difference_type n);

  template <std::size_t... Idx>
  void decrement_(std::index_sequence<Idx...>);

  template <std::size_t... Idx>
  void minuseq_(std::index_sequence<Idx...>, difference_type n);

  template <std::size_t... Idx>
  [[nodiscard]] bool lessthan_(std::index_sequence<Idx...>, const ZiperatorBase& other) const;

  template <std::size_t... Idx>
  [[nodiscard]] bool eq_(std::index_sequence<Idx...>, const ZiperatorBase& other) const;

 private:
  iter_tuple_type iter_tup_;
};

// zip-shortest zipper implementation
template <typename... T>
class ZiperatorShortest : public ZiperatorBase<ZiperatorShortest<T...>, T...> {
  using base_type = ZiperatorBase<ZiperatorShortest<T...>, T...>;
  friend base_type;

  template <std::size_t... Idx>
  [[nodiscard]] bool eq_(std::index_sequence<Idx...>, const ZiperatorShortest& other) const;

 public:
  using base_type::base_type;
};

// zip-equal zipper implementation
template <typename... T>
class ZiperatorEqual : public ZiperatorBase<ZiperatorEqual<T...>, T...> {
  using base_type = ZiperatorBase<ZiperatorEqual<T...>, T...>;
  friend base_type;

  template <std::size_t... Idx>
  [[nodiscard]] bool eq_(std::index_sequence<Idx...>, const ZiperatorEqual& other) const;

 public:
  using base_type::base_type;
};

// The "dispatcher" class for the zip operation. It must hold a tuple of references to the
// objects themselves, so that they don't go out of scope
template <template <typename...> typename ZiperatorType, typename... T>
class Zipper {
  std::tuple<T...> objs_;
  using sequence = std::index_sequence_for<T...>;

 public:
  using iterator =
    typename ZiperatorSelector<ZiperatorType, decltype(objs_), sequence, false>::type;
  using const_iterator =
    typename ZiperatorSelector<ZiperatorType, decltype(objs_), sequence, true>::type;
  using iterator_category = typename iterator::iterator_category;
  using value_type        = typename iterator::value_type;
  using difference_type   = typename iterator::difference_type;
  using pointer           = typename iterator::pointer;
  using reference         = typename iterator::reference;
  using const_reference   = typename const_iterator::reference;

  Zipper() = delete;
  Zipper(T&&... objs);  // NOLINT(google-explicit-constructor)

  [[nodiscard]] iterator begin();
  [[nodiscard]] const_iterator cbegin() const;
  [[nodiscard]] const_iterator begin() const;

  [[nodiscard]] iterator end();
  [[nodiscard]] const_iterator cend() const;
  [[nodiscard]] const_iterator end() const;

 private:
  template <std::size_t... Ns>
  [[nodiscard]] iterator begin_(std::index_sequence<Ns...>);

  template <std::size_t... Ns>
  [[nodiscard]] const_iterator begin_(std::index_sequence<Ns...>) const;

  template <std::size_t... Ns>
  [[nodiscard]] iterator end_(std::index_sequence<Ns...>);

  template <std::size_t... Ns>
  [[nodiscard]] const_iterator end_(std::index_sequence<Ns...>) const;
};

}  // namespace zip_detail

/**
 * @brief Zip a set of containers together.
 *
 * @param args The set of containers to zip.
 *
 * @return A zipper constructed from the set of containers. Calling `begin()` or `end()` on the
 * zipper returns the corresponding iterators.
 *
 * @details The adaptor returned by this routine implements a "zip shortest" zip
 * operation. That is, the returned zipper stops when at least one object or container has
 * reached the end. Iterating past that point results in undefined behavior.
 *
 * The iterators returned by the adaptor support the lowest common denominator of all
 * containers when it comes to iterator functionality. For example, if all containers'
 * iterators support `std::random_access_iterator_tag`, then the returned iterator will as
 * well.
 */
template <typename... T>
[[nodiscard]] zip_detail::Zipper<zip_detail::ZiperatorShortest, T...> zip_shortest(T&&... args);

/**
 * @brief Zip a set of containers of equal length together.
 *
 * @param args The set of containers to zip.
 *
 * @return A zipper constructed from the set of containers of equal size. Calling `begin()` or
 * `end()` on the zipper returns the corresponding iterators.
 *
 * @details The adaptor returned by this routine implements a "zip equal" zip operation. That
 * is, the returned zipper assumes all inputs are of equal size. Debug builds will attempt to
 * verify this invariant upfront, by calling (if applicable) std::size() on the
 * inputs. Iterating past the end results in undefined behavior.
 *
 * The iterators returned by the adaptor support the lowest common denominator of all
 * containers when it comes to iterator functionality. For example, if all containers'
 * iterators support `std::random_access_iterator_tag`, then the returned iterator will as
 * well.
 *
 * @snippet noinit/zip_equal.cc Constructing a zipper
 */
template <typename... T>
[[nodiscard]] zip_detail::Zipper<zip_detail::ZiperatorEqual, T...> zip_equal(T&&... args);

}  // namespace legate::detail

#include <legate/utilities/detail/zip.inl>
