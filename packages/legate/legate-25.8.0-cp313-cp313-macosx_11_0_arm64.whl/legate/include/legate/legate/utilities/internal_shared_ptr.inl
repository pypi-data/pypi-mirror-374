/*
 * SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights
 * reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legate/utilities/assert.h>
#include <legate/utilities/internal_shared_ptr.h>

#include <cstddef>
#include <memory>
#include <utility>

namespace legate {

template <typename T>
void InternalWeakPtr<T>::maybe_destroy_() noexcept
{
  if (ctrl_ && ctrl_->weak_ref_cnt() == 0) {
    // Do NOT delete, move, re-order, or otherwise modify the following lines under ANY
    // circumstances.
    //
    // They must stay exactly as they are. ctrl_->maybe_destroy_control_block() calls the moral
    // equivalent of "delete this", and hence any modification of ctrl_ hereafter is strictly
    // undefined behavior.
    //
    // We must null-out ctrl_ first (via std::exchange) since if this weak ptr is held by a
    // enable_shared_from_this, then maybe_destroy_control_block() could potentially also wipe
    // out *this.
    //
    // BEGIN DO NOT MODIFY
    std::exchange(ctrl_, nullptr)->maybe_destroy_control_block();
    // END DO NOT MODIFY
  }
}

template <typename T>
void InternalWeakPtr<T>::weak_reference_() noexcept
{
  if (ctrl_) {
    ctrl_->weak_ref();
  }
}

template <typename T>
void InternalWeakPtr<T>::weak_dereference_() noexcept
{
  if (ctrl_ && (ctrl_->weak_deref() == 0)) {
    maybe_destroy_();
  }
}

template <typename T>
constexpr InternalWeakPtr<T>::InternalWeakPtr(move_tag, control_block_type* ctrl_block_) noexcept
  : ctrl_{ctrl_block_}
{
}

template <typename T>
InternalWeakPtr<T>::InternalWeakPtr(copy_tag, control_block_type* ctrl_block_) noexcept
  : ctrl_{ctrl_block_}
{
  weak_reference_();
}

// ==========================================================================================

template <typename T>
InternalWeakPtr<T>::InternalWeakPtr(const InternalWeakPtr& other) noexcept
  : InternalWeakPtr{copy_tag{}, other.ctrl_}
{
}

template <typename T>
InternalWeakPtr<T>&
InternalWeakPtr<T>::operator=(  // NOLINT(bugprone-unhandled-self-assignment) yes it does
  const InternalWeakPtr& other) noexcept
{
  InternalWeakPtr{other}.swap(*this);
  return *this;
}

template <typename T>
InternalWeakPtr<T>::InternalWeakPtr(InternalWeakPtr&& other) noexcept
  : InternalWeakPtr{move_tag{}, std::exchange(other.ctrl_, nullptr)}
{
}

template <typename T>
InternalWeakPtr<T>& InternalWeakPtr<T>::operator=(InternalWeakPtr&& other) noexcept
{
  InternalWeakPtr{std::move(other)}.swap(*this);
  return *this;
}

template <typename T>
template <typename U, typename SFINAE>
InternalWeakPtr<T>::InternalWeakPtr(const InternalWeakPtr<U>& other) noexcept
  : InternalWeakPtr{copy_tag{}, other.ctrl_}
{
}

template <typename T>
template <typename U, typename SFINAE>
InternalWeakPtr<T>&
InternalWeakPtr<T>::operator=(  // NOLINT(bugprone-unhandled-self-assignment) yes it does
  const InternalWeakPtr<U>& other) noexcept
{
  InternalWeakPtr{other}.swap(*this);
  return *this;
}

template <typename T>
template <typename U, typename SFINAE>
InternalWeakPtr<T>::InternalWeakPtr(InternalWeakPtr<U>&& other) noexcept
  : InternalWeakPtr{move_tag{}, std::exchange(other.ctrl_, nullptr)}
{
}

template <typename T>
template <typename U, typename SFINAE>
InternalWeakPtr<T>& InternalWeakPtr<T>::operator=(InternalWeakPtr<U>&& other) noexcept
{
  InternalWeakPtr{std::move(other)}.swap(*this);
  return *this;
}

template <typename T>
template <typename U, typename SFINAE>
InternalWeakPtr<T>::InternalWeakPtr(const InternalSharedPtr<U>& other) noexcept
  : InternalWeakPtr{copy_tag{}, other.ctrl_}
{
}

template <typename T>
template <typename U, typename SFINAE>
InternalWeakPtr<T>& InternalWeakPtr<T>::operator=(const InternalSharedPtr<U>& other) noexcept
{
  InternalWeakPtr{other}.swap(*this);
  return *this;
}

template <typename T>
InternalWeakPtr<T>::~InternalWeakPtr() noexcept
{
  weak_dereference_();
}

// ==========================================================================================

template <typename T>
typename InternalWeakPtr<T>::ref_count_type InternalWeakPtr<T>::use_count() const noexcept
{
  return ctrl_ ? ctrl_->strong_ref_cnt() : 0;
}

template <typename T>
bool InternalWeakPtr<T>::expired() const noexcept
{
  return use_count() == 0;
}

// NOLINTBEGIN(bugprone-exception-escape)
template <typename T>
InternalSharedPtr<T> InternalWeakPtr<T>::lock() const noexcept
{
  // Normally the weak ptr ctor for InternalSharedPtr can throw (if the weak ptr is empty) but
  // in this case know it is not, and hence this function is noexcept
  return expired() ? InternalSharedPtr<T>{} : InternalSharedPtr<T>{*this};
}
// NOLINTEND(bugprone-exception-escape)

template <typename T>
void InternalWeakPtr<T>::swap(InternalWeakPtr& other) noexcept
{
  using std::swap;

  swap(other.ctrl_, ctrl_);
}

template <typename T>
void swap(InternalWeakPtr<T>& lhs, InternalWeakPtr<T>& rhs) noexcept
{
  lhs.swap(rhs);
}

// ==========================================================================================

template <typename T>
void InternalSharedPtr<T>::maybe_destroy_() noexcept
{
  if (use_count()) {
    return;
  }
  // If ptr_ is a SharedFromThis enabled class, then we want to temporarily act like we have an
  // extra strong ref. This is to head off the following:
  //
  // 1. We decrement strong refcount to 0 (i.e. we are here).
  // 2. Control block destroys the object (i.e. ptr_)...
  // 3. ... Which eventually calls the SharedFromThis dtor, which calls the weak ptr dtor...
  // 4. ... Which decrements the weak refcount to  0...
  // 5. ... And calls its own ctrl_->maybe_destroy_control_block()
  //
  // And since all 3 counts (strong, weak, and user) are 0, the control block self-destructs
  // out from underneath us! We could implement some complex logic which propagates a bool
  // "weak ptr don't destroy the control block" all the way down the stack somehow, or maybe
  // set a similar flag in the control block, or we can just do this.
  //
  // CAUTION:
  // If element_type is opaque at this point, it may constitute an ODR violation!
  if constexpr (detail::shared_from_this_enabled_v<element_type>) {
    ctrl_->strong_ref();
  }
  ctrl_->destroy_object();
  if constexpr (detail::shared_from_this_enabled_v<element_type>) {
    ctrl_->strong_deref();
  }
  if (LEGATE_DEFINED(LEGATE_USE_DEBUG) && (use_count() > 0)) {
    LEGATE_ABORT(
      "Use-count of shared pointer: ",
      static_cast<void*>(this),
      " has increased during its destructor, effectively reviving the dead object. "
      "This is usually due to a call to shared_from_this(), or stashing the object in "
      "some external cache inside its (or some related object's) destructor. This is not allowed.");
  }
  // Do NOT delete, move, re-order, or otherwise modify the following lines under ANY
  // circumstances.
  //
  // They must stay exactly as they are. ctrl_->maybe_destroy_control_block() calls the moral
  // equivalent of "delete this", and hence any modification of ctrl_ hereafter is strictly
  // undefined behavior.
  //
  // BEGIN DO NOT MODIFY
  ctrl_->maybe_destroy_control_block();
  ctrl_ = nullptr;
  ptr_  = nullptr;
  // END DO NOT MODIFY
}

template <typename T>
void InternalSharedPtr<T>::strong_reference_() noexcept
{
  if (ctrl_) {
    LEGATE_ASSERT(get());
    LEGATE_ASSERT(use_count());
    ctrl_->strong_ref();
  }
}

template <typename T>
void InternalSharedPtr<T>::strong_dereference_() noexcept
{
  if (ctrl_) {
    LEGATE_ASSERT(get());
    if (ctrl_->strong_deref() == 0) {
      maybe_destroy_();
    }
  }
}

template <typename T>
void InternalSharedPtr<T>::weak_reference_() noexcept
{
  if (ctrl_) {
    LEGATE_ASSERT(get());
    LEGATE_ASSERT(use_count());
    ctrl_->weak_ref();
  }
}

template <typename T>
void InternalSharedPtr<T>::weak_dereference_() noexcept
{
  if (ctrl_) {
    LEGATE_ASSERT(get());
    if (ctrl_->weak_deref() == 0) {
      maybe_destroy_();
    }
  }
}

// NOLINTBEGIN(readability-identifier-naming)
template <typename T>
void InternalSharedPtr<T>::user_reference_(SharedPtrAccessTag) noexcept
{
  if (ctrl_) {
    LEGATE_ASSERT(get());
    LEGATE_ASSERT(use_count());
    ctrl_->user_ref();
  }
}
// NOLINTEND(readability-identifier-naming)

// NOLINTBEGIN(readability-identifier-naming)
template <typename T>
void InternalSharedPtr<T>::user_dereference_(SharedPtrAccessTag) noexcept
{
  if (ctrl_) {
    LEGATE_ASSERT(get());
    if (ctrl_->user_deref() == 0) {
      // A user reference is also a strong reference, because a SharedPtr always holds an
      // InternalSharedPtr. Thus, there is no scenario in which a user reference is the last to
      // fall to 0, and we can therefore elide calling maybe_destroy_() here.
      //
      // We want to skip calling it because maybe_destroy_() is called from both weak_deref and
      // strong_deref, so it must call use_count() to check it is actually safe to destroy.
      LEGATE_ASSERT(use_count());
    }
  }
}
// NOLINTEND(readability-identifier-naming)

template <typename T>
template <typename U, typename V>
void InternalSharedPtr<T>::init_shared_from_this_(const EnableSharedFromThis<U>* weak, V* ptr)
{
  if (weak && weak->weak_this_.expired()) {
    using RawU = std::remove_cv_t<U>;

    weak->weak_this_ =
      InternalSharedPtr<RawU>{*this, const_cast<RawU*>(static_cast<const U*>(ptr))};
  }
}

template <typename T>
void InternalSharedPtr<T>::init_shared_from_this_(...)
{
}

// Every non-trivial constructor goes through this function!
template <typename T>
template <typename U>
InternalSharedPtr<T>::InternalSharedPtr(AllocatedControlBlockTag,
                                        control_block_type* ctrl_impl,
                                        U* ptr) noexcept
  : ctrl_{ctrl_impl}, ptr_{ptr}
{
  static_assert(!std::is_void_v<U>, "incomplete type");
  init_shared_from_this_(ptr, ptr);
}

template <typename T>
template <typename U, typename D, typename A>
InternalSharedPtr<T>::InternalSharedPtr(NoCatchAndDeleteTag, U* ptr, D&& deleter, A&& allocator)
  : InternalSharedPtr{AllocatedControlBlockTag{},
                      detail::construct_from_allocator_<
                        detail::SeparateControlBlock<U, std::decay_t<D>, std::decay_t<A>>>(
                        allocator, ptr, ptr, std::forward<D>(deleter), allocator),
                      ptr}
{
}

// ==========================================================================================

template <typename T>
constexpr InternalSharedPtr<T>::InternalSharedPtr(std::nullptr_t) noexcept
{
}

// clang-format off
template <typename T>
template <typename U, typename D, typename A, typename SFINAE>
InternalSharedPtr<T>::InternalSharedPtr(U* ptr, D deleter, A allocator)
  try : InternalSharedPtr{NoCatchAndDeleteTag{}, ptr, deleter, std::move(allocator)}
{
  // Cannot move the deleter, since we may need to use it
}
catch (...)
{
  deleter(ptr);
  throw;
}
// clang-format on

template <typename T>
InternalSharedPtr<T>::InternalSharedPtr(element_type* ptr)
  : InternalSharedPtr{ptr, detail::SharedPtrDefaultDelete<T, element_type>{}}
{
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>::InternalSharedPtr(U* ptr)
  : InternalSharedPtr{ptr, detail::SharedPtrDefaultDelete<T, U>{}}
{
  // NOLINTNEXTLINE(bugprone-sizeof-expression)
  static_assert(sizeof(U) > 0, "incomplete type");
}

template <typename T>
InternalSharedPtr<T>::InternalSharedPtr(const InternalSharedPtr& other) noexcept
  : InternalSharedPtr{AllocatedControlBlockTag{}, other.ctrl_, other.ptr_}
{
  strong_reference_();
}

template <typename T>
InternalSharedPtr<T>&
InternalSharedPtr<T>::operator=(  // NOLINT(bugprone-unhandled-self-assignment): yes it does
  const InternalSharedPtr& other) noexcept
{
  InternalSharedPtr{other}.swap(*this);
  return *this;
}

template <typename T>
InternalSharedPtr<T>::InternalSharedPtr(InternalSharedPtr&& other) noexcept
  : InternalSharedPtr{AllocatedControlBlockTag{},
                      std::exchange(other.ctrl_, nullptr),
                      std::exchange(other.ptr_, nullptr)}
{
  // we do not increment ref-counts here, the other pointer gives up ownership entirely (so
  // refcounts stay at previous levels)
}

template <typename T>
InternalSharedPtr<T>& InternalSharedPtr<T>::operator=(InternalSharedPtr&& other) noexcept
{
  InternalSharedPtr{std::move(other)}.swap(*this);
  return *this;
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>::InternalSharedPtr(const InternalSharedPtr<U>& other) noexcept
  : InternalSharedPtr{AllocatedControlBlockTag{}, other.ctrl_, other.ptr_}
{
  strong_reference_();
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>& InternalSharedPtr<T>::operator=(const InternalSharedPtr<U>& other) noexcept
{
  InternalSharedPtr{other}.swap(*this);
  return *this;
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>::InternalSharedPtr(InternalSharedPtr<U>&& other) noexcept
  : InternalSharedPtr{AllocatedControlBlockTag{},
                      std::exchange(other.ctrl_, nullptr),
                      std::exchange(other.ptr_, nullptr)}
{
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>& InternalSharedPtr<T>::operator=(InternalSharedPtr<U>&& other) noexcept
{
  InternalSharedPtr{std::move(other)}.swap(*this);
  return *this;
}

template <typename T>
template <typename U, typename D, typename SFINAE>
InternalSharedPtr<T>::InternalSharedPtr(std::unique_ptr<U, D>&& ptr)
  : InternalSharedPtr{NoCatchAndDeleteTag{}, ptr.get(), std::move(ptr.get_deleter())}
{
  // We don't want to catch a potentially thrown exception by the constructor above, since
  // normally this would result in a double-delete:
  //
  // 1. We call InternalSharedPtr<T>::InternalSharedPtr(U* ptr, D deleter, A allocator).
  // 2. An exception is thrown, in construct_from_allocator_() (or elsewhere).
  // 3. Ctor in (1.) catches, then calls deleter(ptr) (where deleter is the
  //    unique_ptr.get_deleter()) above, then re-raises.
  // 4. Exception propagates.
  // 5. unique_ptr eventually destructs, and calls get_deleter()(ptr) again.
  //
  // So we release only after we have fully constructed ourselves to preserve strong exception
  // guarantee. If the above constructor throws, this has no effect.
  static_cast<void>(ptr.release());
}

template <typename T>
template <typename U, typename D, typename SFINAE>
InternalSharedPtr<T>& InternalSharedPtr<T>::operator=(std::unique_ptr<U, D>&& ptr)
{
  InternalSharedPtr{std::move(ptr)}.swap(*this);
  return *this;
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>::InternalSharedPtr(const SharedPtr<U>& other) noexcept
  : InternalSharedPtr{other.internal_ptr({})}
{
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>& InternalSharedPtr<T>::operator=(const SharedPtr<U>& other) noexcept
{
  InternalSharedPtr{other}.swap(*this);
  return *this;
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>::InternalSharedPtr(SharedPtr<U>&& other) noexcept
  : InternalSharedPtr{std::move(other.internal_ptr({}))}
{
  // Normally, move-assigning from one shared ptr instance to another does not incur any
  // reference-count updating, however in this case we are "down-casting" from a user reference
  // to just an internal reference. So we must decrement the user count since other is empty
  // after this call.
  user_dereference_({});
}

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>& InternalSharedPtr<T>::operator=(SharedPtr<U>&& other) noexcept
{
  InternalSharedPtr{std::move(other)}.swap(*this);
  return *this;
}

namespace detail {

[[noreturn]] void throw_bad_internal_weak_ptr();

}  // namespace detail

template <typename T>
template <typename U, typename SFINAE>
InternalSharedPtr<T>::InternalSharedPtr(const InternalWeakPtr<U>& other)
  : InternalSharedPtr{AllocatedControlBlockTag{},
                      other.ctrl_,
                      other.ctrl_ ? static_cast<T*>(other.ctrl_->ptr()) : nullptr}
{
  if (!ctrl_) {
    detail::throw_bad_internal_weak_ptr();
  }
  strong_reference_();
}

template <typename T>
template <typename U>
InternalSharedPtr<T>::InternalSharedPtr(const InternalSharedPtr<U>& other,
                                        element_type* ptr) noexcept
  // Do not use the AllocatedControlBlockTag ctor, otherwise this will infinitely loop for
  // enable_shared_from_this classes!
  : ctrl_{other.ctrl_}, ptr_{ptr}
{
  strong_reference_();
}

template <typename T>
template <typename U>
InternalSharedPtr<T>::InternalSharedPtr(InternalSharedPtr<U>&& other, element_type* ptr) noexcept
  : InternalSharedPtr{AllocatedControlBlockTag{}, other.ctrl_, ptr}
{
  other.ctrl_ = nullptr;
  other.ptr_  = nullptr;
}

template <typename T>
InternalSharedPtr<T>::~InternalSharedPtr() noexcept
{
  strong_dereference_();
}

// ==========================================================================================

template <typename T>
void InternalSharedPtr<T>::swap(InternalSharedPtr& other) noexcept
{
  using std::swap;

  swap(other.ctrl_, ctrl_);
  swap(other.ptr_, ptr_);
}

template <typename T>
void swap(InternalSharedPtr<T>& lhs, InternalSharedPtr<T>& rhs) noexcept
{
  lhs.swap(rhs);
}

template <typename T>
void InternalSharedPtr<T>::reset() noexcept
{
  InternalSharedPtr{}.swap(*this);
}

template <typename T>
void InternalSharedPtr<T>::reset(std::nullptr_t) noexcept
{
  reset();
}

template <typename T>
template <typename U, typename D, typename A, typename SFINAE>
void InternalSharedPtr<T>::reset(U* ptr, D deleter, A allocator)
{
  InternalSharedPtr{ptr, std::move(deleter), std::move(allocator)}.swap(*this);
}

// ==========================================================================================

template <typename T>
constexpr typename InternalSharedPtr<T>::element_type& InternalSharedPtr<T>::operator[](
  std::ptrdiff_t idx) noexcept
{
  static_assert(std::is_array_v<T>);
  return get()[idx];
}

template <typename T>
constexpr const typename InternalSharedPtr<T>::element_type& InternalSharedPtr<T>::operator[](
  std::ptrdiff_t idx) const noexcept
{
  static_assert(std::is_array_v<T>);
  return get()[idx];
}

template <typename T>
constexpr typename InternalSharedPtr<T>::element_type* InternalSharedPtr<T>::get() const noexcept
{
  return ptr_;
}

template <typename T>
constexpr typename InternalSharedPtr<T>::element_type& InternalSharedPtr<T>::operator*()
  const noexcept
{
  return *get();
}

template <typename T>
constexpr typename InternalSharedPtr<T>::element_type* InternalSharedPtr<T>::operator->()
  const noexcept
{
  return get();
}

template <typename T>
typename InternalSharedPtr<T>::ref_count_type InternalSharedPtr<T>::use_count() const noexcept
{
  // SharedPtr's are a subset of InternalSharedPtr (since each one holds an InternalSharedPtr),
  // so the number of strong references gives the total unique references held to the pointer.
  return strong_ref_count();
}

template <typename T>
typename InternalSharedPtr<T>::ref_count_type InternalSharedPtr<T>::strong_ref_count()
  const noexcept
{
  return ctrl_ ? ctrl_->strong_ref_cnt() : 0;
}

template <typename T>
typename InternalSharedPtr<T>::ref_count_type InternalSharedPtr<T>::user_ref_count() const noexcept
{
  return ctrl_ ? ctrl_->user_ref_cnt() : 0;
}

template <typename T>
typename InternalSharedPtr<T>::ref_count_type InternalSharedPtr<T>::weak_ref_count() const noexcept
{
  return ctrl_ ? ctrl_->weak_ref_cnt() : 0;
}

template <typename T>
constexpr InternalSharedPtr<T>::operator bool() const noexcept
{
  return get() != nullptr;
}

template <typename T>
SharedPtr<T> InternalSharedPtr<T>::as_user_ptr() const noexcept
{
  return SharedPtr<T>{*this};
}

// ==========================================================================================

template <typename T, typename... Args>
InternalSharedPtr<T> make_internal_shared(Args&&... args)
{
  using RawT           = std::remove_cv_t<T>;
  using allocator_type = std::allocator<RawT>;

  auto alloc = allocator_type{};
  auto control_block =
    detail::construct_from_allocator_<detail::InplaceControlBlock<RawT, allocator_type>>(
      alloc, static_cast<RawT*>(nullptr), alloc, std::forward<Args>(args)...);
  return {typename InternalSharedPtr<T>::AllocatedControlBlockTag{},
          control_block,
          static_cast<RawT*>(control_block->ptr())};
}

// ==========================================================================================

template <typename T, typename U>
InternalSharedPtr<T> static_pointer_cast(const InternalSharedPtr<U>& ptr) noexcept
{
  return {ptr, static_cast<typename InternalSharedPtr<T>::element_type*>(ptr.get())};
}

template <typename T, typename U>
InternalSharedPtr<T> static_pointer_cast(InternalSharedPtr<U>&& ptr) noexcept
{
  return {std::move(ptr), static_cast<typename InternalSharedPtr<T>::element_type*>(ptr.get())};
}

template <typename T, typename U>
InternalSharedPtr<T> const_pointer_cast(const InternalSharedPtr<U>& ptr) noexcept
{
  return {ptr, const_cast<typename InternalSharedPtr<T>::element_type*>(ptr.get())};
}

template <typename T, typename U>
InternalSharedPtr<T> const_pointer_cast(InternalSharedPtr<U>&& ptr) noexcept
{
  return {std::move(ptr), const_cast<typename InternalSharedPtr<T>::element_type*>(ptr.get())};
}

// ==========================================================================================

template <typename T, typename U>
constexpr bool operator==(const InternalSharedPtr<T>& lhs, const InternalSharedPtr<U>& rhs) noexcept
{
  return lhs.get() == rhs.get();
}

template <typename T, typename U>
constexpr bool operator!=(const InternalSharedPtr<T>& lhs, const InternalSharedPtr<U>& rhs) noexcept
{
  return lhs.get() != rhs.get();
}

template <typename T, typename U>
constexpr bool operator<(const InternalSharedPtr<T>& lhs, const InternalSharedPtr<U>& rhs) noexcept
{
  return lhs.get() < rhs.get();
}

template <typename T, typename U>
constexpr bool operator>(const InternalSharedPtr<T>& lhs, const InternalSharedPtr<U>& rhs) noexcept
{
  return lhs.get() > rhs.get();
}

template <typename T, typename U>
constexpr bool operator<=(const InternalSharedPtr<T>& lhs, const InternalSharedPtr<U>& rhs) noexcept
{
  return lhs.get() <= rhs.get();
}

template <typename T, typename U>
constexpr bool operator>=(const InternalSharedPtr<T>& lhs, const InternalSharedPtr<U>& rhs) noexcept
{
  return lhs.get() >= rhs.get();
}

// ==========================================================================================

template <typename T>
constexpr bool operator==(const InternalSharedPtr<T>& lhs, std::nullptr_t) noexcept
{
  return lhs.get() == nullptr;
}

template <typename T>
constexpr bool operator==(std::nullptr_t, const InternalSharedPtr<T>& rhs) noexcept
{
  return nullptr == rhs.get();
}

template <typename T>
constexpr bool operator!=(const InternalSharedPtr<T>& lhs, std::nullptr_t) noexcept
{
  return lhs.get() != nullptr;
}

template <typename T>
constexpr bool operator!=(std::nullptr_t, const InternalSharedPtr<T>& rhs) noexcept
{
  return nullptr != rhs.get();
}

template <typename T>
constexpr bool operator<(const InternalSharedPtr<T>& lhs, std::nullptr_t) noexcept
{
  return lhs.get() < nullptr;
}

template <typename T>
constexpr bool operator<(std::nullptr_t, const InternalSharedPtr<T>& rhs) noexcept
{
  return nullptr < rhs.get();
}

template <typename T>
constexpr bool operator>(const InternalSharedPtr<T>& lhs, std::nullptr_t) noexcept
{
  return lhs.get() > nullptr;
}

template <typename T>
constexpr bool operator>(std::nullptr_t, const InternalSharedPtr<T>& rhs) noexcept
{
  return nullptr > rhs.get();
}

template <typename T>
constexpr bool operator<=(const InternalSharedPtr<T>& lhs, std::nullptr_t) noexcept
{
  return lhs.get() <= nullptr;
}

template <typename T>
constexpr bool operator<=(std::nullptr_t, const InternalSharedPtr<T>& rhs) noexcept
{
  return nullptr <= rhs.get();
}

template <typename T>
constexpr bool operator>=(const InternalSharedPtr<T>& lhs, std::nullptr_t) noexcept
{
  return lhs.get() >= nullptr;
}

template <typename T>
constexpr bool operator>=(std::nullptr_t, const InternalSharedPtr<T>& rhs) noexcept
{
  return nullptr >= rhs.get();
}

// ==========================================================================================

template <typename T>
constexpr EnableSharedFromThis<T>::EnableSharedFromThis(const EnableSharedFromThis&) noexcept
{
}

template <typename T>
constexpr EnableSharedFromThis<T>& EnableSharedFromThis<T>::operator=(
  const EnableSharedFromThis&) noexcept
{
  return *this;
}

// ==========================================================================================

template <typename T>
typename EnableSharedFromThis<T>::shared_type EnableSharedFromThis<T>::shared_from_this()
{
  return shared_type{weak_this_};
}

template <typename T>
typename EnableSharedFromThis<T>::const_shared_type EnableSharedFromThis<T>::shared_from_this()
  const
{
  return const_shared_type{weak_this_};
}

}  // namespace legate

namespace std {

template <typename T>
std::size_t hash<legate::InternalSharedPtr<T>>::operator()(
  const legate::InternalSharedPtr<T>& ptr) const noexcept
{
  return hash<const void*>{}(static_cast<const void*>(ptr.get()));
}

}  // namespace std
