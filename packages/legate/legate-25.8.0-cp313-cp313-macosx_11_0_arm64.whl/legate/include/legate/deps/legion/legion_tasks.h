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


#ifndef __LEGION_TASKS_H__
#define __LEGION_TASKS_H__

#include "legion.h"
#include "legion/runtime.h"
#include "legion/legion_ops.h"
#include "legion/region_tree.h"
#include "legion/legion_mapping.h"
#include "legion/legion_utilities.h"
#include "legion/legion_allocation.h"

namespace Legion {
  namespace Internal {

    /**
     * \class ExternalTask
     * An extention of the external-facing Task to help
     * with packing and unpacking them
     */
    class ExternalTask : public Task, public ExternalMappable {
    public:
      ExternalTask(void);
    public:
      void pack_external_task(Serializer &rez, AddressSpaceID target) const;
      void unpack_external_task(Deserializer &derez, Runtime *runtime);
    public:
      static void pack_output_requirement(
          const OutputRequirement &req, Serializer &rez);
    public:
      static void unpack_output_requirement(
          OutputRequirement &req, Deserializer &derez);
    public:
      virtual void set_context_index(uint64_t index) = 0;
    protected:
      AllocManager *arg_manager;
    };

    /**
     * \class TaskRegions
     * This is a helper class for accessing the region requirements of a task
     */
    class TaskRequirements {
    public:
      TaskRequirements(Task &t) : task(t) { }
    public:
      inline size_t size(void) const 
        { return task.regions.size() + task.output_regions.size(); }
      inline bool is_output_created(unsigned idx) const
        { if (idx < task.regions.size()) return false;
          return (task.output_regions[idx-task.regions.size()].flags &
                        LEGION_CREATED_OUTPUT_REQUIREMENT_FLAG); }
      inline RegionRequirement& operator[](unsigned idx)
        { return (idx < task.regions.size()) ? task.regions[idx] :
                        task.output_regions[idx - task.regions.size()]; }
      inline const RegionRequirement& operator[](unsigned idx) const
        { return (idx < task.regions.size()) ? task.regions[idx] : 
                        task.output_regions[idx - task.regions.size()]; }
    private:
      Task &task;
    };

    /**
     * \class TaskOp
     * This is the base task operation class for all
     * kinds of tasks in the system.
     */
    class TaskOp : public ExternalTask, public PredicatedOp {
    public:
      enum TaskKind {
        INDIVIDUAL_TASK_KIND,
        POINT_TASK_KIND,
        INDEX_TASK_KIND,
        SLICE_TASK_KIND,
        SHARD_TASK_KIND,
      };
      class OutputOptions {
      public:
        OutputOptions(void) : store(0) { }
        OutputOptions(bool global, bool valid, bool grouped)
          : store((global ? 1 : 0) | (valid ? 2 : 0) | (grouped ? 4 : 0)) { }
      public:
        inline bool global_indexing(void) const { return (store & 1); }
        inline bool valid_requirement(void) const { return (store & 2); }
        inline bool grouped_fields(void) const { return (store & 4); }
      private:
        uint8_t store;
      };
    public:
      struct TriggerTaskArgs : public LgTaskArgs<TriggerTaskArgs> {
      public:
        static const LgTaskID TASK_ID = LG_TRIGGER_TASK_ID;
      public:
        TriggerTaskArgs(TaskOp *t)
          : LgTaskArgs<TriggerTaskArgs>(t->get_unique_op_id()), op(t) { }
      public:
        TaskOp *const op;
      };
      struct DeferMappingArgs : public LgTaskArgs<DeferMappingArgs> {
      public:
        static const LgTaskID TASK_ID = LG_DEFER_PERFORM_MAPPING_TASK_ID;
      public:
        DeferMappingArgs(TaskOp *op, MustEpochOp *owner, unsigned cnt,
                         std::vector<unsigned> *performed,
                         std::vector<ApEvent> *eff)
          : LgTaskArgs<DeferMappingArgs>(op->get_unique_op_id()),
            proxy_this(op), must_op(owner), invocation_count(cnt),
            performed_regions(performed), effects(eff) { }
      public:
        TaskOp *const proxy_this;
        MustEpochOp *const must_op;
        const unsigned invocation_count;
        std::vector<unsigned> *const performed_regions;
        std::vector<ApEvent> *const effects;
      };
    struct FinalizeOutputEqKDTreeArgs : 
      public LgTaskArgs<FinalizeOutputEqKDTreeArgs> {
    public:
      static const LgTaskID TASK_ID = LG_FINALIZE_OUTPUT_TREE_TASK_ID;
    public:
      FinalizeOutputEqKDTreeArgs(TaskOp *owner)
        : LgTaskArgs<FinalizeOutputEqKDTreeArgs>(owner->get_unique_op_id()),
          proxy_this(owner) { }
    public:
      TaskOp *const proxy_this;
    };
    struct DeferTriggerChildrenCommitArgs :
        public LgTaskArgs<DeferTriggerChildrenCommitArgs> {
      public:
        static const LgTaskID TASK_ID =LG_DEFER_TRIGGER_CHILDREN_COMMIT_TASK_ID;
      public:
        DeferTriggerChildrenCommitArgs(TaskOp *t)
          : LgTaskArgs<DeferTriggerChildrenCommitArgs>(t->get_unique_op_id()),
            task(t) { }
      public:
        TaskOp *const task;
      };
    public:
      TaskOp(Runtime *rt);
      virtual ~TaskOp(void);
    public:
      virtual UniqueID get_unique_id(void) const;
      virtual uint64_t get_context_index(void) const;
      virtual void set_context_index(uint64_t index);
      virtual bool has_parent_task(void) const;
      virtual const Task* get_parent_task(void) const;
      virtual const std::string_view& get_provenance_string(
          bool human = true) const;
      virtual const char* get_task_name(void) const;
      virtual bool is_reducing_future(void) const;
      virtual void pack_remote_operation(Serializer &rez, AddressSpaceID target,
                                         std::set<RtEvent> &applied) const;
      virtual void pack_profiling_requests(Serializer &rez,
                                           std::set<RtEvent> &applied) const;
    public:
      bool is_remote(void) const;
      bool is_forward_progress_task(void);
      inline bool is_stolen(void) const { return (steal_count > 0); }
      inline bool is_origin_mapped(void) const { return map_origin; }
      inline bool is_replicable(void) const { return replicate; }
      int get_depth(void) const;
    public:
      void set_current_proc(Processor current);
      inline void set_origin_mapped(bool origin) { map_origin = origin; }
      inline void set_replicated(bool repl) { replicate = repl; }
      inline void set_target_proc(Processor next) { target_proc = next; }
    public:
      void set_must_epoch(MustEpochOp *epoch, unsigned index,
                          bool do_registration);
    public:
      void pack_base_task(Serializer &rez, AddressSpaceID target);
      void unpack_base_task(Deserializer &derez,
                            std::set<RtEvent> &ready_events);
      void pack_base_external_task(Serializer &rez, AddressSpaceID target);
      void unpack_base_external_task(Deserializer &derez);
    public:
      void mark_stolen(void);
      void initialize_base_task(InnerContext *ctx,
            const Predicate &p, Processor::TaskFuncID tid,
            Provenance *provenance);
      void validate_region_requirements(void);
    public:
      bool select_task_options(bool prioritize);
    public:
      virtual void activate(void);
      virtual void deactivate(bool free = true);
      virtual const char* get_logging_name(void) const;
      virtual OpKind get_operation_kind(void) const;
      virtual size_t get_region_count(void) const;
      virtual Mappable* get_mappable(void);
      virtual bool invalidates_physical_trace_template(bool &exec_fence) const
        { exec_fence = false; return !regions.empty(); }
    public:
      virtual void trigger_dependence_analysis(void) = 0;
      virtual void trigger_commit(void);
    public:
      virtual void predicate_false(void) = 0;
    public:
      virtual void select_sources(const unsigned index, PhysicalManager *target,
                                  const std::vector<InstanceView*> &sources,
                                  std::vector<unsigned> &ranking,
                                  std::map<unsigned,PhysicalManager*> &points);
      virtual void update_atomic_locks(const unsigned index,
                                       Reservation lock, bool exclusive);
      virtual unsigned find_parent_index(unsigned idx);
      virtual VersionInfo& get_version_info(unsigned idx);
      virtual const VersionInfo& get_version_info(unsigned idx) const;
      virtual std::map<PhysicalManager*,unsigned>*
                                            get_acquired_instances_ref(void);
    public:
      virtual bool distribute_task(void) = 0;
      virtual bool perform_mapping(MustEpochOp *owner = NULL,
                                   const DeferMappingArgs *args = NULL) = 0;
      virtual void launch_task(bool inline_task = false) = 0;
      virtual bool is_stealable(void) const = 0;
      virtual bool is_output_global(unsigned idx) const { return false; }
      virtual bool is_output_valid(unsigned idx) const { return false; } 
      virtual bool is_output_grouped(unsigned idx) const { return false; }
    public:
      virtual TaskKind get_task_kind(void) const = 0;
    public:
      // Returns true if the task should be deactivated
      virtual bool pack_task(Serializer &rez, AddressSpaceID target) = 0;
      virtual bool unpack_task(Deserializer &derez, Processor current,
                               std::set<RtEvent> &ready_events) = 0;
      virtual void perform_inlining(VariantImpl *variant,
                    const std::deque<InstanceSet> &parent_regions) = 0;
    public:
      bool defer_perform_mapping(RtEvent precondition, MustEpochOp *op,
                                    unsigned invocation_count = 0,
                                    std::vector<unsigned> *performed = NULL,
                                    std::vector<ApEvent> *effects = NULL);
    public:
      // Tell the parent context that this task is in a ready queue
      void activate_outstanding_task(void);
      void deactivate_outstanding_task(void);
    public:
      void perform_privilege_checks(void);
    public:
      void clone_task_op_from(TaskOp *rhs, Processor p,
                              bool stealable, bool duplicate_args);
      void update_grants(const std::vector<Grant> &grants);
      void update_arrival_barriers(const std::vector<PhaseBarrier> &barriers);
      void finalize_output_region_trees(void);
    public:
      void compute_parent_indexes(InnerContext *alt_context = NULL);
      void perform_intra_task_alias_analysis(void);
    public:
      // From Memoizable
      virtual const RegionRequirement& get_requirement(unsigned idx) const
        { return logical_regions[idx]; }
      virtual unsigned get_output_offset() const
        { return regions.size(); }
    public: // helper for mapping, here because of inlining
      void validate_variant_selection(MapperManager *local_mapper,
                          VariantImpl *impl, Processor::Kind kind, 
                          const std::deque<InstanceSet> &physical_instances,
                          const char *call_name) const;
    public:
      // These methods get called once the task has executed
      // and all the children have either mapped, completed,
      // or committed.
      void trigger_children_committed(RtEvent pre = RtEvent::NO_RT_EVENT);
    protected:
      // Tasks have two requirements to commit:
      // - all commit dependences must be satisfied (trigger_commit)
      // - all children must commit (children_committed)
      virtual void trigger_task_commit(void) = 0;
    public:
      static void handle_deferred_children_commit(const void *args);
    protected:
      TaskRequirements                          logical_regions;
      // Region requirements to check for collective behavior
      std::vector<unsigned>                     check_collective_regions;
      // A map of any locks that we need to take for this task
      std::map<Reservation,bool/*exclusive*/>   atomic_locks;
      // Set of acquired instances for this task
      std::map<PhysicalManager*,unsigned/*ref count*/> acquired_instances;
    protected:
      std::vector<unsigned>                     parent_req_indexes;
      // The version infos for this task
      LegionVector<VersionInfo>                 version_infos;
    protected:
      // Whether we have an optional future return value
      std::optional<size_t>                     future_return_size;
    protected:
      bool commit_received;
    protected:
      bool options_selected;
      bool memoize_selected;
      bool map_origin;
      bool request_valid_instances;
      bool elide_future_return;
      bool replicate;
    private:
      mutable bool is_local;
      mutable bool local_cached;
    protected:
      bool children_commit;
    protected:
      MapperManager *mapper;
    public:
      // Index for this must epoch op
      unsigned must_epoch_index;
    public:
      // Static methods
      static void process_unpack_task(Runtime *rt, Deserializer &derez);
      static void process_remote_replay(Runtime *rt, Deserializer &derez);
    public:
      static void log_requirement(UniqueID uid, unsigned idx,
                                 const RegionRequirement &req);
    };

