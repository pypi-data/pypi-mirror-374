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

#include <deque>

namespace PRealm {

class REALM_INTERNAL_API_EXTERNAL_LINKAGE ThreadProfiler {
public:
  typedef long long timestamp_t;
  typedef ::realm_id_t ProcID;
  typedef ::realm_id_t MemID;
  typedef ::realm_id_t InstID;

  enum ProfKind {
    FILL_PROF,
    COPY_PROF,
    TASK_PROF,
    INST_PROF,
    PART_PROF,
    EXTERNAL_PROF,
    LAST_PROF, // must be last
  };

  struct NameClosure {
  public:
    void add_instance(const RegionInstance &inst);
    Event find_instance_name(Realm::RegionInstance inst) const;

  public:
    std::vector<RegionInstance> instances;
  };

  struct ProfilingArgs {
  public:
    inline ProfilingArgs(ProfKind k, timestamp_t create = 0)
      : create_time(create), kind(k) { }
  public:
    Event critical;
    Event provenance;
    timestamp_t create_time;
    union {
      Realm::Event inst = Realm::Event::NO_EVENT;
      Processor::TaskFuncID task;
      NameClosure *closure;
    } id;
    ProfKind kind;
  };
  struct ExternalTriggerArgs {
    Event external;
    Event fevent;
    unsigned long long provenance;
  };
  struct ProcDesc {
  public:
    ProcID proc_id;
    Processor::Kind kind;
#ifdef REALM_USE_CUDA
    Realm::Cuda::Uuid cuda_device_uuid;
#endif
  };
  struct MemDesc {
  public:
    MemID mem_id;
    Memory::Kind kind;
    unsigned long long capacity;
  };
  struct ProcMemDesc {
  public:
    ProcID proc_id;
    MemID mem_id;
    unsigned bandwidth;
    unsigned latency;
  };
  struct EventWaitInfo {
  public:
    ProcID proc_id;
    Event fevent;
    Event event;
    unsigned long long backtrace_id;
  };
  struct EventMergerInfo {
  public:
    Event result;
    Event provenance;
    timestamp_t performed;
    std::vector<Event> preconditions;
  };
  struct EventTriggerInfo {
  public:
    Event result;
    Event provenance;
    Event precondition;
    timestamp_t performed;
  };
  struct EventPoisonInfo {
  public:
    Event result;
    Event provenance;
    timestamp_t performed;
  };
  struct ExternalEventInfo {
  public:
    Event external;
    Event fevent;
    timestamp_t created;
    timestamp_t triggered;
    unsigned long long provenance; 
  };
  struct BarrierArrivalInfo {
  public:
    Event result;
    Event provenance;
    Event precondition;
    timestamp_t performed;
  };
  struct ReservationAcquireInfo {
  public:
    Event result;
    Event provenance;
    Event precondition;
    timestamp_t performed;
    Reservation reservation;
  };
  struct InstanceReadyInfo {
  public:
    Event result;
    Event precondition;
    Event unique;
    timestamp_t performed;
  };
  struct InstanceUsageInfo {
  public:
    Event inst_event;
    unsigned long long op_id;
    FieldID field;
  };
  struct FillInstInfo {
  public:
    MemID dst;
    FieldID fid;
    Event dst_inst_uid;
  };
  struct FillInfo {
  public:
    unsigned long long size;
    timestamp_t create, ready, start, stop;
    Event fevent;
    Event creator;
    Event critical;
    std::vector<FillInstInfo> inst_infos;
  };
  struct CopyInstInfo {
  public:
    MemID src, dst;
    FieldID src_fid, dst_fid;
    Event src_inst_uid, dst_inst_uid;
    unsigned num_hops;
    bool indirect;
  };
  struct CopyInfo {
  public:
    unsigned long long size;
    timestamp_t create, ready, start, stop;
    Event fevent;
    Event creator;
    Event critical;
    std::vector<CopyInstInfo> inst_infos;
  };
  struct WaitInfo {
  public:
    timestamp_t wait_start, wait_ready, wait_end;
    Event wait_event;
  };
  struct TaskInfo {
  public:
    Processor::TaskFuncID task_id;
    Processor proc;
    timestamp_t create, ready, start, stop;
    std::vector<WaitInfo> wait_intervals;
    Event creator;
    Event critical;
    Event finish_event;
  };
  struct GPUTaskInfo {
  public:
    Processor::TaskFuncID task_id;
    Processor proc;
    timestamp_t create, ready, start, stop;
    timestamp_t gpu_start, gpu_stop;
    std::vector<WaitInfo> wait_intervals;
    Event creator;
    Event critical;
    Event finish_event;
  };
  struct InstTimelineInfo {
  public:
    Event inst_uid;
    InstID inst_id;
    MemID mem_id;
    unsigned long long size;
    timestamp_t create, ready, destroy;
    Event creator;
  };
  struct ProfTaskInfo {
  public:
    ProcID proc_id;
    timestamp_t start, stop;
    Event creator;
    Event finish_event;
  };
  struct ApplicationInfo {
  public:
    timestamp_t start, stop;
    ProcID proc_id;
    Event fevent;
    unsigned long long provenance;
  };
  struct SpawnInfo {
  public:
    Event fevent;
    timestamp_t spawn;
  };

public:
  ThreadProfiler(Processor p, Realm::Event implicit);
  ThreadProfiler(const ThreadProfiler &rhs) = delete;
  ThreadProfiler &operator=(const ThreadProfiler &rhs) = delete;

public:
  void add_fill_request(ProfilingRequestSet &requests,
                        const std::vector<CopySrcDstField> &dsts,
                        Event critical);
  void add_copy_request(ProfilingRequestSet &requests,
                        const std::vector<CopySrcDstField> &srcs,
                        const std::vector<CopySrcDstField> &dsts,
                        Event critical);
  void add_task_request(ProfilingRequestSet &requests,
                        Processor::TaskFuncID task_id,
                        Event critical, Event fevent,
                        timestamp_t spawn_time = 0);
  Event add_inst_request(ProfilingRequestSet &requests, Event critical);

public:
  inline bool is_implicit(void) const { return implicit_fevent.exists(); }
  Event get_fevent(void) const;
  Processor get_callback_processor(void) const;
  void process_proc_desc(const Processor &p);
  void process_mem_desc(const Memory &m);
  void record_event_wait(Event wait_on, Backtrace &bt, 
      long long start, long long stop);
  void record_event_trigger(Event result, Event precondition);
  void record_event_poison(Event result);
  void record_barrier_use(Event barrier);
  void record_barrier_arrival(Event result, Event precondition);
  void record_event_merger(Event result, const Event *preconditions,
                           size_t num_events);
  void record_external_event(Realm::Event result, const std::string_view &prov);
  void record_reservation_acquire(Reservation r, Event result,
                                  Event precondition);
  Event record_instance_ready(RegionInstance inst, Event result,
                              Event precondition);
  void record_instance_usage(RegionInstance inst, FieldID field_id);
  void process_response(ProfilingResponse &response);
  void process_trigger(const void *args, size_t arglen);
  void process_external(ProfilingResponse &response);
  void record_time_range(long long start, const std::string_view& name);
  size_t dump_inter(long long target_latency);
  void finalize(void);

