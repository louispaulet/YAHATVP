# 2026-11-21 HATVP ingestion and quality-alert investigation

## Scope and evidence

This investigation used read-only Cloud Run, Cloud Logging, Cloud Scheduler,
and Cloud Storage commands in project `yahatvp-pipeline-eu`, region
`europe-west1`. It reviewed execution records, retained structured logs,
`state/latest.json`, the November 16 source metadata and quality report,
Bronze/Silver/Gold object prefixes, and the associated quarantine Parquet.
No production replay, source rewrite, BigQuery write, or Monitoring-policy
change was made.

The deployed job at the latest failure used 8 vCPU, 32 GiB, a 30-minute task
timeout, and one retry. Its image was pipeline SHA
`97fe99f9f96e4fe7865bc34640e737822cc60511`, digest
`sha256:d1972a91b021631860613257112ac4de827a696779345085aef28f226e708203`.

## Chronological execution timeline

Cloud Run execution records are the source of execution outcomes. Email
recovery notices and Monitoring auto-resolution describe alert state; they do
not prove that the pipeline completed. Older structured stage logs are not
available for the August executions, so their source snapshot and processing
stage cannot be reconstructed reliably.

| Date (UTC) | Execution(s) | Symptom and outcome |
| --- | --- | --- |
| Aug 17–19 (Europe/Paris) | `4bklf`, `lnpsr`, `6lssb`, `9mf5x`, `2xvjw`, `w9l47`, `bct7m`, `v9h8n`, `f2gst` | `2xvjw` hit its 512 MiB memory limit. The other eight exited with code 1; retained Cloud Run messages say only “container exited with an error.” Later executions succeeded (`4479p`, `f6mdg`, `6hpsr`, `2sfxd`, `8lnvd`), but the older logs do not establish their stage-by-stage completion or map each email recovery to a particular successful run. Root causes for the code-1 exits are unconfirmed. The exact execution-to-source-date mapping is unavailable; archived official CSV/XML bytes are identical across Aug 16–19. |
| Aug 24 | `46lfw`, `7nddf`, `zsmlc` | 4 GiB and 8 GiB attempts hit the memory limit; `zsmlc` completed successfully at the Cloud Run level at 16 GiB. Stage-by-stage completion logs are unavailable. The involved archived source snapshot is Aug 24. |
| Aug 27 (UTC; Aug 28 Paris) | `h8j9n`, `q57qq`, `hrrp5` | 4 GiB and 16 GiB attempts hit the memory limit; `hrrp5` completed at the Cloud Run level at 32 GiB. Stage-by-stage completion logs are unavailable. The involved archived source snapshot is Aug 28. |
| Aug 30 | `grhrr`, `qhb9x` | 4 GiB attempt hit the memory limit; `qhb9x` completed at the Cloud Run level at 32 GiB. Stage-by-stage completion logs are unavailable. The involved archived source snapshot is Aug 30. |
| Oct 5–6 | `gjt24`, `4tsx8`, `pjq2w` | `gjt24` hit the 4 GiB limit after the official CSV/XML hashes changed. `4tsx8` still hit the 32 GiB limit. The confirmed cause was redundant historical loading of Bronze and Silver for the same dates. The existing fix prefers Bronze where present while retaining Silver-only legacy history. `pjq2w` then completed all 13 BigQuery loads, emitted `pipeline_complete`, and advanced state to Oct 6. See the [October 6 recovery report](2026-10-06-ingestion-memory-recovery.md). |
| Oct 26–27 | `kr8w7`, `fs2z7`, `fzrln` | `kr8w7` completed a replay with reversed publication-status assignment; that interim result was superseded. After the assignment was corrected, both task attempts in `fs2z7` hit the 32 GiB limit during Silver construction/serialization. The serialization-memory fix in `fzrln` then completed all 13 table loads and advanced state to Oct 27. The source bytes matched the Oct 5 snapshot, so this was a replay of known bytes. The warning streak also shows the retry issue: same-date quality reports advanced 21 → 22 → 23 because a failed replay overwrote the report selected by the still-current state. |
| Nov 2 | `978b5` | Successful 14m48s run; all 13 BigQuery tables loaded, `pipeline_complete` emitted, and state advanced to Nov 2. Quality had zero errors, 57,452 flagged records, and warning streak 25. |
| Nov 9 | `k5lzh` | Successful `NO_CHANGE` in 1m18s. It did not rebuild layers or load BigQuery because official hashes were unchanged. |
| Nov 16 | `mhrc2` | Actual failed ingestion. Both task attempts reached the memory limit; `retriedCount=1`. Quality completed with zero errors before the failure. All 10 Bronze partitions were written, but no Nov 16 Silver, Gold, anomaly-registry, or BigQuery completion was observed. There was no `pipeline_complete`, and `state/latest.json` remained at Nov 2. No later successful ingestion exists in the execution list reviewed on Nov 21. |

