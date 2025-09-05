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

// Runtime implementation for Realm

#ifndef REALM_RUNTIME_IMPL_H
#define REALM_RUNTIME_IMPL_H

#include "realm/runtime.h"
#include "realm/id.h"

#include "realm/network.h"
#include "realm/operation.h"
#include "realm/profiling.h"

#include "realm/dynamic_table.h"
#include "realm/codedesc.h"
#include "realm/deppart/partitions.h"

// event and reservation impls are included directly in the node's dynamic tables,
//  so we need their definitions here (not just declarations)
#include "realm/comp_queue_impl.h"
#include "realm/event_impl.h"
#include "realm/barrier_impl.h"
#include "realm/rsrv_impl.h"
#include "realm/subgraph_impl.h"

#include "realm/machine_impl.h"

#include "realm/threads.h"
#include "realm/sampling.h"

#include "realm/module.h"
#include "realm/network.h"

#include "realm/bgwork.h"
#include "realm/activemsg.h"
#include "realm/repl_heap.h"
#include "realm/dynamic_table.h"

#include "realm/shm.h"
#include "realm/hardware_topology.h"

#include <unordered_map>

namespace Realm {

  class ProcessorGroupImpl;
  class MemoryImpl;
  class IBMemory;
  class ProcessorImpl;
  class RegionInstanceImpl;
  class NetworkSegment;

  class Channel; // from transfer/channel.h

  // use a wide tree for local events - max depth will be 2
  // use a narrow tree for remote events - depth is 3, leaves have 128 events
  typedef DynamicTableAllocator<GenEventImpl, 11, 16> LocalEventTableAllocator;
  typedef DynamicTableAllocator<GenEventImpl, 10, 7> RemoteEventTableAllocator;
  typedef DynamicTableAllocator<BarrierImpl, 10, 4> BarrierTableAllocator;
  typedef DynamicTableAllocator<ReservationImpl, 10, 8> ReservationTableAllocator;
  typedef DynamicTableAllocator<ProcessorGroupImpl, 10, 4> ProcessorGroupTableAllocator;
  typedef DynamicTableAllocator<SparsityMapImplWrapper, 10, 4> SparsityMapTableAllocator;
  typedef DynamicTableAllocator<CompQueueImpl, 10, 4> CompQueueTableAllocator;
  typedef DynamicTableAllocator<SubgraphImpl, 10, 4> SubgraphTableAllocator;

  // for each of the ID-based runtime objects, we're going to have an
  //  implementation class and a table to look them up in
  struct Node {
    Node(void);
    ~Node(void);

    Node(const Node &) = delete;
    Node &operator=(const Node &) = delete;
    Node(Node &&) noexcept = delete;
    Node &operator=(Node &&) noexcept = delete;

    // not currently resizable
    std::vector<MemoryImpl *> memories;
    std::vector<IBMemory *> ib_memories;
    std::vector<ProcessorImpl *> processors;
    std::vector<Channel *> dma_channels;

    DynamicTable<RemoteEventTableAllocator> remote_events;
    DynamicTable<BarrierTableAllocator> barriers;
    DynamicTable<ReservationTableAllocator> reservations;
    DynamicTable<CompQueueTableAllocator> compqueues;

    // sparsity maps can be created by other nodes, so keep a
    //  map per-creator_node
    std::vector<atomic<DynamicTable<SparsityMapTableAllocator> *>> sparsity_maps;
    std::vector<atomic<DynamicTable<SubgraphTableAllocator> *>> subgraphs;
    std::vector<atomic<DynamicTable<ProcessorGroupTableAllocator> *>> proc_groups;
  };

  std::ostream &operator<<(std::ostream &os, const Node &node);

  // the "core" module provides the basic memories and processors used by Realm
  class CoreModuleConfig : public ModuleConfig {
    friend class CoreModule;
    friend class RuntimeImpl;

  protected:
    CoreModuleConfig(const HardwareTopology *topo);

    bool discover_resource(void);

  public:
    virtual void configure_from_cmdline(std::vector<std::string> &cmdline);

  protected:
    // configurations
    // CoreModule
    int num_cpu_procs = 1, num_util_procs = 1, num_io_procs = 0;
    int concurrent_io_threads = 1; // Legion does not support values > 1 right now
    size_t sysmem_size = 512 << 20;
    size_t sysmem_ipc_limit = 0; // make the sysmem as shared only if share_sysmem_limit
                                 // == 0 or sysmem_size <= share_sysmem_limit
    size_t stack_size = 2 << 20;
    bool pin_util_procs = false;
    long long cpu_bgwork_timeslice = 0, util_bgwork_timeslice = 0;
    bool use_ext_sysmem = true;