    /**
     * \class RemoteTaskOp
     * This is a remote copy of a TaskOp to be used
     * for mapper calls and other operations
     */
    class RemoteTaskOp : public ExternalTask, public RemoteOp {
    public:
      RemoteTaskOp(Runtime *rt, Operation *ptr, AddressSpaceID src);
      RemoteTaskOp(const RemoteTaskOp &rhs) = delete;
      virtual ~RemoteTaskOp(void);
    public:
      RemoteTaskOp& operator=(const RemoteTaskOp &rhs) = delete;
    public:
      virtual UniqueID get_unique_id(void) const;
      virtual uint64_t get_context_index(void) const;
      virtual int get_depth(void) const;
      virtual bool has_parent_task(void) const;
      virtual const Task* get_parent_task(void) const;
      virtual const std::string_view& get_provenance_string(
          bool human = true) const;
      virtual const char* get_task_name(void) const;
      virtual Domain get_slice_domain(void) const;
      virtual ShardID get_shard_id(void) const;
      virtual size_t get_total_shards(void) const;
      virtual DomainPoint get_shard_point(void) const;
      virtual Domain get_shard_domain(void) const;
      virtual void set_context_index(uint64_t index);
      virtual ContextCoordinate get_task_tree_coordinate(void) const
        { return ContextCoordinate(context_index, index_point); }
    public:
      virtual const char* get_logging_name(void) const;
      virtual OpKind get_operation_kind(void) const;
      virtual void select_sources(const unsigned index, PhysicalManager *target,
                                  const std::vector<InstanceView*> &sources,
                                  std::vector<unsigned> &ranking,
                                  std::map<unsigned,PhysicalManager*> &points);
      virtual void pack_remote_operation(Serializer &rez, AddressSpaceID target,
                                         std::set<RtEvent> &applied) const;
      virtual void unpack(Deserializer &derez);
    };