The execution API contains 18 failed Cloud Run executions in this period (the
first four started late Aug 16 UTC, which was Aug 17 in Europe/Paris), each
with one retry, one failed task, and zero succeeded tasks. This differs from
the 12 failure emails: alert notifications reflect policy transitions, while
the execution list includes separate scheduled and replay attempts. `cvsdg`
was cancelled by a user and is not counted as a failed execution. Full
`PIPELINE_GIT_SHA` values and pinned image digests for failed executions are
listed below; SHA is the build commit injected into each job, while the digest
is the immutable container image identity.

| UTC start | Execution(s) | `PIPELINE_GIT_SHA` | Container image digest | Memory | Result |
| --- | --- | --- | --- | --- | --- |
| Aug 16 22:06–22:09 | `4bklf`, `lnpsr` | `3c64994f2772dc160c3785e4eeed1da8a46e1240` | `ac59adb14ab430b90eafeca9955019bc6479875eda6539547f14e1999f1f35c7` | 512 MiB | Exit 1; error detail unavailable |
| Aug 16 23:50–23:52 | `6lssb`, `9mf5x` | `97af103c9851f8b1d0304a4a59d8299cd0ca4572` | `9e0602050e4709909bd44779ab1278faa0dd7695df9c8ee695eed6012f12da0e` | 512 MiB | Exit 1; error detail unavailable |
| Aug 17 00:37 | `2xvjw` | `dc6810810335af7298e7439037c5badd1394d658` | `2c87fd5a92fa10568acc0c0977019e4d5f60ab676912f0f23455e5539742c838` | 512 MiB | Memory limit |
| Aug 17 17:02 | `w9l47` | `e50eb09e8bda771fc0bac69e4178834c17fbb47d` | `e50929c5d7c7ea53989ae18e6f1855799eb5caa69023d87b7ecd28da08e1f6e1` | 2 GiB | Exit 1; error detail unavailable |
| Aug 18 22:38 | `bct7m` | `9d2797dd5129eac8557cb7a3bc6999bd0f752887` | `52b3fe16fd22cecd414ae25cfc0586ef1924e0a71cc28ceba59006fe15287587` | 2 GiB | Exit 1; error detail unavailable |
| Aug 19 00:27 | `v9h8n` | `5fc19d7d548c8d171f79267ef4b62e48edd415cc` | `373385fa067aaac8dd51801ceb164548acd741f5fcf6bcc3318a298194f00937` | 4 GiB | Exit 1; error detail unavailable |
| Aug 19 00:37 | `f2gst` | `60bbea330d56029917ba9498ff7e941d7228f215` | `103e46c1bf3442a2c05f760886aaab994e5c040b8dec264bd523e341516b0b33` | 4 GiB | Exit 1; error detail unavailable |
| Aug 24 19:57 | `46lfw` | `cb4d5998f19fb9c8c44bb6d2e8fd803cde208135` | `759a5ab299c549196aa8bf5c7a431a3a0c52a5cd7f9924697e18753d565075ee` | 4 GiB | Memory limit |
| Aug 24 20:05 | `7nddf` | `cb4d5998f19fb9c8c44bb6d2e8fd803cde208135` | `759a5ab299c549196aa8bf5c7a431a3a0c52a5cd7f9924697e18753d565075ee` | 8 GiB | Memory limit |
| Aug 27 22:09 | `h8j9n` | `215c48a7150183ccafcd41e91a94ba963c05b577` | `dc9b1a735e7c315c9056f3ea5e0bd92b7cc790fdd16afe77e7cc24021c761ce2` | 4 GiB | Memory limit |
| Aug 27 22:11 | `q57qq` | `215c48a7150183ccafcd41e91a94ba963c05b577` | `dc9b1a735e7c315c9056f3ea5e0bd92b7cc790fdd16afe77e7cc24021c761ce2` | 16 GiB | Memory limit |
| Aug 30 01:28 | `grhrr` | `53529654c477df66dda4e4249dd349ce8c394450` | `4e8ea79fb08909a9cbdf51688464bddc12060ec16032ae7424d7333b5712a0b5` | 4 GiB | Memory limit |
| Oct 5 05:00 | `gjt24` | `e82e8ed9155bca092d676b661513d99d1a05752d` | `c9acc2cf106d1be252e97f256762cfe4177deae99b28ab3980ce01837be42ef1` | 4 GiB | Memory limit |
| Oct 6 19:03 | `4tsx8` | `6ca97ece6ce28a41e0d8c6fb61479693e1eeaf74` | `f57b1be0018ab696f68eab0dbd775e81918b2bf49d8c8c88cbe89fc866554916` | 32 GiB | Memory limit |
| Oct 26 22:31 | `fs2z7` | `359c773ef854655b1ba92dd692d9e6889bbcfba5` | `1e47fc1a203732fa84859845ace1e180381554d560ae5d15e0738f5724078b1e` | 32 GiB | Memory limit |
| Nov 16 06:00 | `mhrc2` | `97fe99f9f96e4fe7865bc34640e737822cc60511` | `d1972a91b021631860613257112ac4de827a696779345085aef28f226e708203` | 32 GiB | Memory limit |