    // RuntimeImpl
    size_t reg_ib_mem_size = 0;
    size_t reg_mem_size = 0;
    size_t disk_mem_size = 0;
    unsigned dma_worker_threads = 0; // unused - warning on application use
#ifdef EVENT_TRACING
      size_t event_trace_block_size = 1 << 20;
      double event_trace_exp_arrv_rate = 1e3;
#endif
#ifdef LOCK_TRACING
      size_t lock_trace_block_size = 1 << 20;
      double lock_trace_exp_arrv_rate = 1e2;
#endif
      // should local proc threads get dedicated cores?
      bool dummy_reservation_ok = true;
      bool show_reservations = false;
      // are hyperthreads considered to share a physical core
      bool hyperthread_sharing = true;
      bool pin_dma_threads = false; // unused - silently ignored on cmdline
      size_t bitset_chunk_size = 32 << 10; // 32KB
      // based on some empirical measurements, 1024 nodes seems like
      //  a reasonable cutoff for switching to twolevel nodeset bitmasks
      //  (measured on an E5-2698 v4)
      int bitset_twolevel = -1024; // i.e. yes if > 1024 nodes
      int active_msg_handler_threads = 0; // default is none (use bgwork)
      bool active_msg_handler_bgwork = true;
      size_t replheap_size = 16 << 20;
      std::string event_trace_file;
      std::string lock_trace_file;
#ifdef NODE_LOGGING
      std::string prefix = ".";
#endif

      // resources
      int res_num_cpus = 0;
      size_t res_sysmem_size = 0;

      // sparstiy maps
      bool report_sparsity_leaks = false;

      // barriers
      int barrier_broadcast_radix = 4;

      // topology of the host
      const HardwareTopology *host_topology = nullptr;
  };

    class CoreModule : public Module {
    public:
      CoreModule(void);
      virtual ~CoreModule(void);

      static ModuleConfig *create_module_config(RuntimeImpl *runtime);

      static Module *create_module(RuntimeImpl *runtime);

      // create any memories provided by this module (default == do nothing)
      //  (each new MemoryImpl should use a Memory from RuntimeImpl::next_local_memory_id)
      virtual void create_memories(RuntimeImpl *runtime);

      // create any processors provided by the module (default == do nothing)
      //  (each new ProcessorImpl should use a Processor from
      //   RuntimeImpl::next_local_processor_id)
      virtual void create_processors(RuntimeImpl *runtime);

      // create any DMA channels provided by the module (default == do nothing)
      virtual void create_dma_channels(RuntimeImpl *runtime);

      // create any code translators provided by the module (default == do nothing)
      virtual void create_code_translators(RuntimeImpl *runtime);

      // clean up any common resources created by the module - this will be called
      //  after all memories/processors/etc. have been shut down and destroyed
      virtual void cleanup(void);

    public:
      MemoryImpl *ext_sysmem;

    protected:
      CoreModuleConfig *config;
    };

    template <typename K, typename V, typename LT = Mutex>
    class LockedMap {
    public:
      bool exists(const K& key) const
      {
	AutoLock<LT> al(mutex);
	typename std::map<K, V>::const_iterator it = map.find(key);
	return (it != map.end());
      }

      bool put(const K& key, const V& value, bool replace = false)
      {
	AutoLock<LT> al(mutex);
	typename std::map<K, V>::iterator it = map.find(key);
	if(it != map.end()) {
	  if(replace) it->second = value;
	  return true;
	} else {
	  map.insert(std::make_pair(key, value));
	  return false;
	}
      }

      V get(const K& key, const V& defval) const
      {
	AutoLock<LT> al(mutex);
	typename std::map<K, V>::const_iterator it = map.find(key);
	if(it != map.end())
	  return it->second;
	else
	  return defval;
      }

    //protected:
      mutable LT mutex;
      std::map<K, V> map;
    };

    class RuntimeImpl {
    public:
      RuntimeImpl(void);
      ~RuntimeImpl(void);

      bool network_init(int *argc, char ***argv);

      void parse_command_line(std::vector<std::string> &cmdline);

