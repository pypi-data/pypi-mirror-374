/*
 * SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights
 * reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legate/utilities/detail/doxygen.h>

#include <cstdint>
#include <exception>
#include <string>

/**
 * @file
 * @brief Class definition for legate::TaskException
 */

namespace legate {

/**
 * @addtogroup task
 * @{
 */

/**
 * @brief An exception class used in cross language exception handling
 *
 * Any client that needs to catch a C++ exception during task execution and have it rethrown
 * on the launcher side should wrap that C++ exception with a `TaskException`. In case the
 * task can raise more than one type of exception, they are distinguished by integer ids;
 * the launcher is responsible for enumerating a list of all exceptions that can be raised
 * and the integer ids are positions in that list.
 */
class TaskException : public std::exception {
 public:
  /**
   * @brief Constructs a `TaskException` object with an exception id and an error message.
   * The id must be a valid index for the list of exceptions declared by the launcher.
   *
   * @param index Exception id
   * @param error_message Error message
   */
  TaskException(std::int32_t index, std::string error_message);

  /**
   * @brief Constructs a `TaskException` object with an error message. The exception id
   * is set to 0.
   *
   * @param error_message Error message
   */
  explicit TaskException(std::string error_message);

  [[nodiscard]] const char* what() const noexcept override;

  /**
   * @brief Returns the exception id
   *
   * @return The exception id
   */
  [[nodiscard]] std::int32_t index() const noexcept;
  /**
   * @brief Returns the error message
   *
   * @return The error message
   */
  [[nodiscard]] const std::string& error_message() const noexcept;

 private:
  std::int32_t index_{-1};
  std::string error_message_{};
};

/** @} */

}  // namespace legate

#include <legate/task/exception.inl>
