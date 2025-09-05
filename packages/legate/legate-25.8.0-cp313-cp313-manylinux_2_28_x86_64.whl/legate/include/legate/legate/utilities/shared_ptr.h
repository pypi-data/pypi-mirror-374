/*
 * SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights
 * reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legate/utilities/detail/type_traits.h>
#include <legate/utilities/internal_shared_ptr.h>

namespace legate {

template <typename T>
class SharedPtr;

template <typename T>
void swap(SharedPtr<T>&, SharedPtr<T>&) noexcept;

template <typename T>
class SharedPtr {
 public:
  using internal_ptr_type = InternalSharedPtr<T>;
  using element_type      = typename internal_ptr_type::element_type;
  using ref_count_type    = typename internal_ptr_type::ref_count_type;

  // Constructors
  constexpr SharedPtr() noexcept = default;

  // NOLINTNEXTLINE(google-explicit-constructor) to mimic std::shared_ptr ctor
  constexpr SharedPtr(std::nullptr_t) noexcept;

  template <typename U,
            typename Deleter,
            typename Alloc = std::allocator<U>,
            typename       = std::enable_if_t<detail::is_ptr_compat_v<U, element_type>>>
  SharedPtr(U* ptr,
            Deleter deleter,
            Alloc allocator = Alloc{});  // NOLINT(performance-unnecessary-value-param)
  template <typename U, typename = std::enable_if_t<detail::is_ptr_compat_v<U, element_type>>>
  explicit SharedPtr(U* ptr);

  SharedPtr(const SharedPtr&) noexcept;
  SharedPtr& operator=(const SharedPtr&) noexcept;
  SharedPtr(SharedPtr&&) noexcept;
  SharedPtr& operator=(SharedPtr&&) noexcept;

  template <typename U,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename SharedPtr<U>::element_type, element_type>>>
  SharedPtr(  // NOLINT(google-explicit-constructor) to mimic std::shared_ptr ctor
    const SharedPtr<U>&) noexcept;
  template <typename U,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename SharedPtr<U>::element_type, element_type>>>
  SharedPtr& operator=(const SharedPtr<U>&) noexcept;
  template <typename U,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename SharedPtr<U>::element_type, element_type>>>
  SharedPtr(  // NOLINT(google-explicit-constructor) to mimic std::shared_ptr ctor
    SharedPtr<U>&&) noexcept;
  template <typename U,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename SharedPtr<U>::element_type, element_type>>>
  SharedPtr& operator=(SharedPtr<U>&&) noexcept;

  explicit SharedPtr(const InternalSharedPtr<element_type>&) noexcept;
  SharedPtr& operator=(const InternalSharedPtr<element_type>&) noexcept;
  explicit SharedPtr(InternalSharedPtr<element_type>&&) noexcept;
  SharedPtr& operator=(InternalSharedPtr<element_type>&&) noexcept;

  template <typename U,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename InternalSharedPtr<U>::element_type, element_type>>>
  explicit SharedPtr(const InternalSharedPtr<U>&) noexcept;
  template <typename U,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename InternalSharedPtr<U>::element_type, element_type>>>
  SharedPtr& operator=(const InternalSharedPtr<U>&) noexcept;
  template <typename U,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename InternalSharedPtr<U>::element_type, element_type>>>
  explicit SharedPtr(InternalSharedPtr<U>&&) noexcept;
  template <typename U,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename InternalSharedPtr<U>::element_type, element_type>>>
  SharedPtr& operator=(InternalSharedPtr<U>&&) noexcept;

  template <typename U,
            typename D,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename std::unique_ptr<U, D>::element_type, element_type>>>
  SharedPtr(  // NOLINT(google-explicit-constructor) to mimic std::shared_ptr ctor
    std::unique_ptr<U, D>&&);
  template <typename U,
            typename D,
            typename = std::enable_if_t<
              detail::is_ptr_compat_v<typename std::unique_ptr<U, D>::element_type, element_type>>>
  SharedPtr& operator=(std::unique_ptr<U, D>&&);

  ~SharedPtr() noexcept;

  // Modifiers
  void swap(SharedPtr&) noexcept;
  // must namespace qualify to disambiguate from member function, otherwise clang balks
  friend void ::legate::swap<>(SharedPtr&, SharedPtr&) noexcept;
  void reset() noexcept;
  void reset(std::nullptr_t) noexcept;
  template <typename U,
            typename D = detail::SharedPtrDefaultDelete<T, U>,
            typename A = std::allocator<U>,
            typename   = std::enable_if_t<detail::is_ptr_compat_v<U, element_type>>>
  void reset(U* ptr,
             D deleter   = D{},
             A allocator = A{});  // NOLINT(performance-unnecessary-value-param)

  // Observers
  [[nodiscard]] constexpr element_type& operator[](std::ptrdiff_t idx) noexcept;
  [[nodiscard]] constexpr const element_type& operator[](std::ptrdiff_t idx) const noexcept;
  [[nodiscard]] constexpr element_type* get() const noexcept;
  [[nodiscard]] constexpr element_type& operator*() const noexcept;
  [[nodiscard]] constexpr element_type* operator->() const noexcept;

  [[nodiscard]] ref_count_type use_count() const noexcept;
  [[nodiscard]] ref_count_type user_ref_count() const noexcept;
  constexpr explicit operator bool() const noexcept;

  class InternalSharedPtrAccessTag {
    InternalSharedPtrAccessTag() = default;

    friend class SharedPtr<T>;
    template <typename U>
    friend class InternalSharedPtr;
  };

  [[nodiscard]] constexpr internal_ptr_type& internal_ptr(InternalSharedPtrAccessTag) noexcept;
  [[nodiscard]] constexpr const internal_ptr_type& internal_ptr(
    InternalSharedPtrAccessTag) const noexcept;

 private:
  struct copy_tag {};
  struct move_tag {};

  template <typename U>
  SharedPtr(copy_tag, const InternalSharedPtr<U>& other) noexcept;
  template <typename U>
  SharedPtr(move_tag, InternalSharedPtr<U>&& other, bool from_internal_ptr) noexcept;

  template <typename U>
  friend class SharedPtr;

  void reference_() noexcept;
  void dereference_() noexcept;

  internal_ptr_type ptr_{};
};

// ==========================================================================================

template <typename T, typename U>
constexpr bool operator==(const SharedPtr<T>& lhs, const SharedPtr<U>& rhs) noexcept;

template <typename T, typename U>
constexpr bool operator!=(const SharedPtr<T>& lhs, const SharedPtr<U>& rhs) noexcept;

template <typename T, typename U>
constexpr bool operator<(const SharedPtr<T>& lhs, const SharedPtr<U>& rhs) noexcept;

template <typename T, typename U>
constexpr bool operator>(const SharedPtr<T>& lhs, const SharedPtr<U>& rhs) noexcept;

template <typename T, typename U>
constexpr bool operator<=(const SharedPtr<T>& lhs, const SharedPtr<U>& rhs) noexcept;

template <typename T, typename U>
constexpr bool operator>=(const SharedPtr<T>& lhs, const SharedPtr<U>& rhs) noexcept;

// ==========================================================================================

template <typename T>
constexpr bool operator==(const SharedPtr<T>& lhs, std::nullptr_t) noexcept;

template <typename T>
constexpr bool operator==(std::nullptr_t, const SharedPtr<T>& rhs) noexcept;

template <typename T>
constexpr bool operator!=(const SharedPtr<T>& lhs, std::nullptr_t) noexcept;

template <typename T>
constexpr bool operator!=(std::nullptr_t, const SharedPtr<T>& rhs) noexcept;

template <typename T>
constexpr bool operator<(const SharedPtr<T>& lhs, std::nullptr_t) noexcept;

template <typename T>
constexpr bool operator<(std::nullptr_t, const SharedPtr<T>& rhs) noexcept;

template <typename T>
constexpr bool operator>(const SharedPtr<T>& lhs, std::nullptr_t) noexcept;

template <typename T>
constexpr bool operator>(std::nullptr_t, const SharedPtr<T>& rhs) noexcept;

template <typename T>
constexpr bool operator<=(const SharedPtr<T>& lhs, std::nullptr_t) noexcept;

template <typename T>
constexpr bool operator<=(std::nullptr_t, const SharedPtr<T>& rhs) noexcept;

template <typename T>
constexpr bool operator>=(const SharedPtr<T>& lhs, std::nullptr_t) noexcept;

template <typename T>
constexpr bool operator>=(std::nullptr_t, const SharedPtr<T>& rhs) noexcept;

}  // namespace legate

namespace std {

template <typename T>
struct hash<legate::SharedPtr<T>> {  // NOLINT(cert-dcl58-cpp) extending std::hash is OK
  [[nodiscard]] std::size_t operator()(const legate::SharedPtr<T>& ptr) const noexcept;
};

}  // namespace std

#include <legate/utilities/shared_ptr.inl>