    /**
     * \class SingleTask
     * This is the parent type for each of the single class
     * kinds of classes.  It also serves as the type that
     * represents a context for each application level task.
     */
    class SingleTask : public TaskOp {
    public:
      struct MispredicationTaskArgs :
        public LgTaskArgs<MispredicationTaskArgs> {
      public:
        static const LgTaskID TASK_ID = LG_MISPREDICATION_TASK_ID;
      public:
        MispredicationTaskArgs(SingleTask *t)
          : LgTaskArgs<MispredicationTaskArgs>(t->get_unique_op_id()),
            task(t) { }
      public:
        SingleTask *const task;
      }; 
      struct OrderConcurrentLaunchArgs : 
        public LgTaskArgs<OrderConcurrentLaunchArgs> { 
      public:
        static const LgTaskID TASK_ID = LG_ORDER_CONCURRENT_LAUNCH_TASK_ID;
      public:
        OrderConcurrentLaunchArgs(SingleTask *t, Processor p, ApEvent s, 
                                  VariantID v)
          : LgTaskArgs<OrderConcurrentLaunchArgs>(t->get_unique_op_id()),
            task(t), processor(p), vid(v), start(s),
            ready(Runtime::create_ap_user_event(NULL)) { }
      public:
        SingleTask *const task;
        const Processor processor;
        const VariantID vid;
        const ApEvent start;
        const ApUserEvent ready;
      };
    public:
      SingleTask(Runtime *rt);
      virtual ~SingleTask(void);
    public:
      virtual void trigger_dependence_analysis(void) = 0;
    public:
      // These two functions are only safe to call after
      // the task has had its variant selected
      bool is_leaf(void) const;
      bool is_inner(void) const;
      inline bool is_concurrent(void) const { return concurrent_task; }
      bool is_created_region(unsigned index) const;
      void update_no_access_regions(void);
      void clone_single_from(SingleTask *task);
    public:
      inline void clone_virtual_mapped(std::vector<bool> &target) const
        { target = virtual_mapped; }
      inline void clone_parent_req_indexes(std::vector<unsigned> &target) const
        { target = parent_req_indexes; }
      inline const std::deque<InstanceSet>&
        get_physical_instances(void) const { return physical_instances; }
      inline const std::vector<bool>& get_no_access_regions(void) const
        { return no_access_regions; }
      inline VariantID get_selected_variant(void) const
        { return selected_variant; }
      inline const std::set<RtEvent>& get_map_applied_conditions(void) const
        { return map_applied_conditions; }
      inline RtEvent get_profiling_reported(void) const
        { return profiling_reported; }
      virtual ContextCoordinate get_task_tree_coordinate(void) const
        { return ContextCoordinate(context_index, index_point); }
    public:
      void enqueue_ready_task(bool use_target_processor,
                              RtEvent wait_on = RtEvent::NO_RT_EVENT);
      RtEvent perform_versioning_analysis(const bool post_mapper);
      virtual bool replicate_task(void);
      virtual void initialize_map_task_input(Mapper::MapTaskInput &input,
                                             Mapper::MapTaskOutput &output,
                                             MustEpochOp *must_epoch_owner);
      virtual bool finalize_map_task_output(Mapper::MapTaskInput &input,
                                            Mapper::MapTaskOutput &output,
                                            MustEpochOp *must_epoch_owner);
      void handle_post_mapped(RtEvent pre = RtEvent::NO_RT_EVENT);
    protected:
      void prepare_output_instance(unsigned index,
                                   InstanceSet &instance_set,
                                   const RegionRequirement &req,
                                   Memory target,
                                   const LayoutConstraintSet &constraints);
    public:
      virtual InnerContext* create_implicit_context(void);
      void configure_execution_context(Mapper::ContextConfigOutput &config);
      void set_shard_manager(ShardManager *manager);
    protected: // mapper helper call
      void validate_target_processors(const std::vector<Processor> &prcs) const;
    protected:
      bool invoke_mapper(MustEpochOp *must_epoch_owner);
      bool map_all_regions(MustEpochOp *must_epoch_owner,
                              const DeferMappingArgs *defer_args);
      void perform_post_mapping(const TraceInfo &trace_info);
      void check_future_return_bounds(FutureInstance *instance) const;
      void create_leaf_memory_pools(VariantImpl *impl,
          std::map<Memory,PoolBounds> &dynamic_pool_bounds);
    public:
      bool acquire_leaf_memory_pool(Memory memory, const PoolBounds &bounds,
                                    RtEvent *safe_for_unbounded_pools);
      void release_leaf_memory_pool(Memory memory);
    protected:
      void pack_single_task(Serializer &rez, AddressSpaceID target);
      void unpack_single_task(Deserializer &derez,
                              std::set<RtEvent> &ready_events);
    public:
      virtual void pack_profiling_requests(Serializer &rez,
                                           std::set<RtEvent> &applied) const;
      virtual int add_copy_profiling_request(const PhysicalTraceInfo &info,
                               Realm::ProfilingRequestSet &requests,
                               bool fill, unsigned count = 1);
      virtual bool handle_profiling_response(
          const Realm::ProfilingResponse &response, const void *orig,
          size_t orig_length, LgEvent &fevent, bool &failed_alloc);
      virtual void handle_profiling_update(int count);
      void finalize_single_task_profiling(void);
    public:
      virtual void activate(void);
      virtual void deactivate(bool free = true);
      virtual bool is_top_level_task(void) const { return false; }
      virtual bool is_shard_task(void) const { return false; }
      virtual SingleTask* get_origin_task(void) const = 0;
    public:
      virtual void predicate_false(void) = 0;
      virtual void launch_task(bool inline_task = false);
      virtual bool distribute_task(void) = 0;
      virtual bool perform_mapping(MustEpochOp *owner = NULL,
                                   const DeferMappingArgs *args = NULL) = 0;
      virtual void handle_future_size(size_t return_type_size,
                                      std::set<RtEvent> &applied_events) = 0;
      virtual uint64_t order_collectively_mapped_unbounded_pools(
          uint64_t lamport_clock, bool need_result)
        { assert(false); return lamport_clock; }
      virtual ApEvent order_concurrent_launch(ApEvent start, VariantImpl *impl)
        { assert(false); return start; }
      virtual void record_output_extent(unsigned idx,
          const DomainPoint &color, const DomainPoint &extents) 
        { assert(false); }
      virtual void record_output_registered(RtEvent registered,
                                            std::set<RtEvent> &applied_events)
        { assert(false); }
      virtual void trigger_replay(void);
      // For tasks that are sharded off by control replication
      virtual void shard_off(RtEvent mapped_precondition);
      virtual bool is_stealable(void) const = 0;
    public:
      virtual TaskKind get_task_kind(void) const = 0;
    public:
      // Override these methods from operation class
      virtual void trigger_mapping(void);
    protected:
      friend class ShardManager;
      virtual void trigger_task_commit(void) = 0;
    public:
      virtual bool send_task(Processor target,
          std::vector<SingleTask*> &others) = 0;
      virtual bool pack_task(Serializer &rez, AddressSpaceID target) = 0;
      virtual bool unpack_task(Deserializer &derez, Processor current,
                               std::set<RtEvent> &ready_events) = 0; 
      virtual void perform_inlining(VariantImpl *variant,
                    const std::deque<InstanceSet> &parent_regions);
    public:
      virtual void handle_future(ApEvent effects, FutureInstance *instance,
                                 const void *metadata, size_t metasize,
                                 FutureFunctor *functor,
                                 Processor future_proc,
                                 bool own_functor) = 0;
      virtual void handle_mispredication(void) = 0;
    public:
      virtual void perform_concurrent_task_barrier(void) = 0;
    public:
      // From Memoizable
      virtual ApEvent replay_mapping(void);
    public:
      virtual void perform_replicate_collective_versioning(unsigned index,
          unsigned parent_req_index, LegionMap<LogicalRegion,
            CollectiveVersioningBase::RegionVersioning> &to_perform);
      virtual void convert_replicate_collective_views(
          const CollectiveViewCreatorBase::RendezvousKey &key,
          std::map<LogicalRegion,
            CollectiveViewCreatorBase::CollectiveRendezvous> &rendezvous);
    public:
      void handle_remote_profiling_response(Deserializer &derez);
      static void process_remote_profiling_response(Deserializer &derez);
    public:
      virtual void concurrent_allreduce(ProcessorManager *manager, 
          uint64_t lamport_clock, VariantID vid, bool poisoned) = 0;
      void record_inner_termination(ApEvent termination_event);
    protected:
      virtual TaskContext* create_execution_context(VariantImpl *v,
          std::set<ApEvent> &launch_events, bool inline_task, bool leaf_task);
    public:
      static void order_concurrent_task_launch(const void *args);
    protected:
      // Boolean for each region saying if it is virtual mapped
      std::vector<bool>                           virtual_mapped;
      // Regions which are NO_ACCESS or have no privilege fields
      std::vector<bool>                           no_access_regions; 
    protected:
      std::vector<Processor>                      target_processors;
      // Hold the result of the mapping 
      std::deque<InstanceSet>                     physical_instances;
      std::vector<ApEvent>                        region_preconditions;
      std::vector<std::vector<PhysicalManager*> > source_instances;
      std::vector<Memory>                         future_memories;
      std::map<Memory,MemoryPool*>                leaf_memory_pools;
    protected: // Mapper choices 
      std::vector<unsigned>                       untracked_valid_regions;
      VariantID                                   selected_variant;
      TaskPriority                                task_priority;
      bool                                        perform_postmap;
    protected:
      // Events that must be triggered before we are done mapping
      std::set<RtEvent>                     map_applied_conditions;
      // The single task termination event encapsulates the exeuction of the
      // task being done and all child operations and their effects being done
      // It does NOT encapsulate the 'effects_complete' of this task
      // Only the actual operation completion event captures that
      ApUserEvent                           single_task_termination;
    protected:
      TaskContext*                          execution_context;
      RemoteTraceRecorder*                  remote_trace_recorder;
      // For replication of this task
      ShardManager*                         shard_manager;
    protected:
      mutable bool leaf_cached, is_leaf_result;
      mutable bool inner_cached, is_inner_result;
    protected:
      std::vector<ProfilingMeasurementID>      task_profiling_requests;
      std::vector<ProfilingMeasurementID>      copy_profiling_requests;
      RtUserEvent                                   profiling_reported;
      int                                           profiling_priority;
      int                                           copy_fill_priority;
      std::atomic<int>                  outstanding_profiling_requests;
      std::atomic<int>                  outstanding_profiling_reported;
#ifdef DEBUG_LEGION
    protected:
      // For checking that premapped instances didn't change during mapping
      std::map<unsigned/*index*/,
               std::vector<Mapping::PhysicalInstance> > premapped_instances;
#endif
    };

