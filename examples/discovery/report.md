# Fossil investigation

Target: **https://github.com/django-q2/django-q2**

Case `7135c3b24f45` · Fossil 0.1.0 · 2026-10-17T23:39:06.228534+00:00

## Finding

- **https://github.com/Koed00/django-q**: `corroborated_derivation`; confidence: high (statement plus source overlap). The target explicitly describes derivation from this candidate, and distinctive application source overlap corroborates the declaration. Exact historical scope and intermediate upstreams may remain unresolved.
- **https://github.com/althonos/pronto@3384010dfb4fc7c66a219f59276adef3288a886b**: `corroborated_component`; confidence: high (component statement plus source overlap). A source file declares derivation and distinctive code overlap corroborates a component relationship. This does not establish whole-project ancestry.
- **https://github.com/adamspd/django-appointment**: `not_established`; confidence: insufficient. Available evidence does not establish a meaningful relationship. Similar descriptions, conventions, licenses, and dependencies do not establish ancestry.

Confidence labels describe evidence strength, not calibrated probabilities. No finding is a plagiarism or legal judgment.

## Scope and timeline

### https://github.com/django-q2/django-q2

120 text files; 69 source files; snapshot `06bcfba62a1ecc19381bf123b3bb86956171e6002ff54005add64f44738f96c3`.
Revision `d9814a4d63c0da9446014c5b326cd202f5440422`; dirty working tree: False; shallow history: True.
Sampled 271 commits (limit 500): committed dates 2020-07-13T17:21:32+02:00 through 2026-10-13T16:56:40+02:00.
GitHub repository created: 2022-09-03T22:01:52Z. Repository creation is not code publication or authorship.
Dependencies: asgiref, backports-zoneinfo, django, django-picklefield, importlib-metadata, sphinx-rtd-theme, sqlparse, typing-extensions, tzdata, zipp.
License/notice evidence: [LICENSE](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/LICENSE) (`f1aa85367a2ac13f9798651a429be00ccb8dc11ce76bc2c6092d0b4e5555875c`).

### https://github.com/Koed00/django-q

91 text files; 51 source files; snapshot `c8ce0f94c35183ae09445f761e4b1c024d1eea53e451e25630988bf5b2b152d6`.
Revision `85baaccd2c3adfe0a414d4237465163e9ff6e5a0`; dirty working tree: False; shallow history: True.
Sampled 500 commits (limit 500): committed dates 2016-02-03T16:41:52+01:00 through 2021-06-26T14:04:16+02:00.
GitHub repository created: 2015-06-14T12:37:08Z. Repository creation is not code publication or authorship.
Dependencies: ansicon, arrow, asgiref, blessed, django, django-picklefield, jinxed, python-dateutil, pytz, six, sqlparse, typing-extensions, wcwidth.
License/notice evidence: [LICENSE](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/LICENSE) (`f1aa85367a2ac13f9798651a429be00ccb8dc11ce76bc2c6092d0b4e5555875c`).

### https://github.com/althonos/pronto@3384010dfb4fc7c66a219f59276adef3288a886b

