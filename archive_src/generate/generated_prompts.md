### PR 18036 – [link](https://github.com/PrefectHQ/prefect/pull/18036)

Prompt
------
```text
Add the referencing package to the project’s dependencies to resolve the ModuleNotFoundError when importing ObjectSchema and Schema.
```

**Linked issues**

* [#18035](https://github.com/PrefectHQ/prefect/issues/18035)

---

### PR 18018 – [link](https://github.com/PrefectHQ/prefect/pull/18018)

Prompt
------
```text
Ensure RedisLockManager is made serializable so that cached tasks using IsolationLevel.SERIALIZABLE can run under RayTaskRunner and DaskTaskRunner without pickling or tokenization errors.
```

**Linked issues**

* [#18017](https://github.com/PrefectHQ/prefect/issues/18017)

---

### PR 18013 – [link](https://github.com/PrefectHQ/prefect/pull/18013)

Prompt
------
```text
Add a ClusterRole granting get, list, and watch on namespaces and customresourcedefinitions and bind it to the worker’s ServiceAccount via a ClusterRoleBinding.
```

**Linked issues**

* [#485](https://github.com/PrefectHQ/prefect-helm/issues/485)

---

### PR 18003 – [link](https://github.com/PrefectHQ/prefect/pull/18003)

Prompt
------
```text
Extend event filtering and triggering mechanisms to allow specifying a logical operator (OR/AND) for resources_in_roles filters, introduce a label_pairs attribute to EventRelatedFilter to match multiple related resource key/value pairs, and update event triggers to natively support matching multiple related resources in a single trigger.
```

**Linked issues**

* [#16978](https://github.com/PrefectHQ/prefect/issues/16978)
* [#16979](https://github.com/PrefectHQ/prefect/issues/16979)
* [#17891](https://github.com/PrefectHQ/prefect/issues/17891)

---

### PR 17995 – [link](https://github.com/PrefectHQ/prefect/pull/17995)

Prompt
------
```text
Investigate the technical rationale behind enforcing lowercase letters, numbers, and underscores in variable names, and update the migration guide to clearly explain this restriction and guide users on renaming hyphenated identifiers.
```

**Linked issues**

* [#17865](https://github.com/PrefectHQ/prefect/issues/17865)

---

### PR 17993 – [link](https://github.com/PrefectHQ/prefect/pull/17993)

Prompt
------
```text
Catch FileNotFoundError from uv.find_uv_bin during import, fall back to a no-op or configurable binary path, and log a warning instead of allowing flows to crash when the uv binary is missing.
```

**Linked issues**

* [#17988](https://github.com/PrefectHQ/prefect/issues/17988)

---