    /**
     * \class MultiTask
     * This is the parent type for each of the multi-task
     * kinds of classes.
     */
    class MultiTask : public PointwiseAnalyzable<CollectiveViewCreator<TaskOp> > {
    public:
      typedef std::map<DomainPoint,DomainPoint> OutputExtentMap; 
      struct FutureHandles : public Collectable {
      public:
        std::map<DomainPoint,DistributedID> handles;
      };
      struct ConcurrentGroup {
        ConcurrentGroup(void)
          : exchange(NULL), group_points(0), color_points(0),
            lamport_clock(0), variant(0), poisoned(false) { }
        union ConcurrentPrecondition {
          ConcurrentPrecondition(void)
            : interpreted(RtUserEvent::NO_RT_USER_EVENT) { }
          RtUserEvent interpreted;
          RtBarrier traced;
        } precondition;
        std::vector<RtEvent> preconditions;
        std::map<Processor,DomainPoint> processors;
        std::vector<std::pair<PointTask*,ProcessorManager*> > point_tasks;
        std::vector<std::pair<SliceTask*,AddressSpace> > slice_tasks;
        std::vector<ShardID> shards;
        ConcurrentAllreduce *exchange;
        size_t group_points; // local points for this shard
        size_t color_points; // global points across all shards
        // This barrier is only here to help with a bug that currently
        // exists in the CUDA driver between collective kernel launches
        // and invocations of cudaMalloc, once it is fixed then we should
        // be able to remove it
        RtBarrier task_barrier;
        uint64_t lamport_clock;
        VariantID variant;
        bool poisoned;
      };
    public:
      MultiTask(Runtime *rt);
      virtual ~MultiTask(void);
    public:
      bool is_sliced(void) const;
      void slice_index_space(void);
      void trigger_slices(void);
      void clone_multi_from(MultiTask *task, IndexSpace is, Processor p,
                            bool recurse, bool stealable); 
      RtBarrier get_concurrent_task_barrier(Color color) const;
    public:
      virtual void activate(void);
      virtual void deactivate(bool free = true);
      virtual bool is_reducing_future(void) const { return (redop > 0); }
      virtual Domain get_slice_domain(void) const;
      virtual ShardID get_shard_id(void) const { return 0; }
      virtual size_t get_total_shards(void) const { return 1; }
      virtual DomainPoint get_shard_point(void) const { return DomainPoint(0); }
      virtual Domain get_shard_domain(void) const 
        { return Domain(DomainPoint(0),DomainPoint(0)); }
      virtual bool is_pointwise_analyzable(void) const;
    public:
      virtual void trigger_dependence_analysis(void) = 0;
    public:
      virtual void predicate_false(void) = 0;
      virtual void premap_task(void) = 0;
      virtual bool distribute_task(void) = 0;
      virtual bool perform_mapping(MustEpochOp *owner = NULL,
                                   const DeferMappingArgs *args = NULL) = 0;
      virtual void launch_task(bool inline_task = false) = 0;
      virtual bool is_stealable(void) const = 0;
    public:
      virtual TaskKind get_task_kind(void) const = 0;
    public:
      virtual void trigger_mapping(void);
    protected:
      virtual void trigger_task_commit(void) = 0;
    public:
      virtual bool pack_task(Serializer &rez, AddressSpaceID target) = 0;
      virtual bool unpack_task(Deserializer &derez, Processor current,
                               std::set<RtEvent> &ready_events) = 0;
      virtual void perform_inlining(VariantImpl *variant,
                    const std::deque<InstanceSet> &parent_regions) = 0;
    public:
      virtual SliceTask* clone_as_slice_task(IndexSpace is,
                      Processor p, bool recurse, bool stealable) = 0;
      virtual void reduce_future(const DomainPoint &point,
                                 FutureInstance *instance, ApEvent effects) = 0;
      virtual void register_must_epoch(void) = 0;
    public:
      void pack_multi_task(Serializer &rez, AddressSpaceID target);
      void unpack_multi_task(Deserializer &derez,
                             std::set<RtEvent> &ready_events);
    public:
      // Return true if it is safe to delete the future
      bool fold_reduction_future(FutureInstance *instance, ApEvent effects);
      void report_concurrent_mapping_failure(Processor processor,
          const DomainPoint &one, const DomainPoint &two) const;
    protected:
      std::list<SliceTask*> slices;
      bool sliced;
    protected:
      IndexSpaceNode *launch_space; // global set of points
      IndexSpace internal_space; // local set of points
      FutureMap future_map;
      size_t future_map_coordinate;
      FutureHandles *future_handles;
      ReductionOpID redop;
      bool deterministic_redop;
      const ReductionOp *reduction_op;
      Future redop_initial_value;
      FutureMap point_arguments;
      std::vector<FutureMap> point_futures;
      std::vector<OutputOptions> output_region_options;
      std::vector<OutputExtentMap> output_region_extents;
      // For handling reductions of types with serdez methods
      const SerdezRedopFns *serdez_redop_fns;
      std::atomic<FutureInstance*> reduction_instance;
      ApEvent reduction_instance_precondition;
      std::vector<ApEvent> reduction_fold_effects;
      // Only for handling serdez reductions
      void *serdez_redop_state;
      size_t serdez_redop_state_size;
      // Reduction metadata
      void *reduction_metadata;
      size_t reduction_metasize;
      // Temporary storage for future results
      std::map<DomainPoint,
        std::pair<FutureInstance*,ApEvent> > temporary_futures;
      // used for detecting cases where we've already mapped a mutli task
      // on the same node but moved it to a different processor
      bool first_mapping;
    protected:
      ConcurrentID concurrent_functor;
      unsigned concurrent_points; 
      std::map<Color,ConcurrentGroup> concurrent_groups;
    protected:
      uint64_t collective_lamport_clock;
      RtUserEvent collective_lamport_clock_ready;
      size_t collective_unbounded_points;
    protected:
      bool children_commit_invoked;
    protected:
      Future predicate_false_future;
      void *predicate_false_result;
      size_t predicate_false_size;
    protected:
      // These are the mapped events for individual point tasks in the
      // index space launch for doing pointwise mapping dependences
      std::map<DomainPoint,RtEvent> point_mapped_events; 
    };