30 text files; 12 source files; snapshot `0602af44b7a43f33daa2af205311dc067b89e34d56b983eadf1174d4e2bb3a83`.
Revision `3384010dfb4fc7c66a219f59276adef3288a886b`; dirty working tree: False; shallow history: True.
Sampled 95 commits (limit 500): committed dates 2016-07-02T00:02:01+01:00 through 2016-08-11T21:07:41+01:00.
GitHub repository created: 2016-07-01T23:02:01Z. Repository creation is not code publication or authorship.
Dependencies: lxml, six, sphinx, sphinx-rtd-theme, sphinxcontrib-napoleon.
License/notice evidence: [LICENSE](https://github.com/althonos/pronto/blob/3384010dfb4fc7c66a219f59276adef3288a886b/LICENSE) (`589ed823e9a84c56feb95ac58e7cf384626b9cbf4fda2a907bc36e103de1bad2`).

### https://github.com/adamspd/django-appointment

230 text files; 75 source files; snapshot `aadd6b7f0daa6237ed96f17de405677657e07e9b952a8f59fef2a4736b6f89a8`.
Revision `730d2aa6ec39e9df0c39c936b4dfe9ba0f09f28b`; dirty working tree: False; shallow history: True.
Sampled 305 commits (limit 500): committed dates 2025-03-24T11:28:46+01:00 through 2026-10-08T11:36:43Z.
GitHub repository created: 2023-04-23T07:32:02Z. Repository creation is not code publication or authorship.
Dependencies: babel, colorama, django, django-phonenumber-field, django-q2, django-recurrence, icalendar, mkdocs, mkdocs-material, phonenumbers, pillow, pymdown-extensions, python-dotenv, requests, setuptools, tblib.
License/notice evidence: [LICENSE](https://github.com/adamspd/django-appointment/blob/730d2aa6ec39e9df0c39c936b4dfe9ba0f09f28b/LICENSE) (`21e270ed03515da1ce5cf2d15a293dcb5df1798a1a007d00df874d1ac2f22ec7`).

Dates can be rewritten, imported, or inherited. The earliest sampled commit is not automatically an origin date.

## Hypotheses and evidence

### https://github.com/Koed00/django-q

Hypothesis: a meaningful relationship to the target. Decision: **corroborated_derivation**.

The target explicitly describes derivation from this candidate, and distinctive application source overlap corroborates the declaration. Exact historical scope and intermediate upstreams may remain unresolved.

Direction: candidate → target (target's declaration, corroborated by overlap).

Lead provenance:
- GitHub fork parent metadata
- GitHub fork source metadata
- Target reference at README.rst:6: Django Q2 is a fork of Django Q. Big thanks to Ilan Steemers for starting this project. Unfortunately, development has stalled since June 2021. Django Q2 is the new updated version of Django Q, with dependencies updates,
- Target reference at docs/index.rst:11:     Django Q2 is a fork of Django Q. Big thanks to Ilan Steemers for starting this project. Unfortunately, development of Django Q has stalled since June 2021. Django Q2 is the new updated version of Django Q, with depen
- GitHub repositories search: django-q in:name; https://github.com/Koed00/django-q
- Target reference at CHANGELOG.md:1003: - v0.5.3 \[\#49\](https://github.com/Koed00/django-q/pull/49) (\[Koed00\](https://github.com/Koed00))
- Target reference at CHANGELOG.md:1004: - adds 'catch_up' configuration option \[\#48\](https://github.com/Koed00/django-q/pull/48) (\[Koed00\](https://github.com/Koed00))
- Target reference at CHANGELOG.md:1005: - consolidates redis ping \[\#47\](https://github.com/Koed00/django-q/pull/47) (\[Koed00\](https://github.com/Koed00))
- Target statement at [README.rst](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/README.rst#L6-L6): Django Q2 is a fork of Django Q. Big thanks to Ilan Steemers for starting this project. Unfortunately, development has stalled since June 2021. Django Q2 is the new updated version of Django Q, with dependencies updates, docs updates and several bug fixes. Original repository: https://github.com/Koed00/django-q
- Target statement at [docs/index.rst](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/docs/index.rst#L11-L11):     Django Q2 is a fork of Django Q. Big thanks to Ilan Steemers for starting this project. Unfortunately, development of Django Q has stalled since June 2021. Django Q2 is the new updated version of Django Q, with dependencies updates, docs updates and several bug fixes. Original repository: https://github.com/Koed00/django-q
Shared commit IDs (102 sampled): `029fd316f4f55b8b39741d818055e07df7811e2e`, `071d5c5507797b620fd43bd2858793c56fd3646e`, `07d0a8c0d11650cad97d0b51607499d14d329e2f`, `099d4c64c5e8d4535fb1a2e0c15aff3e1fdb2b11`, `109d078510d1cf56dc497d229f86997c804d2fac`, `10df8351ff98bc1aa3a219f7b15a7a87b82ebc3f`, `11744bf33c43bab078f396ee5965eb737b94102e`, `13632da35fe26f4e4f9b1e072150cd69a4127fb7`.

Application token coverage: 32.2%; 24 matched application files. This is a bounded lexical measurement, not an ancestry probability.

Shared dependencies (context only): asgiref, django, django-picklefield, sqlparse, typing-extensions.

2 file pairs skipped by the deterministic diff work budget; see case.json for paths. A negative result is incomplete for those pairs.

- contiguous_tokens: 821 tokens; context: application.
  Target [django_q/tasks.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tasks.py#L580-L767) lines 580–767; candidate [django_q/tasks.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tasks.py#L569-L758) lines 569–758.
  Token fingerprint `fab102bf1ca164a29298b1234e91b7d12cd8a2e307e598c8c59a99e10735b92b`.

Example from target (untrusted source text):

````text
        self.broker = broker or get_broker()
        self.cached = cached
        self.sync = sync
        self.started = False

    def append(self, func, *args, **kwargs):
        """
        add a task to the chain
        takes the same parameters as async_task()
        """
        self.chain.append((func, args, kwargs))
````

- contiguous_tokens: 564 tokens; context: application.
  Target [django_q/tasks.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tasks.py#L152-L277) lines 152–277; candidate [django_q/tasks.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tasks.py#L147-L272) lines 147–272.
  Token fingerprint `085dc0ddda07e82e58df278ad2edce3a31f1c48201b308bf7982de3ff4719c88`.

Example from target (untrusted source text):

````text
        if r is not None:
            return r
        if (time() - start) * 1000 >= wait >= 0:
            break
        sleep(0.01)


def result_cached(task_id, wait=0, broker=None):
    """
    Return the result from the cache backend
    """
````

- contiguous_tokens: 472 tokens; context: application.
  Target [django_q/tasks.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tasks.py#L349-L465) lines 349–465; candidate [django_q/tasks.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tasks.py#L342-L457) lines 342–457.
  Token fingerprint `bff60212dd98edb8e012c0a250b321b7562bc4571f42c5340777a2e0689a5792`.

Example from target (untrusted source text):

````text
                        cluster=task.get("cluster"),
                        started=task["started"],
                        stopped=task["stopped"],
                        result=task["result"],
                        group=task.get("group"),
                        success=task["success"],
                    )
                    task_list.append(t)
            return task_list
        if (time() - start) * 1000 >= wait >= 0:
            break
````

- contiguous_tokens: 948 tokens; context: test/example / test/example.
  Target [django_q/tests/test_cached.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tests/test_cached.py#L30-L130) lines 30–130; candidate [django_q/tests/test_cached.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tests/test_cached.py#L26-L126) lines 26–126.
  Token fingerprint `acabfa9bacd9805abd6f43c68a5f88e436b0d2727bfe6cb181996dc56d6ac304`.

Example from target (untrusted source text):

````text
@pytest.fixture
def broker(monkeypatch):
    monkeypatch.setattr(Conf, "DJANGO_REDIS", "default")
    return get_broker()


@pytest.mark.django_db
def test_cached(broker):
    broker.purge_queue()
    broker.cache.clear()
    group = "cache_test"
````

- contiguous_tokens: 560 tokens; context: test/example / test/example.
  Target [django_q/tests/test_cached.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tests/test_cached.py#L154-L236) lines 154–236; candidate [django_q/tests/test_cached.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tests/test_cached.py#L129-L211) lines 129–211.
  Token fingerprint `962911ee4c9e5dc0808e420de00134484c637e8c2373fe6b483dd23350c17b7b`.

Example from target (untrusted source text):

````text
@pytest.mark.django_db
def test_chain(broker):
    broker.purge_queue()
    broker.cache.clear()
    task_chain = Chain(sync=True)
    task_chain.append("math.floor", 1)
    task_chain.append("math.copysign", 1, -1)
    task_chain.append("math.floor", 2)
    assert task_chain.length() == 3
    assert task_chain.current() is None
    task_chain.run()
````

- contiguous_tokens: 207 tokens; context: application.
  Target [django_q/cluster.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/cluster.py#L129-L171) lines 129–171; candidate [django_q/cluster.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/cluster.py#L100-L142) lines 100–142.
  Token fingerprint `ee32d857f355bd0003ad38566d556c50f885e777c855ce9dc24b7245f3bda91c`.

Example from target (untrusted source text):

````text
        )
        self.stop()

    @property
    def stat(self) -> Status:
        if self.sentinel:
            return Stat.get(pid=self.pid, cluster_id=self.cluster_id)
        return Status(pid=self.pid, cluster_id=self.cluster_id)

    @property
    def name(self) -> str:
````

- contiguous_tokens: 163 tokens; context: application.
  Target [django_q/cluster.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/cluster.py#L203-L224) lines 203–224; candidate [django_q/cluster.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/cluster.py#L170-L191) lines 170–191.
  Token fingerprint `5e15fcc58f507baf10462a2e35ecf2a6fa72f1c9d1c1e480b1b493b4810a3765`.

Example from target (untrusted source text):

````text
    def start(self):
        self.broker.ping()
        self.spawn_cluster()
        self.guard()

    def status(self) -> str:
        if not self.start_event.is_set() and not self.stop_event.is_set():
            return Conf.STARTING
        elif self.start_event.is_set() and not self.stop_event.is_set():
            if self.result_queue.empty() and self.task_queue.empty():
                return Conf.IDLE
````

- contiguous_tokens: 162 tokens; context: application.
  Target [django_q/cluster.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/cluster.py#L226-L256) lines 226–256; candidate [django_q/cluster.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/cluster.py#L191-L220) lines 191–220.
  Token fingerprint `1b2cb2d34fe017050215f05b04b5ebb766391b185555ee789386146a972fa614`.

Example from target (untrusted source text):

````text
        )
        p.daemon = True
        if target == worker:
            p.daemon = Conf.DAEMONIZE_WORKERS
            p.timer = args[2]
            self.pool.append(p)
        p.start()
        return p

    def spawn_pusher(self) -> Process:
        return self.spawn_process(pusher, self.task_queue, self.event_out, self.broker)
````

- contiguous_tokens: 382 tokens; context: test/example / test/example.
  Target [django_q/tests/test_brokers.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tests/test_brokers.py#L236-L303) lines 236–303; candidate [django_q/tests/test_brokers.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tests/test_brokers.py#L248-L315) lines 248–315.
  Token fingerprint `0a65f044623538c6543c494a2af60cd3426c506d118bb731c02379368985fc31`.

Example from target (untrusted source text):

````text
        broker.acknowledge(task[0])
    assert broker.lock_size() == 0
    # delete queue
    broker.enqueue("test")
    broker.purge_queue()
    broker.delete_queue()


@pytest.mark.django_db
def test_orm(monkeypatch):
    monkeypatch.setattr(Conf, "ORM", "default")
````

- contiguous_tokens: 315 tokens; context: test/example / test/example.
  Target [django_q/tests/test_brokers.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tests/test_brokers.py#L303-L355) lines 303–355; candidate [django_q/tests/test_brokers.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tests/test_brokers.py#L315-L367) lines 315–367.
  Token fingerprint `c888c9a972bf5de38261ef8ad76e6534873eb59c9df52cb093be6276b64f6ab0`.

Example from target (untrusted source text):

````text
    monkeypatch.setattr(Conf, "MONGO", {"host": MONGO_HOST, "port": 27017})
    # check broker
    broker = get_broker(list_key="mongo_test")
    assert broker.ping() is True
    assert broker.info() is not None
    # clear before we start
    broker.delete_queue()
    # async_task
    broker.enqueue("test")
    assert broker.queue_size() == 1
    # dequeue
````

- contiguous_tokens: 269 tokens; context: test/example / test/example.
  Target [django_q/tests/test_brokers.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tests/test_brokers.py#L112-L172) lines 112–172; candidate [django_q/tests/test_brokers.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tests/test_brokers.py#L123-L183) lines 123–183.
  Token fingerprint `30a85af919bd0f9cf4c06bb9c760747ca99719a2e83f4bf3e54c5e9dc87186a0`.

Example from target (untrusted source text):

````text
@pytest.mark.skipif(
    not os.getenv("IRON_MQ_TOKEN"), reason="requires IronMQ credentials"
)
def test_ironmq(monkeypatch):
    monkeypatch.setattr(
        Conf,
        "IRON_MQ",
        {
            "token": os.getenv("IRON_MQ_TOKEN"),
            "project_id": os.getenv("IRON_MQ_PROJECT_ID"),
        },
````

- contiguous_tokens: 448 tokens; context: test/example / test/example.
  Target [django_q/tests/test_scheduler.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/tests/test_scheduler.py#L235-L334) lines 235–334; candidate [django_q/tests/test_scheduler.py](https://github.com/Koed00/django-q/blob/85baaccd2c3adfe0a414d4237465163e9ff6e5a0/django_q/tests/test_scheduler.py#L131-L230) lines 131–230.
  Token fingerprint `f3b84d5d1cfb8e6ff92a95b1b08fcf47675cbc739fbde8415a70eff72f5bd933`.

Example from target (untrusted source text):

````text
    assert schedule.next_run < timezone.now() + timedelta(hours=1)
    task = fetch(schedule.task)
    assert task is not None
    assert task.success is True
    assert task.result < 0
    # Once schedule with delete
    once_schedule = create_schedule(
        "django_q.tests.tasks.word_multiply",
        2,
        word="django",
        schedule_type=Schedule.ONCE,
````

37 further matches are recorded in case.json.

Alternative explanations: shared upstream sources, templates, vendored modules, and independent implementation remain relevant. Matching identifiers and long contiguous blocks are stronger than shared descriptions, but do not by themselves identify who copied whom.

### https://github.com/althonos/pronto@3384010dfb4fc7c66a219f59276adef3288a886b

Hypothesis: a meaningful relationship to the target. Decision: **corroborated_component**.

A source file declares derivation and distinctive code overlap corroborates a component relationship. This does not establish whole-project ancestry.

Direction: candidate → target (target's declaration, corroborated by overlap).

Lead provenance:
- Target reference at django_q/queues.py:3: https://github.com/althonos/pronto/commit/3384010dfb4fc7c66a219f59276adef3288a886b
- Target statement at [django_q/queues.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/queues.py#L3-L3): https://github.com/althonos/pronto/commit/3384010dfb4fc7c66a219f59276adef3288a886b

Application token coverage: 0.3%; 1 matched application files. This is a bounded lexical measurement, not an ancestry probability.

Shared dependencies (context only): sphinx-rtd-theme.

- contiguous_tokens: 85 tokens; context: application.
  Target [django_q/queues.py](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/queues.py#L11-L52) lines 11–52; candidate [pronto/utils.py](https://github.com/althonos/pronto/blob/3384010dfb4fc7c66a219f59276adef3288a886b/pronto/utils.py#L186-L244) lines 186–244.
  Token fingerprint `faf397e0efacbf7f2c41b4d92f2ac65815e598974dc087c9d61edb1fbe8f4c76`.

Example from target (untrusted source text):

````text
class SharedCounter:
    """A synchronized shared counter.

    The locking done by multiprocessing.Value ensures that only a single
    process or thread may read or write the in-memory ctypes object. However,
    in order to do n += 1, Python performs a read followed by a write, so a
    second process may read the old value before the new one is written by
    the first process. The solution is to use a multiprocessing.Lock to
    guarantee the atomicity of the modifications to Value.

    This class comes almost entirely from Eli Bendersky's blog:
````

Alternative explanations: shared upstream sources, templates, vendored modules, and independent implementation remain relevant. Matching identifiers and long contiguous blocks are stronger than shared descriptions, but do not by themselves identify who copied whom.

### https://github.com/adamspd/django-appointment

Hypothesis: a meaningful relationship to the target. Decision: **not_established**.

Available evidence does not establish a meaningful relationship. Similar descriptions, conventions, licenses, and dependencies do not establish ancestry.

Direction: undetermined.

Lead provenance:
- GitHub repositories search: django-q2 in:name,description,readme; https://github.com/adamspd/django-appointment

Application token coverage: 0.0%; 0 matched application files. This is a bounded lexical measurement, not an ancestry probability.

Shared dependencies (context only): django.

No sufficiently distinctive contiguous source match passed the threshold. This rejects this lead under the tested methods; it does not prove unrelatedness.

Alternative explanations: shared upstream sources, templates, vendored modules, and independent implementation remain relevant. Matching identifiers and long contiguous blocks are stronger than shared descriptions, but do not by themselves identify who copied whom.

## Discovery trail

- target evidence: Extracted 23 non-self repository references; these are leads, not ancestry findings
- code search: "generate_mo_files" → failed: GitHub HTTP 401 for /search/code?q=%22generate_mo_files%22&per_page=5; code search needs a token, and rate limits may apply
- repository search: django-q in:name → 5 results
- repository search: pronto in:name → 5 results
- repository search: django-q2 in:name,description,readme → 5 results
- Koed00/django-q: corroborated_derivation; GitHub fork parent metadata; GitHub fork source metadata; Target reference at README.rst:6: Django Q2 is a fork of Django Q. Big thanks to Ilan Steemers for starting this project. Unfortunately, development has stalled since June 2021. Django Q2 is the new updated version of Django Q, with dependencies updates,; Target reference at docs/index.rst:11:     Django Q2 is a fork of Django Q. Big thanks to Ilan Steemers for starting this project. Unfortunately, development of Django Q has stalled since June 2021. Django Q2 is the new updated version of Django Q, with depen; GitHub repositories search: django-q in:name; https://github.com/Koed00/django-q; Target reference at CHANGELOG.md:1003: - v0.5.3 \[\#49\](https://github.com/Koed00/django-q/pull/49) (\[Koed00\](https://github.com/Koed00)); Target reference at CHANGELOG.md:1004: - adds 'catch_up' configuration option \[\#48\](https://github.com/Koed00/django-q/pull/48) (\[Koed00\](https://github.com/Koed00)); Target reference at CHANGELOG.md:1005: - consolidates redis ping \[\#47\](https://github.com/Koed00/django-q/pull/47) (\[Koed00\](https://github.com/Koed00))
- althonos/pronto@3384010dfb4fc7c66a219f59276adef3288a886b: corroborated_component; Target reference at django_q/queues.py:3: https://github.com/althonos/pronto/commit/3384010dfb4fc7c66a219f59276adef3288a886b
- adamspd/django-appointment: not_established; GitHub repositories search: django-q2 in:name,description,readme; https://github.com/adamspd/django-appointment
- althonos/pronto: not examined: candidate budget; GitHub repositories search: pronto in:name; https://github.com/althonos/pronto
- bmentges/django-cart: not examined: candidate budget; GitHub repositories search: django-q2 in:name,description,readme; https://github.com/bmentges/django-cart
- chrisdl/Django-QuerySet-Cheatsheet: not examined: candidate budget; GitHub repositories search: django-q in:name; https://github.com/chrisdl/Django-QuerySet-Cheatsheet
- django-cms/django-cms-quickstart: not examined: candidate budget; GitHub repositories search: django-q in:name; https://github.com/django-cms/django-cms-quickstart
- dobarkod/django-queryinspect: not examined: candidate budget; GitHub repositories search: django-q in:name; https://github.com/dobarkod/django-queryinspect
- FormstoneClassic/Pronto: not examined: candidate budget; GitHub repositories search: pronto in:name; https://github.com/FormstoneClassic/Pronto
- LibrePhotos/librephotos: not examined: candidate budget; GitHub repositories search: django-q2 in:name,description,readme; https://github.com/LibrePhotos/librephotos
- ori-drs/pronto: not examined: candidate budget; GitHub repositories search: pronto in:name; https://github.com/ori-drs/pronto
- philipn/django-rest-framework-filters: not examined: candidate budget; GitHub repositories search: django-q2 in:name,description,readme; https://github.com/philipn/django-rest-framework-filters
- prontolabs/pronto: not examined: candidate budget; GitHub repositories search: pronto in:name; https://github.com/prontolabs/pronto
- tomwalker/django_quiz: not examined: candidate budget; GitHub repositories search: django-q in:name; https://github.com/tomwalker/django_quiz
- vadimdemedes/pronto: not examined: candidate budget; GitHub repositories search: pronto in:name; https://github.com/vadimdemedes/pronto
- wsvincent/awesome-django: not examined: candidate budget; GitHub repositories search: django-q2 in:name,description,readme; https://github.com/wsvincent/awesome-django
- GDay/django-q2: not examined: candidate budget; Target reference at README.rst:247: .. |image0| image:: https://github.com/GDay/django-q2/actions/workflows/test.yml/badge.svg?branch=master; Target reference at README.rst:248:    :target: https://github.com/GDay/django-q2/actions?query=workflow%3Atests; Target reference at README.rst:33: See the 'changelog &lt;https://github.com/GDay/django-q2/blob/master/CHANGELOG.md&gt;'__ for all changes.; Target reference at CHANGELOG.md:133: ## \[v1.5.4\](https://github.com/GDay/django-q2/tree/v1.5.4) (2023-06-29); Target reference at CHANGELOG.md:139: ## \[v1.5.3\](https://github.com/GDay/django-q2/tree/v1.5.3) (2023-05-14); Target reference at CHANGELOG.md:147: ## \[v1.5.2\](https://github.com/GDay/django-q2/tree/v1.5.2) (2023-04-13); Target reference at CHANGELOG.md:151: - Added Django 4.2 to the test matrix, fixed deprecation warning https://github.com/GDay/django-q2/pull/89; Target reference at CHANGELOG.md:154: ## \[v1.5.1\](https://github.com/GDay/django-q2/tree/v1.5.1) (2023-04-02)
- gintas/django-picklefield: not examined: candidate budget; Target reference at README.rst:39: -  'Django-picklefield &lt;https://github.com/gintas/django-picklefield&gt;'__; Target reference at docs/install.rst:53: -  'Django-picklefield &lt;https://github.com/gintas/django-picklefield&gt;'__
- jquast/blessed: not examined: candidate budget; Target reference at README.rst:107: For the management commands to work, you will need to install Blessed: &lt;https://github.com/jquast/blessed&gt;; Target reference at docs/install.rst:60: -  'Blessed &lt;https://github.com/jquast/blessed&gt;'__ is used to display the statistics in the terminal::
- ui/django-rq: not examined: candidate budget; Target reference at README.rst:239:    'Django-RQ &lt;https://github.com/ui/django-rq&gt;'__ and; Target reference at README.rst:240:    'RQ &lt;https://github.com/ui/django-rq&gt;'__
- zacharyvoase/humanhash: not examined: candidate budget; Target reference at README.rst:242:    'HumanHash &lt;https://github.com/zacharyvoase/humanhash&gt;'__
- andymccurdy/redis-py: not examined: candidate budget; Target reference at docs/brokers.rst:35: * Requires 'Redis-py &lt;https://github.com/andymccurdy/redis-py&gt;'__ client library: ''pip install redis''; Target reference at docs/configure.rst:235: For more information on these settings please refer to the 'Redis-py &lt;https://github.com/andymccurdy/redis-py&gt;'__ documentation; Target reference at docs/install.rst:64: -  'Redis-py &lt;https://github.com/andymccurdy/redis-py&gt;'__ client by Andy McCurdy is used  to interface with both the Redis::
- apps/dependabot: not examined: candidate budget; Target reference at CHANGELOG.md:483: - Bump django from 3.0.2 to 3.0.3 \[\#411\](https://github.com/Koed00/django-q/pull/411) (\[dependabot\[bot\]\](https://github.com/apps/dependabot)); Target reference at CHANGELOG.md:506: - Bump django from 2.2.5 to 2.2.8 \[\#395\](https://github.com/Koed00/django-q/pull/395) (\[dependabot\[bot\]\](https://github.com/apps/dependabot))
- boto/boto3: not examined: candidate budget; Target reference at docs/brokers.rst:60: * Requires the 'boto3 &lt;https://github.com/boto/boto3&gt;'__ client library: ''pip install boto3''; Target reference at docs/install.rst:82: - 'Boto3 &lt;https://github.com/boto/boto3&gt;'__  is used for the Amazon SQS broker in favor of the now deprecating boto library::

## Uncertainty and reproducibility

- Analysis is bounded: 1 MB per file, 50 MB per snapshot, 10,000 files; ignored build/dependency directories and non-UTF-8/binary files are not analyzed.
- Only supported source extensions are compared. Python uses native tokenization, normalizes quote style and removes docstrings; other languages/Python syntax failures use a heuristic lexer.
- Source token limits: 30,000 per file and 200,000 per snapshot. Coverage is measured only within eligible analyzed application files, not the whole repository.
- At most 60 candidate file pairs per repository are selected; pairs exceeding 500,000 estimated token-equality operations are skipped and recorded; heavy rewrites, short code, and cross-language ports may be missed.
- Confidence is a transparent rule-based label, not a statistically calibrated probability.
- Local Git-ignored files and obvious credential filenames are excluded. This is not a comprehensive secret scanner; snapshots may contain private source.
- License files are reported as evidence; no legal conclusion about license compatibility or compliance is made.
- https://github.com/django-q2/django-q2: Git history limited to depth 200 and up to 500 sampled commits; cached revision reused unless --refresh is supplied.
- https://github.com/Koed00/django-q: Git history limited to depth 200 and up to 500 sampled commits; cached revision reused unless --refresh is supplied.
- https://github.com/althonos/pronto@3384010dfb4fc7c66a219f59276adef3288a886b: Skipped per-file limit: tests/resources/cl.ont
- https://github.com/althonos/pronto@3384010dfb4fc7c66a219f59276adef3288a886b: Git history limited to depth 200 and up to 500 sampled commits; cached revision reused unless --refresh is supplied.
- https://github.com/adamspd/django-appointment: Skipped per-file limit: docs/images/logo.png
- https://github.com/adamspd/django-appointment: Git history limited to depth 200 and up to 500 sampled commits; cached revision reused unless --refresh is supplied.

The case contains the acquired text snapshots, SHA-256 file manifest, query/request trail, sampled Git history, comparisons, and algorithm parameters. Run `fossil replay PATH_TO_CASE` to verify snapshot hashes and recompute comparisons offline. Replay verifies this saved sample and recorded method, not authenticity of the editable external metadata/history ledger, completeness of the internet, or historical truth.