The official raw archives from Aug 16–19 share CSV hash
`156463f08b88dd884dcbb0721d9295869c8df7595cf98696162030123938dd29` and XML
hash `865261857f88ec6c262558bc115b37b94f97ea3418b6829267aa6cbd1458fdaf`; the
retained task logs do not tie each early execution to one of those same-byte
snapshot dates. The Aug 24 runs map to raw snapshot Aug 24 (CSV
`322417dace3e2dd8477e8456228a78723fad32bef76b592f8cb6dc66e35331fa`, XML
`62cfae5c9651bf23620083ba8fbb9195efbad3190d7a49bf4d663bd87a7e7d4b`). The
Aug 27 UTC runs occurred just after midnight in Paris and used the Aug 28 raw
snapshot (CSV `045c59703b14482387ceaa9f932b52232130a27c6d0fd18c0baae557ae8b3cf8`,
XML `5d65b2abc50f4749a16470c70d90033ec4e7833af3c98f6c111afb1e1e705c77`). The
The Aug 30 source snapshot has CSV hash
`045c59703b14482387ceaa9f932b52232130a27c6d0fd18c0baae557ae8b3cf8` and XML
hash `5d65b2abc50f4749a16470c70d90033ec4e7833af3c98f6c111afb1e1e705c77`. The
Oct 5 and Oct 26 snapshots have the same hashes (CSV
`781fc5e54b20bda1be5b095dcd76bbfee674cee342ec36e694099f6781704597`, XML
`a042d437b9b05f0af0aa93e7e95f18b038fb21c0eb8a3b69f499dc1e66bcd9cb`); the Oct
6 retry processed Oct 5 bytes. The Oct 6 recovery report contains the source
and successful-load evidence.

The Nov 16 execution ran from 06:00:30 to 06:20:27 UTC. Attempt 0 logged
quality completion at 06:06:39 and was terminated by signal 9 at 06:11:13;
retry attempt 1 logged quality completion at 06:16:14 and was terminated at
06:20:23. Cloud Run reports exit code 0 with the explicit message that the
configured memory limit was reached. The failed-execution Monitoring incident
opened at 06:26 and auto-resolved at 06:29; that auto-resolution was not a
successful ingestion. The warning event was logged on both attempts.