    /**
     * \class IndividualTask
     * This class serves as the basis for all individual task
     * launch calls performed by the runtime.
     */
    class IndividualTask : public SingleTask,
                           public LegionHeapify<IndividualTask> {
    public:
      static const AllocationType alloc_type = INDIVIDUAL_TASK_ALLOC;
    public:
      IndividualTask(Runtime *rt);
      IndividualTask(const IndividualTask &rhs);
      virtual ~IndividualTask(void);
    public:
      IndividualTask& operator=(const IndividualTask &rhs);
    public:
      virtual void activate(void);
      virtual void deactivate(bool free = true);
    protected:
      virtual SingleTask* get_origin_task(void) const { return orig_task; }
      virtual Domain get_slice_domain(void) const { return Domain::NO_DOMAIN; }
      virtual ShardID get_shard_id(void) const { return 0; }
      virtual size_t get_total_shards(void) const { return 1; }
      virtual DomainPoint get_shard_point(void) const { return DomainPoint(0); }
      virtual Domain get_shard_domain(void) const
        { return Domain(DomainPoint(0),DomainPoint(0)); }
      virtual Operation* get_origin_operation(void) 
        { return is_remote() ? orig_task : this; } 
    public:
      Future initialize_task(InnerContext *ctx,
                             const TaskLauncher &launcher,
                             Provenance *provenance,
                             bool top_level=false,
                             bool must_epoch_launch = false,
                             std::vector<OutputRequirement> *outputs = NULL);
      void perform_base_dependence_analysis(void);
    protected:
      void create_output_regions(std::vector<OutputRequirement> &outputs);
    public:
      virtual bool has_prepipeline_stage(void) const { return true; }
      virtual void trigger_prepipeline_stage(void);
      virtual void trigger_dependence_analysis(void);
      virtual void trigger_ready(void);
      virtual void report_interfering_requirements(unsigned idx1,unsigned idx2); 
      virtual bool record_trace_hash(TraceRecognizer &recognizer, uint64_t idx);
      // Virtual method for creating the future for this task so that
      // we can overload for control replication
      virtual Future create_future(void);
    public:
      virtual void predicate_false(void);
      virtual bool distribute_task(void);
      virtual bool perform_mapping(MustEpochOp *owner = NULL,
                                   const DeferMappingArgs *args = NULL);
      virtual bool finalize_map_task_output(Mapper::MapTaskInput &input,
                                            Mapper::MapTaskOutput &output,
                                            MustEpochOp *must_epoch_owner);
      virtual void handle_future_size(size_t return_type_size,
                                      std::set<RtEvent> &applied_events);
      virtual void record_output_registered(RtEvent registered,
                                      std::set<RtEvent> &applied_events); 
      virtual bool is_stealable(void) const;
      virtual bool replicate_task(void);
    public:
      virtual bool is_output_valid(unsigned idx) const;
      virtual bool is_output_grouped(unsigned idx) const;
    public:
      virtual TaskKind get_task_kind(void) const;
    public:
      virtual void trigger_complete(ApEvent effects);
      virtual void trigger_task_commit(void);
    public:
      virtual void handle_future(ApEvent effects, FutureInstance *instance,
                                 const void *metadata, size_t metasize,
                                 FutureFunctor *functor,
                                 Processor future_proc,
                                 bool own_functor);
      virtual void handle_mispredication(void);
      virtual void prepare_map_must_epoch(void);
    public:
      virtual bool send_task(Processor target,
          std::vector<SingleTask*> &others);
      virtual bool pack_task(Serializer &rez, AddressSpaceID target);
      virtual bool unpack_task(Deserializer &derez, Processor current,
                               std::set<RtEvent> &ready_events);
      virtual bool is_top_level_task(void) const { return top_level_task; }
    public:
      void set_concurrent_postcondition(RtEvent postcondition);
      virtual uint64_t order_collectively_mapped_unbounded_pools(
          uint64_t lamport_clock, bool need_result);
      virtual ApEvent order_concurrent_launch(ApEvent start, VariantImpl *impl);
      virtual void concurrent_allreduce(ProcessorManager *manager, 
          uint64_t lamport_clock, VariantID vid, bool poisoned);
      virtual void perform_concurrent_task_barrier(void);
      void finish_concurrent_allreduce(uint64_t lamport_clock, bool poisoned);
    protected:
      void pack_remote_complete(Serializer &rez, ApEvent effect);
      void pack_remote_commit(Serializer &rez, RtEvent precondition);
      void unpack_remote_complete(Deserializer &derez);
      void unpack_remote_commit(Deserializer &derez);
    public:
      // From MemoizableOp
      virtual void complete_replay(ApEvent pre);
    public:
      static void process_unpack_remote_future_size(Deserializer &derez);
      static void process_unpack_remote_mapped(Deserializer &derez);
      static void process_unpack_remote_complete(Deserializer &derez);
      static void process_unpack_remote_commit(Deserializer &derez);
      static void handle_remote_output_registration(Deserializer &derez);
      static void handle_concurrent_request(Deserializer &derez,
                                            AddressSpaceID source);
      static void handle_concurrent_response(Deserializer &derez);
    protected: 
      Future result; 
    protected:
      std::vector<OutputOptions> output_region_options;
      // Event for when the output regions are registered with the context
      RtEvent output_regions_registered;
      RtEvent remote_commit_precondition;
    protected:
      // Events for concurrent task launches, only used for when this task
      // is part of a must-epoch launch
      RtUserEvent concurrent_precondition;
      RtEvent concurrent_postcondition;
    protected:
      // Information for remotely executing task
      IndividualTask *orig_task; // Not a valid pointer when remote
      UniqueID remote_unique_id;
    protected:
      Future predicate_false_future;
      void *predicate_false_result;
      size_t predicate_false_size;
    protected:
      bool sent_remotely;
    protected:
      friend class Internal;
      // Special field for the top level task
      bool top_level_task;
    };

    /**
     * \class PointTask
     * A point task is a single point of an index space task
     * launch.  It will primarily be managed by its enclosing
     * slice task owner.
     */
    class PointTask : public SingleTask, public ProjectionPoint,
                      public LegionHeapify<PointTask> {
    public:
      static const AllocationType alloc_type = POINT_TASK_ALLOC;
    public:
      PointTask(Runtime *rt);
      PointTask(const PointTask &rhs);
      virtual ~PointTask(void);
    public:
      PointTask& operator=(const PointTask &rhs);
    public:
      virtual void activate(void);
      virtual void deactivate(bool free = true);
      virtual Operation* get_origin_operation(void); 
      virtual SingleTask* get_origin_task(void) const { return orig_task; }
      virtual Domain get_slice_domain(void) const 
        { return Domain(index_point,index_point); }
      virtual ShardID get_shard_id(void) const { return 0; }
      virtual size_t get_total_shards(void) const { return 1; }
      virtual DomainPoint get_shard_point(void) const { return DomainPoint(0); }
      virtual Domain get_shard_domain(void) const
        { return Domain(DomainPoint(0),DomainPoint(0)); }
      virtual bool is_reducing_future(void) const;
    public:
      virtual void trigger_dependence_analysis(void);
      virtual void trigger_replay(void);
      virtual void report_interfering_requirements(unsigned idx1,unsigned idx2);
    public:
      virtual void predicate_false(void);
      virtual bool distribute_task(void);
      virtual bool perform_mapping(MustEpochOp *owner = NULL,
                                   const DeferMappingArgs *args = NULL);
      virtual void handle_future_size(size_t return_type_size,
                                      std::set<RtEvent> &applied_events);
      virtual void shard_off(RtEvent mapped_precondition);
      virtual bool is_stealable(void) const;
      virtual bool replicate_task(void);
      virtual VersionInfo& get_version_info(unsigned idx);
      virtual const VersionInfo& get_version_info(unsigned idx) const;
      virtual bool is_output_global(unsigned idx) const; 
      virtual bool is_output_valid(unsigned idx) const;
      virtual bool is_output_grouped(unsigned idx) const;
      virtual void record_output_extent(unsigned idx,
          const DomainPoint &color, const DomainPoint &extents);
      virtual void record_output_registered(RtEvent registered,
                                            std::set<RtEvent> &applied_events);
      virtual bool finalize_map_task_output(Mapper::MapTaskInput &input,
                                            Mapper::MapTaskOutput &output,
                                            MustEpochOp *must_epoch_owner);
      virtual void perform_inlining(VariantImpl *variant,
                    const std::deque<InstanceSet> &parent_regions);
    public:
      virtual TaskKind get_task_kind(void) const;
    public:
      virtual void trigger_complete(ApEvent effects);
      virtual void trigger_task_commit(void);
    public:
      virtual bool send_task(Processor target,
          std::vector<SingleTask*> &others);
      virtual bool pack_task(Serializer &rez, AddressSpaceID target);
      virtual bool unpack_task(Deserializer &derez, Processor current,
                               std::set<RtEvent> &ready_events);
    public:
      virtual void handle_future(ApEvent effects, FutureInstance *instance,
                                 const void *metadata, size_t metasize,
                                 FutureFunctor *functor,
                                 Processor future_proc,
                                 bool own_functor);
      virtual void handle_mispredication(void);
    public:
      virtual uint64_t order_collectively_mapped_unbounded_pools(
          uint64_t lamport_clock, bool need_result);
      virtual ApEvent order_concurrent_launch(ApEvent start, VariantImpl *impl);
      virtual void concurrent_allreduce(ProcessorManager *manager,
          uint64_t lamport_clock, VariantID vid, bool poisoned);
      virtual void perform_concurrent_task_barrier(void);
      bool check_concurrent_variant(VariantID vid);
    public:
      // ProjectionPoint methods
      virtual const DomainPoint& get_domain_point(void) const;
      virtual void set_projection_result(unsigned idx, LogicalRegion result);
      virtual void record_intra_space_dependences(unsigned index,
             const std::vector<DomainPoint> &dependences);
      virtual void record_pointwise_dependence(uint64_t previous_context_index,
          const DomainPoint &previous_point, ShardID shard_id);
      virtual const Operation* as_operation(void) const { return this; }
    public:
      void initialize_point(SliceTask *owner, const DomainPoint &point,
                            const FutureMap &point_arguments, bool inline_task,
                            const std::vector<FutureMap> &point_futures,
                            bool record_future_pointwise_dependences);
      RtEvent perform_pointwise_analysis(void);
    public:
      // From MemoizableOp
      virtual void complete_replay(ApEvent pre);
    public:
      // From Memoizable
      virtual TraceLocalID get_trace_local_id(void) const;
    public:
      virtual size_t get_collective_points(void) const;
      virtual bool find_shard_participants(std::vector<ShardID> &shards);
      virtual RtEvent convert_collective_views(unsigned requirement_index,
                       unsigned analysis_index, LogicalRegion region,
                       const InstanceSet &targets, InnerContext *physical_ctx,
                       CollectiveMapping *&analysis_mapping, bool &first_local,
                       LegionVector<FieldMaskSet<InstanceView> > &target_views,
                       std::map<InstanceView*,size_t> &collective_arrivals);
      virtual RtEvent perform_collective_versioning_analysis(unsigned index,
                       LogicalRegion handle, EqSetTracker *tracker,
                       const FieldMask &mask, unsigned parent_req_index);
    public: // Collective stuff for replicated versions of this point task
      virtual void perform_replicate_collective_versioning(unsigned index,
          unsigned parent_req_index, LegionMap<LogicalRegion,
            CollectiveVersioningBase::RegionVersioning> &to_perform);
      virtual void convert_replicate_collective_views(
          const CollectiveViewCreatorBase::RendezvousKey &key,
          std::map<LogicalRegion,
            CollectiveViewCreatorBase::CollectiveRendezvous> &rendezvous); 
    public: 
      bool has_remaining_inlining_dependences(
            std::map<PointTask*,unsigned> &remaining,
            std::map<RtEvent,std::vector<PointTask*> > &event_deps) const;
      void complete_point_projection(void);
    protected:
      friend class SliceTask;
      PointTask                   *orig_task;
      SliceTask                   *slice_owner;
    protected:
      std::vector<RtEvent> pointwise_mapping_dependences;
    protected:
      Color concurrent_color;
      RtBarrier concurrent_task_barrier;
      // This is the concurrent precondition event that we need to signal
      // when the preconditions are met for this point task. For non-traced
      // execution this will be a user event that we signal. For traced
      // code (either recording or replaying) this will be a barrier that
      // we will arrive on for each point task.
      union ConcurrentPrecondition {
        ConcurrentPrecondition(void)
          : interpreted(RtUserEvent::NO_RT_USER_EVENT) { }
        RtUserEvent interpreted;
        RtBarrier traced;
      } concurrent_precondition;
      // This is the postcondition event that need to wait for before
      // doing the concurrent lamport max all-reduce. It ensures that
      // the preconditions for all the points in the concurrent task
      // have been met and therefore it's safe to do the lamport protocol
      RtEvent concurrent_postcondition;
    };

