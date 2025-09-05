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

// implementation sparsity maps

#ifndef REALM_DEPPART_SPARSITY_IMPL_H
#define REALM_DEPPART_SPARSITY_IMPL_H

#include "realm/indexspace.h"
#include "realm/sparsity.h"
#include "realm/id.h"

#include "realm/activemsg.h"
#include "realm/nodeset.h"
#include "realm/atomics.h"
#include <limits>
#include <functional>
#include <memory>

namespace Realm {

  class PartitioningMicroOp;

  /**
   * SparsityMapRefCounter is an internal object that proxies
   * referrence counting for sparsity maps including remote node
   * requests.
   * */
  class SparsityMapRefCounter {
  public:
    typedef ::realm_id_t id_t;
    id_t id;
    SparsityMapRefCounter(::realm_id_t id);

    [[nodiscard]] Event add_references(unsigned count);
    void remove_references(unsigned count, Event wait_on);

    struct SparsityMapAddReferenceMessage {
      id_t id;
      Event wait_on;
      unsigned count;

      static void handle_message(NodeID sender, const SparsityMapAddReferenceMessage &msg,
                                 const void *data, size_t datalen);
    };

    struct SparsityMapRemoveReferencesMessage {
      id_t id;
      Event wait_on;
      unsigned count;

      static void handle_message(NodeID sender,
                                 const SparsityMapRemoveReferencesMessage &msg,
                                 const void *data, size_t datalen);
    };

    static ActiveMessageHandlerReg<SparsityMapAddReferenceMessage>
        sparse_untyped_add_references_message_handler_reg;
    static ActiveMessageHandlerReg<SparsityMapRemoveReferencesMessage>
        sparse_untyped_remove_references_message_handler_reg;
  };

  template <int N, typename T>
  class SparsityMapCommunicator {
  public:
    virtual ~SparsityMapCommunicator() = default;

    virtual void send_request(SparsityMap<N, T> me, bool request_precise,
                              bool request_approx);

    virtual void send_contribute(SparsityMap<N, T> me, size_t piece_count,
                                 size_t total_count, bool disjoint,
                                 const void *data = nullptr, size_t datalen = 0);

    virtual void send_contribute(NodeID target, SparsityMap<N, T> me, size_t piece_count,
                                 size_t total_count, bool disjoint,
                                 const void *data = nullptr, size_t datalen = 0);

    virtual size_t recommend_max_payload(NodeID owner, bool with_congestion);
  };

  /**
   * SparsityMapImpl is the actual dynamically allocated object that exists on
   * each "interested" node for a given SparsityMap - it inherits from
   * SparsityMapPublicImpl and adds the "private" storage and functionality -
   * this separation is primarily to avoid the installed version of of Realm
   * having to include all the internal .h files.
   * TODO(apryakhin@): Consider doing an doxygen style.
   */
  template <int N, typename T>
  class SparsityMapImpl : public SparsityMapPublicImpl<N, T> {
  public:
    SparsityMapImpl(SparsityMap<N, T> _me, NodeSet &subscribers);

    SparsityMapImpl(SparsityMap<N, T> _me, NodeSet &subscribers,
                    SparsityMapCommunicator<N, T> *_sparsity_comm);

    // actual implementation - SparsityMapPublicImpl's version just calls this one
    Event make_valid(bool precise = true);

    static SparsityMapImpl<N, T> *lookup(SparsityMap<N, T> sparsity);

    // methods used in the population of a sparsity map

    // when we plan out a partitioning operation, we'll know how many
    //  different uops are going to contribute something (or nothing) to
    //  the sparsity map - once all of those contributions arrive, we can
    //  finalize the sparsity map
    void set_contributor_count(int count);
    void record_remote_contributor(NodeID contributor);

    void contribute_nothing(void);
    void contribute_dense_rect_list(const std::vector<Rect<N, T>> &rects, bool disjoint);
    void contribute_raw_rects(const Rect<N, T> *rects, size_t count, size_t piece_count,
                              bool disjoint, size_t total_count);

    // adds a microop as a waiter for valid sparsity map data - returns true
    //  if the uop is added to the list (i.e. will be getting a callback at some point),
    //  or false if the sparsity map became valid before this call (i.e. no callback)
    bool add_waiter(PartitioningMicroOp *uop, bool precise);