      void finish_configure(void);

      bool configure_from_command_line(std::vector<std::string> &cmdline);

      void start(void);

      bool register_task(Processor::TaskFuncID taskid, Processor::TaskFuncPtr taskptr);
      bool register_reduction(ReductionOpID redop_id, const ReductionOpUntyped *redop);
      bool register_custom_serdez(CustomSerdezID serdez_id, const CustomSerdezUntyped *serdez);

      Event collective_spawn(Processor target_proc, Processor::TaskFuncID task_id, 
			     const void *args, size_t arglen,
			     Event wait_on = Event::NO_EVENT, int priority = 0);

      Event collective_spawn_by_kind(Processor::Kind target_kind, Processor::TaskFuncID task_id, 
				     const void *args, size_t arglen,
				     bool one_per_node = false,
				     Event wait_on = Event::NO_EVENT, int priority = 0);

      void run(Processor::TaskFuncID task_id = 0, 
	       Runtime::RunStyle style = Runtime::ONE_TASK_ONLY,
	       const void *args = 0, size_t arglen = 0, bool background = false);

      // requests a shutdown of the runtime - returns true if request is a duplicate
      bool request_shutdown(Event wait_on, int result_code);

      // indicates shutdown has been initiated, wakes up a waiter if already present
      void initiate_shutdown(void);

      // shutdown the runtime
      void shutdown(Event wait_on = Event::NO_EVENT, int result_code = 0);

      // returns value of result_code passed to shutdown()
      int wait_for_shutdown(void);

      bool create_configs(int argc, char **argv);

      // return the configuration of a specific module
      ModuleConfig *get_module_config(const std::string &name) const;

      // three event-related impl calls - get_event_impl() will give you either
      //  a normal event or a barrier, but you won't be able to do specific things
      //  (e.g. trigger a GenEventImpl or adjust a BarrierImpl)
      EventImpl *get_event_impl(Event e);
      GenEventImpl *get_genevent_impl(Event e);
      BarrierImpl *get_barrier_impl(Event e);

      ReservationImpl *get_lock_impl(ID id);
      MemoryImpl *get_memory_impl(ID id) const;
      IBMemory *get_ib_memory_impl(ID id) const;
      ProcessorImpl *get_processor_impl(ID id); // TODO: refactor it to const version
      ProcessorGroupImpl *get_procgroup_impl(ID id);
      RegionInstanceImpl *get_instance_impl(ID id);
      SparsityMapImplWrapper *get_sparsity_impl(ID id);
      SparsityMapImplWrapper *get_available_sparsity_impl(NodeID target_node);
      void free_sparsity_impl(SparsityMapImplWrapper *impl);
      CompQueueImpl *get_compqueue_impl(ID id);
      SubgraphImpl *get_subgraph_impl(ID id);

#ifdef DEADLOCK_TRACE
      void add_thread(const pthread_t *thread);
#endif
      static void realm_backtrace(int signal);

    public:
      MachineImpl *machine;

      LockedMap<ReductionOpID, ReductionOpUntyped *> reduce_op_table;
      LockedMap<CustomSerdezID, CustomSerdezUntyped *> custom_serdez_table;

      atomic<size_t> num_untriggered_events;
      Node *nodes; // TODO: replace with std::vector<Node>
      size_t num_nodes;
      DynamicTable<LocalEventTableAllocator> local_events;
      LocalEventTableAllocator::FreeList *local_event_free_list;
      BarrierTableAllocator::FreeList *local_barrier_free_list;
      ReservationTableAllocator::FreeList *local_reservation_free_list;
      CompQueueTableAllocator::FreeList *local_compqueue_free_list;

      // keep a free list for each node we allocate maps on (i.e. indexed
      //   by owner_node)
      std::vector<SparsityMapTableAllocator::FreeList *> local_sparsity_map_free_lists;
      std::vector<SubgraphTableAllocator::FreeList *> local_subgraph_free_lists;
      std::vector<ProcessorGroupTableAllocator::FreeList *> local_proc_group_free_lists;