    /**
     * \class ShardTask
     * A shard task is copy of a single task that is used for
     * executing a single copy of a control replicated task.
     * It implements the functionality of a single task so that 
     * we can use it mostly transparently for the execution of 
     * a single shard.
     */
    class ShardTask : public SingleTask {
    public:
      ShardTask(Runtime *rt, SingleTask *source, InnerContext *parent,
          ShardManager *manager, ShardID shard_id,
          Processor target, VariantID chosen);
      ShardTask(Runtime *rt, InnerContext *parent_ctx, Deserializer &derez,
          ShardManager *manager, ShardID shard_id, Processor target,
          VariantID chosen);
      ShardTask(const ShardTask &rhs) = delete;
      virtual ~ShardTask(void);
    public:
      ShardTask& operator=(const ShardTask &rhs) = delete;
    public:
      virtual void activate(void); 
      virtual void deactivate(bool free = true);
      virtual Domain get_slice_domain(void) const;
      virtual ShardID get_shard_id(void) const { return shard_id; }
      virtual size_t get_total_shards(void) const;
      virtual DomainPoint get_shard_point(void) const;
      virtual Domain get_shard_domain(void) const;
      virtual SingleTask* get_origin_task(void) const 
        { assert(false); return NULL; }
      virtual bool is_shard_task(void) const { return true; }
      virtual bool is_top_level_task(void) const; 
      // Set this to true so we always eagerly evaluate future functors
      // at the end of a task to get an actual future instance to pass back
      virtual bool is_reducing_future(void) const { return true; }
    public:
      // From MemoizableOp
      virtual void trigger_replay(void);
    public:
      virtual void trigger_dependence_analysis(void);
      virtual void predicate_false(void);
      virtual bool distribute_task(void);
      virtual RtEvent perform_must_epoch_version_analysis(MustEpochOp *own);
      virtual bool perform_mapping(MustEpochOp *owner = NULL,
                                   const DeferMappingArgs *args = NULL);
      virtual void handle_future_size(size_t return_type_size,
                                      std::set<RtEvent> &applied_events);
      virtual bool is_stealable(void) const;
      virtual void initialize_map_task_input(Mapper::MapTaskInput &input,
                                             Mapper::MapTaskOutput &output,
                                             MustEpochOp *must_epoch_owner);
      virtual bool finalize_map_task_output(Mapper::MapTaskInput &input,
                                            Mapper::MapTaskOutput &output,
                                            MustEpochOp *must_epoch_owner);
    public:
      virtual TaskKind get_task_kind(void) const;
    public:
      // Override these methods from operation class
      virtual void trigger_mapping(void); 
      virtual void trigger_complete(ApEvent effects);
    protected:
      virtual void trigger_task_commit(void);
    public:
      virtual bool send_task(Processor target,
          std::vector<SingleTask*> &others);
      virtual bool pack_task(Serializer &rez, AddressSpaceID target);
      virtual bool unpack_task(Deserializer &derez, Processor current,
                               std::set<RtEvent> &ready_events); 
      virtual void perform_inlining(VariantImpl *variant,
              const std::deque<InstanceSet> &parent_regions);
    public:
      virtual void handle_future(ApEvent effects, FutureInstance *instance,
                                 const void *metadata, size_t metasize,
                                 FutureFunctor *functor,
                                 Processor future_proc,
                                 bool own_functor); 
      virtual void handle_mispredication(void);
    public:
      virtual uint64_t order_collectively_mapped_unbounded_pools(
          uint64_t lamport_clock, bool need_result);
      virtual void concurrent_allreduce(ProcessorManager *manager,
          uint64_t lamport_clock, VariantID vid, bool poisoned);
      virtual void perform_concurrent_task_barrier(void);
    public:
      virtual RtEvent convert_collective_views(unsigned requirement_index,
                       unsigned analysis_index, LogicalRegion region,
                       const InstanceSet &targets, InnerContext *physical_ctx,
                       CollectiveMapping *&analysis_mapping, bool &first_local,
                       LegionVector<FieldMaskSet<InstanceView> > &target_views,
                       std::map<InstanceView*,size_t> &collective_arrivals);
      virtual RtEvent perform_collective_versioning_analysis(unsigned index,
                       LogicalRegion handle, EqSetTracker *tracker,
                       const FieldMask &mask, unsigned parent_req_index);
    protected:
      virtual TaskContext* create_execution_context(VariantImpl *v,
          std::set<ApEvent> &launch_events, bool inline_task, bool leaf_task);
    public:
      virtual InnerContext* create_implicit_context(void);
    public:
      void dispatch(void);
      void return_resources(ResourceTracker *target,
                            std::set<RtEvent> &preconditions);
      void report_leaks_and_duplicates(std::set<RtEvent> &preconditions);
      void handle_collective_message(Deserializer &derez);
      void handle_rendezvous_message(Deserializer &derez);
      void handle_compute_equivalence_sets(Deserializer &derez);
      void handle_output_equivalence_set(Deserializer &derez);
      void handle_refine_equivalence_sets(Deserializer &derez);
      void handle_intra_space_dependence(Deserializer &derez);
      void handle_resource_update(Deserializer &derez,
                                  std::set<RtEvent> &applied);
      void handle_created_region_contexts(Deserializer &derez,
                                          std::set<RtEvent> &applied);
      void handle_trace_update(Deserializer &derez, AddressSpaceID source);
      void handle_find_trace_local_sets(Deserializer &derez,
                                        AddressSpaceID source);
      ApBarrier handle_find_trace_shard_event(size_t temp_index, ApEvent event,
                                              ShardID remote_shard);
      ApBarrier handle_find_trace_shard_frontier(size_t temp_index, ApEvent event,
                                                 ShardID remote_shard);
      RtEvent handle_pointwise_dependence(uint64_t context_index, 
          const DomainPoint &point, ShardID shard, RtUserEvent to_trigger);
      ReplicateContext* get_replicate_context(void) const;
    public:
      void initialize_implicit_task(TaskID tid, MapperID mid, Processor proxy);
    public:
      const ShardID shard_id;
    };