The failed run used the official HATVP snapshot dated Nov 16 and the retained
static Wayback sources dated Aug 23. The official CSV was 3,353,267 bytes,
SHA-256 `1160ee0f3c2b6425b63ca9bd13eb5ed0cba43a7125ae446cb52c9e1576c69412`;
the XML was 83,795,862 bytes, SHA-256
`d1516daccd9f88321b05c804fb2ac99d9fb655a7614840c7bd4a7ed955e81e29`. Both
hashes differ from the last processed Nov 2 state (CSV
`02354fed12a7fdd8309851c957eac1de48d11c8c0e5fc1e9aa6adc85fe34c9e2`; XML
`203a6bbb1b804b9d6b9aa2c6ab84ef033539575d3933135e51e208c37e253021`). Raw
bytes and metadata are preserved under the Nov 16 source snapshot.

## Confirmed causes and distinctions

### Nov 16 memory failure

The memory-limit failure is confirmed. Object state narrows its location to
`build_silver`: the pipeline wrote all ten Bronze tables before constructing
Silver, but wrote no Silver files. Code order confirms BigQuery loading follows
the full Bronze/Silver/Gold build, so this execution could not have partially
loaded BigQuery. It also could not advance processed state, which occurs only
after the BigQuery call returns.

The code retained all parsed source-table lists while Silver created
publication-annotated cumulative rows. Six Bronze-only tables are not inputs to
Silver or Gold; their current snapshot has about 753,751 rows in total. Holding
those Python records through Silver construction is the targeted, code-supported
memory cause. No heap profile or peak RSS was available, so the exact byte
contribution is not measured. The repair drops references to those six lists
only after their Bronze files have been written. All ten Bronze outputs remain
unchanged and retained.

This differs from the confirmed October causes: Oct 6 redundantly loaded
historical Bronze and Silver; Oct 26 had a separate Silver serialization-memory
problem after publication-status code was corrected. Those fixes remain intact.
The August code-1 exits have insufficient evidence for a root-cause claim.

### Warning recurrence and classification

The Nov 16 quality report was warning-bearing, not a failed quality check:
status `warning`, zero errors, 40,357 warnings, 57,622 flagged records, and no
10% flagged-record regression (increase 0.296%). The persisted warning streak
was 26. All report and quarantine records remain available; none was deleted or
rewritten.

| Classification | Evidence and disposition |
| --- | --- |
| Confirmed parser/transformation defects | None identified in this snapshot. Required-field and declaration-ID checks were zero, catastrophic row reductions were zero, and the report completed before the memory failure. This does not prove every source field is correct. |
| Known source-data issues | 13,110 duplicate declaration-ID findings and 23,854 repeated-name findings. Names are not identity keys; duplicate IDs and all source rows remain retained. The 297 negative incomes, 45 negative assets, and 10 incomes above €10 million remain review flags. HATVP has acknowledged entry errors and later amendments; some negative bank-account balances can reflect overdrafts. No value was corrected. |
| Expected/statistical outliers | 2,081 income and 703 asset robust outliers are descriptive review flags, not proof of error. The report also records 257 income sections with no populated rows. These are preserved as warnings. |
| False-positive risk | Repeated-name findings would be false positives if treated as same-person evidence. The existing rule labels them as warnings and explicitly retains them; no name-based deduplication was added. A generic negative-asset flag can include a valid overdraft, so the source remains visible for review. |
| New unexplained regression | None indicated by this report: structural error checks are zero, catastrophic reductions are zero, and the flagged-record increase is below the existing regression threshold. The new actionable issue was ingestion memory exhaustion, not source quality. |

The warning event logic previously emitted `quality_warning_streak` on every
warning report once streak reached two, including unchanged findings. A
same-date replay on Oct 26 also incremented the streak because the failed run
overwrote the quality report that the unchanged `state/latest.json` pointed to.
This produced warning events at streaks 21, 22, and 23 for Oct 26, then 24 on
Oct 27. On Nov 16, both failed attempts logged streak 26 because processed
state still pointed to Nov 2. These repeated events can reopen the weekly
auto-closing alert for already-reviewed findings.