      // legacy behavior if Runtime::run() is used
      bool run_method_called;
#ifdef DEADLOCK_TRACE
      unsigned next_thread;
      unsigned signaled_threads;
      pthread_t all_threads[MAX_NUM_THREADS];
      unsigned thread_counts[MAX_NUM_THREADS];
#endif
      Mutex shutdown_mutex;
      Mutex::CondVar shutdown_condvar;
      bool shutdown_request_received;  // has a request for shutdown arrived
      Event shutdown_precondition;
      int shutdown_result_code;
      bool shutdown_initiated;  // is it time to start shutting down
      atomic<bool> shutdown_in_progress; // are we actively shutting down?
      std::unordered_map<realm_id_t, SharedMemoryInfo> remote_shared_memory_mappings;
      std::unordered_map<realm_id_t, SharedMemoryInfo> local_shared_memory_mappings;

      HardwareTopology host_topology;
      bool topology_init = false; // TODO: REMOVE it
      CoreReservationSet *core_reservations;
      BackgroundWorkManager bgwork;
      IncomingMessageManager *message_manager;
      EventTriggerNotifier event_triggerer;

      OperationTable optable;

      SamplingProfiler sampling_profiler;

      ReplicatedHeap repl_heap; // used for sparsity maps, instance layouts

      bool shared_peers_use_network_module = true;

      class DeferredShutdown : public EventWaiter {
      public:
	void defer(RuntimeImpl *_runtime, Event wait_on);

	virtual void event_triggered(bool poisoned, TimeLimit work_until);
	virtual void print(std::ostream& os) const;
	virtual Event get_finish_event(void) const;

      protected:
	RuntimeImpl *runtime;
      };
      DeferredShutdown deferred_shutdown;
      
    public:
      // used by modules to add processors, memories, etc.
      void add_memory(MemoryImpl *m);
      void add_ib_memory(IBMemory *m);
      void add_processor(ProcessorImpl *p);
      void add_dma_channel(Channel *c);
      void add_code_translator(CodeTranslator *t);

      void add_proc_mem_affinity(const Machine::ProcessorMemoryAffinity& pma);
      void add_mem_mem_affinity(const Machine::MemoryMemoryAffinity& mma);

      Memory next_local_memory_id(void);
      Memory next_local_ib_memory_id(void);
      Processor next_local_processor_id(void);
      CoreReservationSet& core_reservation_set(void);

      const std::vector<CodeTranslator *>& get_code_translators(void) const;

      template <typename T>
      T *get_module(const char *name) const
      {
        Module *mod = get_module_untyped(name);
        if(mod)
          return checked_cast<T *>(mod);
        else
          return 0;
      }

    protected:
      friend class Runtime;

      Module *get_module_untyped(const char *name) const;

      /// @brief Auxilary function to create Network::shared_peers using either ipc
      /// mailbox or relying on network modules
      void create_shared_peers(void);

      /// @brief Auxilary function for handling the sharing mechanism of all registered
      /// memories across the machine
      /// @note requires a coordination of Network::barriers, so may be fatal if this call
      /// fails
      /// @return True if successful, false otherwise
      bool share_memories(void);

      ID::IDType num_local_memories, num_local_ib_memories, num_local_processors;
      NetworkSegment reg_ib_mem_segment;
      NetworkSegment reg_mem_segment;

      ModuleRegistrar module_registrar;
      bool modules_created;
      bool module_configs_created;
      std::vector<Module *> modules;
      std::vector<CodeTranslator *> code_translators;

      std::vector<NetworkModule *> network_modules;
      std::vector<NetworkSegment *> network_segments;

      std::map<std::string, ModuleConfig*> module_configs;
    };

    extern RuntimeImpl *runtime_singleton;
    inline RuntimeImpl *get_runtime(void) { return runtime_singleton; }

    // due to circular dependencies in include files, we need versions of these that
    //  hide the RuntimeImpl intermediate
    inline EventImpl *get_event_impl(Event e) { return get_runtime()->get_event_impl(e); }
    inline GenEventImpl *get_genevent_impl(Event e) { return get_runtime()->get_genevent_impl(e); }
    inline BarrierImpl *get_barrier_impl(Event e) { return get_runtime()->get_barrier_impl(e); }

    // active messages

    struct RuntimeShutdownRequest {
      Event wait_on;
      int result_code;

      static void handle_message(NodeID sender,const RuntimeShutdownRequest &msg,
				 const void *data, size_t datalen);
    };
      
    struct RuntimeShutdownMessage {
      int result_code;

      static void handle_message(NodeID sender,const RuntimeShutdownMessage &msg,
				 const void *data, size_t datalen);
    };
      
}; // namespace Realm

#endif // ifndef REALM_RUNTIME_IMPL_H