    /**
     * \class IndexTask
     * An index task is used to represent an index space task
     * launch performed by the runtime.  It will only live
     * on the node on which it was created.  Eventually the
     * mapper will slice the index space, and the corresponding
     * slice tasks for the index space will be distributed around
     * the machine and eventually returned to this index space task.
     */
    class IndexTask : public MultiTask, public LegionHeapify<IndexTask> {
    private:
      struct OutputRegionTagCreator {
      public:
        OutputRegionTagCreator(TypeTag *_type_tag, int _color_ndim)
          : type_tag(_type_tag), color_ndim(_color_ndim) { }
        template<typename DIM, typename COLOR_T>
        static inline void demux(OutputRegionTagCreator *creator)
        {
          switch (DIM::N + creator->color_ndim)
          {
#define DIMFUNC(DIM)                                             \
            case DIM:                                            \
              {                                                  \
                *creator->type_tag =                             \
                  NT_TemplateHelper::encode_tag<DIM, COLOR_T>(); \
                break;                                           \
              }
            LEGION_FOREACH_N(DIMFUNC)
#undef DIMFUNC
            default:
              assert(false);
          }
        }
      private:
        TypeTag *type_tag;
        int color_ndim;
      };
    public:
      static const AllocationType alloc_type = INDEX_TASK_ALLOC;
    public:
      IndexTask(Runtime *rt);
      IndexTask(const IndexTask &rhs);
      virtual ~IndexTask(void);
    public:
      IndexTask& operator=(const IndexTask &rhs);
    public:
      FutureMap initialize_task(InnerContext *ctx,
                                const IndexTaskLauncher &launcher,
                                IndexSpace launch_space,
                                Provenance *provenance, bool track,
                                std::vector<OutputRequirement> *outputs = NULL);
      Future initialize_task(InnerContext *ctx,
                             const IndexTaskLauncher &launcher,
                             IndexSpace launch_space,
                             Provenance *provenance,
                             ReductionOpID redop,
                             bool deterministic, bool track,
                             std::vector<OutputRequirement> *outputs = NULL);
      void initialize_regions(const std::vector<RegionRequirement> &regions);
      void initialize_predicate(const Future &pred_future,
                                const UntypedBuffer &pred_arg);
      void perform_base_dependence_analysis(void);
    protected:
      void create_output_regions(std::vector<OutputRequirement> &outputs,
                                 IndexSpace launch_space);
    public:
      virtual void activate(void);
      virtual void deactivate(bool free = true);
    public:
      virtual void prepare_map_must_epoch(void);
    protected:
      void record_output_extents(
          std::vector<OutputExtentMap> &output_extents);
      virtual void record_output_registered(RtEvent registered);
      Domain compute_global_output_ranges(IndexSpaceNode *parent,
                                          IndexPartNode *part,
                                          const OutputExtentMap& output_sizes,
                                          const OutputExtentMap& local_sizes);
      void validate_output_extents(unsigned index,
                                   const OutputRequirement& output_requirement,
                                   const OutputExtentMap& output_sizes) const;
    public:
      virtual void finalize_output_regions(bool first_invocation);
    public:
      virtual bool has_prepipeline_stage(void) const { return true; }
      virtual void trigger_prepipeline_stage(void);
      virtual void trigger_dependence_analysis(void);
      virtual void report_interfering_requirements(unsigned idx1,unsigned idx2);
      virtual bool record_trace_hash(TraceRecognizer &recognizer, uint64_t idx);
    public:
      virtual void trigger_ready(void);
      virtual void predicate_false(void);
      virtual void premap_task(void);
      virtual bool distribute_task(void);
      virtual bool perform_mapping(MustEpochOp *owner = NULL,
                                   const DeferMappingArgs *args = NULL);
      virtual void launch_task(bool inline_task = false);
      virtual bool is_stealable(void) const;
      virtual void trigger_complete(ApEvent effects);
    public:
      virtual TaskKind get_task_kind(void) const;
    protected:
      virtual void trigger_task_commit(void);
    public:
      virtual bool pack_task(Serializer &rez, AddressSpaceID target);
      virtual bool unpack_task(Deserializer &derez, Processor current,
                               std::set<RtEvent> &ready_events);
      virtual void perform_inlining(VariantImpl *variant,
                    const std::deque<InstanceSet> &parent_regions);
    public:
      virtual SliceTask* clone_as_slice_task(IndexSpace is,
                  Processor p, bool recurse, bool stealable);
    public:
      virtual void reduce_future(const DomainPoint &point, 
                                 FutureInstance *instance, ApEvent effects);
    public:
      virtual void pack_profiling_requests(Serializer &rez,
                                           std::set<RtEvent> &applied) const;
      virtual int add_copy_profiling_request(const PhysicalTraceInfo &info,
                               Realm::ProfilingRequestSet &requests,
                               bool fill, unsigned count = 1);
      virtual bool handle_profiling_response(
          const Realm::ProfilingResponse &response, const void *orig,
          size_t orig_length, LgEvent &fevent, bool &failed_alloc);
      virtual void handle_profiling_update(int count);
    public:
      virtual void register_must_epoch(void);
    public:
      virtual size_t get_collective_points(void) const;
    public:
      // Make this a virtual method so for control replication we can 
      // create a different type of future map for the task
      virtual FutureMap create_future_map(TaskContext *ctx,
                    IndexSpace launch_space, IndexSpace shard_space);
      void rendezvous_concurrent_mapped(const DomainPoint &point, 
          Processor target, Color color, RtEvent precondition); 
      void rendezvous_concurrent_mapped(Deserializer &derez);
      // Also virtual for control replication override
      virtual void finalize_concurrent_mapped(void);
      virtual void initialize_concurrent_group(Color color, size_t local,
          size_t global, RtBarrier barrier, const std::vector<ShardID> &shards);
      virtual void concurrent_allreduce(Color color, SliceTask *slice,
          AddressSpaceID slice_space, size_t points, uint64_t lamport_clock,
          VariantID vid, bool poisoned);
      virtual uint64_t collective_lamport_allreduce(uint64_t lamport_clock,
                                          size_t points, bool need_result);
    public:
      virtual RtEvent find_intra_space_dependence(const DomainPoint &point,
          RtUserEvent to_trigger = RtUserEvent::NO_RT_USER_EVENT);
      virtual RtEvent find_pointwise_dependence(
          const DomainPoint &point, GenerationID gen,
          RtUserEvent to_trigger = RtUserEvent::NO_RT_USER_EVENT);
    public:
      void record_origin_mapped_slice(SliceTask *local_slice);
      void initialize_must_epoch_concurrent_group(Color color,
          RtUserEvent precondition);
    protected:
      // Virtual so can be overridden by ReplIndexTask
      virtual void create_future_instances(std::vector<Memory> &target_mems);
      // Callback for control replication to perform reduction for sizes
      // and provide an event for when the result is ready
      virtual void finish_index_task_reduction(void);
    public:
      void return_point_mapped(const DomainPoint &point, RtEvent mapped);
      void return_slice_complete(unsigned points, ApEvent effects,
                             void *metadata = NULL, size_t metasize = 0);
      void return_slice_commit(unsigned points, RtEvent applied_condition);
    public:
      void unpack_point_mapped(Deserializer &derez, AddressSpaceID source);
      void unpack_slice_complete(Deserializer &derez);
      void unpack_slice_commit(Deserializer &derez);
      void unpack_slice_collective_versioning_rendezvous(Deserializer &derez,
                                        unsigned index, size_t total_points);
    public:
      // From MemoizableOp
      virtual void trigger_replay(void);
    public:
      void enumerate_futures(const Domain &domain);
    public:
      static void process_slice_mapped(Deserializer &derez,
                                       AddressSpaceID source);
      static void process_slice_complete(Deserializer &derez);
      static void process_slice_commit(Deserializer &derez);
      static void process_slice_find_intra_dependence(Deserializer &derez);
    protected:
      friend class SliceTask;
      Future reduction_future;
      std::optional<size_t> reduction_future_size;
      unsigned total_points;
      unsigned mapped_points;
      unsigned completed_points;
      unsigned committed_points;
    protected:
      std::vector<SliceTask*> origin_mapped_slices;
      std::vector<FutureInstance*> reduction_instances;
      std::vector<Memory> serdez_redop_targets;
    protected:
      std::set<RtEvent> map_applied_conditions;
      std::vector<RtEvent> output_preconditions;
      std::set<RtEvent> commit_preconditions;
    protected:
      std::map<DomainPoint,RtUserEvent> pending_pointwise_dependences;
    protected:
      std::vector<ProfilingMeasurementID>      task_profiling_requests;
      std::vector<ProfilingMeasurementID>      copy_profiling_requests;
      RtUserEvent                                   profiling_reported;
      int                                           profiling_priority;
      int                                           copy_fill_priority;
      std::atomic<int>                  outstanding_profiling_requests;
      std::atomic<int>                  outstanding_profiling_reported;
    protected:
      // For checking aliasing of points in debug mode only
      std::set<std::pair<unsigned,unsigned> > interfering_requirements;
      std::map<DomainPoint,std::vector<LogicalRegion> > point_requirements;
#ifdef DEBUG_LEGION
    public:
      void check_point_requirements(const DomainPoint &point,
          const std::vector<LogicalRegion> &point_regions);
#endif
    };