    void remote_data_request(NodeID requestor, bool send_precise, bool send_approx);
    void remote_data_reply(NodeID requestor, bool send_precise, bool send_approx);

    SparsityMap<N, T> me;

    struct RemoteSparsityRequest {
      SparsityMap<N, T> sparsity;
      bool send_precise;
      bool send_approx;

      static void handle_message(NodeID sender, const RemoteSparsityRequest &msg,
                                 const void *data, size_t datalen);
    };

    struct RemoteSparsityContrib {
      SparsityMap<N, T> sparsity;
      size_t piece_count; // non-zero only on last piece of contribution
      bool disjoint;      // if set, all rectangles (from this source and any other)
                          //   are known to be disjoint
      size_t total_count; // if non-zero, advertises the known total number of
                          //  recangles in the sparsity map

      static void handle_message(NodeID sender, const RemoteSparsityContrib &msg,
                                 const void *data, size_t datalen);
    };

    struct SetContribCountMessage {
      SparsityMap<N, T> sparsity;
      size_t count;

      static void handle_message(NodeID sender, const SetContribCountMessage &msg,
                                 const void *data, size_t datalen);
    };

  protected:
    void finalize(void);

    static ActiveMessageHandlerReg<RemoteSparsityRequest> remote_sparsity_request_reg;
    static ActiveMessageHandlerReg<RemoteSparsityContrib> remote_sparsity_contrib_reg;
    static ActiveMessageHandlerReg<SetContribCountMessage> set_contrib_count_msg_reg;

    atomic<int> remaining_contributor_count{0};
    atomic<int> total_piece_count{0}, remaining_piece_count{0};
    Mutex mutex;
    std::vector<PartitioningMicroOp *> approx_waiters, precise_waiters;
    bool precise_requested{0}, approx_requested{0};
    Event precise_ready_event = Event::NO_EVENT;
    Event approx_ready_event = Event::NO_EVENT;
    NodeSet remote_precise_waiters, remote_approx_waiters;
    NodeSet &remote_subscribers;
    size_t sizeof_precise{0};

    std::unique_ptr<SparsityMapCommunicator<N, T>> sparsity_comm;
  };

  class SparsityMapImplWrapper;
  class SparsityWrapperCommunicator {
  public:
    virtual ~SparsityWrapperCommunicator() = default;
    virtual void unsubscribe(SparsityMapImplWrapper *impl, NodeID sender, ID id);
  };

  // we need a type-erased wrapper to store in the runtime's lookup table
  class SparsityMapImplWrapper {
  public:
    static constexpr ID::ID_Types ID_TYPE = ID::ID_SPARSITY;

    SparsityMapImplWrapper(void);
    SparsityMapImplWrapper(SparsityWrapperCommunicator *_communicator,
                           bool _report_leaks);
    ~SparsityMapImplWrapper(void);

    void init(ID _me, unsigned _init_owner);
    void recycle(void);
    void unsubscribe(NodeID node);

    void add_references(unsigned count, Event wait_on = Event::NO_EVENT);
    void remove_references(unsigned count, Event wait_on);

    static ID make_id(const SparsityMapImplWrapper &dummy, int owner, ID::IDType index)
    {
      return ID::make_sparsity(owner, 0, index);
    }

    ID me{(ID::IDType)-1};
    unsigned owner{std::numeric_limits<unsigned>::max()};
    SparsityMapImplWrapper *next_free{nullptr};
    atomic<DynamicTemplates::TagType> type_tag{0};
    atomic<void *> map_impl{nullptr}; // actual implementation
    atomic<unsigned> references{0};
    NodeSet subscribers;
    std::unique_ptr<SparsityWrapperCommunicator> communicator;
    bool report_leaks{false};

    std::function<void(void *)> map_deleter;

    template <int N, typename T>
    SparsityMapImpl<N, T> *get_or_create(SparsityMap<N, T> me);

    struct UnsubscribeMessage {
      ::realm_id_t id;
      static void handle_message(NodeID sender, const UnsubscribeMessage &msg,
                                 const void *data, size_t datalen);
    };
    static ActiveMessageHandlerReg<UnsubscribeMessage> unsubscribe_message_handler_reg;
  };

}; // namespace Realm

#endif // REALM_DEPPART_SPARSITY_IMPL_H

#include "realm/deppart/sparsity_impl.inl"