  static ThreadProfiler &get_thread_profiler(void);

public:
  const Processor local_proc;
  const Realm::Event implicit_fevent;
  const long long start_time;
private:
  std::deque<EventWaitInfo> event_wait_infos;
  std::deque<EventMergerInfo> event_merger_infos;
  std::deque<EventTriggerInfo> event_trigger_infos;
  std::deque<EventPoisonInfo> event_poison_infos;
  std::deque<ExternalEventInfo> external_event_infos;
  std::deque<BarrierArrivalInfo> barrier_arrival_infos;
  std::deque<ReservationAcquireInfo> reservation_acquire_infos;
  std::deque<InstanceReadyInfo> instance_ready_infos;
  std::deque<InstanceUsageInfo> instance_usage_infos;
  std::deque<FillInfo> fill_infos;
  std::deque<CopyInfo> copy_infos;
  std::deque<TaskInfo> task_infos;
  std::deque<GPUTaskInfo> gpu_task_infos;
  std::deque<InstTimelineInfo> inst_timeline_infos;
  std::deque<ProfTaskInfo> prof_task_infos;
  std::deque<ApplicationInfo> application_infos;
  std::deque<SpawnInfo> spawn_infos;
  std::vector<ProcID> proc_ids;
  std::vector<MemID> mem_ids;
  std::vector<WaitInfo> implicit_waits;
};

inline CopySrcDstField::CopySrcDstField(void)
    : inst(RegionInstance::NO_INST), field_id(FieldID(-1)), size(0),
      redop_id(0), red_fold(false), red_exclusive(false), serdez_id(0),
      subfield_offset(0), indirect_index(-1) {
  fill_data.indirect = 0;
}

inline CopySrcDstField::CopySrcDstField(const CopySrcDstField &copy_from)
    : inst(copy_from.inst), field_id(copy_from.field_id), size(copy_from.size),
      redop_id(copy_from.redop_id), red_fold(copy_from.red_fold),
      red_exclusive(copy_from.red_exclusive), serdez_id(copy_from.serdez_id),
      subfield_offset(copy_from.subfield_offset),
      indirect_index(copy_from.indirect_index) {
  // we know there's a fill value if the field ID is -1
  if (copy_from.field_id == FieldID(-1)) {
    if (size <= MAX_DIRECT_SIZE) {
      // copy whole buffer to make sure indirect is initialized too
      memcpy(fill_data.direct, copy_from.fill_data.direct, MAX_DIRECT_SIZE);
    } else {
      if (copy_from.fill_data.indirect) {
        fill_data.indirect = malloc(size);
        memcpy(fill_data.indirect, copy_from.fill_data.indirect, size);
      } else
        fill_data.indirect = 0;
    }
  } else
    fill_data.indirect = 0;
}

inline CopySrcDstField &
CopySrcDstField::operator=(const CopySrcDstField &copy_from) {
  if (this == &copy_from)
    return *this; // self-assignment
  if ((field_id != FieldID(-1)) && (size > MAX_DIRECT_SIZE) &&
      fill_data.indirect)
    free(fill_data.indirect);

  inst = copy_from.inst;
  field_id = copy_from.field_id;
  size = copy_from.size;
  redop_id = copy_from.redop_id;
  red_fold = copy_from.red_fold;
  red_exclusive = copy_from.red_exclusive;
  serdez_id = copy_from.serdez_id;
  subfield_offset = copy_from.subfield_offset;
  indirect_index = copy_from.indirect_index;

  // we know there's a fill value if the field ID is -1
  if (copy_from.field_id == FieldID(-1)) {
    if (size <= MAX_DIRECT_SIZE) {
      // copy whole buffer to make sure indirect is initialized too
      memcpy(fill_data.direct, copy_from.fill_data.direct, MAX_DIRECT_SIZE);
    } else {
      if (copy_from.fill_data.indirect) {
        fill_data.indirect = malloc(size);
        memcpy(fill_data.indirect, copy_from.fill_data.indirect, size);
      } else
        fill_data.indirect = 0;
    }
  } else
    fill_data.indirect = 0;

  return *this;
}

inline CopySrcDstField::~CopySrcDstField(void) {
  if ((field_id == FieldID(-1)) && (size > MAX_DIRECT_SIZE)) {
    free(fill_data.indirect);
  }
}

inline CopySrcDstField &
CopySrcDstField::set_field(RegionInstance _inst, FieldID _field_id,
                           size_t _size, size_t _subfield_offset /*= 0*/) {
  inst = _inst;
  field_id = _field_id;
  size = _size;
  subfield_offset = _subfield_offset;
  return *this;
}

inline CopySrcDstField &
CopySrcDstField::set_indirect(int _indirect_index, FieldID _field_id,
                              size_t _size, size_t _subfield_offset /*= 0*/) {
  indirect_index = _indirect_index;
  field_id = _field_id;
  size = _size;
  subfield_offset = _subfield_offset;
  return *this;
}

inline CopySrcDstField &CopySrcDstField::set_redop(ReductionOpID _redop_id,
                                                   bool _is_fold,
                                                   bool _is_excl) {
  redop_id = _redop_id;
  red_fold = _is_fold;
  red_exclusive = _is_excl;
  return *this;
}

inline CopySrcDstField &CopySrcDstField::set_serdez(CustomSerdezID _serdez_id) {
  serdez_id = _serdez_id;
  return *this;
}

inline CopySrcDstField &CopySrcDstField::set_fill(const void *_data,
                                                  size_t _size) {
  field_id = -1;
  size = _size;
  if (size <= MAX_DIRECT_SIZE) {
    memcpy(&fill_data.direct, _data, size);
  } else {
    fill_data.indirect = malloc(size);
    memcpy(fill_data.indirect, _data, size);
  }
  return *this;
}

template <typename T>
inline CopySrcDstField &CopySrcDstField::set_fill(T value) {
  return set_fill(&value, sizeof(T));
}

inline CopySrcDstField::operator Realm::CopySrcDstField(void) const {
  Realm::CopySrcDstField result;
  result.inst = inst;
  result.field_id = field_id;
  result.size = size;
  result.redop_id = redop_id;
  result.red_fold = red_fold;
  result.red_exclusive = red_exclusive;
  result.serdez_id = serdez_id;
  result.subfield_offset = subfield_offset;
  result.indirect_index = indirect_index;
  static_assert(sizeof(result.fill_data) == sizeof(fill_data));
  memcpy(&result.fill_data, &fill_data, sizeof(fill_data));
  return result;
}

inline bool Event::is_barrier(void) const {
  const Realm::ID identity(id);
  return identity.is_barrier();
}

inline void Event::wait(void) const {
  if (!exists())
    return;
  Backtrace bt;
  bt.capture_backtrace();
  const long long start = Realm::Clock::current_time_in_nanoseconds();
  Realm::Event::wait();
  const long long stop = Realm::Clock::current_time_in_nanoseconds();
  ThreadProfiler::get_thread_profiler().record_event_wait(*this, bt, start, stop);
}

inline void Event::wait_faultaware(bool &poisoned) const {
  if (!exists())
    return;
  Backtrace bt;
  bt.capture_backtrace();
  const long long start = Realm::Clock::current_time_in_nanoseconds();
  Realm::Event::wait_faultaware(poisoned);
  const long long stop = Realm::Clock::current_time_in_nanoseconds();
  ThreadProfiler::get_thread_profiler().record_event_wait(*this, bt, start, stop);
}

/*static*/ inline Event Event::merge_events(const Event *wait_for,
                                            size_t num_events) {
  const Event result = Realm::Event::merge_events(wait_for, num_events);
  ThreadProfiler::get_thread_profiler().record_event_merger(result, wait_for,
                                                            num_events);
  return result;
}

/*static*/ inline Event Event::merge_events(Event ev1, Event ev2, Event ev3,
                                            Event ev4, Event ev5, Event ev6) {
  size_t num_events;
  if (ev6.exists())
    num_events = 6;
  else if (ev5.exists())
    num_events = 5;
  else if (ev4.exists())
    num_events = 4;
  else if (ev3.exists())
    num_events = 3;
  else
    num_events = 2;
  const Event events[] = {ev1, ev2, ev3, ev4, ev5, ev6};
  const Event result = Realm::Event::merge_events(events, num_events);
  ThreadProfiler::get_thread_profiler().record_event_merger(result, events,
                                                            num_events);
  return result;
}

/*static*/ inline Event Event::merge_events(const std::set<Event> &wait_for) {
  const std::vector<Event> events(wait_for.begin(), wait_for.end());
  const Event result =
      Realm::Event::merge_events(&events.front(), events.size());
  ThreadProfiler::get_thread_profiler().record_event_merger(
      result, &events.front(), events.size());
  return result;
}

/*static*/ inline Event Event::merge_events(const span<const Event> &wait_for) {
  const Event result =
      Realm::Event::merge_events(wait_for.data(), wait_for.size());
  ThreadProfiler::get_thread_profiler().record_event_merger(
      result, wait_for.data(), wait_for.size());
  return result;
}

/*static*/ inline Event Event::merge_events_ignorefaults(const Event *wait_for,
                                                         size_t num_events) {
  const Event result =
      Realm::Event::merge_events_ignorefaults(wait_for, num_events);
  ThreadProfiler::get_thread_profiler().record_event_merger(result, wait_for,
                                                            num_events);
  return result;
}

/*static*/ inline Event
Event::merge_events_ignorefaults(const std::set<Event> &wait_for) {
  const std::vector<Event> events(wait_for.begin(), wait_for.end());
  const Event result =
      Realm::Event::merge_events_ignorefaults(&events.front(), events.size());
  ThreadProfiler::get_thread_profiler().record_event_merger(
      result, &events.front(), events.size());
  return result;
}

/*static*/ inline Event
Event::merge_events_ignorefaults(const span<const Event> &wait_for) {
  const Event result =
      Realm::Event::merge_events_ignorefaults(wait_for.data(), wait_for.size());
  ThreadProfiler::get_thread_profiler().record_event_merger(
      result, wait_for.data(), wait_for.size());
  return result;
}

/*static*/ inline Event Event::ignorefaults(Event wait_for) {
  const Event result = Realm::Event::ignorefaults(wait_for);
  ThreadProfiler::get_thread_profiler().record_event_merger(result, &wait_for,
                                                            1);
  return result;
}

inline void UserEvent::trigger(Event wait_on, bool ignore_faults) const {
  ThreadProfiler::get_thread_profiler().record_event_trigger(*this, wait_on);
  Realm::UserEvent copy;
  copy.id = id;
  copy.trigger(wait_on, ignore_faults);
}

inline void UserEvent::cancel(void) const {
  ThreadProfiler::get_thread_profiler().record_event_poison(*this);
  Realm::UserEvent copy;
  copy.id = id;
  copy.cancel();
}

/*static*/ inline UserEvent UserEvent::create_user_event(void) {
  return UserEvent(Realm::UserEvent::create_user_event());
}

inline Barrier::operator Realm::Barrier(void) const {
  Realm::Barrier result;
  result.id = id;
  result.timestamp = timestamp;
  return result;
}

/*static*/ inline Barrier Barrier::create_barrier(unsigned expected_arrivals,
                                                  ReductionOpID redop,
                                                  const void *initial_value,
                                                  size_t initial_value_size) {
  return Realm::Barrier::create_barrier(expected_arrivals, redop, initial_value,
                                        initial_value_size);
}

/*static*/ inline Barrier
Barrier::create_barrier(const Barrier::ParticipantInfo *expected_arrivals,
                        size_t num_participants, ReductionOpID redop,
                        const void *initial_value, size_t initial_value_size) {
  return Realm::Barrier::create_barrier(expected_arrivals, num_participants,
                                        redop, initial_value,
                                        initial_value_size);
}

inline Barrier
Barrier::set_arrival_pattern(const Barrier::ParticipantInfo *expected_arrivals,
                             size_t num_participants) {
  Realm::Barrier barrier = *this;
  return barrier.set_arrival_pattern(expected_arrivals, num_participants);
}

inline void Barrier::destroy_barrier(void) {
  Realm::Barrier barrier = *this;
  barrier.destroy_barrier();
}

inline Barrier Barrier::advance_barrier(void) const {
  Realm::Barrier barrier = *this;
  return barrier.advance_barrier();
}

inline Barrier Barrier::alter_arrival_count(int delta) const {
  Realm::Barrier barrier = *this;
  return barrier.alter_arrival_count(delta);
}

inline Barrier Barrier::get_previous_phase(void) const {
  Realm::Barrier barrier = *this;
  return barrier.get_previous_phase();
}

inline void Barrier::arrive(unsigned count, Event wait_on, const void *value,
                            size_t size) const {
  ThreadProfiler::get_thread_profiler().record_barrier_arrival(*this, wait_on);
  Realm::Barrier copy;
  copy.id = id;
  copy.timestamp = timestamp;
  copy.arrive(count, wait_on, value, size);
}

inline bool Barrier::get_result(void *value, size_t value_size) const {
  Realm::Barrier barrier = *this;
  return barrier.get_result(value, value_size);
}

inline Event Reservation::acquire(unsigned mode, bool exclusive,
                                  Event wait_on) const {
  const Event result = Realm::Reservation::acquire(mode, exclusive, wait_on);
  ThreadProfiler::get_thread_profiler().record_reservation_acquire(
      *this, result, wait_on);
  return result;
}

inline Event Reservation::try_acquire(bool retry, unsigned mode, bool exclusive,
                                      Event wait_on) const {
  const Event result =
      Realm::Reservation::try_acquire(retry, mode, exclusive, wait_on);
  ThreadProfiler::get_thread_profiler().record_reservation_acquire(
      *this, result, wait_on);
  return result;
}

inline Event Processor::spawn(TaskFuncID func_id, const void *args,
                              size_t arglen, Event wait_on,
                              int priority) const {
  ProfilingRequestSet no_requests;
  return spawn(func_id, args, arglen, no_requests, wait_on, priority);
}

/*static*/ inline ProcessorGroup ProcessorGroup::create_group(
    const Processor* members, size_t num_members) {
  return ProcessorGroup(Realm::ProcessorGroup::create_group(members, num_members));
}

/*static*/ inline ProcessorGroup ProcessorGroup::create_group(
    const span<const Processor>& members) {
  return create_group(members.data(), members.size());
}

inline void ProcessorGroup::destroy(Event wait_on) const {
  Realm::ProcessorGroup copy;
  copy.id = id;
  copy.destroy(wait_on);
}

/*static*/ inline Event RegionInstance::create_instance(
    RegionInstance &inst, Memory memory, const InstanceLayoutGeneric &ilg,
    const ProfilingRequestSet &requests, Event wait_on) {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler &profiler = ThreadProfiler::get_thread_profiler();
  inst.unique_event = profiler.add_inst_request(alt_requests, wait_on);
  Event result = Realm::RegionInstance::create_instance(inst, memory, ilg,
                                                        alt_requests, wait_on);
  return profiler.record_instance_ready(inst, result, wait_on);
}

/*static*/ inline Event RegionInstance::create_instance(
    RegionInstance &inst, Memory memory, InstanceLayoutGeneric *ilg,
    const ProfilingRequestSet &requests, Event wait_on) {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler &profiler = ThreadProfiler::get_thread_profiler();
  inst.unique_event = profiler.add_inst_request(alt_requests, wait_on);
  Event result = Realm::RegionInstance::create_instance(inst, memory, *ilg,
                                                        alt_requests, wait_on);
  delete ilg;
  return profiler.record_instance_ready(inst, result, wait_on);
}

/*static*/ inline Event RegionInstance::create_external_instance(
    RegionInstance &inst, Memory memory, const InstanceLayoutGeneric &ilg,
    const ExternalInstanceResource &resource,
    const ProfilingRequestSet &requests, Event wait_on) {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler &profiler = ThreadProfiler::get_thread_profiler();
  inst.unique_event = profiler.add_inst_request(alt_requests, wait_on);
  Event result = Realm::RegionInstance::create_external_instance(
      inst, memory, ilg, resource, alt_requests, wait_on);
  return profiler.record_instance_ready(inst, result, wait_on);
}

/*static*/ inline Event RegionInstance::create_external_instance(
    RegionInstance &inst, Memory memory, InstanceLayoutGeneric *ilg,
    const ExternalInstanceResource &resource,
    const ProfilingRequestSet &requests, Event wait_on) {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler &profiler = ThreadProfiler::get_thread_profiler();
  inst.unique_event = profiler.add_inst_request(alt_requests, wait_on);
  Event result = Realm::RegionInstance::create_external_instance(
      inst, memory, *ilg, resource, alt_requests, wait_on);
  delete ilg;
  return profiler.record_instance_ready(inst, result, wait_on);
}

/*static*/ inline Event
RegionInstance::create_external(RegionInstance &inst, Memory memory,
                                uintptr_t base, InstanceLayoutGeneric *ilg,
                                const ProfilingRequestSet &requests,
                                Event wait_on) {
  // this interface doesn't give us a size or read-only ness, so get the size
  //  from the layout and assume it's read/write
  ExternalMemoryResource res(reinterpret_cast<void *>(base), ilg->bytes_used);
  return create_external_instance(inst, memory, ilg, res, requests, wait_on);
}

template <int N, typename T>
/*static*/ inline Event RegionInstance::create_instance(
    RegionInstance &inst, Memory memory, const IndexSpace<N, T> &space,
    const std::vector<size_t> &field_sizes, size_t block_size,
    const ProfilingRequestSet &reqs, Event wait_on) {
  // smoosh hybrid block sizes back to SOA for now
  if (block_size > 1)
    block_size = 0;
  InstanceLayoutConstraints ilc(field_sizes, block_size);
  // We use fortran order here
  int dim_order[N];
  for (int i = 0; i < N; i++)
    dim_order[i] = i;
  InstanceLayoutGeneric *layout =
      InstanceLayoutGeneric::choose_instance_layout<N, T>(space, ilc,
                                                          dim_order);
  Event result = create_instance(inst, memory, *layout, reqs, wait_on);
  delete layout;
  return result;
}

template <int N, typename T>
/*static*/ inline Event RegionInstance::create_instance(
    RegionInstance &inst, Memory memory, const IndexSpace<N, T> &space,
    const std::map<FieldID, size_t> &field_sizes, size_t block_size,
    const ProfilingRequestSet &reqs, Event wait_on) {
  // smoosh hybrid block sizes back to SOA for now
  if (block_size > 1)
    block_size = 0;
  InstanceLayoutConstraints ilc(field_sizes, block_size);
  // We use fortran order here
  int dim_order[N];
  for (int i = 0; i < N; i++)
    dim_order[i] = i;
  InstanceLayoutGeneric *layout =
      InstanceLayoutGeneric::choose_instance_layout<N, T>(space, ilc,
                                                          dim_order);
  Event result = create_instance(inst, memory, *layout, reqs, wait_on);
  delete layout;
  return result;
}

template <int N, typename T>
/*static*/ inline Event RegionInstance::create_instance(
    RegionInstance &inst, Memory memory, const Rect<N, T> &rect,
    const std::vector<size_t> &field_sizes, size_t block_size,
    const ProfilingRequestSet &prs, Event wait_on) {
  return RegionInstance::create_instance<N, T>(
      inst, memory, IndexSpace<N, T>(rect), field_sizes, block_size, prs,
      wait_on);
}

template <int N, typename T>
/*static*/ inline Event RegionInstance::create_instance(
    RegionInstance &inst, Memory memory, const Rect<N, T> &rect,
    const std::map<FieldID, size_t> &field_sizes, size_t block_size,
    const ProfilingRequestSet &prs, Event wait_on) {
  return RegionInstance::create_instance<N, T>(
      inst, memory, IndexSpace<N, T>(rect), field_sizes, block_size, prs,
      wait_on);
}

template <int N, typename T>
/*static*/ inline Event RegionInstance::create_file_instance(
    RegionInstance &inst, const char *file_name, const IndexSpace<N, T> &space,
    const std::vector<FieldID> &field_ids,
    const std::vector<size_t> &field_sizes, realm_file_mode_t file_mode,
    const ProfilingRequestSet &prs, Event wait_on) {
  // this old interface assumes an SOA layout of fields in memory, starting at
  //  the beginning of the file
  InstanceLayoutConstraints ilc(field_ids, field_sizes, 0 /*SOA*/);
  int dim_order[N];
  for (int i = 0; i < N; i++)
    dim_order[i] = i;
  InstanceLayoutGeneric *ilg;
  ilg = InstanceLayoutGeneric::choose_instance_layout(space, ilc, dim_order);

  ExternalFileResource res(file_name, file_mode);
  return create_external_instance(inst, res.suggested_memory(), ilg, res, prs,
                                  wait_on);
}

inline Event RegionInstance::fetch_metadata(Processor target) const {
  return Realm::RegionInstance::fetch_metadata(target);
}

template <int N, typename T>
inline IndexSpace<N, T> RegionInstance::get_indexspace(void) const {
  return Realm::RegionInstance::get_indexspace<N, T>();
}

template <int N>
inline IndexSpace<N, int> RegionInstance::get_indexspace(void) const {
  return Realm::RegionInstance::get_indexspace<N, int>();
}

template <typename FT, int N, typename T>
inline GenericAccessor<FT, N, T>::GenericAccessor(RegionInstance inst,
                                                  FieldID field_id,
                                                  size_t subfield_offset)
    : Realm::GenericAccessor<FT, N, T>(inst, field_id, subfield_offset) {
  ThreadProfiler::get_thread_profiler().record_instance_usage(inst, field_id);
}

template <typename FT, int N, typename T>
inline GenericAccessor<FT, N, T>::GenericAccessor(RegionInstance inst,
                                                  FieldID field_id,
                                                  const Rect<N, T> &subrect,
                                                  size_t subfield_offset)
    : Realm::GenericAccessor<FT, N, T>(inst, field_id, subrect,
                                       subfield_offset) {
  ThreadProfiler::get_thread_profiler().record_instance_usage(inst, field_id);
}

template <typename FT, int N, typename T>
inline AffineAccessor<FT, N, T>::AffineAccessor(RegionInstance inst,
                                                FieldID field_id,
                                                size_t subfield_offset)
    : Realm::AffineAccessor<FT, N, T>(inst, field_id, subfield_offset) {
  ThreadProfiler::get_thread_profiler().record_instance_usage(inst, field_id);
}

template <typename FT, int N, typename T>
inline AffineAccessor<FT, N, T>::AffineAccessor(RegionInstance inst,
                                                FieldID field_id,
                                                const Rect<N, T> &subrect,
                                                size_t subfield_offset)
    : Realm::AffineAccessor<FT, N, T>(inst, field_id, subrect,
                                      subfield_offset) {
  ThreadProfiler::get_thread_profiler().record_instance_usage(inst, field_id);
}

template <typename FT, int N, typename T>
template <int N2, typename T2>
inline AffineAccessor<FT, N, T>::AffineAccessor(
    RegionInstance inst, const Matrix<N2, N, T2> &transform,
    const Point<N2, T2> &offset, FieldID field_id, size_t subfield_offset)
    : Realm::AffineAccessor<FT, N, T>(inst, transform, offset, field_id,
                                      subfield_offset) {
  ThreadProfiler::get_thread_profiler().record_instance_usage(inst, field_id);
}

template <typename FT, int N, typename T>
template <int N2, typename T2>
inline AffineAccessor<FT, N, T>::AffineAccessor(
    RegionInstance inst, const Matrix<N2, N, T2> &transform,
    const Point<N2, T2> &offset, FieldID field_id, const Rect<N, T> &subrect,
    size_t subfield_offset)
    : Realm::AffineAccessor<FT, N, T>(inst, transform, offset, field_id,
                                      subrect, subfield_offset) {
  ThreadProfiler::get_thread_profiler().record_instance_usage(inst, field_id);
}

template <typename FT, int N, typename T>
inline MultiAffineAccessor<FT, N, T>::MultiAffineAccessor(
    RegionInstance inst, FieldID field_id, size_t subfield_offset)
    : Realm::MultiAffineAccessor<FT, N, T>(inst, field_id, subfield_offset) {
  ThreadProfiler::get_thread_profiler().record_instance_usage(inst, field_id);
}

template <typename FT, int N, typename T>
inline MultiAffineAccessor<FT, N, T>::MultiAffineAccessor(
    RegionInstance inst, FieldID field_id, const Rect<N, T> &subrect,
    size_t subfield_offset)
    : Realm::MultiAffineAccessor<FT, N, T>(inst, field_id, subrect,
                                           subfield_offset) {
  ThreadProfiler::get_thread_profiler().record_instance_usage(inst, field_id);
}

template <int N, typename T>
inline Event Rect<N, T>::fill(const std::vector<CopySrcDstField> &dsts,
                              const ProfilingRequestSet &requests,
                              const void *fill_value, size_t fill_value_size,
                              Event wait_on, int priority) const {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler::get_thread_profiler().add_fill_request(alt_requests, dsts,
                                                         wait_on);
  std::vector<Realm::CopySrcDstField> alt_dsts(dsts.size());
  for (unsigned idx = 0; idx < dsts.size(); idx++)
    alt_dsts[idx] = dsts[idx];
  return Realm::Rect<N, T>::fill(alt_dsts, alt_requests, fill_value,
                                 fill_value_size, wait_on, priority);
}

template <int N, typename T>
inline Event Rect<N, T>::copy(const std::vector<CopySrcDstField> &srcs,
                              const std::vector<CopySrcDstField> &dsts,
                              const ProfilingRequestSet &requests,
                              Event wait_on, int priority) const {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler::get_thread_profiler().add_copy_request(alt_requests, srcs,
                                                         dsts, wait_on);
  std::vector<Realm::CopySrcDstField> alt_srcs(srcs.size());
  for (unsigned idx = 0; idx < srcs.size(); idx++)
    alt_srcs[idx] = srcs[idx];
  std::vector<Realm::CopySrcDstField> alt_dsts(dsts.size());
  for (unsigned idx = 0; idx < dsts.size(); idx++)
    alt_dsts[idx] = dsts[idx];
  return Realm::Rect<N, T>::copy(alt_srcs, alt_dsts, alt_requests, wait_on,
                                 priority);
}

template <int N, typename T>
inline Event Rect<N, T>::copy(const std::vector<CopySrcDstField> &srcs,
                              const std::vector<CopySrcDstField> &dsts,
                              const IndexSpace<N, T> &mask,
                              const ProfilingRequestSet &requests,
                              Event wait_on, int priority) const {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler::get_thread_profiler().add_copy_request(alt_requests, srcs,
                                                         dsts, wait_on);
  std::vector<Realm::CopySrcDstField> alt_srcs(srcs.size());
  for (unsigned idx = 0; idx < srcs.size(); idx++)
    alt_srcs[idx] = srcs[idx];
  std::vector<Realm::CopySrcDstField> alt_dsts(dsts.size());
  for (unsigned idx = 0; idx < dsts.size(); idx++)
    alt_dsts[idx] = dsts[idx];
  return Realm::Rect<N, T>::copy(alt_srcs, alt_dsts, mask, alt_requests,
                                 wait_on, priority);
}

template <int N, typename T>
inline Event IndexSpace<N, T>::fill(const std::vector<CopySrcDstField> &dsts,
                                    const ProfilingRequestSet &requests,
                                    const void *fill_value,
                                    size_t fill_value_size, Event wait_on,
                                    int priority) const {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler::get_thread_profiler().add_fill_request(alt_requests, dsts,
                                                         wait_on);
  std::vector<Realm::CopySrcDstField> alt_dsts(dsts.size());
  for (unsigned idx = 0; idx < dsts.size(); idx++)
    alt_dsts[idx] = dsts[idx];
  return Realm::IndexSpace<N, T>::fill(alt_dsts, alt_requests, fill_value,
                                       fill_value_size, wait_on, priority);
}

template <int N, typename T>
inline Event IndexSpace<N, T>::copy(const std::vector<CopySrcDstField> &srcs,
                                    const std::vector<CopySrcDstField> &dsts,
                                    const ProfilingRequestSet &requests,
                                    Event wait_on, int priority) const {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler::get_thread_profiler().add_copy_request(alt_requests, srcs,
                                                         dsts, wait_on);
  std::vector<Realm::CopySrcDstField> alt_srcs(srcs.size());
  for (unsigned idx = 0; idx < srcs.size(); idx++)
    alt_srcs[idx] = srcs[idx];
  std::vector<Realm::CopySrcDstField> alt_dsts(dsts.size());
  for (unsigned idx = 0; idx < dsts.size(); idx++)
    alt_dsts[idx] = dsts[idx];
  return Realm::IndexSpace<N, T>::copy(alt_srcs, alt_dsts, alt_requests,
                                       wait_on, priority);
}

template <int N, typename T>
inline Event IndexSpace<N, T>::copy(
    const std::vector<CopySrcDstField> &srcs,
    const std::vector<CopySrcDstField> &dsts,
    const std::vector<const typename CopyIndirection<N, T>::Base *> &indirects,
    const ProfilingRequestSet &requests, Event wait_on, int priority) const {
  ProfilingRequestSet alt_requests = requests;
  // TODO: need a way to get the instances for the indirects
  std::abort();
  ThreadProfiler::get_thread_profiler().add_copy_request(alt_requests, srcs,
                                                         dsts, wait_on);
  std::vector<Realm::CopySrcDstField> alt_srcs(srcs.size());
  for (unsigned idx = 0; idx < srcs.size(); idx++)
    alt_srcs[idx] = srcs[idx];
  std::vector<Realm::CopySrcDstField> alt_dsts(dsts.size());
  for (unsigned idx = 0; idx < dsts.size(); idx++)
    alt_dsts[idx] = dsts[idx];
  return Realm::IndexSpace<N, T>::copy(alt_srcs, alt_dsts, indirects,
                                       alt_requests, wait_on, priority);
}

inline Event IndexSpaceGeneric::copy(const std::vector<CopySrcDstField> &srcs,
                                     const std::vector<CopySrcDstField> &dsts,
                                     const ProfilingRequestSet &requests,
                                     Event wait_on, int priority) const {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler::get_thread_profiler().add_copy_request(alt_requests, srcs,
                                                         dsts, wait_on);
  std::vector<Realm::CopySrcDstField> alt_srcs(srcs.size());
  for (unsigned idx = 0; idx < srcs.size(); idx++)
    alt_srcs[idx] = srcs[idx];
  std::vector<Realm::CopySrcDstField> alt_dsts(dsts.size());
  for (unsigned idx = 0; idx < dsts.size(); idx++)
    alt_dsts[idx] = dsts[idx];
  return Realm::IndexSpaceGeneric::copy(alt_srcs, alt_dsts, alt_requests,
                                        wait_on, priority);
}

template <int N, typename T>
inline Event IndexSpaceGeneric::copy(
    const std::vector<CopySrcDstField> &srcs,
    const std::vector<CopySrcDstField> &dsts,
    const std::vector<const typename CopyIndirection<N, T>::Base *> &indirects,
    const ProfilingRequestSet &requests, Event wait_on, int priority) const {
  ProfilingRequestSet alt_requests = requests;
  ThreadProfiler::get_thread_profiler().add_copy_request(alt_requests, srcs,
                                                         dsts, wait_on);
  std::vector<Realm::CopySrcDstField> alt_srcs(srcs.size());
  for (unsigned idx = 0; idx < srcs.size(); idx++)
    alt_srcs[idx] = srcs[idx];
  std::vector<Realm::CopySrcDstField> alt_dsts(dsts.size());
  for (unsigned idx = 0; idx < dsts.size(); idx++)
    alt_dsts[idx] = dsts[idx];
  return Realm::IndexSpaceGeneric::copy<N, T>(alt_srcs, alt_dsts, indirects,
                                              alt_requests, wait_on, priority);
}

inline void Machine::get_all_processors(std::set<Processor> &pset) const {
  // Container type problem is dumb
  Realm::Machine::get_all_processors(
      *reinterpret_cast<std::set<Realm::Processor> *>(&pset));
}

inline void Machine::get_local_processors(std::set<Processor> &pset) const {
  // Container type problem is dumb
  Realm::Machine::get_local_processors(
      *reinterpret_cast<std::set<Realm::Processor> *>(&pset));
}

inline void Machine::get_local_processors_by_kind(std::set<Processor> &pset,
                                                  Processor::Kind kind) const {
  // Container type problem is dumb
  Realm::Machine::get_local_processors_by_kind(
      *reinterpret_cast<std::set<Realm::Processor> *>(&pset), kind);
}

inline void Machine::get_shared_processors(Memory m, std::set<Processor> &pset,
                                           bool local_only) const {
  // Container type problem is dumb
  Realm::Machine::get_shared_processors(
      m, *reinterpret_cast<std::set<Realm::Processor> *>(&pset), local_only);
}

/*static*/ inline Machine Machine::get_machine(void) {
  return Realm::Machine::get_machine();
}

inline void prealm_time_range(long long start_time_in_ns, const std::string_view& name) {
  ThreadProfiler::get_thread_profiler().record_time_range(start_time_in_ns, name);
}

} // namespace PRealm