    /**
     * \class SliceTask
     * A slice task is a (possibly whole) fraction of an index
     * space task launch.  Once slice task object is made for
     * each slice created by the mapper when (possibly recursively)
     * slicing up the domain of the index space task launch.
     */
    class SliceTask : public MultiTask, public ResourceTracker,
                      public LegionHeapify<SliceTask> {
    public:
      static const AllocationType alloc_type = SLICE_TASK_ALLOC;
    public:
      SliceTask(Runtime *rt);
      SliceTask(const SliceTask &rhs);
      virtual ~SliceTask(void);
    public:
      SliceTask& operator=(const SliceTask &rhs);
    public:
      virtual void activate(void);
      virtual void deactivate(bool free = true);
      virtual Operation* get_origin_operation(void) { return index_owner; }
    public:
      virtual void trigger_dependence_analysis(void);
    public:
      virtual void predicate_false(void);
      virtual void premap_task(void);
      virtual bool distribute_task(void);
      virtual VersionInfo& get_version_info(unsigned idx);
      virtual const VersionInfo& get_version_info(unsigned idx) const;
      virtual bool perform_mapping(MustEpochOp *owner = NULL,
                                   const DeferMappingArgs *args = NULL);
      virtual void launch_task(bool inline_task = false);
      virtual bool is_stealable(void) const;
      virtual bool is_output_global(unsigned idx) const;
      virtual bool is_output_valid(unsigned idx) const;
      virtual bool is_output_grouped(unsigned idx) const;
      virtual void trigger_complete(ApEvent effects);
    public:
      virtual TaskKind get_task_kind(void) const;
    public:
      bool send_task(Processor target, PointTask *point,
                          std::vector<SingleTask*> &others);
      void pack_slice_task(Serializer &rez, AddressSpaceID target,
                           const std::vector<PointTask*> &to_send);
      virtual bool pack_task(Serializer &rez, AddressSpaceID target);
      virtual bool unpack_task(Deserializer &derez, Processor current,
                               std::set<RtEvent> &ready_events);
      virtual void perform_inlining(VariantImpl *variant,
                    const std::deque<InstanceSet> &parent_regions);
    public:
      virtual SliceTask* clone_as_slice_task(IndexSpace is,
                  Processor p, bool recurse, bool stealable);
      virtual void reduce_future(const DomainPoint &point,
                                 FutureInstance *instance, ApEvent effects);
      void handle_future(ApEvent complete, const DomainPoint &point,
                         FutureInstance *instance, const void *metadata, 
                         size_t metasize, FutureFunctor *functor,
                         Processor future_proc, bool own_functor); 
    public:
      virtual void register_must_epoch(void);
      PointTask* clone_as_point_task(const DomainPoint &point,
                                     bool inline_task);
      size_t enumerate_points(bool inline_task);
      void set_predicate_false_result(const DomainPoint &point,
                                      TaskContext *execution_context);
    public:
      void check_target_processors(void) const;
      void update_target_processor(void);
      void expand_replay_slices(std::list<SliceTask*> &slices);
    protected:
      virtual void trigger_task_commit(void);
    public:
      RtEvent find_intra_space_dependence(const DomainPoint &point);
      void return_privileges(TaskContext *point_context,
                             std::set<RtEvent> &preconditions);
      void record_point_mapped(PointTask *point,
          RtEvent child_mapped, bool shard_off = false);
      void record_point_complete(ApEvent child_effects);
      void record_point_committed(RtEvent commit_precondition =
                                  RtEvent::NO_RT_EVENT);
    public:
      void handle_future_size(size_t future_size, const DomainPoint &p);
      void record_output_extent(unsigned index,
          const DomainPoint &color, const DomainPoint &extent);
      void record_output_registered(RtEvent registered,
                                    std::set<RtEvent> &applied_events);
      void rendezvous_concurrent_mapped(const DomainPoint &point,
          Processor target, Color color, RtEvent precondition);
      uint64_t collective_lamport_allreduce(
          uint64_t lamport_clock, bool need_result);
      void concurrent_allreduce(PointTask *point, ProcessorManager *manager,
          uint64_t lamport_clock, VariantID vid, bool poisoned);
      void finish_concurrent_allreduce(Color color, uint64_t lamport_clock,
          bool poisoned, VariantID vid, RtBarrier concurrent_task_barrier);
    protected:
      void send_rendezvous_concurrent_mapped(void);
      void forward_completion_effects(void);
      void pack_remote_complete(Serializer &rez, ApEvent slice_effects);
      void pack_remote_commit(Serializer &rez, RtEvent applied_condition);
    public:
      static void handle_slice_return(Runtime *rt, Deserializer &derez);
    public: // Privilege tracker methods
      virtual void receive_resources(uint64_t return_index,
              std::map<LogicalRegion,unsigned> &created_regions,
              std::vector<DeletedRegion> &deleted_regions,
              std::set<std::pair<FieldSpace,FieldID> > &created_fields,
              std::vector<DeletedField> &deleted_fields,
              std::map<FieldSpace,unsigned> &created_field_spaces,
              std::map<FieldSpace,std::set<LogicalRegion> > &latent_spaces,
              std::vector<DeletedFieldSpace> &deleted_field_spaces,
              std::map<IndexSpace,unsigned> &created_index_spaces,
              std::vector<DeletedIndexSpace> &deleted_index_spaces,
              std::map<IndexPartition,unsigned> &created_partitions,
              std::vector<DeletedPartition> &deleted_partitions,
              std::set<RtEvent> &preconditions);
    public:
      // From MemoizableOp
      virtual void trigger_replay(void);
      virtual void complete_replay(ApEvent instance_ready_event);
    public:
      virtual size_t get_collective_points(void) const;
      virtual bool find_shard_participants(std::vector<ShardID> &shards);
      virtual RtEvent perform_collective_versioning_analysis(unsigned index,
                       LogicalRegion handle, EqSetTracker *tracker,
                       const FieldMask &mask, unsigned parent_req_index);
      void perform_replicate_collective_versioning(unsigned index,
          unsigned parent_req_index,
          LegionMap<LogicalRegion,RegionVersioning> &to_perform);
      void convert_replicate_collective_views(const RendezvousKey &key,
            std::map<LogicalRegion,CollectiveRendezvous> &rendezvous);

      virtual void finalize_collective_versioning_analysis(unsigned index,
          unsigned parent_req_index,
          LegionMap<LogicalRegion,RegionVersioning> &to_perform);
      virtual RtEvent convert_collective_views(unsigned requirement_index,
                       unsigned analysis_index, LogicalRegion region,
                       const InstanceSet &targets, InnerContext *physical_ctx,
                       CollectiveMapping *&analysis_mapping, bool &first_local,
                       LegionVector<FieldMaskSet<InstanceView> > &target_views,
                       std::map<InstanceView*,size_t> &collective_arrivals);
      virtual void rendezvous_collective_mapping(unsigned requirement_index,
                                  unsigned analysis_index,
                                  LogicalRegion region,
                                  RendezvousResult *result,
                                  AddressSpaceID source,
                                  const LegionVector<
                                   std::pair<DistributedID,FieldMask> > &insts);
      static void handle_collective_rendezvous(Deserializer &derez,
                                       Runtime *runtime, AddressSpaceID source);
      static void handle_collective_versioning_rendezvous(Deserializer &derez,
                                                          Runtime *runtime);
      static void handle_rendezvous_concurrent_mapped(Deserializer &derez);
      static void handle_collective_allreduce_request(Deserializer &derez,
                                                      AddressSpaceID source);
      static void handle_collective_allreduce_response(Deserializer &derez);
      static void handle_concurrent_allreduce_request(Deserializer &derez,
                                                      AddressSpaceID source);
      static void handle_concurrent_allreduce_response(Deserializer &derez);
      static void handle_remote_output_extents(Deserializer &derez);
      static void handle_remote_output_registration(Deserializer &derez);
    protected:
      friend class IndexTask;
      friend class PointTask;
      friend class ReplMustEpochOp;
      std::vector<PointTask*> points;
    protected:
      unsigned num_unmapped_points;
      std::atomic<unsigned> num_uncompleted_points;
      unsigned num_uncommitted_points;
    protected:
      IndexTask *index_owner;
      UniqueID remote_unique_id;
      bool origin_mapped;
      DomainPoint reduction_instance_point;
    protected:
      std::set<RtEvent> commit_preconditions;
    };

  }; // namespace Internal
}; // namespace Legion

#endif // __LEGION_TASKS_H__
