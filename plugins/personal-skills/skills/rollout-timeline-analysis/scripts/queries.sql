-- Minimal PerfettoSQL queries for rollout-timeline-analysis traces (*.perfetto.json)
-- Aligned with the unified 4-track schema: Agent Inference / Tool Execution / Policy Job / Policy / Robot
-- Run in Perfetto UI Query (SQL) tab or via:
--   trace_processor_shell -q queries.sql <episode>.perfetto.json

-- 1. Process / thread track summary (slice count, cumulative duration, max slice)
SELECT
  COALESCE(p.name, 'pid:' || p.pid) AS process_name,
  COALESCE(t.name, 'tid:' || t.tid) AS thread_name,
  COUNT(*) AS slice_count,
  ROUND(SUM(s.dur) / 1e9, 3) AS cumulative_s,
  ROUND(MAX(s.dur) / 1e9, 3) AS max_slice_s
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
LEFT JOIN process p ON t.upid = p.upid
WHERE s.dur >= 0
GROUP BY process_name, thread_name
ORDER BY process_name, cumulative_s DESC;

-- 2. Agent HTTP request breakdown: failures, retries, cancellations, and missing usage
SELECT
  s.id AS slice_id,
  s.name AS slice_name,
  ROUND(s.ts / 1e9, 3) AS start_s,
  ROUND(s.dur / 1e9, 3) AS dur_s,
  EXTRACT_ARG(s.arg_set_id, 'args.request_id') AS request_id,
  EXTRACT_ARG(s.arg_set_id, 'args.attempt') AS attempt,
  EXTRACT_ARG(s.arg_set_id, 'args.status') AS status,
  EXTRACT_ARG(s.arg_set_id, 'args.status_code') AS status_code,
  EXTRACT_ARG(s.arg_set_id, 'args.usage_present') AS usage_present,
  EXTRACT_ARG(s.arg_set_id, 'args.error') AS error
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = 'Agent Inference'
  AND t.name = 'agent_inference'
  AND (
    EXTRACT_ARG(s.arg_set_id, 'args.status') != 'ok'
    OR CAST(COALESCE(EXTRACT_ARG(s.arg_set_id, 'args.attempt'), 1) AS INT) > 1
    OR CAST(COALESCE(EXTRACT_ARG(s.arg_set_id, 'args.usage_present'), 1) AS INT) = 0
  )
ORDER BY s.ts;

-- 3. Interval union (critical path) for Agent HTTP inference without double-counting overlap
WITH http_raw AS (
  SELECT s.ts AS start_ts, s.ts + s.dur AS end_ts
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = 'Agent Inference' AND t.name = 'agent_inference' AND s.dur > 0
),
http_ordered AS (
  SELECT
    start_ts,
    end_ts,
    MAX(end_ts) OVER (
      ORDER BY start_ts, end_ts
      ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
    ) AS prev_max_end
  FROM http_raw
),
http_grouped AS (
  SELECT
    start_ts,
    end_ts,
    SUM(CASE WHEN prev_max_end IS NULL OR start_ts > prev_max_end THEN 1 ELSE 0 END)
      OVER (ORDER BY start_ts, end_ts) AS grp
  FROM http_ordered
),
http_union AS (
  SELECT MIN(start_ts) AS u_start, MAX(end_ts) AS u_end
  FROM http_grouped
  GROUP BY grp
)
SELECT
  ROUND((SELECT COALESCE(SUM(end_ts - start_ts), 0) FROM http_raw) / 1e9, 3) AS http_cumulative_s,
  ROUND(COALESCE(SUM(u_end - u_start), 0) / 1e9, 3) AS http_critical_path_union_s
FROM http_union;

-- 4. Overlap between Agent HTTP union and Policy / Robot stateful action union
WITH http_raw AS (
  SELECT s.ts AS start_ts, s.ts + s.dur AS end_ts
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = 'Agent Inference' AND t.name = 'agent_inference' AND s.dur > 0
),
http_ordered AS (
  SELECT start_ts, end_ts,
    MAX(end_ts) OVER (ORDER BY start_ts, end_ts ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_max
  FROM http_raw
),
http_union AS (
  SELECT MIN(start_ts) AS s, MAX(end_ts) AS e
  FROM (
    SELECT start_ts, end_ts,
      SUM(CASE WHEN prev_max IS NULL OR start_ts > prev_max THEN 1 ELSE 0 END)
        OVER (ORDER BY start_ts, end_ts) AS grp
    FROM http_ordered
  )
  GROUP BY grp
),
robot_raw AS (
  SELECT s.ts AS start_ts, s.ts + s.dur AS end_ts
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = 'Policy / Robot' AND t.name = 'robot_actions' AND s.dur > 0
),
robot_ordered AS (
  SELECT start_ts, end_ts,
    MAX(end_ts) OVER (ORDER BY start_ts, end_ts ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_max
  FROM robot_raw
),
robot_union AS (
  SELECT MIN(start_ts) AS s, MAX(end_ts) AS e
  FROM (
    SELECT start_ts, end_ts,
      SUM(CASE WHEN prev_max IS NULL OR start_ts > prev_max THEN 1 ELSE 0 END)
        OVER (ORDER BY start_ts, end_ts) AS grp
    FROM robot_ordered
  )
  GROUP BY grp
)
SELECT
  ROUND(COALESCE((SELECT SUM(e - s) FROM robot_union), 0) / 1e9, 3) AS robot_stateful_union_s,
  ROUND(COALESCE(SUM(MIN(h.e, r.e) - MAX(h.s, r.s)), 0) / 1e9, 3) AS http_robot_overlap_s
FROM http_union h
JOIN robot_union r ON MAX(h.s, r.s) < MIN(h.e, r.e);

-- 5. Policy Job control events & lifecycle drain diagnostics
SELECT
  COALESCE(p.name, 'pid:' || p.pid) AS process_name,
  COALESCE(t.name, 'tid:' || t.tid) AS thread_name,
  s.name AS slice_name,
  ROUND(s.ts / 1e9, 3) AS start_s,
  ROUND(s.dur / 1e9, 3) AS dur_s,
  EXTRACT_ARG(s.arg_set_id, 'args.job_id') AS job_id,
  EXTRACT_ARG(s.arg_set_id, 'args.unit_id') AS unit_id,
  EXTRACT_ARG(s.arg_set_id, 'args.status') AS status
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE (p.name = 'Policy Job' AND t.name = 'control')
   OR (p.name = 'Policy / Robot' AND s.name LIKE 'error:%')
   OR (p.name = 'Tool Execution' AND s.name = 'lifecycle:graph_drain')
ORDER BY s.ts;