The repair leaves warning checks, the two-snapshot threshold, and the 10%
quality-regression threshold unchanged. It hashes stable warning evidence,
ignoring only snapshot/provenance metadata. The initial second-snapshot alert
still fires; after that, another warning event fires only when the finding
fingerprint changes. Reprocessing a date already present in successful state
does not increment its streak. Reports and quarantine artifacts still contain
all warnings. The live Monitoring policy was not changed. Because older reports
do not have fingerprints, the first post-deployment run can emit one baseline
event while recording the new fingerprint.

## Repairs and validation

- `src/hatvp/pipeline/flow.py`: after Bronze persistence, remove parsed tables
  outside `SILVER_TABLES` from the live mapping before Silver construction.
  Bronze, Silver, Gold, publication-state, and provenance contracts are
  unchanged.
- `src/hatvp/quality/helpers.py`, `telemetry.py`, and `__init__.py`: add a
  compact stable fingerprint, make same-date streak calculation
  idempotent, and emit alert events only at the initial threshold or when
  warning evidence changes.
- `tests/test_pipeline_memory.py` and `tests/test_quality_alerts.py`: cover the
  Bronze-before-release boundary, Silver input preservation, stable/changeable
  fingerprints, same-date retries, and aggregate-only warning checks.
- `tests/test_pipeline_failures.py`: make the BigQuery failure fixture simulate
  some tables loading before failure; assert processed state remains unchanged.
  The loader emits `bigquery_load_complete` only after all table operations
  return, and pipeline completion/state advancement follow that point.
- `README.md`, `ops/monitoring/README.md`, `TODO.md`, and `CHANGELOG.md`:
  document alert behavior, current operational state, and this investigation.
- `reports/00-index.md` indexes the report. The prior long-form tracking files
  are preserved in [`the TODO archive`](../../documentation_archive/20261121T192159Z_TODO.md)
  and [`the changelog archive`](../../documentation_archive/20261121T192159Z_CHANGELOG.md).

Focused validation passed: 15 tests across the new regressions, existing
quality telemetry, and pipeline failure tests. The requested full CI sequence
also passed: `uv sync --locked`, Ruff check, Ruff format check, `uv build`, and
`uv run pytest` (192 passed). These local commands ran on Python 3.14.7. The
historical CI reference to `src/hatvp/layers/history_paths.py` does not match
the current repository; that file is absent. The current line-budget test now
passes for every tracked module.

The push-triggered [GitHub Actions run 44941647862](https://github.com/louispaulet/YAHATVP/actions/runs/44941647862)
completed successfully: the test job passed all requested CI steps using
Python 3.12, deployment configuration passed, and the deploy job completed.
The Cloud Run Job is now Ready on commit
`f67575622f7c26012ad9673653c59ee7707d8e2b`, image digest
`sha256:d31c2180f8a8a14034a663030bfbecaf188b4a4268c65b40628bc4c00d5e15ee`.
Its verified profile remains 8 vCPU, 32 GiB, one retry, and 1800-second
timeout. Deployment did not start an execution: the latest execution remains
the failed Nov 16 run and `state/latest.json` still records Nov 2.

## Resource comparison and operational follow-up

The failure occurred on the unchanged 8-vCPU/32-GiB profile after roughly 20
minutes. Storage measured 1.387 GB raw, 501 MB Bronze, 266 MB Silver, 200 MB
Gold, and 13 MB anomaly registry. These are object sizes, not process memory
measurements. The code repair releases the six non-Silver table lists (about
753,751 current rows) before building cumulative Silver; there is no
post-repair production RSS or duration measurement yet. Keep the 32 GiB limit
until a successful scheduled run supplies evidence for any resource-profile
change.

The Nov 16 hashes differ from processed state, so that snapshot still needs
normal processing. The enabled weekly scheduler is set for Nov 23 at 07:00
Europe/Paris (06:00 UTC). No forced replay was started. Review that scheduled
execution for all 13 BigQuery tables,
`pipeline_complete`, state advancement after full success, retained historical
Silver/publication behavior, and absence of a new memory failure. Any manual
replay requires explicit production approval. Continue human review of
duplicate IDs, repeated names, negative values, and statistical outliers; do
not alter source values or alert policies to clear the existing findings.
