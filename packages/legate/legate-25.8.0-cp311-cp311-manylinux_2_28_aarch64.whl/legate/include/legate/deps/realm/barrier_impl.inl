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

// Barrier implementations for Realm

// nop, but helps IDEs
#include "realm/barrier_impl.h"

// can't include runtime_impl.h because it's including us, but we need this declaration:
// include "realm/runtime_impl.h"
namespace Realm {
  extern BarrierImpl *get_barrier_impl(Event e);
};

namespace Realm {

  TYPE_IS_SERIALIZABLE(Realm::RemoteNotification);

  ////////////////////////////////////////////////////////////////////////
  //
  // class BarrierImpl

  inline Barrier
  BarrierImpl::current_barrier(Barrier::timestamp_t timestamp /*= 0*/) const
  {
    ID id(me);
    gen_t gen = this->generation.load() + 1;
    if(gen > id.barrier_generation().MAXVAL)
      return Barrier::NO_BARRIER;
    id.barrier_generation() = gen;
    Barrier b = id.convert<Barrier>();
    b.timestamp = timestamp;
    return b;
  }

  inline Barrier BarrierImpl::make_barrier(gen_t gen,
                                           Barrier::timestamp_t timestamp /*= 0*/) const
  {
    ID id(me);
    if(gen > id.barrier_generation().MAXVAL)
      return Barrier::NO_BARRIER;
    id.barrier_generation() = gen;
    Barrier b = id.convert<Barrier>();
    b.timestamp = timestamp;
    return b;
  }

  ////////////////////////////////////////////////////////////////////////
  //
  // struct BarrierTriggerPayload
  //

  template <typename S>
  bool serdez(S &ser, const BarrierTriggerPayload &notification)
  {
    bool success = false;
    success = (ser & notification.remotes) && (ser & notification.reduction);
    return success;
  }

  ////////////////////////////////////////////////////////////////////////
  //
  // struct BarrierTriggerMessageArgs
  //

  template <typename S>
  bool serdez(S &ser, const BarrierTriggerMessageArgs &args)
  {
    bool success = false;

    success = (ser & args.internal.trigger_gen) && (ser & args.internal.previous_gen) &&
              (ser & args.internal.first_generation) && (ser & args.internal.redop_id) &&
              (ser & args.internal.migration_target) &&
              (ser & args.internal.base_arrival_count) &&
              (ser & args.internal.broadcast_index);

    return success;
  }

}; // namespace Realm

