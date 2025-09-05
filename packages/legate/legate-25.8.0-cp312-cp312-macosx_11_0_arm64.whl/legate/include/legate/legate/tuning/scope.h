/*
 * SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights
 * reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legate/mapping/machine.h>
#include <legate/runtime/exception_mode.h>
#include <legate/tuning/parallel_policy.h>
#include <legate/utilities/detail/doxygen.h>
#include <legate/utilities/memory.h>

#include <cstdint>
#include <memory>
#include <string>
#include <string_view>

/**
 * @file
 * @brief Class definition for legate::Scope
 */

namespace legate {

/**
 * @addtogroup tuning
 * @{
 */

/**
 * @brief A helper class to configure task execution
 *
 * The Scope class offers APIs to configure runtime parameters for task execution. The parameters
 * set by a Scope object are effective only for the lifetime of the object. Currently, Scope can be
 * used to configure the following parameters:
 *
 * 1) Task priority: Each task is associated with a priority value. The higher the value, the
 * earlier among a set of ready-to-run tasks the task will get scheduled for execution. (the task
 * with a higher priority, however, does not preempt another with a lower priority that is already
 * running on the processor.) Task priorities are a signed 32-bit integer value. By default, all
 * tasks get assigned to 0 for the priorities.
 *
 * 2) Provenance: User programs or libraries often want to attach provenance information to each of
 * their operations and have it rendered in profiling outputs. Such information can be passed as a
 * string via a Scope object, which then will be attached to all operations issued within the
 * Scope's lifetime.
 *
 * 3) Machine: By default, Legate operations target the entire machine available for the program.
 * When a user program wants to assign a subset of the machine to its operations, it can subdivide
 * the machine using the machine API (see `Machine` for details) and set a sub-machine for the scope
 * using Scope. All operations within the lifetime of the Scope object can use only the sub-machine
 * for their execution.
 *
 * 4) Parallelization policies: Legate has default policies to parallelize tasks, which the user
 * program might want to override. In this case, the user program can set a new `ParallelPolicy`
 * object to the scope to install new parallelization policies (see `ParallelPolicy`).
 *
 * Each parameter can be set only once via each Scope object. Multiple attempts to set the same
 * parameter would raise an exception.
 */
class Scope {
 public:
  /**
   * @brief Constructs an empty Scope object
   */
  Scope();
  /**
   * @brief Constructs a Scope with a given task priority
   *
   * Equivalent to
   * @code{.cpp}
   * auto scope = Scope();
   * scope.set_priority(priority);
   * @endcode
   *
   * @param priority Task priority to set to the scope
   */
  explicit Scope(std::int32_t priority);
  /**
   * @brief Constructs a Scope with a given exception mode
   *
   * Equivalent to
   * @code{.cpp}
   * auto scope = Scope();
   * scope.set_exception_mode(exception_mode);
   * @endcode
   *
   * @param exception_mode Exception mode to set to the scope
   */
  explicit Scope(ExceptionMode exception_mode);
  /**
   * @brief Constructs a Scope with a given provenance string
   *
   * Equivalent to
   * @code{.cpp}
   * auto scope = Scope();
   * scope.set_provenance(provenance);
   * @endcode
   *
   * @param provenance Provenance string to set to the scope
   */
  explicit Scope(std::string provenance);
  /**
   * @brief Constructs a Scope with a given machine
   *
   * Equivalent to
   * @code{.cpp}
   * auto scope = Scope();
   * scope.set_machine(machine);
   * @endcode
   *
   * The given machine is intersected with the machine from the outer scope
   *
   * @param machine Machine to use within the scope
   *
   * @throw std::runtime_error If the intersected machine is empty
   *
   * @see set_machine
   */
  explicit Scope(const mapping::Machine& machine);
  /**
   * @brief Constructs a Scope with a given parallel policy.
   *
   * Equivalent to
   * @code{.cpp}
   * auto scope = Scope();
   * scope.set_parallel_policy(parallel_policy);
   * @endcode
   *
   * @param parallel_policy Parallel policy to use within the scope.
   *
   * @see set_parallel_policy
   */
  explicit Scope(ParallelPolicy parallel_policy);
  /**
   * @brief Sets a given task priority to the scope
   *
   * @param priority Task priority to set to the scope
   *
   * @throw std::invalid_argument If a task priority has already been set via this Scope object
   */
  Scope&& with_priority(std::int32_t priority) &&;
  /**
   * @brief Sets a given exception mode to the scope
   *
   * @param exception_mode Exception mode to set to the scope
   *
   * @throw std::invalid_argument If an exception mode has already been set via this Scope object
   */
  Scope&& with_exception_mode(ExceptionMode exception_mode) &&;
  /**
   * @brief Sets a given provenance string to the scope
   *
   * @param provenance Provenance string to set to the scope
   *
   * @throw std::invalid_argument If a provenance string has already been set via this Scope object
   */
  Scope&& with_provenance(std::string provenance) &&;
  /**
   * @brief Sets a given machine to the scope
   *
   * @param machine Machine to use within the scope
   *
   * The given machine is intersected with the machine from the outer scope
   *
   * @throw std::runtime_error If the intersected machine is empty
   * @throw std::invalid_argument If a machine has already been set via this Scope object
   *
   * @see set_machine
   */
  Scope&& with_machine(const mapping::Machine& machine) &&;
  /**
   * @brief Sets a given parallel policy to the scope.
   *
   * @param parallel_policy Parallel policy to set to the scope.
   *
   * @throw std::invalid_argument If a parallel policy has already been set via this Scope object.
   *
   * @return Scope.
   *
   * @see set_parallel_policy()
   */
  Scope&& with_parallel_policy(ParallelPolicy parallel_policy) &&;
  /**
   * @brief Sets a given task priority to the scope.
   *
   * @param priority Task priority to set to the scope.
   *
   * @throw std::invalid_argument If a task priority has already been set via this Scope object.
   */
  void set_priority(std::int32_t priority);
  /**
   * @brief Sets a given exception mode to the scope
   *
   * @param exception_mode Exception mode to set to the scope
   *
   * @throw std::invalid_argument If an exception mode has already been set via this Scope object
   */
  void set_exception_mode(ExceptionMode exception_mode);
  /**
   * @brief Sets a given provenance string to the scope
   *
   * @param provenance Provenance string to set to the scope
   *
   * @throw std::invalid_argument If a provenance string has already been set via this Scope object
   */
  void set_provenance(std::string provenance);
  /**
   * @brief Sets a given machine to the scope
   *
   * The given machine is intersected with the machine from the outer scope, so the actual machine
   * used in this scope will always be a subset of the outer scope's.
   *
   * For example, if the machine of the current scope has GPUs 2, 3, 4, and 5, and a new scope is
   * created with another machine with GPUs 3, 4, 5, and 6, then only the GPUs 3, 4, and 5 will be
   * set to the new scope.
   *
   * @param machine Machine to use within the scope
   *
   * @throw std::runtime_error If the intersected machine is empty
   * @throw std::invalid_argument If a machine has already been set via this Scope object
   */
  void set_machine(const mapping::Machine& machine);
  /**
   * @brief Sets a given parallel policy to the scope.
   *
   * If `parallel_policy` is streaming, the scheduling window size will be artificially
   * inflated to allow for better streaming for the duration of the scope.
   *
   * @param parallel_policy Parallel policy to set to the scope.
   *
   * @throw std::invalid_argument If a parallel policy has already been set via this Scope object.
   */
  void set_parallel_policy(ParallelPolicy parallel_policy);
  /**
   * @brief Returns the task priority of the current scope
   *
   * return Current task priority
   */
  [[nodiscard]] static std::int32_t priority();
  /**
   * @brief Returns the exception mode of the current scope
   *
   * @return Current exception mode
   */
  [[nodiscard]] static legate::ExceptionMode exception_mode();
  /**
   * @brief Returns the provenance string of the current scope
   *
   * @return Current provenance string
   */
  [[nodiscard]] static std::string_view provenance();
  /**
   * @brief Returns the machine of the current scope
   *
   * @return Current machine
   */
  [[nodiscard]] static mapping::Machine machine();
  /**
   * @brief Returns the parallel policy of the current scope.
   *
   * @return Current parallel policy.
   */
  [[nodiscard]] static const ParallelPolicy& parallel_policy();

  ~Scope();

  Scope(const Scope&)            = delete;
  Scope& operator=(const Scope&) = delete;
  Scope(Scope&&)                 = default;
  Scope& operator=(Scope&&)      = default;

  class Impl;

 private:
  std::unique_ptr<Impl, DefaultDelete<Impl>> impl_{};
};

extern template class DefaultDelete<Scope::Impl>;

/** @} */

}  // namespace legate
